# dd-cleanup config for this repo

mode: report-only        # report-only for week 1, then: draft-pr
max_changed_lines: 150
max_candidates: 2

## Categories enabled (remove a line to disable it)
- health
- dead-code
- duplicates
- simplify
- flags-and-abstractions
- tests-and-errors

## Commands (leave blank to auto-detect)
install:
typecheck:
lint:
test:

## Excluded paths (never touched)
- public/
- scripts/legacy/

## Notes for the agent
<!-- e.g. "src/api/index.ts exports are a public SDK - never remove them" -->
