# Notes on the 1.1.0 draft (internal, not published)

Draft of 12 November 2026. Nothing published, uploaded or pushed. DOI_PLACEHOLDER_1_1 stands where the version DOI goes. standard.status is set to released to match 1.0.1 and is yours to confirm when you ship.

Decisions that need your call
1. Section 9 of the standard calls a change to how an outcome is decided a major change. This revision is numbered 1.1.0 as asked. The public change log says so in one sentence.
2. Status reasons are the closed list of three. For QIA-F7 and FLT-44 the status rests on a numeric reading, so a CANNOT_TELL status there may carry the outcome reason of that reading. That widens the closed list slightly for those two entries.
3. Worked example. The benchmark and its body are not named in the public text, per the no-named-competitor rule. The plan is called Test A of a Heuremen LLC recount plan. Under 1.1.0 it reads CANNOT_TELL (TOO_WIDE_TO_RESOLVE) if 0.05 is taken as the size that matters. It reads CONSISTENT if 0.15 is the size that matters. The plan names both numbers and does not say which is the size that matters.
4. The 1.0.1 change log quotes the old wording of FLT-05 and FLT-23, which contains "actually" and "by hand". Those are verbatim old text.
5. JSON field change. source now holds the test provenance (published or Heuremen LLC test). The old source value (FAULTS.html, GUARDS.html) moved to text_source and now holds the published URL.
6. NIST text was read from the AI 100-1 PDF. Seven mappings removed. Four of the referee's named weak fits were kept (F1 to MAP 2.3, FLT-04 to MAP 2.3, FLT-23 to MEASURE 1.2, FLT-24 to MEASURE 2.1) because the subcategory text does fit.
7. Not carried over from 1.0.1: CHECKS.md, SHA256SUMS.txt, its .ots stamp and the web folder. They need regenerating after your review.
