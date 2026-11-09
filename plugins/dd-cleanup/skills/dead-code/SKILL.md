---
name: dead-code
description: Find and remove provably dead code (unused files, exports, functions) in this repo using Knip/vulture plus evidence checks, gated by tests and reviewer agents.
argument-hint: "[--report-only] [--local]"
disable-model-invocation: true
---
Read `../run/SKILL.md` (relative to this skill's folder) and follow it exactly with
CATEGORY=dead-code and these extra arguments: `$ARGUMENTS`.
The category instructions are in `../run/categories/dead-code.md`.
