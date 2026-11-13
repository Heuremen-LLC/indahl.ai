# Referee, RANK New Jersey section (read-only refuting pass, 2026-11-10)

Verdict: **FIX THEN SHIP**

Code: rank_index_referee/nj/code/ (xl.py own xlsx reader, hs.py, k8.py, k8_no_eoc.py, ccd.py, particip.py, schoolday.py, claims_check.py, cds.py, copy_lint.py). Outputs: out/. Re-pulled files: dl/. Nothing imported or copied from rank_index code. UA "HeuremenRANK-referee/0.1 (+https://indahl.ai/oy)".

## Re-pulls
- nj.gov NJSLA files, 2023-24 and 2024-25: ALG01, GEO01, ALG02, ELA03-09, MAT03-08, SC05, SC08, SC11 (34 files), all HTTP 200. The five HS files are byte-identical (sha256) to the desk copies.
- nj.gov SPR 2023-24 database: HTTP 200, sha256 fd36785b...ce086b, identical to the desk copy. SPR 2024-25 read from the desk copy (sha256 546cc2c0...07ea matches desk SOURCES).
- CCD 2024-25 via Urban API: grade 9-12 counts and lunch counts for all 10 high schools, enrollment and teacher FTE for all 16 K-8 schools, FRL for 4 K-8 schools.
- CDS: Stevens 2025-26 B1 "Total All Undergraduates 4206" (rendered page 5). Rowan 2025-26 B1 "Total all undergraduates 17,157". TCNJ PDF: HTTP 403 (refusal recorded, not worked around). Montclair URL: HTTP 302 with empty body, not followed further.
- NJGPA files: guessed nj.gov paths 404, desk copies used for the suppression count only.

## Recount results (0 differences unless listed)
- High schools: every math, reading, science, graduation, enrollment and lunch figure reproduces the desk value. Math weighted values: HTHS 100.0, Edison 100.0, UCMHS 90.62, Biotech 98.8, Woodbridge 98.6, BCA 97.79, AIT 85.25, BCTHS 93.05, McNair 83.22, Allied 72.5. Science and reading sums equal the desk notes. Graduation (SPR 2023-24 FederalGraduationRates, 2024 4-year): equal for all 10. CCD: all 10 enrollments and all 30 lunch counts equal.
- K-8 display figures: all 32 desk values reproduce (both years).
- Participation: 104 rates and 104 "not in the figure" values equal. Registered To Test and Not Tested read "*" in every row for all 26 schools: 5,122 rows in 34 NJSLA files plus 551 rows in 4 NJGPA files, 0 exceptions.
- School day: SPR SchoolDay both years equal for all 26 (state prints identical values in both years).
- Schedule excerpts: every "..."-separated piece found in its saved copy (UCVTS 2025-26 calendar is an image PDF, found in ocr.txt only).
- Rank-claim quotes: 33 of 39 found as rendered text. 6 are not verbatim (see D5).

