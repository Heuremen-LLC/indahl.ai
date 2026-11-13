# RANK referee pass, step one listing (2026-11-10)

Verdict: **FIX THEN SHIP**

Method: every list and method page re-read from US News in our own browser tab (signed-in session, Load More pressed to see past row 10). Own extractor in page JS, own comparison in code/compare.py (shares nothing with build_data.py or build_page.py). My reading is in out/usnews_read_20261110.tsv, the rows past the cut and the method weights in out/edge_rows.txt, the diff in out/compare_out.txt, and the visible page text in out/body_text.txt.

## What matches
- Membership on all lists, by the rank-10 rule with edge ties kept whole. No school is missing and none is extra. The row after the cut on each list: hs #11 Whitney, nu #12 Columbia and Dartmouth, nlac #11 Air Force Academy, mba #11 Darden and Yale, law #12 Vanderbilt, eng #11 Cornell, edu #13 Johns Hopkins, Stanford and Penn, and med Tier 2 starting with Dartmouth (Geisel). Tier 1 in medicine is exactly the 16 schools on the page.
- Every rank, tie mark and name. Every place except the ones listed below. High school graduation rate, college readiness and enrollment for all 10 rows. College enrollment for 20 of 21 rows.
- Editions: high schools 2026-2027, colleges 2027, elementary and middle 2027, graduate 2026.
- Every list link and method link. Every weight on all 8 method pages. Colleges: Faculty resources adds to 11 percent for National Universities (3+2+6) and 15 percent for others (4+3+8), as the note says.
- The elementary and middle method page says "There is no national ranking".
- PLAN.md was committed in b25e87f (11:07:22). The data, build code and body came in c00531f (11:11:15). PLAN.md has not changed since the seal.
- Copy: no semicolons, no digits in h2, no AI statements, no adjectives about schools, staff or US News, and no cause named. The tiers and the absent K-8 national list are stated as US News states them. Copyright: the page shows only rank, name, place, the figures to be checked and short method quotes, all linked. High schools show 2 printed figures and colleges 1. No full US News table is republished. This stays within the plan's rule.

## Differences (19)
| List | School | Field | Desk | US News prints |
|---|---|---|---|---|
| nu | University of Chicago | enrollment | (blank) | 7,453 (fall 2025) |
| edu | University of Texas--Austin | place | (blank) | Austin, TX |
| edu | University of Virginia | place | (blank) | Charlottesville, VA |
| med | all 16 Tier 1 schools | place | (blank, but the table has a Place column) | Houston TX, Cleveland OH, Atlanta GA, Rochester MN, Columbus OH, Los Angeles CA, La Jolla CA, San Francisco CA, Aurora CO, Gainesville FL, Pittsburgh PA, Rochester NY, Tampa FL, Dallas TX, Nashville TN, New Haven CT (in desk order) |

Not a data difference: the footer link https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/rank returned 404 when I checked it.

## Fixes in order
1. Fill the UChicago enrollment cell with "7,453 (fall 2025)".
2. Fill the places for edu UT Austin (Austin, TX) and UVA (Charlottesville, VA).
3. Fill the 16 medicine places as above, or drop the Place column from the medicine table.
4. Push code/rank to the public repo before ship, or hold the footer link until it resolves.
5. Optional: the college weights line could print 11 percent on the National Universities list and 15 percent on the Liberal Arts list, not "11-15 percent" on both. The note already explains it, so this is not required.
