# Lexical baseline on gold dev (12 Nov ~15:05)
Defined in PLAN_A_v2 section 4: any content word of the PRESENT line in the top 6 chunks means PRESENT. Run: lexical/lexical_baseline.py,
result in lexical/dev_result.json.

As defined, it calls PRESENT on almost everything for F1, F2 and F6. Cue words like "result", "figure" and "table" appear in almost
any paper. On fresh gold it would act as the always-PRESENT constant for those codes. F3: PRESENT on 18 of 22 flagged against 42 of
70 unflagged, difference 0.218, Newcombe 95 percent [-0.011, 0.378]. The interval reaches zero, so it is CANNOT_TELL. F1: difference
0.059 [-0.084, 0.142].

The definition was pre-registered and is not changed here. A stricter cue rule (phrase cues, or a count threshold) would have to be
fixed before any fresh recount is read. That is a question for Sage.
