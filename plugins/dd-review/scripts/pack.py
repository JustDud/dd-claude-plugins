#!/usr/bin/env python3
"""Assemble the dd-review packet: literal SHAs, diff size class, risk classes, spec and commands.

Usage: pack.py [--base REF] [--spec PATH] [--out .dd-review/packet.json]
Prints the packet JSON and writes it to --out.
"""
import argparse, json, os, re, subprocess, sys

def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()

def default_branch():
    ref = git("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False)
    if ref:
        return ref.rsplit("/", 1)[-1]
    for b in ("main", "master", "develop"):
        if git("rev-parse", "--verify", "--quiet", f"origin/{b}", check=False) or \
           git("rev-parse", "--verify", "--quiet", b, check=False):
            return b
    return "main"

IGNORED = re.compile(r"(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|poetry\.lock|uv\.lock|Cargo\.lock|"
                     r"\.lock$|\.min\.(js|css)$|\.map$|(^|/)(dist|build|generated|__generated__|vendor)/|\.snap$)")
TEST = re.compile(r"(^|/)(tests?|__tests__)/|_test\.|\.test\.|\.spec\.|(^|/)test_[^/]+$|conftest\.py$")
RISK = {
    "auth": r"auth|login|session|token|password|permission|rbac|acl|oauth|jwt",
    "payments": r"payment|billing|invoice|stripe|checkout|price|subscription",
    "data_migration": r"migrat|schema|\.sql$|alembic|prisma",
    "public_api": r"(^|/)(api|routes?|controllers?|handlers?|openapi|graphql|proto)(/|\.)|index\.(ts|js)$|__init__\.py$",
    "ui": r"\.(tsx|jsx|vue|svelte|html|css|scss)$|(^|/)(components?|pages|app|views)/",
    "ci_config": r"(^|/)\.github/|dockerfile|docker-compose|\.ya?ml$|\.env|config",
    "input_parsing": r"pars|serial|upload|request|form|valid",
    "performance_sensitive": r"(^|/)(workers?|jobs?|queue|cron|db|repositor|query|cache)",
}

def find_spec(explicit):
    if explicit:
        return explicit if os.path.exists(explicit) else None
    for c in ("SPEC.md", "spec.md", "PLAN.md", "plan.md", "docs/SPEC.md", "docs/spec.md"):
        if os.path.exists(c):
            return c
    for d in ("docs/specs", "specs", ".plans", "docs/plans", ".planning"):
        if os.path.isdir(d):
            files = sorted((os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md")),
                           key=os.path.getmtime, reverse=True)
            if files:
                return files[0]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--spec")
    ap.add_argument("--out", default=".dd-review/packet.json")
    a = ap.parse_args()

    os.chdir(git("rev-parse", "--show-toplevel"))
    head = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    db = default_branch()
    base_ref = a.base or (f"origin/{db}" if git("rev-parse", "--verify", "--quiet", f"origin/{db}", check=False) else db)
    base = git("merge-base", base_ref, "HEAD", check=False) or git("rev-parse", base_ref)

    numstat = git("diff", "--numstat", f"{base}..{head}")
    files, counted = [], 0
    for line in numstat.splitlines():
        add, rem, path = line.split("\t", 2)
        n = (int(add) if add.isdigit() else 0) + (int(rem) if rem.isdigit() else 0)
        ignored = bool(IGNORED.search(path))
        files.append({"path": path, "lines": n, "test": bool(TEST.search(path)), "ignored": ignored})
        if not ignored:
            counted += n
    uncommitted = bool(git("status", "--porcelain", check=False))

    size = "S" if counted < 50 else "M" if counted <= 400 else "L" if counted <= 1000 else "XL"
    paths = " ".join(f["path"].lower() for f in files if not f["ignored"])
    risks = sorted(k for k, rx in RISK.items() if re.search(rx, paths))

    pr_body = None
    if subprocess.run(["which", "gh"], capture_output=True).returncode == 0:
        r = subprocess.run(["gh", "pr", "view", "--json", "title,body,url"], capture_output=True, text=True)
        if r.returncode == 0:
            pr_body = json.loads(r.stdout)

    spec = find_spec(a.spec)
    packet = {
        "base_sha": base, "head_sha": head, "base_ref": base_ref, "branch": branch,
        "default_branch": db, "uncommitted_changes": uncommitted,
        "changed_lines": counted, "size": size, "risk_classes": risks,
        "files": files, "spec_path": spec, "spec_mode": "spec" if spec else ("pr_description" if pr_body else "reconstructed"),
        "pr": pr_body,
        "has_claude_md": os.path.exists("CLAUDE.md") or os.path.exists(".claude/CLAUDE.md"),
        "has_review_md": os.path.exists("REVIEW.md"),
        "stack": [s for s, f in (("node", "package.json"), ("python", "pyproject.toml"), ("python", "requirements.txt"),
                                  ("go", "go.mod"), ("rust", "Cargo.toml")) if os.path.exists(f)],
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(packet, fh, indent=2)
    print(json.dumps(packet, indent=2))

if __name__ == "__main__":
    main()
