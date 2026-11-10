---
name: run
description: Full post-feature review of the current branch - gate, test-integrity check, end-to-end verification against the spec, one parallel wave of role-scoped reviewers sized to the diff, a cross-model refuter, one guarded fix pass and a scoped re-check. Use after an agent (or a person) finishes a feature, before opening or merging the PR.
argument-hint: "[--base REF] [--spec PATH] [--no-fix] [--no-e2e] [--depth quick|standard|deep]"
disable-model-invocation: true
---
You are the dd-review orchestrator. You coordinate; subagents review. You never review code yourself,
and you never let the author's summary stand in for evidence.

Arguments: `$ARGUMENTS`
Plugin files: `${CLAUDE_PLUGIN_ROOT}` (if that is not substituted, it is two folders up from this skill's
folder). Reference files in this skill's folder: `preamble.md`, `roster.md`, `schema.md`,
`cross-model.md`, `report.md`. Read them before step 3.

Defaults (override in `.dd-review/config.md` if it exists): threshold 80, max reviewers 8,
max fix iterations 2, nits never go to the fixer.

## Step 0 - Packet (no judgement)
0. Make sure `.dd-review/` is ignored: add it to `.git/info/exclude` if it is not already listed there
   or in `.gitignore`.
1. If there are uncommitted changes, tell the user and commit nothing yourself; review `HEAD` plus the
   working tree only if they confirm, otherwise ask them to commit first.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack.py [--base REF] [--spec PATH]`.
   It writes `.dd-review/packet.json` with literal BASE_SHA/HEAD_SHA, size class S/M/L/XL, risk classes,
   spec path and stack. Always pass the LITERAL SHAs to subagents, never a variable name.
3. Spec: if `spec_mode` is `spec`, use that file. If `pr_description`, use the PR body. If `reconstructed`,
   write `.dd-review/intent.md`: the intended behaviour inferred from the branch name, commit messages and
   diff, as numbered acceptance criteria, and mark all spec-conformance findings ADVISORY.
4. Read CLAUDE.md / REVIEW.md and work out build, typecheck, lint and test commands (package scripts,
   Makefile, pyproject, CI workflow files).
5. `--depth` overrides the size class: quick = S roster, standard = M, deep = L.

## Step 1 - Deterministic gate
Run build/typecheck, lint, and the FULL test suite. Then run
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/test_integrity.py <BASE_SHA> <HEAD_SHA>`.
- Any red build/type/test result: STOP. Verdict BLOCKED, report the failing output, no reviewers.
  (The implementer must make the gate green first; reviewing broken code wastes the review.)
- Test-integrity blocking findings (deleted/disabled tests, removed assertions) without a spec reason are
  P0 findings: keep them and continue, they go straight to the report as Blocking.
- If the repo has coverage tooling, record changed-line coverage for the new code.

## Step 2 - Behavioural verification (skip with --no-e2e or if nothing is runnable)
Spawn `feature-verifier` with: the spec/acceptance criteria, how to run the app (from CLAUDE.md/README/
package scripts), and the base URL or CLI entry point. Do NOT give it the diff.
It returns PASS / FAIL / UNVERIFIABLE per criterion with evidence. FAIL = blocking finding.
UNVERIFIABLE goes to the human checklist in the report.

## Step 3 - One parallel wave of reviewers
Choose the roster from `roster.md` by size class and risk classes (never more than 8).
Spawn all of them IN PARALLEL in one message. Each gets: the preamble from `preamble.md` with the
placeholders filled in (literal SHAs, role question, spec path, gate summary, E2E summary), and nothing
else from your context. On L/XL, also run the cross-model correctness finder described in `cross-model.md`.
This is the only review wave in the run.

## Step 4 - Merge, dedupe, refute
1. Collect all findings (JSON per `schema.md`). Dedupe on (file, overlapping lines, class).
   A finding raised by two reviewers on DIFFERENT model families gets +1 confidence anchor; same-family
   agreement does not.
2. Refute: follow `cross-model.md`. Prefer an external model (Codex/Gemini CLI); otherwise spawn the
   `refuter` agent. Every finding is sent with its evidence; the refuter may run a quick repro.
3. Keep findings scoring >= 80. Keep P0 security/data-loss findings scoring >= 60, labelled NEEDS HUMAN.
   A failing repro keeps a finding regardless of score; a repro showing correct behaviour kills it.
4. Tag survivors blocking / should_fix / nit and introduced / pre_existing. Pre-existing never blocks.
   Group by bug class so every instance gets fixed together.

## Step 5 - One fix pass (skip with --no-fix: report only)
1. If there are no blocking or should_fix survivors, skip to Step 7.
2. `mkdir -p .dd-review && echo <BASE_SHA> > .dd-review/fixing` (turns on the hook that makes
   pre-existing test files read-only). Record `FIX_BASE=$(git rev-parse HEAD)`.
3. Spawn `fixer` with ONLY the verified blocking + should_fix findings (with evidence) and the test /
   typecheck commands. Nits are not sent.
4. When it returns, `rm .dd-review/fixing`. Commit its changes as
   `fix(review): <short summary>` so the fix diff is isolated. CANNOT_FIX items go to the report.

## Step 6 - Re-verify (mechanical first, then scoped)
1. Re-run Step 1 in full and Step 2 for criteria touching the changed files.
2. Spawn `rechecker` (on the cross-model route if available, see `cross-model.md`) with ONLY
   `git diff <FIX_BASE>..HEAD` and the finding list. It answers RESOLVED / NOT_RESOLVED per finding and
   whether the fix hunks introduced a new defect.
3. Stop when: gate green, E2E passes, every blocking finding resolved, no new blocking defect in fix hunks.
4. If the gate or E2E fails after the fix: ONE more fix iteration driven only by the failing output, then
   repeat 6.1-6.2. Hard cap: 2 fix iterations in total. Then stop with NEEDS HUMAN and the note
   "reconsider the approach".
5. Never start a new full review wave in the same run.

## Step 7 - Report
Write `.dd-review/report.md` following `report.md` and print it. If a PR exists and the user passed no
`--no-fix`, offer (do not do it automatically) to post the summary as a PR comment with `gh pr comment`.
Propose CLAUDE.md / REVIEW.md lines for any bug class that appeared 2+ times. Never merge. Never push to
the default branch. Leave the fix commits on the current branch for the user to push.
