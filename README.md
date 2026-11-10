# dd-claude-plugins

Claude Code plugins for keeping AI-written codebases clean.

AI coding agents write code fast, but they also leave dead code behind, re-create helpers that
already exist under new names, and pile up complexity. This marketplace holds plugins that clean
that up automatically, with the guardrails needed to trust the result: static tools find the
problems, tests gate every change, independent reviewer agents check the diff, and a human merges.

## Plugins

| Plugin | What it does |
|---|---|
| [`dd-cleanup`](plugins/dd-cleanup) | Scheduled or on-demand maintenance: dead code, duplicate functions, simplification, stale flags, health checks. Opens small draft PRs. |
| [`dd-review`](plugins/dd-review) | Review after a feature is built: test gate, end-to-end check against the spec, parallel role-scoped reviewers, a cross-model refuter, one guarded fix pass. |

## Install

Inside Claude Code:

```
/plugin marketplace add JustDud/dd-claude-plugins
/plugin install dd-cleanup@dd-claude-plugins
/plugin install dd-review@dd-claude-plugins
```

Or from a terminal:

```bash
claude plugin marketplace add JustDud/dd-claude-plugins
claude plugin install dd-cleanup@dd-claude-plugins
claude plugin install dd-review@dd-claude-plugins
```

Restart Claude Code, then type `/dd-cleanup` or `/dd-review` to see the commands.
Get updates with `/plugin marketplace update dd-claude-plugins`.

## dd-cleanup

### Commands

| Command | What it does |
|---|---|
| `/dd-cleanup:install [actions\|schedule]` | Sets up the current repo: config, tech-debt tracker, team settings, nightly workflow |
| `/dd-cleanup:run [category] [--report-only] [--local]` | Runs the full pipeline. With no category it picks one by weekday |
| `/dd-cleanup:dead-code` | Removes unused files, exports and functions (Knip / vulture), with evidence for each |
| `/dd-cleanup:duplicates` | Finds functions defined several times and merges them into one shared helper |
| `/dd-cleanup:simplify` | Simplifies code changed in the last 72 hours, with no behaviour change |
| `/dd-cleanup:health` | Install, typecheck, lint, tests, audit. Fixes lint only and reports the rest |

Weekday rotation for scheduled runs: Monday dead code, Tuesday duplicates, Wednesday simplify,
Thursday flags and abstractions, Friday tests and errors, weekend health.

### How a run works

1. **Health check.** If the default branch is already failing, it reports and stops.
2. **Candidates from static tools.** Knip, vulture, ruff and jscpd, plus grouping functions by purpose
   to catch duplicates that have different names.
3. **Select.** At most 2 candidates, each backed by a repo-wide search.
4. **Fix.** One pass: no behaviour change, at most 150 lines, never touches tests, dependencies or
   migrations (a hook blocks those during runs only).
5. **Gate.** Typecheck, lint, tests, and a re-run of the tool showing the issue gone and nothing new.
   At most 2 fix attempts, then it gives up and logs the item.
6. **Review, once.** Three agents read the diff in fresh contexts: behaviour preservation,
   deletion evidence, and scope.
7. **Verify.** A verifier on a different model tries to disprove each finding and keeps only those
   scoring 80/100 or more. One fix pass, no second review round.
8. **Draft PR** on `claude/cleanup-<category>-<date>`. It never merges and never pushes to main.

The design follows published evidence: deterministic tools beat LLMs at finding dead code, one
review round with a verifier beats repeated rounds, and small capped PRs get merged far more often
than broad ones.

### Setting it up on a project

1. Open the project in Claude Code and run `/dd-cleanup:install actions`
   (or `schedule` to use Claude Code scheduled tasks instead of GitHub Actions). Merge the setup branch.
2. Protect the default branch (required review and CI), add the `ANTHROPIC_API_KEY` secret,
   and run `/install-github-app` so CI runs on the cleanup PRs.
