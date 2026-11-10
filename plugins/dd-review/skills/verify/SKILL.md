---
name: verify
description: Behavioural check only - runs the app and verifies each acceptance criterion of the spec end to end with evidence (screenshots, command output). No code review. Use to confirm a feature actually works.
argument-hint: "[--spec PATH]"
disable-model-invocation: true
---
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack.py $ARGUMENTS` (if `${CLAUDE_PLUGIN_ROOT}` is not
   substituted, the scripts folder is two folders up from this skill's folder) to locate the spec.
   If there is no spec, ask the user for the acceptance criteria, or reconstruct them from the PR and
   commits into `.dd-review/intent.md` and show them to the user before running.
2. Work out how to run the app from CLAUDE.md, README and package scripts.
3. Spawn the `feature-verifier` agent with the criteria and run instructions only (not the diff).
4. Print a table: criterion, PASS / FAIL / UNVERIFIABLE, evidence. For each FAIL, give the observed vs
   expected behaviour. Do not fix anything.
