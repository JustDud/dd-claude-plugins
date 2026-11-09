#!/usr/bin/env bash
# Blocks edits to tests, migrations, generated code and lockfiles, but ONLY while a
# cleanup run is active (marker file .dd-cleanup/active exists in the repo root).
# Normal coding sessions are unaffected. Exit code 2 blocks the tool call.
input=$(cat)
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
[ -f "$root/.dd-cleanup/active" ] || exit 0

if command -v jq >/dev/null 2>&1; then
  f=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
else
  f=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)
fi
[ -z "$f" ] && exit 0

# Extra protected globs can be listed one per line in .dd-cleanup/protected
extra=""
[ -f "$root/.dd-cleanup/protected" ] && extra=$(grep -v '^\s*#' "$root/.dd-cleanup/protected")

case "$f" in
  *.dd-cleanup/*) exit 0 ;;
  */test/*|*/tests/*|*/__tests__/*|*_test.*|*.test.*|*.spec.*|*/test_*|*conftest.py|\
  */migrations/*|*/generated/*|*/__generated__/*|*/vendor/*|\
  *package-lock.json|*pnpm-lock.yaml|*yarn.lock|*poetry.lock|*uv.lock|*.lock|\
  */.github/workflows/*)
    echo "dd-cleanup: protected path during a cleanup run: $f. Report it in the PR body or tracker instead of editing." >&2
    exit 2 ;;
esac

while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  # shellcheck disable=SC2254
  case "$f" in $pat) echo "dd-cleanup: protected by .dd-cleanup/protected ($pat): $f" >&2; exit 2 ;; esac
done <<< "$extra"
exit 0
