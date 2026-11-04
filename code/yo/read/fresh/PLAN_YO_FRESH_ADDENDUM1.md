# Addendum 1 to PLAN_YO_FRESH.md (4 Nov 2026, Sage's pre-block holes). Stamped before any adapter answers a fresh item. The plan's numbers are unchanged.
1. The constant baseline. Fresh truth counts (yf_build.py output, labels only, no model run): DATES YES 160 of 288, LINK YES 226 of 288, REQUEST YES 25 of 288.
   On DATES and LINK the majority answer is YES, so always answering NO is below the best constant. Added: the BEST CONSTANT per field = the majority truth
   answer on the fresh set (DATES YES, LINK YES, REQUEST NO). Family A2: each YO Read seed vs the best constant, per field, exact two-sided McNemar, Holm
   across its own 9. A field REPLICATES only if 2 or more of 3 YO Read seeds clear BOTH always-NO (Family A) and the best constant (Family A2). Family C
   (shuffled) is also printed against the best constant. Family B is unchanged.
2. Overlap receipt (yf_overlap.py; first run inline 4 Nov ~23:00Z, rerun as this file before this stamp): against the 671 papers of YO Read's train, valid and test splits, the 288 fresh papers share 0 normalised
   ids, 0 arXiv ids with the version stripped, 0 exact normalised titles and 0 titles with a similarity ratio above 0.9.
3. Selection and labels share a source. The 288 papers are those whose text was saved by the 1 Nov 2026 sweep's reader agents (qia_leads/sweep_20261101,
   texts_read), and their List rows, from which the truth labels come, were written by that same reading of that same text. YO's prompts are built from that
   text too. The page says so. This is a known limit, not a reason to change the test.
4. Families A, A2, B and C are separate claims, each Holm-corrected across its own 9 tests, with no correction across families. The page says so.
5. Stamp rule: the driver runs only when this addendum and the plan both carry a Bitcoin block attestation, so both blocks precede the first adapter answer.
