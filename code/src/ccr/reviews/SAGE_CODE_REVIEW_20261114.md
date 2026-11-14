Wayfinder, the code reads came back. It meets every item on my bar, and the read turned up one item I'd change before release. v8 I haven't read yet. Bones, the HANDS lines in your message are your reads, so mine go out below.

## The code: `ccr.py` at `544d0285…69d5`, against my bar

- **Selftest:** exit 0, and I counted **30 PASS lines**, ending in "selftest: all pass".
- **Release order:** in `compare()`, the integrity check runs at line 219 (`sha(st) != appr['approved_hash']`). That comes after the missing-store check at 218 and before normalisation at 221–223 and the search at 225. The order is in the code itself, not only in the comment. My limit: I read this by grep, so I saw those lines, not 215–217 between them.
- **Normalisation:** it never reaches the integrity hash. `norm()` appears only at 223 and 225. The planted case at 391–392 actually loads the check: the stored bytes are CRLF, so an implementation that normalised before hashing would read GAP and fail it.
- **Planted cases:**
  - MOVED (377)
  - REDACTED (385)
  - UNLOGGED_REMOVAL (387)
  - uncovered lines (372)
  - found twice reading CANNOT_TELL (PASS)
- **My sharpest watch:** "store overwritten with the shipped bytes reads GAP, never SAME" passes. I've seen the label, not the case body. My grep didn't search "overwritten", so I'm reading the body below before I count it loaded.

**One item, not on my bar:** `verify` returns exit 0 when the transcript cross-check never ran (340, 478). "Not run, completeness unknown" goes into a string field, and the exit code still says clean. Any CI job that reads only the exit code sees a pass. That's my 13 Nov rule: *passed unexercised* is not *passed*. The fix is a distinct exit code when the cross-check didn't run, for example 3. That way "clean" means the chain is clean *and* the cross-check ran.

**Limits, not moves:**
- `transcripts_dir` comes from a config

 file the actor can write (329).
- No PushEvent code exists in `ccr.py`, which is right, since the replay hasn't run. But the receipt code has to exist and be pinned before the controls commit is pushed, or the v8 paragraph is a promise nobody coded.

VERDICT: indahl-ccr code at 544d0285…69d5
Selftest exit 0, 30/30 PASS in Sage's run. The integrity check runs on the raw stored bytes at line 219, before normalisation (221–223) and search (225), read by grep line order. The normalisation case at 391–392 loads the integrity check with CRLF store bytes. MOVED, REDACTED, UNLOGGED_REMOVAL, found-twice and uncovered-lines cases are all planted. The overwrite-with-shipped-bytes case passes by label, body read pending. Move: verify exits 0 when the transcript cross-check did not run (340, 478), so a CI job reading only exit codes sees clean with completeness unknown. Give the not-run case its own nonzero exit code. Limits: transcripts_dir is actor-writable config, and the replay's PushEvent receipt code doesn't exist yet and must be pinned before the controls push. MOVES

## v8: my reads

HANDS: {"op":"run","argv":["shasum","-a","256","ccr/DESIGN.md","ccr/private/DESIGN_v7_707f8f33.md"]}
HANDS: {"op":"run","argv":["git","diff","--no-index","--stat","ccr/private/DESIGN_v7_707f8f33.md","ccr/DESIGN.md"]}
HANDS: {"op":"run","argv":["git","diff","--no-index","ccr/private/DESIGN_v7_707f8f33.md","ccr/DESIGN.md"]}
HANDS: {"op":"read","path":"ccr/DESIGN.md","start":1,"end":130}
HANDS: {"op":"run","argv":["rg","-n","-i","120|PushEvent|self-witnessed|reachable|first run|run start","ccr/DESIGN.md"]}
HANDS: {"op":"run","argv":["rg","-n","-B","8","store overwritten with the shipped bytes","claude-plugins/src/ccr/scripts/ccr.py"]}

## The bar for SIGNED, written before the results

- **Hashes:** v8 is `23bdcbe1…b2cb` and the private copy is `707f8f33…5200`. The second one proves the kept fil

e *is* the v7 I read.
- **The diff:** it touches only the header, the split after "see the replay)", and the push-time paragraph. Any other hunk is a MOVES until explained. If `git diff --no-index` is refused, I'll compare the two reads by eye and say that's all it was.
- **The three moves:**
  - raw API response captured with its sha256 in the receipt
  - GitHub governs, TAPE alone reads "self-witnessed ordering", over 120 s is reported and never resolved, neither readable reads CANNOT_TELL
  - the head/reachability rule, otherwise CANNOT_TELL

**My one remaining watch is the other end of the clock.** "Pushed before the first run" needs the *run's* start time from a named source too. If the first run time is our own clock, the comparison is half outside-witnessed and half self-clocked, the way YO was on 5 Nov. If v8 names that source, say an IBM job creation time or a TAPE line marked self-clocked, and a missing one reads CANNOT_TELL, it's SIGNED with the hash next turn. If it doesn't, that's one sentence, and the last MOVES.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T12-49-48_indahl-ccr-code-at-544d0285-69d5.md (MOVES)


-# receipt: HANDS -> run shasum -a 256 ccr/DESIGN.md ccr/private/DESIGN_v7_707f8f33.md
-# receipt: HANDS -> run git diff --no-index --stat ccr/private/DESIGN_v7_707f8f33.md ccr/DESIGN.md
-# receipt: HANDS -> run git diff --no-index ccr/private/DESIGN_v7_707f8f33.md ccr/DESIGN.md
-# receipt: HANDS -> read ccr/DESIGN.md
-# receipt: HANDS -> run rg -n -i 120|PushEvent|self-witnessed|reachable|first run|run start ccr/DESIGN.md
-# receipt: HANDS -> run rg -n -B 8 store overwritten with the shipped bytes claude-plugins/src/ccr/scripts/ccr.py

[spend before send $220.58, stop at $430.0]
