# Indahl CCR: Custody Chain Receipts (design note v4, 14 Nov 2026, before any code)

v2 applied Sage's MOVES on v1. v3 applied her three MOVES on v2: the race definition, what anchoring can and cannot catch, and approvals
computed by ccr with a scope. v4 applies her three MOVES on v3: range approvals located by content, when a race between two reads is
shown, and a heartbeat that does not depend on the hooks it checks. Her verbatim reviews are kept in ccr/private/. Every place v1 said "shown" where it meant "inferred" is
split below into what the chain SHOWS and what a reader JUDGES.

Wayfinder named it. Banks hold back on agents partly because nothing answers "who did this" with proof, so blame lands on the newest
actor. Today's crossed stream is the specimen: a source file was edited while a ship was running, the build read the edited file, and the
outside review covered version A while version B shipped. With a chain that binds approvals to hashes, that reads as a fact: approved A,
shipped B, and which entry wrote B.

## The core: approvals bound to hashes

A review, sign-off or verification is an entry that names the exact hashes it approved. A ship, deploy or release is an entry that names
the exact hashes it sent out. `ccr approve` and `ccr release` hash the files themselves at that moment. An agent never types the
hashes, because a typed hash is only the agent's word. Every approval carries approved_scope: the whole file, or the line range that
was actually read. A range approval never stands in for the whole file, and it is located by content, never by line number:
- `ccr approve` stores the hash of the approved bytes and the bytes themselves. The approved bytes are kept because a range cannot be
  found again from its hash alone. Everything else stays hash-only by default.
- `ccr release` searches the released file for those exact bytes. Found once reads SAME, with the line offset recorded if it moved.
  Found more than once reads CANNOT_TELL (ambiguous). Not found reads CHANGED.
- Release also reports every released line that no approval covered, for example "approved lines unchanged, 6 lines shipped outside
  any approval". A range approval never passes silently.
- Matching is on exact bytes, unless a normalisation (such as line endings) is declared in the entry.
Today's specimen reads correctly under this: the new paragraph landed inside the reviewed span, so the approved block is not found and
the result is CHANGED. `ccr why` compares the two. "Approved A, deployed B" is SHOWN only where both bindings exist. Anything
without a declared binding is INFERRED and labelled so. This is the part a bank needs, and it is v1.

## One entry

- seq, prev_hash, entry_hash (sha256 over the canonical entry), signature
- actor: session id, agent_id and agent_type when inside a subagent, model id as the transcript records it, and the principal named in
  config, marked principal_asserted_by_operator in every entry and export (it is a label, not an identity)
- instruction: a pointer to the NEAREST real instruction, which inside a subagent is the parent's Task prompt, not the user turn, plus
  the distance to it (actions since that instruction). A long autonomous run shows a long distance instead of pretending each action
  answers the user's last words.
- action: tool name and the arguments' sha256. Arguments themselves are stored only if config opts in (a secret or personal data
  cannot be removed from an append-only chain, so the default is hash-only).
- pre and post: a PreToolUse half and a PostToolUse half, paired by id. A pre with no post reads CANNOT_TELL on the result. A call the
  hooks or permissions denied is an entry too.
- reads and writes: path and sha256 (before and after for writes), with reads_observed and writes_observed set to tool (the tool
  reports its files, as Read, Edit and Write do), watched_paths (a watcher saw them) or none. A Bash build has none unless paths are
  watched, and an empty list then says "not observed", never "touched nothing".
- approval: for review entries, approved_hashes and approved_scope, computed by ccr. For release entries, released_hashes.
- verification: a read-back in the four outcomes, linked by seq, with verifier and verified_by_same_actor. An action with no read-back is
  UNVERIFIED.
- clock: wall time stated as this machine's clock, and seq, which is the order that counts

## Two answers, never one enum

`ccr why <path or hash>` gives two separate answers:
1. ATTRIBUTION, shown from the chain: which entry wrote this hash, or UNATTRIBUTED (no entry wrote it: a person in an editor, a script,
   anything outside the hooks), or GAP (a missing seq, an unpaired pre, or a head that does not match its anchor). Race detection runs
   BEFORE naming a writer. A race is either of two things: two writers to one path inside the race window, or a write to a path between
   two reads of it that a binding treats as the same version (a review read A, a write, a build read B). The second is the common one.
   Comparing the approval read against the release read is what shows it. A race between two reads is SHOWN only when both reads are
   bound by ccr (`ccr approve` and `ccr release`). Where either read is unbound, the race is INFERRED and labelled so.
2. CAUSE, judged: AGENT (went beyond its instruction), INSTRUCTION (did what it was asked), ENVIRONMENT (race, stale read, tool fault) or
   CANNOT_TELL, always with who judged it and from which entries. Cause is never presented as the same kind of proof as attribution.

## The key and the anchor

- The signing key sits outside the actor's reach: a separate user for the hook process, or a non-exportable keychain key. An agent that
  can read the key can re-sign a rewritten chain, so a reachable key voids the signatures.
- Tail truncation leaves a valid-looking chain with no gap. Only an outside copy of the head catches it, so head anchoring is v1: the
  head hash goes on our own TAPE and to a public push on a fixed cadence, and `ccr verify` compares. A head older than its anchor, or a
  chain shorter than the anchored length, reads GAP.
- Hooks switched off write nothing, so the chain stays contiguous and every anchor still matches. Anchoring cannot catch it. It shows
  only from outside the chain: a later read finds a hash no entry wrote (UNATTRIBUTED), or an outside record of sessions (the session
  transcript files, a session-start heartbeat on TAPE) shows a session with no entries. That session cross-check is v1, and a session
  with no entries reads GAP. The outside record must not come from the hook path it checks: a heartbeat written by a hook goes dark with
  the other hooks. The heartbeat comes from the launcher that starts the session, and the transcript files serve as the second record.

## v1 must include

1. Hash-bound approvals and releases computed by ccr, with approved_scope, and the comparison between them
2. The key outside the agent's reach, head anchoring, and the session cross-check for hooks switched off
3. reads_observed and writes_observed
4. Pre and post pairing, with denied calls recorded
5. The race window fixed BEFORE the replay, and a check of how far it can move before the verdict flips

## The replay, with controls set first

Built from the real logs, not a staged scene: Bones's session transcript and Sage's hands_log.jsonl (which holds her read of version A
with its output hash). The event spans three actors on two machines, so v1 imports a second chain or it sees only half. Two controls are
defined before running:
- a sequential negative: edit, then ship, then a review of the shipped hash. It must not read as a race.
- an unattributed edit from an editor outside the hooks. It must read UNATTRIBUTED.

The replay states what today's record can and cannot show. The review of version A was a line-range read with no file hash (the
shasum exited 1, and the hands_log hash covers a line-numbered excerpt, not the file bytes). So "approved A" is INFERRED, "Edit wrote B"
is SHOWN (Edit reports its file), and the cause, ENVIRONMENT, is JUDGED. It is a fair test of attribution and race detection. It is not a
demonstration of hash-bound approval, because that did not exist when it happened.

## Limits, stated

- The chain proves order and integrity from its first entry. Completeness holds only up to its last anchor, and only for sessions the
  cross-check saw. A session that no outside record knows about is invisible to both.
- Hooks see what Claude Code shows them. Bash reads and writes are unobserved unless paths are watched, and the entry says so.
- Cause is a judgement from the record, labelled with its judge.
- The landscape claim (what other drafts and products do not offer) is secondhand until the Sahu and SCITT drafts are read first-hand,
  and stays out of anything public until then.
