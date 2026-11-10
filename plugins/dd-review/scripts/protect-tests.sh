#!/usr/bin/env bash
# During a dd-review fix pass (marker .dd-review/fixing holds the base SHA), block edits to
# test files that already existed at the base commit. New test files are allowed.
# Outside a fix pass this hook does nothing. Exit code 2 blocks the tool call.
input=$(cat)
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
marker="$root/.dd-review/fixing"
[ -f "$marker" ] || exit 0
base=$(head -n1 "$marker" | tr -d '[:space:]')
[ -z "$base" ] && exit 0

if command -v jq >/dev/null 2>&1; then
  f=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
else
  f=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)
fi
[ -z "$f" ] && exit 0
rel="${f#"$root"/}"

case "$rel" in
  */test/*|test/*|*/tests/*|tests/*|*/__tests__/*|*_test.*|*.test.*|*.spec.*|*/test_*|test_*|*conftest.py|*/__snapshots__/*|*.snap)
    if git -C "$root" cat-file -e "$base:$rel" 2>/dev/null; then
      echo "dd-review: $rel is a pre-existing test file and is read-only during the fix pass. Add a new test file instead, or return CANNOT_FIX with a reason if the test itself is wrong." >&2
      exit 2
    fi ;;
esac
exit 0