## Differences
| # | Where | Desk | Referee | Severity |
|---|---|---|---|---|
| D1 | Page line 557, NJ high school weights note | "Research activity 50, Quality assessment 25, Faculty resources 20, Student selectivity 5" | Graduate engineering/education weights. Must be the high school six (30/10/20/20/10/10) | must fix |
| D2 | McNair mathematics, MISMATCH | 80 printed vs 83.2 (ALG01+GEO01) | Arithmetic right, but US News does not name which math tests. Leaving ALG01 out reproduces all 10 printed NJ HS math figures (McNair GEO01 80.2 -> 80, UCMHS 90.6, AIT 85.2, Allied 72.5 -> 73 from 37 of 51, BCTHS 93.4, others unchanged). Same pattern in K-8: grade-level tests only, 2023-24, give 32 of 32 equal (valid rows only). "Same quantity" is not shown, so the plan reads CANNOT_TELL (definition) | must fix |
| D3 | NJ college enrollment, 5 scored rows (4 match, Stevens mismatch) | US News year "fall 2025" | No NJ capture records a year for these profiles (raw/nj_colleges_20261110.txt has none, "(fall 2025)" appears only on national list captures). Capture the year in the browser or score cannot tell (year). Stevens B1 4206 re-read and confirmed | must fix |
| D4 | Page line 554, test-file ruler | "checked at the source US News names, the state's own test files" | US News names "2023-2024 state assessment data" only. The choice of test files over SPR was made after the first run (CHECKS P10) and the page does not say so | must fix |
| D5 | Rank-claim quotes not verbatim | Biotech: two sentences spliced without a mark (the HTHS bullet between them is dropped). Spaces inserted by tag stripping: NJIT "Report ’s", Rutgers-Newark "U .S.", Princeton PAW "Universities ,", Drew "2026 list ,", Stevens "Overall U.S. News & World Report : No. 59" (heading merged, space before colon) | Rendered text: "Report’s", "U.S.", "Universities,", "2026 list,", "U.S. News & World Report: No. 59 nationally". Add an ellipsis to the Biotech splice | must fix |
| D6 | Participation table "Not in the figure" | 100 minus participation rate, labelled as students not in the figure | The state defines Not Tested as registered without a valid scale score, and does not publish how alternate-assessment takers enter its participation rate. Label the column "100 minus participation rate" | fix |
| D7 | Alternate assessment column | "fewer than 10 registered, or N, in every grade" | 2023-24 SPR prints "*" (9 rows) or "N" (70 rows). The "Fewer then 10 students registered for DLM" text is 2024-25 only (316 rows). Say each year as printed | fix |
| D8 | Rank claims, "What it states" | "page dated 2026-09-22" on 5 matches (NJIT 85, Rutgers 44/73/95, Monmouth 169) | Each page names 2027 in its text (checked). Say "2027 named on the page" so the match visibly meets the stated rule | fix |
| D9 | Glenwood claim row | Date cell "null" | "not printed" | fix |
| D10 | Rutgers-Newark SAT and ACT rows | reason not printed, note "The US News page prints no year" | Note should say the figure is not printed | fix |
| D11 | Sources tables | HS "State assessment proficiency: public" | Same kind of indicator is "public inputs, US News calculation" for K-8. HS method text does not say the indicator is published | fix |
| D12 | HS recompute note | "underserved student performance ... measured against what a model US News fits would expect" | Method: compared with the state average for nonunderserved students. The table itself says "public inputs, US News calculation". Note and table disagree | fix |
| D13 | College sources table | Standardized tests "public" | Method: "with adjustments for higher reporting" -> public inputs, US News calculation | fix |
| D14 | Sources wording beyond the captured method text | "(state records)" for HS graduation, "IB share with US News", "Survey of presidents, provosts and deans", "Common Data Set item I1/I2/C9" | Not in raw/*method*. Either capture the sentence or drop the words. CDS "public" holds only where a school posts a CDS (6 of 12 NJ colleges post none for 2025-26) or IPEDS carries it | minor |
| D15 | CHECKS P10 | "equal the 2023-24 test files in 21 of 32" | 21 of 24 compared (8 not compared) | CHECKS only |
| D16 | Gap | K-8 enrollment and student-teacher ratio printed, not checked | CCD 2024-25 equals all 16 enrollments and all 16 ratios after rounding. Year not named for K-8, so cannot tell (year) with both shown | optional |

## P10 judgement
Both rulers (NJ SPR and NJDOE assessment files) are named in Addendum 1, so scoring against the test files is inside the sealed plan. It was chosen after the first run reduced 10 differences to 1, which the plan allows only if labelled. The label exists in CHECKS but not on the page, and the page's sentence says US News names the test files, which the method text does not. The SPR figure is shown in each math and reading note (not science, SPR 2023-24 has no single science figure). The construction of the math figure (which tests, weighted by valid scores) is the desk's own and the one mismatch depends on including ALG01 (D2).

## Rank claims
Alexander Hamilton (#8 stated, #9 on the list): cannot tell is right under the rule. The page names "2026–2027" and is dated 2026-08-25, before the 2027 K-8 posts on other saved pages (Milton about 2026-10-26, Paterson 2026-10-29). Drew ("2026 list", 85th): cannot tell is right under the rule (edition as the page names it). The 12 matches each equal rank, list and the edition named on the page.

## Copy
No semicolons, no digits in headings, no AI statements, no adjectives or causes in our text in the NJ section (own lint, quotes removed). "Best" occurs only in list names and quotes.

## Fixes in order
1. D1 weights note. 2. D2 McNair to cannot tell (definition), tallies 70/0/10, show both readings. 3. D3 capture the college enrollment year or score cannot tell. 4. D4 page sentence and an after-the-first-run label. 5. D5 quotes. 6. D6, D7 participation labels. 7. D8-D10 claim and college cells. 8. D11-D14 sources tables. 9. D15 CHECKS. 10. D16 optional.
