# Addendum 2 to PLAN_YO_FRESH.md (4 Nov 2026, Sage VERDICT 23:08Z on Addendum 1: MOVES). Stamped before any adapter answers a fresh item.
Addendum 1's baseline rules (A, A2, B, C, C2, Holm 9 each, plain accuracy) stand. What changes is the set they are scored on.
1. Why. yr_data.truth sets DATES and LINK to YES when a List entry has no F4 note, so for papers whose reader wrote no F4 note those labels are defaults,
   not reads (98 of the 288 have no F4 note). yf_build.py also accepted read labels that only start with "Full text" (123 partial reads) where yr_data.py
   requires exactly "Full text", and it skipped zenodo_* and openalex_* text files. Ten fresh papers are the same work as a paper YO Read was built on
   under another DOI (List version field "open copy read (...)"), and four more pairs were matched by Sage's dig on title or content. The exclusion set
   was rebuilt from today's List (671) instead of the 688 papers the adapters were built on (list.json.pre-removal-20261102).
2. PRIMARY set (yf_primary.py, labels only, no model run): a fresh paper is kept only if it is not in the 688, its read label is exactly "Full text",
   its List entry has an F4 note, and it is not a same-work match. Result, stated before the block: 88 papers, 264 items. Dropped: not exactly
   "Full text" 123, no F4 note 72, same work by version field 3, same work by title/content pair 2 (the other same-work papers were already dropped
   by the first two checks). YES shares: DATES 46/88 = 0.523, LINK 70/88 = 0.795, REQUEST 12/88 = 0.136. Best constant: YES, YES, NO.
3. 88 is below about 100: this test is UNDERPOWERED, and the page says so. The filter is not widened to rescue it.
4. Primary and secondary. All verdicts (REPLICATES, PASS) are read on the PRIMARY set only. The full 288 are scored the same way as a SECONDARY
   reading, printed below the primary and labelled as including default-YES labels and partial reads. The adapters answer all 288 once; the primary
   is a subset of those answers, so no item is run twice.
5. Disclosure: the per-field YES counts of the 288 were printed by yf_build.py before PLAN_YO_FRESH.md was stamped. The primary set is chosen on label
   provenance only (read label, F4 note, same-work), never on any model answer, and none exists.
6. Receipts saved before the block: KNOWN_GOOD.text (truth 1.000 and flipped 0.000 on the 288 and on the primary), PRIMARY_SET.text, and
   yf_score_tests.out (the scorer on planted perfect, planted null and planted always-YES answers). The planted runs I described at 22:52Z were run in a
   scratch folder and their output was not kept; the saved file replaces them.
7. The driver requires Bitcoin block attestations on the plan, Addendum 1 and this addendum, each verified by yf_gate.py before the first adapter loads.
8. Family B is read together with A and A2. A field's B PASS is read as "the gain needs the real answers" only if that field also REPLICATES (A and A2).
   Otherwise it prints "PASS on B alone, not read as needing the real answers". Reason: the saved planted always-YES run (yf_score_tests.out) passes B
   on LINK only because the planted self-label arm is worse, while YO Read reads nothing.
