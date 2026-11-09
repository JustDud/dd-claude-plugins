---
name: install
description: Set up the current repo for dd-cleanup - adds config, tech-debt tracker, gitignore entries, team plugin settings and (optionally) the nightly GitHub Actions workflow or a cloud scheduled task.
argument-hint: "[actions|schedule|none]"
disable-model-invocation: true
---
Set up this repository for dd-cleanup. Templates are in `../../templates/` relative to this skill's folder.
Show the user what you will add, then do it on a branch `chore/dd-cleanup-setup` (not the default branch).

1. Create `.dd-cleanup/config.md` from `templates/config.md`. Fill in the detected install/typecheck/lint/test
   commands (see `../run/categories/_stack.md`). Keep `mode: report-only`.
2. Create `docs/tech-debt-tracker.md` from `templates/tech-debt-tracker.md` if missing.
3. Add to `.gitignore`: `.dd-cleanup/active`, `.dd-cleanup/last-report.md`, `.dd-cleanup/jscpd/`.
4. Add to `.claude/settings.json` (merge, do not overwrite) so teammates get the plugin automatically:
   ```json
   {
     "extraKnownMarketplaces": {
       "dd-claude-plugins": { "source": { "source": "github", "repo": "JustDud/dd-claude-plugins" } }
     },
     "enabledPlugins": { "dd-cleanup@dd-claude-plugins": true }
   }
   ```
   
5. If CLAUDE.md has no "Shared utilities" section, add an empty one with the line:
   "Before writing a new helper, search this list and the codebase for an existing one."
6. Scheduler, depending on `$ARGUMENTS` (ask if empty):
   - `actions`: copy `templates/dd-cleanup.yml` to `.github/workflows/dd-cleanup.yml`, and tell the
     user to add the `ANTHROPIC_API_KEY` (or `CLAUDE_CODE_OAUTH_TOKEN`) secret and install the Claude GitHub App
     (`/install-github-app`) so CI runs on the cleanup PRs.
   - `schedule`: tell the user to run `/schedule` with: "weekdays at 3:17am UK time, in this repo, run /dd-cleanup:run".
   - `none`: skip.
7. Commit `chore: set up dd-cleanup`, then remind the user:
   - protect the default branch (required review + required CI; the bot must not be able to bypass it);
   - week 1 is report-only; change `mode: draft-pr` in `.dd-cleanup/config.md` after reviewing the reports;
   - when a cleanup PR is rejected, fix the cause in the plugin or CLAUDE.md so it does not recur.
