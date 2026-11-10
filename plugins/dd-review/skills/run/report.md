# Report format (.dd-review/report.md)

```markdown
# dd-review: <branch> (<BASE_SHA short>..<HEAD_SHA short>)

**Verdict: READY | READY WITH NOTES | BLOCKED | NEEDS HUMAN**
<N> verified findings (<b> blocking, <s> should-fix, <n> nits) - <f> fixed in this run.
Size <S/M/L/XL>, <lines> lines, reviewers: <list>, refuter: <model/route>.

## 1. Gate
| Check | Command | Result |
(build, typecheck, lint, tests, test integrity, coverage if available - with the key output lines)

## 2. Acceptance criteria
| # | Criterion | Result | Evidence |
(PASS / FAIL / UNVERIFIABLE, with command output or screenshot path)

## 3. Verified findings
Grouped blocking -> should_fix. For each: ID, file:lines, claim, trigger, verifier score,
status (FIXED in <commit> / CANNOT_FIX: reason / OPEN).

## 4. Rejected findings
<details> list: ID, claim, refutation reason. </details>

## 5. Nits and advisory notes
Nits, simplicity and architecture notes. Not blocking.

## 6. Pre-existing issues
Found in unchanged code. Not blocking.

## 7. Human checklist
UNVERIFIABLE criteria and NEEDS HUMAN findings, as checkboxes.

## 8. Suggested CLAUDE.md / REVIEW.md additions
One line per recurring bug class.

## 9. Cost
Stages run, agents spawned, fix iterations used.
```

Verdict rules:
- BLOCKED: gate red, or an open blocking finding.
- NEEDS HUMAN: fix cap reached, a NEEDS HUMAN security/data-loss finding, or UNVERIFIABLE spec criteria
  that block confidence.
- READY WITH NOTES: no open blocking; open should_fix, nits or advisory notes.
- READY: none of the above.
