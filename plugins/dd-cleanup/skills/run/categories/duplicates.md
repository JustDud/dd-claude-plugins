# Category: duplicates

Candidates, two passes:
1. Token clones: run jscpd (see `_stack.md`). Keep clones of >= 10 lines or found at >= 3 locations.
2. Semantic duplicates (same intent, different names/code - what AI agents produce most):
   - List exported/top-level functions with a one-line purpose each (grep + read signatures and docstrings).
   - Group them by intent (e.g. "format date", "retry HTTP call", "parse env var", "slugify").
   - Within each group, compare implementations and edge cases. A group with 2+ functions doing the
     same job is a candidate.
   Spawn subagents to do the grouping per top-level directory if the repo is large.

Selecting:
- Take the top 1-2 clusters only. Keep the implementation that is most used, best tested, and handles
  the most edge cases. If the implementations differ in edge cases, note the differences in the PR and
  keep behaviour identical for every caller; if that is impossible, do not merge them - add a tracker item.
- Migrate every call site in the same PR. No re-export shims unless the old name is public.
- Add the kept helper to the "Shared utilities" section of CLAUDE.md: `- <name> (<path>): <purpose>`.

Gate re-run: jscpd must show the clone gone and no new clones.
