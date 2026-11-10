# Cross-model routing

Models are better at reviewing code another model wrote than their own: they tend to miss the kinds of
bugs they introduce. So the refuter (and on L/XL one correctness finder) should be a different model
family from the author.

## Pick the route once, at Step 4
1. `command -v codex` -> use Codex CLI:
   `codex exec --sandbox read-only --skip-git-repo-check "<prompt>"`
   (if your codex version lacks a flag, drop it; keep it read-only).
2. else `command -v gemini` -> `gemini -p "<prompt>"`.
3. else fall back to the in-plugin agent (`refuter`, `rechecker`, or `correctness-reviewer` run with a
   different model than the other reviewers). Note in the report: "cross-model route unavailable,
   same-family refuter used" - this is weaker evidence.

The author is assumed to be Claude unless the user says otherwise. If the author was Codex/GPT, invert:
the refuter should be a Claude agent.

Write long prompts to a file and pass them with command substitution, e.g.
`codex exec --sandbox read-only "$(cat .dd-review/refute-prompt.md)"`. Ask for JSON and parse it.
If the external call fails or times out (>10 min), fall back to the in-plugin agent and say so.

## Cross-model correctness finder (L/XL)
Send the preamble from preamble.md with the correctness role question. External models from the GPT
family tend to under-report: keep the sentence "Report ALL candidates ... with honest confidence"
and add "Aim to surface every plausible candidate; filtering happens later."

## Refuter prompt (external route) - same text as agents/refuter.md body
Paste the body of `${CLAUDE_PLUGIN_ROOT}/agents/refuter.md` (everything after the front matter), followed
by the literal SHAs, the spec path and the findings JSON.

## Re-checker prompt (external route)
Paste the body of `${CLAUDE_PLUGIN_ROOT}/agents/rechecker.md`, followed by FIX_BASE, HEAD and the
finding list.
