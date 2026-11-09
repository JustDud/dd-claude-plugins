# Category: flags-and-abstractions

Candidates:
1. Feature flags / config switches that are permanently on or off: search for the flag helper(s)
   used in this repo (e.g. `isEnabled(`, `featureFlags.`, `FLAG_`, LaunchDarkly/PostHog/Unleash calls)
   and find flags hard-coded to one value or rolled out to 0% / 100% (check config files or, if an MCP
   connector for the flag service exists, query it). Remove the dead branch and the flag reference.
   Never delete the flag in the external service; list it in the PR for a human to retire.
2. Leaky abstractions ("abstraction police"): modules reaching into another module's internals,
   UI code calling the DB/HTTP layer directly where a service layer exists, duplicated config parsing,
   layers that only forward arguments.

Rules: one flag or one abstraction fix per run. If it would exceed 150 lines, write a plan into the
tracker instead of doing it.