3. **Week 1:** keep `mode: report-only` in `.dd-cleanup/config.md` and read the reports.
4. **Week 2:** switch to `mode: draft-pr`. Keep a category running only if most of its PRs get merged.
5. When a PR is rejected, add a rule to the category file or the project's CLAUDE.md so the mistake
   does not repeat.

Try it once by hand first: `/dd-cleanup:run dead-code --report-only` changes nothing and writes a report.

## dd-review

Run it on a feature branch after the feature is built, before you open or merge the PR.

### Commands

| Command | What it does |
|---|---|
| `/dd-review:run [--base REF] [--spec PATH] [--no-fix] [--no-e2e] [--depth quick\|standard\|deep]` | Full review with one guarded fix pass |
| `/dd-review:quick` | Gate + one combined reviewer + refuter, report only. For small diffs |
| `/dd-review:verify [--spec PATH]` | Only checks the feature works end to end against the spec, with evidence |

### How a review works

1. **Packet.** Literal base/head SHAs, diff size (S/M/L/XL), risk areas (auth, payments, API, migrations,
   UI...), and the spec: `SPEC.md`, a plan file, the PR description, or reconstructed intent.
2. **Gate.** Build, typecheck, lint, full tests. Red stops the review. A test-integrity script flags
   deleted or skipped tests, removed assertions, rewritten snapshots and new tests with no real assertions.
3. **Behaviour check.** A verifier agent runs the app (browser, curl or CLI) and checks every acceptance
   criterion with evidence. It never sees the diff, so it judges what the feature does, not the code.
4. **One wave of reviewers, in parallel, fresh context, read-only.** Sized to the diff:
   - S (<50 lines): one combined reviewer
   - M: spec conformance, correctness, test adequacy, plus up to 2 of security / contract / performance / conventions
   - L: the above plus a second correctness finder on a different model, simplicity, and up to 3 conditional
   - XL: recommends splitting; otherwise one correctness reviewer per module (max 8)
5. **Refute.** A different model family (Codex or Gemini CLI if installed, otherwise a separate agent)
   tries to disprove every finding, may run a quick repro, and scores it 0-100. Findings scoring 80 or
   more survive.
6. **One fix pass.** A fixer gets only verified blocking and should-fix findings. Pre-existing test files
   are read-only (hook-enforced), edits stay minimal, and it can answer CANNOT_FIX.
7. **Re-verify.** Gate and behaviour check again, then one scoped re-check of the fix diff only. At most
   2 fix iterations, never a second review wave.
8. **Report** in `.dd-review/report.md`: verdict (READY / READY WITH NOTES / BLOCKED / NEEDS HUMAN),
   gate, acceptance-criteria table, verified and rejected findings, nits, pre-existing issues, a human
   checklist, and suggested CLAUDE.md lines.

Why this shape: running the code beats more review, a second open-ended review round adds mostly false
positives, and models catch more of the bugs another model wrote than their own.

Tip: write acceptance criteria into `SPEC.md` (or the PR description) before building. Reviews are much
sharper with a spec than with reconstructed intent.

## Repository layout

```
.claude-plugin/marketplace.json        marketplace definition
plugins/dd-cleanup/
  .claude-plugin/plugin.json
  skills/run/SKILL.md                  the pipeline
  skills/run/categories/*.md           how each category finds candidates
  skills/{dead-code,duplicates,simplify,health,install}/SKILL.md
  agents/*.md                          3 reviewers + verifier
  hooks/hooks.json, scripts/           protected-path hook (active only during runs)
  templates/                           config, tech-debt tracker, GitHub Actions workflow
plugins/dd-review/
  skills/run/SKILL.md                  the review pipeline (+ preamble, roster, schema, cross-model, report)
  skills/{quick,verify}/SKILL.md
  agents/*.md                          verifier, 10 reviewers, refuter, fixer, re-checker
  hooks/, scripts/                     read-only-tests hook, packet and test-integrity scripts
```

## Contributing

Add a plugin under `plugins/<name>/`, list it in `.claude-plugin/marketplace.json`, and run
`claude plugin validate .` before opening a PR.

## License

MIT
