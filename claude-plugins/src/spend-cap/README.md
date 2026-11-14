# Indahl Spend Cap

Agents run up cost quietly: a loop that retries, a subagent fan-out, a long unattended run. This Claude Code plugin adds a hook that runs before every tool call. It reads the session's own transcript and its subagents' transcripts, adds up the tokens recorded there, and refuses the tool call once the session is over the budget you set. The agent is told why and asked to stop and report what is done.

**What it does and does not do.** It refuses tool calls. It does not stop the session. It checks before each tool call, so the call already in flight (a long build, a subagent), any refused retries and the final report all run past the cap. It guards against a runaway loop, not against an agent that edits the budget file to keep going.

## Set a budget

Put a file at `.claude/spend-cap.json` in the project, at `~/.claude/spend-cap.json` for every project, or both. When both exist, both are enforced, so the stricter one wins and a project's file can never loosen your own cap.

```json
{ "max_tokens": 5000000, "warn_at": 0.8 }
```

`max_tokens` counts raw tokens: input, output, cache writes and cache reads, unweighted. Cache reads often dominate. In one long session we measured 1.28 billion raw tokens, of which almost all were cache reads. To count cache reads at a lower weight, set it yourself:

```json
{ "max_tokens": 200000000, "cache_read_weight": 0.1 }
```

Cache reads bill at about a tenth of input on Anthropic's list today. Check your own provider. For a cost cap, give your own prices per million tokens. None are built in, because prices change:

```json
{ "max_usd": 20, "prices_per_mtok": { "input": 5, "output": 25, "cache_write": 6.25, "cache_read": 0.5 } }
```

One price set applies to every model in the session, so a cheaper subagent model is counted at the same prices.

**A budget file that cannot be read, or one with a limit missing the numbers it needs, refuses tool calls until it is fixed or deleted.** A person who wrote a cap believes it is on. With no budget file at all, the hook does nothing.

## What you see

- When a limit's `warn_at` share is first passed (80 percent by default), one warning goes to you and to the agent, with all four token classes. Seen live on 14 Nov 2026 (Claude Code 2.1.325): the agent quoted the warning back word for word.
- Over a limit, the tool call is refused, and the agent gets the reason with the four classes. Seen live, including inside a subagent: the subagent quoted the refusal and told the person how to raise the budget instead of trying to change the file.
- If the hook cannot read the transcript, the call is allowed, with a visible note that the budget could not be checked.

## Install

```
/plugin marketplace add Heuremen-LLC/indahl.ai
/plugin install indahl-spend-cap@heuremen
```

## Check it

- `python3 scripts/spend_cap.py report <transcript.jsonl>` prints the totals for one session.
- `python3 scripts/spend_cap.py selftest` runs 21 planted cases.
- Set `INDAHL_SPEND_CAP_LOG=/path/to/file` to log, for each tool call, what the hook was handed and what it decided.

## Limits

- It counts what the transcripts record for this session and its subagents. Work started outside the session, such as a background script calling an API, is not seen.
- A new transcript starts a new count: `/clear`, resuming in a new session, or a fresh session.
- A message written on several transcript lines is counted once. In one long session's main transcript (2,455 messages), 1,762 messages repeated, always with identical usage.
- Each check runs one message behind. The message that asks for a tool call is written to the transcript after the check, so the first tool call of a session is never refused, and each agent's latest message is counted at its next call. Seen live. Overshoot grows with parallel subagents: each one's first tool call is checked before its own first message is counted. In one live run with a 100,000-token cap, the session ended at 236,083.
- Inside a subagent, the hook is handed the main session's transcript, plus the subagent's id (seen live). The subagent's own transcript, in the session's subagents folder, is read too, so the whole session counts against one budget.
- It needs a working `python3` or `python` on PATH. On Windows, `python3` is often the Microsoft Store stub, which runs nothing, so the hook command falls back to `python`. If neither runs, tool calls are refused with that reason, so the cap never goes silently off. The fallback was tested by hand in Git Bash on Windows, not yet from a live Windows Claude Code session. The selftest passes on Windows (Python 3.13).
- Each check reads every transcript file in full. On a session with 126 MB of transcripts it took 0.17 seconds with a warm disk cache, against the hook's 15-second timeout.

Standard library only. Nothing leaves the machine. Heuremen LLC, https://indahl.ai. Refereed before release by Sage, the outside referee on our work. MIT licence.

## Credits

Windows fix, 14 Nov 2026: Sage asked, Bones found and fixed. Sage, the outside referee on our work, asked whether `python3` resolves on Windows. Bones ran it on a Windows machine, found it was the Microsoft Store stub that runs nothing (exit 49), so the hook would fail without a word and the check would be silently off, and fixed it in every plugin hook. The hook now falls back to `python`.

Sage also caught, before release: the duplicate-message key that collapsed id-less lines into one, a project budget file that could loosen or disable the person's own cap, a cache-read weighting that moved the count about nine times inside the word "tokens", and the README claiming warnings reached the agent before that was seen live. She asked for the live runs that confirmed the warning, the subagent path and the deny inside a subagent.
