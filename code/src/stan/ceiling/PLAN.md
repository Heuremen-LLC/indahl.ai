# STAN ceiling check, plan (written before any item was judged)

Question: for each dev (item, code) pair where the List marks the code PRESENT, does the title+abstract text (gold_items.json `text`) hold the evidence the recount used?

Data. Gold items with split == 'dev' only (98 items). Test split is not read for any purpose. Each item is joined by arXiv id to /Users/heuremen/bones-forge/qia_leads/matrix_page/list.json (codes, basis[code] = per-code notes) and to trackrecord/record.json (recount `found` text, used only when basis[code] is missing).
Unit. One (dev item, code) pair where the List `codes` contains the code. Pairs where the gold item lists a code the List does not are counted and reported but not judged.

Judgments: IN_ABSTRACT, PARTLY, NOT_IN_ABSTRACT, CANNOT_TELL (note too thin or absent). Quote the abstract sentence for IN_ABSTRACT and PARTLY.
Rules fixed in advance:
- F4 (reading not released: run dates, counts, circuits, job ids, data links) is an absence. An abstract can state a release but cannot show a missing release. NOT_IN_ABSTRACT, unless the abstract itself says something that settles it (for example "no data are released"), which would be IN_ABSTRACT.
- F1, F2, F3, F6, F7: IN_ABSTRACT only if the abstract itself contains the claim wording the note quotes AND the note's reason is visible from it (for example the abstract says "up to X%" and the note says that is a maximum). PARTLY if the claim wording is in the abstract but the reason needs the body, table or figure. NOT_IN_ABSTRACT if the quoted claim or the evidence is not in the abstract or needs a table, figure, file or recomputation.
- F5 (recompute) and F6 (text vs table) need the table or data by definition. IN_ABSTRACT only if the abstract contradicts itself.
- F3 (no interval on a bounded reading): IN_ABSTRACT if the abstract states a yes/no verdict on a reading with no interval printed in it, and the note says no interval. That shows presence from the abstract only for the headline sentence, so PARTLY unless the abstract is the quoted place.
- CANNOT_TELL when no basis note and no recount found text exists, or the note does not say what evidence was used.
Judge: Claude Sonnet, one reader. A person should check the seeded sample (seed 1112, 20 pairs).

Pre-registered reading (pooled IN_ABSTRACT share, Wilson 95%):
- upper end < 0.25: the abstract is the ceiling, v2 on full text is justified.
- lower end > 0.5: full text is not the main fix.
- otherwise: CANNOT_TELL, split by code.
CANNOT_TELL pairs are excluded from the denominator of both shares and reported separately. Shares are IN_ABSTRACT / (all judged non-CANNOT_TELL), and (IN_ABSTRACT+PARTLY) / same.

## Addendum (before judging, after counting pairs)
The List marks 224 pairs on the 98 dev items. 24 are Q-codes (Q9, Q12, Q13, Q17, Q18, Q19) and are outside F1 to F7, so they are not judged. The remaining 200 F1 to F7 pairs equal the gold codes exactly. One dev item (d2d4a7dab90f) has no title or text in gold_items.json, so it has an empty abstract. Its one pair (F5) rests on a released CSV and is judged NOT_IN_ABSTRACT.
Rule detail used for F3: IN_ABSTRACT when the note quotes an abstract sentence that is a verdict or point value and the note says no width or interval accompanies it. F2 "up to X" in the abstract counts as IN_ABSTRACT only when the note's reason is that the figure is a maximum.
