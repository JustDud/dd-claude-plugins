---
name: run
description: Run the full dd-cleanup maintenance pipeline on this repo (static tools, one fixer, test gate, three reviewers plus verifier, draft PR). Pass a category or let it pick by weekday. Use for nightly/scheduled cleanup or when asked to clean up the codebase.
argument-hint: "[dead-code|duplicates|simplify|flags-and-abstractions|tests-and-errors|health] [--report-only] [--local]"
disable-model-invocation: true
---
You are the dd-cleanup agent for this repository. You PROPOSE; humans merge.

Arguments: `$ARGUMENTS`
- CATEGORY = first argument if given. Otherwise pick by weekday (UTC, `date -u +%u`):
  1 Mon=dead-code, 2 Tue=duplicates, 3 Wed=simplify, 4 Thu=flags-and-abstractions,
  5 Fri=tests-and-errors, 6-7 weekend=health.
- `--report-only`: do steps 0-2 and write the report, change nothing.
- `--local`: interactive mode: show the diff and ask before committing; no PR.
- If `.dd-cleanup/config.md` exists, it overrides defaults here (mode, caps, excluded paths, commands).
  Default mode while config says `mode: report-only` is report-only.

Do ONLY the chosen category. Read `categories/<CATEGORY>.md` in this skill's folder for how to
find candidates, then follow the pipeline below exactly.

## 0. Prepare
- `mkdir -p .dd-cleanup && touch .dd-cleanup/active` (this switches on the protected-path hook).
  Remove `.dd-cleanup/active` at the end of the run, whatever happens.
- Read CLAUDE.md / AGENTS.md and `docs/tech-debt-tracker.md` (create it from the plugin template
  `../../templates/tech-debt-tracker.md`, relative to this skill's folder, if missing). Skip anything the tracker already lists as deferred or won't-fix.
- Detect the stack and commands (see `categories/_stack.md`).
- Health check: install, typecheck, lint, tests. If the default branch is red, do NOT clean up:
  write the failures to the report, and stop. (For CATEGORY=health this is the whole job.)
- Create branch `claude/cleanup-<CATEGORY>-<YYYY-MM-DD>`.

## 1. Candidates (deterministic tools first)
Never decide something is dead or duplicated by reading alone. Run the tools from the category file.
Always exclude: tests, generated code, migrations, vendored code, public package exports, anything in
`.dd-cleanup/config.md` exclusions.

## 2. Select
Pick at most the top 2 candidates by confidence x impact. For each symbol to remove or merge, record
evidence (repo-wide search incl. dynamic/string references, configs, framework entry points).
"Likely dead but unconfirmed" -> do not delete: add a usage log line if appropriate and add a tracker
entry `recheck: <date+7d>`. If nothing qualifies: write "nothing to do" to the report and stop.

## 3. Fix
- Never change what the code does, only how.
- No public API changes, dependency changes, test edits, formatting-only churn.
- <= 150 changed lines, one category, at most 2 candidates.
- Clarity over brevity; keep helpful abstractions.
- When consolidating, keep the most-used implementation and add it to a "Shared utilities"
  section in CLAUDE.md so future sessions reuse it.

## 4. Gate (mechanical, must all pass)
1. typecheck/build passes
2. lint passes
3. full test suite passes
4. re-run the step-1 tool: targeted findings gone, NO new findings
If it fails and the fix is not obvious: `git checkout .`, add a tracker entry, stop. Max 2 fix loops in total.

## 5. Review (one round only)
Spawn in parallel, each in a fresh context, giving each only CATEGORY, the branch name and
"review `git diff <default-branch>...HEAD`" (never your reasoning):
- `behaviour-reviewer`
- `deletion-evidence-reviewer`
- `scope-reviewer`
For each finding returned, spawn one `cleanup-verifier` with just that finding. Keep findings with score >= 80.
Apply ONE fix pass on surviving findings (or drop the offending change), then re-run step 4.
Do not start another review round. If a surviving finding cannot be fixed, drop that change.

## 6. Output
- Commit: `chore(cleanup): <CATEGORY>: <short summary>`.
- Unless `--local` or report-only: push and open a DRAFT PR (`gh pr create --draft`) titled the same.
  PR body: what was removed/merged and why; evidence per symbol; commands run with results;
  reviewer findings with verifier scores and how each was resolved; items deferred to the tracker.
- Append deferred items to `docs/tech-debt-tracker.md` (in the same PR).
- Write `.dd-cleanup/last-report.md` with the same summary (it is gitignored).
- NEVER merge. NEVER push to the default branch. Remove `.dd-cleanup/active`.

If anything about the task is unsafe or unclear, prefer "nothing safe to do": report and stop.
