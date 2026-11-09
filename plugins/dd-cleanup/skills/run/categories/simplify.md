# Category: simplify

Scope: only files changed on the default branch in the last 72 hours:
`git log --since=72.hours --name-only --pretty=format: origin/HEAD | sort -u`
(fall back to the last 20 commits if nothing changed). Skip files over 800 lines unless the change
is local to one function.

Look for, in priority order:
- redundant code paths, dead branches, impossible conditions
- needless abstraction: single-use wrappers, pass-through layers, one-implementation interfaces
- deep nesting that early returns would flatten
- nested ternaries, clever one-liners that hide intent
- copy-pasted blocks within the same file
- obvious inefficiencies with zero behaviour change (repeated work in loops, N+1 lookups on in-memory data)

Do not: rename public things, reformat whole files, change error messages, or "improve" working code
just for taste. Clarity over brevity. Keep abstractions that serve tests or callers.

Gate: typecheck, lint, tests; no tool re-run needed beyond lint.
