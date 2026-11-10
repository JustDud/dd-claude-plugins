#!/usr/bin/env python3
"""Detect test tampering and weak tests between two commits.

Usage: test_integrity.py BASE_SHA [HEAD_SHA]
Prints JSON: {"findings": [...], "summary": "..."}. Exit code 0 always; the orchestrator decides.
Checks: deleted test files, newly skipped/only/xfail tests, removed assertions in pre-existing tests,
changed expected values, rewritten snapshots, new test files with no (or only weak) assertions.
"""
import json, re, subprocess, sys

TEST = re.compile(r"(^|/)(tests?|__tests__)/|_test\.|\.test\.|\.spec\.|(^|/)test_[^/]+$|conftest\.py$")
SNAP = re.compile(r"\.snap$|/__snapshots__/")
ASSERT = re.compile(r"\b(assert\w*|expect\s*\(|should\.|t\.(is|equal|deepEqual|true|false|throws)|self\.assert\w+|require\.\w+|pytest\.raises)")
STRONG = re.compile(r"(toEqual|toStrictEqual|toBe\(|toThrow|toMatchObject|toHaveBeenCalledWith|assertEqual|assertRaises|"
                    r"pytest\.raises|assert\s+[^\n]*(==|!=|<|>|\bin\b|\bis\b)|deepEqual|\.equal\()")
WEAK_ONLY = re.compile(r"(toBeDefined|toBeTruthy|toBeFalsy|not\.toBeNull|toMatchSnapshot|toMatchInlineSnapshot|"
                       r"toHaveBeenCalled\(\)|assertIsNotNone|assertTrue\(|assert\s+\w+\s*$)")
SKIP = re.compile(r"(\b(it|test|describe)\.(skip|only|todo)\b|\bx(it|describe|test)\b|\bf(it|describe)\b|"
                  r"@pytest\.mark\.(skip|xfail)|pytest\.skip\(|@unittest\.skip|t\.Skip\(|#\[ignore\])")

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout

def main():
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    findings = []
    status = git("diff", "--name-status", "--find-renames", f"{base}..{head}")
    for line in status.splitlines():
        parts = line.split("\t")
        code, path = parts[0], parts[-1]
        if not (TEST.search(path) or SNAP.search(path)):
            continue
        if code.startswith("D"):
            findings.append({"severity": "blocking", "class": "test_deleted", "file": path,
                             "claim": "Pre-existing test file deleted"})
            continue
        if SNAP.search(path) and code.startswith("M"):
            findings.append({"severity": "should_fix", "class": "snapshot_rewritten", "file": path,
                             "claim": "Snapshot rewritten; confirm the new output is intended by the spec"})
            continue
        diff = git("diff", "-U0", f"{base}..{head}", "--", path)
        added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
        removed = [l[1:] for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
        if any(SKIP.search(l) for l in added):
            findings.append({"severity": "blocking", "class": "test_disabled", "file": path,
                             "claim": "Adds skip/only/xfail/todo markers",
                             "evidence": [l.strip() for l in added if SKIP.search(l)][:5]})
        if code.startswith("A"):
            body = git("show", f"{head}:{path}")
            n_assert = len(ASSERT.findall(body))
            n_strong = len(STRONG.findall(body))
            if n_assert == 0:
                findings.append({"severity": "blocking", "class": "test_no_assertions", "file": path,
                                 "claim": "New test file contains no assertions"})
            elif n_strong == 0:
                findings.append({"severity": "should_fix", "class": "test_weak_oracle", "file": path,
                                 "claim": "New tests have no value-checking assertions (only existence/truthiness/snapshot/mock-called checks)"})
        else:
            rem_asserts = [l for l in removed if ASSERT.search(l)]
            add_asserts = [l for l in added if ASSERT.search(l)]
            if len(rem_asserts) > len(add_asserts):
                findings.append({"severity": "blocking", "class": "assertions_removed", "file": path,
                                 "claim": f"{len(rem_asserts) - len(add_asserts)} assertion line(s) removed from a pre-existing test",
                                 "evidence": [l.strip() for l in rem_asserts][:5]})
            elif rem_asserts and add_asserts:
                findings.append({"severity": "should_fix", "class": "expectations_changed", "file": path,
                                 "claim": "Expected values changed in a pre-existing test; each change needs a spec reason",
                                 "evidence": [l.strip() for l in rem_asserts][:5]})
    blocking = sum(f["severity"] == "blocking" for f in findings)
    print(json.dumps({"summary": f"{len(findings)} test-integrity findings ({blocking} blocking)",
                      "findings": findings}, indent=2))

if __name__ == "__main__":
    main()
