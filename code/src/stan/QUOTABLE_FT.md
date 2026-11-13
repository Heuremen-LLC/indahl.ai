# Which statuses a quote from the retrieved full-text chunks can show (frozen 12 Nov 2026, ~15:00)

This follows PLAN_A_v2.md section 2 (commit 0004ee3), applied to the standard's text only: the Test and the PRESENT and ABSENT
lines, as printed by scripts/common.py code_block.

The rule: a status is quotable when its Test can be completed from one passage of the paper body. It is not quotable when the
Test needs (a) a released file outside the PDF, (b) a recomputation or new run, or (c) a statement about every item in the paper.
ABSENT is not quotable unless the code's own Test or ABSENT line names a place where the absence is visible.

Written before any full-text teacher score was read in full. A dry run of the scorer on about a quarter of the teacher rows was
seen at 14:25. The full-text ceiling (ceiling_ft/) was known when this was written. The rule above was fixed in PLAN_A_v2 before
this file existed.

| Code | PRESENT | ABSENT | From the standard's text |
|---|---|---|---|
| F1 Self-built reference | quotable | quotable | The Test is "read how it was built". PRESENT is one passage saying the reference came from the same setup or vendor figures. The ABSENT line names a place: "a separate source named in the paper". |
| F2 Selected result | quotable | quotable | PRESENT is one passage stating the headline as a maximum, best case or projection. The ABSENT line names a place: the headline "with the row count printed" or "a single pre-named row". |
| F3 Reading without a width | quotable | not quotable | PRESENT is one bounded reading stated yes or no. ABSENT says "each bounded reading", which is a universal (c). |
| F4 Reading not released | not quotable | not quotable | Both need the paper and its files (a). "Not stated well enough to name the readings" is a claim about the whole paper (c). |
| F5 Number recomputes differently | not quotable | not quotable | The Test is "recompute" (b). |
| F6 Text differs from own table | not quotable | not quotable | The Test sets text beside a table, figure or file, which is two places, often a figure or file (a). ABSENT says "every checked statement" (c). |
| F7 Classical comparison available | not quotable | not quotable | Needs a classical run (b). |

## Cells that go on, after the ceiling (PLAN_A_v2 sections 1 and 2)
- F1 PRESENT and F2 PRESENT: quotable, and the full-text ceiling passed for both codes.
- F1 ABSENT and F2 ABSENT: quotable by the rule, but no ceiling reading exists for them. The ceiling measured only recount-flagged
  (PRESENT) evidence, and old gold cannot score ABSENT. They are held until fresh recounts record explicit ABSENT, then measured.
- F3 PRESENT: quotable, but retrieval-limited in the ceiling (10 of 20). Reported, not trained.
- F6: the ceiling was exploratory at the line, but F6 is not quotable by this rule. Out.
- F4, F5, F7: not quotable, and untested in the ceiling. Out.

**So two cells go on: F1 PRESENT and F2 PRESENT.** Two more (F1 ABSENT, F2 ABSENT) wait on fresh recounts. That is the finding
Sage asked to see stated: for most of this standard, the paper body alone cannot show the status. The standard's checks live in
files, recomputations and whole-paper scope (the full-text ceiling found 23 percent of flagged evidence outside the extracted text).
