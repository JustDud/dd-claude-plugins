# Category: health

Run: install, typecheck, lint, tests, dependency audit (`npm audit --omit=dev` / `pip-audit` / `uvx pip-audit`).

- Auto-fix ONLY lint and formatting issues with the project's own fixer (`eslint --fix`, `ruff check --fix`,
  `ruff format`, `prettier --write`) in files that already have violations. Open a PR only if that
  produces changes.
- REPORT everything else: type errors, failing tests, audit advisories, outdated major versions.
  Never upgrade dependencies. Never change lockfiles.
- Write the report to `.dd-cleanup/last-report.md` and, if there are failures on the default branch,
  open (or update) a single GitHub issue titled "dd-cleanup health: <date>" with `gh issue create`.
