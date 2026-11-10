---
name: quick
description: Fast dd-review for small changes - gate, test-integrity check and one combined reviewer plus refuter, report only, no fix pass. Use for small diffs or a quick check before pushing.
argument-hint: "[--base REF] [--spec PATH]"
disable-model-invocation: true
---
Read `../run/SKILL.md` (relative to this skill's folder) and follow it with these changes:
- Force `--depth quick`: Step 3 uses only `combined-reviewer`, regardless of size.
- Skip Step 2 (no end-to-end run) unless the user passes `--e2e`.
- Skip Steps 5 and 6: report only, no fixes.
Extra arguments: `$ARGUMENTS`.
