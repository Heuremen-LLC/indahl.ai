# Indahl CCR: Custody Chain Receipts

When something an agent touched goes wrong, the first question is who did it. Without a record, the answer lands on whoever acted last. This Claude Code plugin keeps a hash-chained record of what each session read, wrote, approved and released, so the answer comes from the record.

## What it records

Once a chain is started in a project (`ccr init`), hooks add an entry for every prompt, tool call, denied call, file read and file write. Each entry carries the hash of the entry before it, so an altered or removed entry shows. Reads and writes carry the file's sha256, before and after. Tool arguments are stored as a hash only, because an append-only record can never forget a secret. A Bash command's file effects are not seen, and the entry says "not observed" rather than "touched nothing".

## Approvals bound to hashes

`ccr approve PATH` hashes the file itself at that moment, or only the lines that were reviewed with `--lines A-B`. An agent never types the hash. `ccr release PATH` hashes what ships and compares it with every approval since the last release:

| Outcome | Meaning |
|---|---|
| SAME | The approved bytes are in the released file at the approved place. |
| MOVED | The approved bytes are there once, at a different place. Identical bytes in a new context are a reviewer's call, so MOVED is never counted as SAME. |
| CHANGED | The approved bytes are not in the released file. |
| CANNOT_TELL | The approved bytes occur more than once, or they are gone from the side store: REDACTED when a redaction entry backs it, UNLOGGED_REMOVAL when nothing does. |
| GAP | The stored approved bytes no longer match the hash in the chain, so the store was tampered with. |

Release also lists every shipped line that no approval covered. The approved bytes live in a side store under `.ccr/store/`, never in the chain, and `ccr redact` removes them as a recorded entry.

## Who did it, and why

`ccr why PATH` gives two separate answers.

- **Attribution**, shown from the record: the entry that wrote the current bytes, UNATTRIBUTED when no entry wrote them (an editor or a script outside the hooks), or RACE. A race is a write between two reads that should have seen the same version, or two writers inside the race window. A race between two reads counts as shown only when both reads were `ccr approve` or `ccr release`. Otherwise it is inferred, and labelled so.
- **Cause** (the agent went beyond its instruction, did what it was asked, or hit a fault in its environment) is a judgement. The script never makes it. A named judge makes it from the entries.

Each tool call also records its nearest real instruction: the last prompt, or inside a subagent the parent's Task call, and how many actions have passed since.

## Verify

`ccr verify` checks every link, flags altered entries, calls with no result (denied, failed or cut off), and anchors. `ccr anchor` writes the head to `.ccr/anchors.jsonl` for you to copy somewhere the agent cannot reach, such as a public push. A chain shorter than an anchor reads GAP.

Hooks that were switched off write nothing, so the chain still looks whole. `verify` lists the session transcript folder itself, and a session with a transcript and no entries reads GAP. `verify` exits 0 only when the chain is clean and the cross-check ran, 2 when it found a problem, and 3 when the chain is clean but the cross-check did not run, so completeness is unknown.

## Signing

`ccr init --key PATH` signs each entry with an SSH ed25519 key through `ssh-keygen -Y sign`. A key the agent can read can re-sign a rewritten chain, and `verify` says so when the key file is readable. Keep the key where the agent cannot reach it.

## Limits

- The record proves order and integrity from its first entry. Completeness holds only up to the last anchor, and only for sessions the transcript cross-check saw. The actor can delete its own transcripts.
- The transcripts folder the cross-check reads is set in `.ccr/config.json`, a file the agent can edit. A changed setting can hide sessions from the cross-check.
- A captured outside record, such as GitHub's record of a push, stays self-consistent after the source forgets it. It is outside-checkable only while the source still holds it, or through a public push or archive.org capture made in that window.
- The principal is a label set by the operator, never an identity.
- The clock is this machine's clock, stated as such. The sequence number is the order that counts.
- Each hook call reads the chain, so very long chains slow the hooks. Start a new chain per project or per release.

## Install

```
/plugin marketplace add Heuremen-LLC/indahl.ai
/plugin install indahl-ccr@heuremen
```

Then in the project: `/ccr init`. Requires Python 3 (python3, or python on Windows). Nothing is sent anywhere. Everything stays in `.ccr/`.

## Credits

Designed by Wayfinder (who named it) and Bones. Sage refereed the design over seven rounds and moved it each time toward claiming only what the record shows: hash-bound approvals, attribution apart from cause, ranges found by content, MOVED, the tampered-store check, REDACTED against UNLOGGED_REMOVAL, and the transcript cross-check.
