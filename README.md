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

## Install

Inside Claude Code:

```
/plugin marketplace add JustDud/dd-claude-plugins
/plugin install dd-cleanup@dd-claude-plugins
```

Or from a terminal:

```bash
claude plugin marketplace add JustDud/dd-claude-plugins
claude plugin install dd-cleanup@dd-claude-plugins
```

Restart Claude Code, then type `/dd-cleanup` to see the commands.
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
```

## Contributing

Add a plugin under `plugins/<name>/`, list it in `.claude-plugin/marketplace.json`, and run
`claude plugin validate .` before opening a PR.

## License

MIT
