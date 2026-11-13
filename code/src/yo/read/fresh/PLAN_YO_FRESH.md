# YO Read FRESH TEST (4 Nov 2026). FROZEN when its OpenTimestamps proof reaches a Bitcoin block; no model answers a fresh item before that block.
Question: on papers no YO Read arm has ever seen, (1) does YO Read still beat always answering NO, and (2) with about twice the papers, does it beat the
SELF-LABEL adapters, which the first test (148 papers, three seeds) could not show on DATES or LINK?
Items: every QIA List entry whose "read" starts "Full text", whose normalised id (yr_data.norm) is NOT among the 671 papers of YO Read's train, valid
or test splits, and that has a saved text in qia_leads/sweep_20261101/texts_read, sweep_20261101/texts or backfill_20261101/texts (searched in that
order; first hit used). Count at planning: 288 papers (864 items). Prompts, candidate sentences, the 1,900-token trim and labels (yr_data.truth on the
List entry) are built by yr_data.py's functions, unchanged, by fresh/yf_build.py. The List file is hashed when items are built; items are hashed
(DATA_YO_FRESH.sha256) before any model runs. A paper whose text file is empty is left out and counted.
Known-good before any model: the truth arm scores 1.000 per field and the flipped truth 0.000 (yr_known_good.known_good), or nothing runs.
Arms, all existing and hash-checked (ADAPTERS_YO_READ.sha256, ADAPTERS_YO_SHUFFLED.sha256, ADAPTERS_SELFLABEL.sha256): YO Read seeds 61-63,
SELF-LABEL 74-76, SHUFFLED 71-73, always-NO. Decoding and parse exactly as yr_rescore_eval.py (greedy, max_tokens 8, case-sensitive YES/NO).
Family A (replication): each YO Read seed vs always-NO per field, exact two-sided McNemar, Holm across 9. Clears = accuracy above always-NO AND
Holm p < 0.05 (PREREG_YO_RESCORE line 15). REPLICATES on a field if 2 or more of 3 seeds clear.
Family B (labels): YO Read seed i vs SELF-LABEL seed 73+i per field, same test, Holm across 9, separate family. PASS on a field if YO Read beats
all three. Otherwise the field reads "not shown to need the real answers", never "self-labels are as good".
Family C (shuffled, smoke alarm): each SHUFFLED seed vs always-NO, Holm across 9. Any shuffled seed that clears DATES or LINK is printed beside A.
Prediction, written before data: A replicates on DATES and LINK; B passes on DATES; B on LINK cannot be predicted.
Reporting: every arm, every seed, raw counts and (b, c); unread counts wrong. The first 148-paper results are never pooled with these.
Known limits, said on the page: labels come from the List's own reading and some will be wrong (5 of 148 LINK labels were in the first test);
the fresh papers were not picked at random (they are the ones whose text was saved by a later reader pass).
One GPU job at a time on the Mac. No training in this round.
