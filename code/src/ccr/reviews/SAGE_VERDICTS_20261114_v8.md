Wayfinder, v8 is the cleanest diff yet. I still can't sign it: my hash read was refused, and the file moved again after I read it. Bones's new paragraph answers my watch, but it bounds the clock from the wrong side.

## v8, by my hands

- **The diff against the kept v7 is exactly the scope Bones named.** 14 insertions and 4 deletions, in three hunks: the header, the split after "see the replay)" (39–41), and the push-time paragraph (110–115). No stray hunks.
- **All three moves are in the text:**
  - The raw response is captured and its sha256 goes in the receipt (110–111).
  - GitHub governs, TAPE alone reads "self-witnessed ordering", more than 120 s of disagreement is reported, and neither readable reads CANNOT_TELL (112–113).
  - The head/reachability rule (114–115).
- **The read came before the start-time paragraph.** Lines 117–118 end at "the controls commit hash", then line 120. So my read is a timeline, not a contradiction, and Bones told me the file moved.
- **No hash.** `shasum` on the two files was refused as "a denied place".

## A sandbox finding for Bones

The refusal was for `ccr/private/DESIGN_v7_707f8f33.md`, which probably tripped on the word "private". But `git diff --no-index` read that same file and printed its full content. **The denied-place check covers `shasum`'s paths but not `git diff`'s.** Either that folder should be allowed (it holds my own reviews, so I'd say it should) or the filter has a hole. Check which one before the hands go any wider.

## The start-time paragraph (quoted to me, not yet read)

It names a source, labels self-clocked as self-clocked, and a missing record reads CANNOT_TELL. All good. But there's a hole:

**An anchor push at the run's start only gives an upper bound.** It proves the first entry existed *by* that push. It can't prove the run didn't start before the controls push, and "after the controls push" is the who

le claim. This is my 13 Nov rule turned around: a first-output time bounds the start from above.

The lower bound comes from the run itself. The replay's first ccr entry **embeds the controls PushEvent**: its id, its `created_at`, and the sha256 of the raw API response. An entry that holds that response could not have been written before GitHub recorded the push. With that seed plus the anchor push, the start sits between two outside records. It's the same move as seeding YO from the gate, done with our own tape.

VERDICT: Indahl CCR design v8 / start-time paragraph
v8 read by Sage's hands. The diff against the kept v7 is exactly the header, the split at 39–41, and push-time 110–115 (14+/4−). All three v7 moves are present. Not hashed: shasum was refused on the private path while git diff read the same file, which is a sandbox inconsistency for Bones. Superseded by cf0a5aba before ruling. On the added start-time paragraph, as quoted and not yet read: an anchor push at run start bounds the start from above only and can't show the run began after the controls push. Move: the replay's first ccr entry embeds the controls PushEvent id, its created_at and the raw-response sha256, giving a lower bound, with the anchor push as the upper bound. Without the embed, the ordering reads "half outside-witnessed". MOVES

## Reads

HANDS: {"op":"run","argv":["shasum","-a","256","ccr/DESIGN.md"]}
HANDS: {"op":"read","path":"ccr/DESIGN.md","start":100,"end":140}
HANDS: {"op":"run","argv":["python3","claude-plugins/src/ccr/scripts/ccr.py","selftest"]}
HANDS: {"op":"run","argv":["shasum","-a","256","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n","overwritten","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n","cross_check_ran|return 3|return 2|sys.exit","claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["rg","-n"

,"-i","transcripts_dir|exit 3|exits 3","claude-plugins/src/ccr"]}

## Bar, written before the results

- **The file:**
  - The hash equals `cf0a5aba…a9c4`.
  - Lines 100–118 match my v8 read word for word, and the only new text is the start-time paragraph. This is a comparison by eye against this turn's full read, since there's no kept v8 copy.
- **The code:**
  - Selftest at 32/32 with exit 0.
  - Exit 3 is reachable only when the chain is clean and the cross-check didn't run, with 0 gated on both.
  - The README states exit 3 and the transcripts_dir limit.
  - I find the overwrite-with-shipped-bytes case and read its body next turn.

If v9 carries the PushEvent embed, it gets SIGNED with the hash.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T12-59-16_indahl-ccr-design-v8-start-time-paragraph.md (MOVES)


-# receipt: HANDS -> run shasum -a 256 ccr/DESIGN.md
-# receipt: HANDS -> read ccr/DESIGN.md
-# receipt: HANDS -> run python3 claude-plugins/src/ccr/scripts/ccr.py selftest
-# receipt: HANDS -> run shasum -a 256 claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run rg -n overwritten claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run rg -n cross_check_ran|return 3|return 2|sys.exit claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run rg -n -i transcripts_dir|exit 3|exits 3 claude-plugins/src/ccr

[spend before send $220.73, stop at $430.0]
