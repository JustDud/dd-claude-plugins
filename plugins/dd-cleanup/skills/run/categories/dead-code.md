# Category: dead-code

Candidates:
1. Run the stack's dead-code tool (see `_stack.md`). For TS/JS use Knip's JSON output: unused files,
   unused exports, unused dependencies (report deps only, never edit manifests).
2. Python: `vulture` items at 100% confidence are candidates; 60-90% items need search evidence.
3. Unused locals/imports from ruff/ESLint are cheap wins; batch them only within the files you already touch.

Rules:
- Knip/vulture false positives come from dynamic imports, framework conventions, reflection and
  public exports. If one appears, add the symbol to the tool's ignore/whitelist config is NOT allowed
  in this run; record it in the tracker as a "tool config" item instead.
- "Likely dead" (reachable only via a rarely-used path): add a log line such as
  `logger.warning("dd-cleanup: possibly dead path <name> hit")` ONLY if the repo has a logger,
  and add a tracker item `recheck: <date+7d>`. Delete it on a later run if logs show no hits.
- Gate re-run: the same tool must no longer report the removed items and must report nothing new.
