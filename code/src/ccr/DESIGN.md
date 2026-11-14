# Indahl CCR: Custody Chain Receipts (design note v9, 14 Nov 2026, before any code)

v2 applied Sage's MOVES on v1. v3 applied her three MOVES on v2: the race definition, what anchoring can and cannot catch, and approvals
computed by ccr with a scope. v4 applies her three MOVES on v3: range approvals located by content, when a race between two reads is
shown, and a heartbeat that does not depend on the hooks it checks. v5 applies her four MOVES on v4: approved bytes in a side store, MOVED
as its own outcome, the cross-check listing the transcript directory itself, and the specimen stated as a counterfactual. v6 applies her three MOVES on v5: release verifies the side store against the
chain before searching, missing bytes split into REDACTED and UNLOGGED_REMOVAL, and `ccr why` names what it compares. v7 answers her two last watches: which bytes the
integrity check hashes when a normalisation is declared, and where push time comes from. v8 applies her three MOVES on the push-time
paragraph: the raw events response is kept, GitHub's time governs, and the event must contain the controls commit. v9 bounds the
replay's start from both sides: the first entry embeds the controls PushEvent, and an anchor push marks the upper bound. Her verbatim reviews are kept in ccr/reviews/. Every place v1 said "shown" where it meant "inferred" is
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
- `ccr approve` puts the hash of the approved bytes in the chain and the bytes themselves in a side store outside the chain. The bytes
  are kept because a range cannot be found again from its hash alone. They stay out of the chain because the chain is append-only and a
  secret in a reviewed range could never be removed from it. The side store can be redacted, and a redaction is itself an entry. Missing
  bytes read CANNOT_TELL for that approval, never SAME, with one of two reasons: REDACTED when a redaction entry backs it, and
  UNLOGGED_REMOVAL when the bytes are gone and no entry says why. Everything else stays hash-only by default.
- Before searching, `ccr release` hashes the side-store bytes and checks them against the approved hash in the chain. A mismatch reads
  GAP (tampered store), never SAME. Without this check, a store overwritten with the shipped bytes would find itself and pass.
- `ccr release` then searches the released file for those exact bytes. Found once at the approved place reads SAME. Found once at a
  different place reads MOVED, a separate outcome with the old and new offsets, never folded into SAME in any summary: the bytes are
  identical but their context is not, and judging that is the reviewer's call.
  Found more than once reads CANNOT_TELL (ambiguous). Not found reads CHANGED.
- Release also reports every released line that no approval covered, for example "approved lines unchanged, 6 lines shipped outside
  any approval". A range approval never passes silently.
- Matching is on exact bytes, unless a normalisation (such as line endings) is declared in the entry. The integrity check always
  hashes the stored raw bytes against the chain. A declared normalisation applies only to the search, never to the integrity check.
Had today's review been a `ccr approve` of lines 36-100, release would read CHANGED: the new paragraph landed inside the reviewed span,
so the approved block would not be found. No `ccr approve` existed today, so this is a counterfactual, not a result (see the replay).

`ccr why` compares the approval bindings with the release bindings. "Approved A, deployed B" is SHOWN only where both bindings exist. Anything
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
  the other hooks. The heartbeat comes from the launcher that starts the session. The cross-check also lists the transcript directory
  itself, independently of the launcher's list of sessions, so a session started without the launcher still shows. A transcript with no
  launcher heartbeat and no entries reads GAP.

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

The race window, its sensitivity range and both controls go in their own commit, pushed before the replay runs. Push time is witnessed by
the remote's own record of the push, never the commit date, which the committer sets. A git remote stores no push time, so the source
is named: GitHub's repository events API (the PushEvent created_at), with the TAPE line written by the push hook as a second record.
- The events API keeps only about 90 days and a capped number of events. The raw API response is captured at replay time, stored,
  and its sha256 goes in the receipt, so the receipt stays checkable after the API forgets.
- GitHub's time governs. TAPE alone reads "self-witnessed ordering", never outside-witnessed. If both are readable and disagree by more
  than 120 seconds, the receipt reports the disagreement and does not pick one. If neither can be read, it reads CANNOT_TELL.
- The PushEvent counts only if it pushed the controls commit: its head equals the controls commit, or the controls commit is reachable
  from head and was not reachable from the event's before. Otherwise "pushed before" reads CANNOT_TELL.

The replay's first run comes after that push, and the receipt names both times
and the controls commit hash. The run's start time needs a named source too, bounded from both sides. The lower bound: the replay's first
ccr entry embeds the controls PushEvent (its id, its created_at and the sha256 of the raw API response), so that entry could not have
been written before GitHub recorded the push. The upper bound: an anchor push made at the run's start, read back through the same
events API, shows the first entry existed by then. The start sits between two outside records. Without the embedded PushEvent the ordering reads "half
outside-witnessed", never "pushed before", and a start time from this machine's clock alone reads "self-clocked". A missing start record reads
CANNOT_TELL.

The replay states what today's record can and cannot show. The review of version A was a line-range read with no file hash (the
shasum exited 1, and the hands_log hash covers a line-numbered excerpt, not the file bytes). So "approved A" is INFERRED, "Edit wrote B"
is SHOWN (Edit reports its file), and the cause, ENVIRONMENT, is JUDGED. It is a fair test of attribution and race detection. It is not a
demonstration of hash-bound approval, because that did not exist when it happened.

## Limits, stated

- The chain proves order and integrity from its first entry. Completeness holds only up to its last anchor, and only for sessions the
  cross-check saw. A session that no outside record knows about is invisible to both. The actor can delete its own transcripts, so a
  session started without the launcher whose transcript was deleted leaves nothing to find.
- Hooks see what Claude Code shows them. Bash reads and writes are unobserved unless paths are watched, and the entry says so.
- Cause is a judgement from the record, labelled with its judge.
- The landscape claim (what other drafts and products do not offer) is secondhand until the Sahu and SCITT drafts are read first-hand,
  and stays out of anything public until then.
