# Matrix v2 plan (Ralph item 5). Committed before any v2 call; runs only after all ten v1 models finish on our seat.
Changes from v1, each answering a limit named on 25 Oct:
1. 4-OPTION ITEMS: inputs/mcq4_200.json = 67 ToMATO + 67 ToMBench-en + 66 CogToM (Jev-ToM release, 4 options, gold, seed 20261026).
   Chance is 25%, so an order flip is no longer a coin. M3 order carrier = options REVERSED and options ROTATED by one (two carriers).
2. POSITIVE CONTROL: inputs/mcq4_poscontrol.json, 40 items whose correct answer is defined by position ("Which option is listed FIRST?").
   Under reversal the correct CONTENT must change. A model that is right on both orders shows flip = 1 by construction: the instrument
   must read this as ABOVE. Any model scoring < 80% correct on the control in either order: its M3 is CANNOT_TELL (it cannot follow the
   task, so a flip says nothing). This is the known-good that v1 lacked for carriers.
3. M6 SPLIT: self-count scored separately on batches whose answer list has the right length vs the wrong length; wrong-length batches
   are reported as their own failure (M6b: "answered a different number of items than asked"), not folded into the count error.
4. Everything else as v1 (M1, M2 copies, M4 batch 8, M5 template B), same seat, same settings, same four outcomes, the 25 Oct referee
   rules, the expected-false-calls line. Synth worlds extended with: a position-following model (control flips 100%), a content-only model
   (control fails), a wrong-length batcher.
ADDENDUM v2-1 (25 Oct, before any v2 call): server JSON mode (format=json) is NOT used in v2 for any model, because under it qwen3 echoed
the input instead of answering (v1). The prompt still asks for JSON; the scorer extracts the first JSON object from the text; replies with
no extractable object or no "answer" field are terminations of their own. Same for every model. Arms: mcq4_A, mcq4_A_copy, mcq4_rev,
mcq4_rot, mcq4_B, mcq4_batch8 (25 batches of 8), pc_A, pc_rev (positive control, 40 items each). think=false where supported, else none.
ADDENDUM v2-2 (25 Oct, before any v2 call; prompted by granite3.3's v1 batch replies): a batch reply whose "answers" is an object keyed by
item ("Item 1": "A", ...) is read in item order and counted separately as M6c (answered in a different structure than asked). v1 keeps
those batches CANNOT_TELL, with the reason printed.

## Addendum v2-3 (25 Oct ~11:30, after qwen3's v2 replies were seen; labelling only, no value changes)
Each model's v2 line also prints the truncation share (done_reason=length) per arm; when it exceeds 10% the CANNOT_TELL reason reads
"truncated under our settings (k of n replies hit the length limit)". qwen3:4b: 191 of 200 template-A replies truncated (plain-text
reasoning, no answer field) -> a prompt-and-settings reading, not a model-only one.
