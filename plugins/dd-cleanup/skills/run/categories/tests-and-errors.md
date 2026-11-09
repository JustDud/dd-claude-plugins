# Category: tests-and-errors

This category mostly REPORTS. Test files are protected by the hook during cleanup runs.

Candidates:
1. Flaky tests: run the suite 3 times (`--repeat`/loop) or read recent CI failures via `gh run list`
   and `gh run view --log-failed`. For each flaky test, find the root cause in NON-test code
   (race, shared state, time, ordering). Fix only if the cause is in production code; otherwise report.
2. Errors: if an error tracker is connected (e.g. Sentry via MCP), take the top unresolved error
   by frequency and root-cause it. Fix only with a reproducing test already present or describable.
3. Silent failures: grep for swallowed exceptions (`except: pass`, `catch {}`, `.catch(() => {})`)
   and unhandled promise rejections in recently changed code. Report; fix only obvious ones.
4. Tests that can never fail (no assertions, always-true asserts): REPORT ONLY, never delete.

Output: at most one PR for a production-code fix; everything else goes in the report and tracker.
