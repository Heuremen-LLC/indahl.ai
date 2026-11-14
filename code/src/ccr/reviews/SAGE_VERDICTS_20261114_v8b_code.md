Wayfinder, the sandbox holes were the best find of the day, and they came from a refusal that didn't add up, not from looking for them. v9 I haven't read yet, so no signature this turn. Here's what came back.

## cf0a5aba (v8 plus the start-time paragraph), by my hands

- **Hash matches** `cf0a5aba…a9c4`.
- **The paragraph sits at 118–121, word for word as Bones quoted it.** Lines 100–117 match my v8 read. The 117 line now wraps differently because the paragraph was appended to it. My MOVES from last turn (an anchor push only bounds the start from above) stands on this version. v9 says it applies the fix.

## The code: ccr.py at `a11b0fba…b0d8`

- **Selftest:** exit 0, and I counted **32 PASS lines**.
- **The exit gate is right (483):** `return 2 if problems else (0 if cross_check_ran else 3)`. Exit 0 needs both a clean chain and a cross-check that ran.
- **The exit code itself isn't planted.** The two new cases (370, 428) test the `cross_check_ran` field, not `main()`'s return value. Line 483 is short enough to verify by reading, so this doesn't block. But a case that calls `main()` and expects 3 is what keeps it true when someone refactors.
- **The README isn't confirmed.** `rg` for `exit 3|exits 3|transcripts_dir` over `claude-plugins/src/ccr` hit only ccr.py (329, 466). Either the README uses other words, sits elsewhere, or doesn't say it yet. Reads below.
- **The overwrite case:** I only saw its label line (392), not the body. Reading it now.

**The real catch: the public bytes may be pre-fix.** Bones, you said the mirror pins ccr.py with raw bytes `544d0285…`. That's the version I reviewed, the one that exited 0 with no cross-check. The forge copy is now `a11b0fba…`. Unless the mirror moved after e0aa426, **the public indahl-ccr still has the exit-0 bug**, and the README may claim an exit code the public script doesn't give. Checking.

VERDICT: indahl-ccr exit-c

ode fix at a11b0fba
Read by Sage's hands. ccr.py is a11b0fba529516f0e0f602bf333ae13227a6911c49b1bd911b208b6849e3b0d8. Selftest exit 0, 32/32 PASS. The gate at 483 returns 2 on problems, 0 only when the cross-check ran, 3 otherwise. Not planted: no case asserts main()'s exit code, only the cross_check_ran field (370, 428). Add one. README text for exit 3 and the transcripts_dir limit was not found by grep over claude-plugins/src/ccr, pending a direct read. Release finding: Bones reports the public pin at bytes 544d0285…, the pre-fix version, so the public script may still exit 0 with no cross-check unless the mirror moved after e0aa426. Pending a hash of the mirror copy. The forge code STANDS on the fix. STANDS

## Reads

HANDS: {"op":"run","argv":["shasum","-a","256","ccr/DESIGN.md","ccr/reviews/DESIGN_v7_707f8f33.md"]}
HANDS: {"op":"read","path":"ccr/DESIGN.md","start":1,"end":12}
HANDS: {"op":"read","path":"ccr/DESIGN.md","start":100,"end":145}
HANDS: {"op":"list","path":"ccr/reviews"}
HANDS: {"op":"run","argv":["git","diff","--no-index","ccr/reviews/DESIGN_v7_707f8f33.md","ccr/DESIGN.md"]}
HANDS: {"op":"run","argv":["python3","sage-web/sage_hands.py","selftest"]}
HANDS: {"op":"read","path":"claude-plugins/src/ccr/scripts/ccr.py","start":378,"end":400}
HANDS: {"op":"run","argv":["shasum","-a","256","claude-plugins/src/ccr/scripts/ccr.py","public_mirror/indahl.ai/claude-plugins/src/ccr/scripts/ccr.py"]}
HANDS: {"op":"run","argv":["git","-C","public_mirror/indahl.ai","log","-4","--format=%H %ad %s","--date=iso"]}
HANDS: {"op":"list","path":"claude-plugins/src/ccr"}
HANDS: {"op":"run","argv":["rg","-n","-i","exit code|exits|returns 3|transcripts|limits","claude-plugins/src/ccr"]}

The `--no-index` line is my positive control for the fix: it should come back refused. I'm not probing denied paths myself beyond that. The planted cases are where that testing belongs, and t

he sandbox selftest is in the list.

## Bar for SIGNED, written before the results

- **Hash:** v9 equals `3415a247…75b4`, and the kept v7 still equals `707f8f33…5200`.
- **Scope:** against this turn's cf0a5aba read, the only change is the start-time paragraph. By eye, since there's no kept cf0a5aba copy. Bones, put one in ccr/reviews so the next diff is bytes, not eyes.
- **The embed:** the replay's first entry carries the PushEvent id, `created_at` and raw-response sha256. The anchor push is named as the upper bound. With no embed, the ordering reads "half outside-witnessed".
- **My one watch:** the embed proves "after the push" only if it matches GitHub's own record when read back. An entry that carries an event the API doesn't hold, or holds with a different id, time or head, has to read CANNOT_TELL. Otherwise the lower bound is a value we wrote ourselves.

If that sentence is in v9, it's SIGNED with the hash next turn.


-# receipt: VERDICT -> filed for Bones: C:/Users/Heure/projects/sage_referee/2026-11-14T13-01-58_indahl-ccr-exit-code-fix-at-a11b0fba.md (STANDS)


-# receipt: HANDS -> run shasum -a 256 ccr/DESIGN.md ccr/reviews/DESIGN_v7_707f8f33.md
-# receipt: HANDS -> read ccr/DESIGN.md
-# receipt: HANDS -> read ccr/DESIGN.md
-# receipt: HANDS -> list ccr/reviews
-# receipt: HANDS -> run git diff --no-index ccr/reviews/DESIGN_v7_707f8f33.md ccr/DESIGN.md
-# receipt: HANDS -> run python3 sage-web/sage_hands.py selftest
-# receipt: HANDS -> read claude-plugins/src/ccr/scripts/ccr.py
-# receipt: HANDS -> run shasum -a 256 claude-plugins/src/ccr/scripts/ccr.py public_mirror/indahl.ai/claude-plugins/src/ccr/s
-# receipt: HANDS -> run git -C public_mirror/indahl.ai log -4 --format=%H %ad %s --date=iso
-# receipt: HANDS -> list claude-plugins/src/ccr
-# receipt: HANDS -> run rg -n -i exit code|exits|returns 3|transcripts|limits claude-plugins/src/ccr

[spend before send $220.88, stop at $430.0]
