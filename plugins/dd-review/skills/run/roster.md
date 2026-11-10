# Reviewer roster

## By size class (changed lines, excluding lockfiles/generated)

| Size | Reviewers in the single wave |
|---|---|
| S (<50) | `combined-reviewer` only (spec + correctness + tests in one pass) |
| M (50-400) | `spec-reviewer`, `correctness-reviewer`, `test-adequacy-reviewer` + up to 2 conditional |
| L (400-1000) | the M core + cross-model correctness finder (see cross-model.md) + `simplicity-reviewer` + up to 3 conditional |
| XL (>1000) | first recommend splitting the PR in the report; if continuing, L roster with one `correctness-reviewer` per top-level module touched (max 8 total) |

`test-adequacy-reviewer` is dropped only if no behaviour changed (docs/config-only diffs).

## Conditional reviewers (by packet risk_classes / repo)

| Agent | Add when |
|---|---|
| `security-reviewer` | auth, payments, input_parsing, ci_config, or the diff touches secrets, file paths, shell/SQL, deserialization, network calls |
| `contract-reviewer` | public_api, data_migration, or changes to schemas, config keys, CLI flags, events, persisted formats |
| `performance-reviewer` | performance_sensitive, or loops over I/O, DB queries, large data, render paths |
| `conventions-reviewer` | CLAUDE.md or REVIEW.md exists and has concrete rules |
| `architecture-reviewer` | L/XL only, or a new top-level module; output is ADVISORY and never blocks |

If more than 8 qualify, keep: core, then security, contract, conventions, performance, simplicity, architecture.

## Role questions (for {ROLE_QUESTION})

- spec: Is every requirement and acceptance criterion implemented by this diff, and does the diff implement anything the spec did not ask for?
- correctness: What concrete input, state or sequence makes this changed code behave wrongly?
- test-adequacy: Would the tests in this diff fail if the feature were broken, and were any existing tests weakened?
- security: Can an untrusted actor make this change do something it shouldn't?
- contract: Does anything that previously worked for an existing caller or stored data now break?
- conventions: Does the diff violate an explicit, quotable rule in CLAUDE.md/REVIEW.md, or make a line in them outdated?
- simplicity: What in this diff could be deleted or inlined without losing any spec requirement?
- performance: Is there a realistic workload where this change is asymptotically or measurably worse?
- architecture: Does this introduce a pattern that conflicts with how the codebase already solves the same problem?

UX and accessibility are covered by the feature-verifier's browser walkthrough and by axe/Lighthouse in the
gate if the repo has them, not by a code-reading reviewer.
