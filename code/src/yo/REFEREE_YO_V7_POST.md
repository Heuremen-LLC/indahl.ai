# REFEREE_YO_V7_POST -- outside referee for yo7_post_draft.md (read-only; checked against yo7_results.text, yo7s_results.text, PLAN_YO_V7.md, PLAN_YO_V7S.md, REFEREE_YO_V7S.md, yo7*.yaml, data7/train.jsonl, ADAPTERS files, eval6_test6 reply files, LIVE_READER_ON, yo4_compare.py outcome())

VERDICT: every number, band and outcome word in A, B and C matches the raw files. The four-outcome words follow outcome(lo, hi, 0.02). The recipe and rule accounts match the plans. Four wording flags (one is a false sentence), two minor.

## What was checked and holds
- Section A rows 2 to 10: every YO v4 value, every seed value (order 51, 52, 53, 54, 55), every difference and band, every outcome word, and every denominator (2,320 / 1,974 / 426 / 2,400 / 928 / 8). Row 5 diffs are all inside +-0.02 (52 and 55 are +0.003 [0.000, 0.010]), so "consistent for all five" holds. Row 10 FUTURE7 exact counts 8, 7, 7, 8, 8, 7 hold.
- Row 11 baselines (0.636, 0.400, nothing, all) match the TEST6 nothing/all/daterule rows.
- Row 13: 25 of 890 TEST6 replies differ between seed 51 and seed 53 (counted from eval6_test6_yo_v7 and v7c). Adapter hashes differ (36fb23d3... against 0b565243...). Seeds 51 and 53 both find 2,320 of 2,320 and R6c bands are identical. The seed 54 runaway reply is in TEST4 (REFEREE_YO_V7S item 5, structural check "no JSON: 1").
- Data: data7/train.jsonl has 11,400 rows, 9,000 audit prompts and 2,400 verdict prompts. That equals 1,200 + 1,200 + 1,200 + 600 (v6 kinds) + 2,400 whole-window + 1,200 band + 1,200 replay audit + 2,400 verdict replay (600 per truth) as PLAN_YO_V7 and yo7_data.py state. (The jsonl has only prompt/completion, so kind counts beyond the two job types rest on the plan and the builder, not on a tag in the file.)
- Rule account: first plan needed both seeds (PLAN_YO_V7 "only if both seeds pass"), seed 51 named there as the model that would go to work, seeds fixed before data was built, the retest plan needs all three new seeds (PLAN_YO_V7S), and "no seed is chosen by its scores". All hold.
- No semicolons in any publishable sentence (the only one is in the draft's own header line, which is not published).

## FLAGS

### F1 (false sentence) Section C: "none flagged more young qubits or found fewer stale ones"
Problem: seed 55 flagged more young previous-day qubits at the point level (R6a 0.003 against YO v4 0.000, +0.003 [+0.000, +0.010], consistent). "None flagged more" is false as written. What the readings show is that no seed was shown to flag more (no R6a ABOVE, no R6b false-flag ABOVE).
Fix: "and none was shown to flag more young qubits or to find fewer stale ones."

### F2 Section B: "without flagging more young qubits"
Problem: same issue. Seed 55 R6a is 0.003 against 0.000. Seed 54 R6b false flags is -0.004 [-0.034, +0.025], cannot tell, so for 54 the claim of fewer flags is not shown either way.
Fix: "without being shown to flag more young qubits".

### F3 Section B and C: "now does the live reads" / "replaces YO v4 for the live reads from 1 November 2026"
Problem: LIVE_READER_ON still reads "adapters/v4 4737100d6e008afa". Section D says the gate file changes only after the post is live. The two sentences state as done what has not happened yet.
Fix: either change LIVE_READER_ON (with sha256) before the post goes up, or write "by the rule written before training, YO v7 seed 51 replaces YO v4 for the live reads" without "now" and without a date until the file has changed.

### F4 Row 13 last sentence: "The readings were recomputed with separate code by a referee of the same model family as the writer."
Problem: not stated in REFEREE_YO_V7S.md or any raw results file. The referee file says only "independent code in /tmp/ref". It rests on CHECKS.md L12 only. It is also an AI-assistance statement on a public surface (standing rule: no AI statements on site beyond the footer rule). The same sentence did not appear in the published v5 or v6 drafts.
Fix: "The readings were recomputed with separate code from the raw reply files and agree with every row above." (Both parts are in REFEREE_YO_V7S items 1 and 2.)

### F5 (omission that reads as stronger than the record) Section C: "not shown worse within the plan's bands" covers only the share of flags that are right
Problem: the paragraph reports the one lower reading it names (R3) and not the other lower point estimates. The four-outcome verdict (row 9) is lower than YO v4 at the point level for seeds 52, 53 and 54 (0.960, 0.960, 0.965 against 0.975, all cannot tell). A reader of B and C alone sees only gains. Row 9 does carry it, so this is wording, not a missing number.
Fix: add to C: "On the four-outcome verdicts three of the five seeds read 0.960 to 0.965 against YO v4's 0.975, which the bands cannot tell apart."

### F6 (minor) Row 8: "the upper end of the band is at zero" for seeds 54 and 55
Problem: the raw upper bounds are +0.00005 (seed 54) and +0.0001 (seed 55), printed +0.000 (REFEREE_YO_V7S item 4: the bound is the discrete floor, not a margin). "At zero" is fine as a print reading, but the sentence below it ("not shown worse, which is not the same as equal") already carries the right claim.
Fix (optional): "the upper end of the band prints as +0.000".

### F7 (minor, process) Row 12 / Row 1: the retest is described correctly but the draft never says it was added after the first two seeds were read
Problem: Row 1 says "The two seeds split, so a second plan, committed before any new seed was trained". PLAN_YO_V7S says its "Why" was defined after the data. The v4 row on the lab page labels the same situation ("Seed 46 was added to the plan after the seed 45 readings were seen"). Row 12 does state it in effect. Consistency of house style only.
Fix (optional): in row 12 add "The retest was planned after the first two seeds were read."

## Wording checks passed
- No "equal" claim anywhere. Row 8 says "not the same as equal". Row 10 says eight records cannot separate them.
- No mechanism named as cause (the draft says what was restored, not why it helped).
- Section B opens with "YO v7, trained again ..." and carries no count of our things in the heading position. Section C heading "YO v7, at work" is clean.
