# Pipeline calibration: Bones re-read of a seeded sample of verified_auto (12 Nov 2026, night)
Sample: 20 of 74 papers with a two-reader finding in batches 11-28, random.seed(20261112), list in pipeline_calib_sample.json.
Result: 20 of 20 papers keep at least one confirmed counted finding (Wilson 95% [0.84, 1.00]).
Rows: 22; confirmed 21; CANNOT_TELL 1 (2607.23119 F6, "three may contain a sub-solar component": the 2023-11-09 m2 90% interval
[1.01, 1.35] is not sub-solar, but "may contain" is hedged; the paper stays counted through its F5 row).
Checked by hand against text: 2405.18934 (Table I gives 2x3x10 = 60, text says 54), 2406.01784 (SFHo 5.7% vs printed 25,
SFHx 33.4% vs 22), 2409.05068 (GPU 21.75 vs 33.60 ms, ~12 not ~2), 2412.01058 (20 dB body vs ~40 dB caption, same Fig. 6).
Quotes: 92 segments machine-checked against index/text; the 9 misses are hyphenation, reader labels or joined table cells, all
found by hand in the text.
Reading: the pipeline does not over-flag against Bones. The rate gap (74/216 = 0.34 vs hand arm 12/84 = 0.14) is not reader
precision. Test queued: batches 1-7 re-drafted through the current pipeline (redraft_01..07), compared paper by paper.
