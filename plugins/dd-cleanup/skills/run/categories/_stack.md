# Stack detection and default commands

Prefer commands defined in `.dd-cleanup/config.md`, then package scripts / Makefile targets, then these.

| Signal | Typecheck | Lint | Tests | Dead code | Duplicates |
|---|---|---|---|---|---|
| `package.json` + `tsconfig.json` | `npx tsc --noEmit` | `npm run lint` (or `npx eslint .`) | `npm test` | `npx knip --reporter json` (+ ESLint no-unused-vars / `tsc --noUnusedLocals --noEmit`) | `npx jscpd --min-lines 10 --reporters json --output .dd-cleanup/jscpd .` |
| `package.json` (JS only) | - | as above | `npm test` | `npx knip --reporter json` | as above |
| `pyproject.toml` / `requirements*.txt` | `pyright` or `mypy .` if configured | `ruff check .` | `pytest -q` | `vulture . --min-confidence 80` (delete only 100% items without further proof) + `ruff check --select F401,F841` | `npx jscpd --min-lines 10 --format python --reporters json --output .dd-cleanup/jscpd .` |
| `go.mod` | `go build ./...` | `go vet ./...` | `go test ./...` | `staticcheck -checks U1000 ./...` | jscpd as above |

Use pnpm/yarn/uv/poetry equivalents when their lockfile is present. If a tool is missing, run it via
`npx`/`uvx` rather than adding it as a dependency. Never add dependencies.
Monorepos: run per package that changed, or per package listed in config.
