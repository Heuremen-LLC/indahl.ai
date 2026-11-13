# RANK step two, outside referee pass (2026-11-10)

Verdict: FIX THEN SHIP

Own code: code/xl.py (stdlib xlsx reader), code/recompute.py. Output: out/referee_rows.json. Fresh pulls in out/pulls/.

## 1. Recompute of checks.json
HS 75 rows: 57 match, 0 mismatch, 18 cannot tell. Same outcomes, values and years as the desk, row for row (reason label for Davidson maths/reading is "binned public figure" here, "floor or range unsettled" at the desk, same outcome).
Colleges, enrollment rows: 8 NU + 6 NLAC match, 7 cannot tell (not found). Same as desk. The 4 sampled display computations (MIT, Harvard acceptance, under-20, 4-year) agree.
Law 55 rows: GPA, LSAT, acceptance 33 of 33 match, same values. First-time bar 11 cannot tell, same.
DIFFERENCES: 11. Law ultimate bar passage, all 11 schools. Desk MATCH with "Year US News names: 2021 and 2022 graduates". Referee CANNOT_TELL (year not printed). No capture in raw/ names a year for ultimate bar or says US News averages two classes unweighted. law_pages capture prints only "ultimate bar passage rate (2 year average)". grad_method capture has no ultimate-bar year. The desk's year comes from the desk, not from US News. Data side: the unweighted 2021+2022 average agrees in 11 of 11 (pooled 2021+2022 also 11 of 11, 2022+2023 average 3 of 11, 2022 alone 5 of 11), so the pairing is likely right, but by the sealed rule it is a year we inferred.

## 2. Years
- HS assessments 2023-24, graduation class of 2024: quoted in hs_method. Data also discriminates: where 2023-24 and 2024-25 state figures differ (Signature maths, Masterman maths, Tesla maths, SWW science, SASM science, SASM graduation) US News equals 2023-24 / class of 2024 every time. Method also says US News fell back to 2023 or 2022 graduation data where 2024 was missing. Not stated on the page.
- Enrollment and lunch shares, CCD 2024-25: the hs_method quote is truncated ("...pertains to 2024-2025", subject not captured). The data settles it: the 2023-24 grade 9-12 sums differ from the US News figure at all 10 schools, the 2024-25 sums equal it at all 10, and 2023-24 lunch shares would miss at several schools (Signature 6 against 7, Gwinnett 29 against 25). Keep, but re-capture the full sentence or label the year "2024-25 (matches CCD 2024-25 only)".
- College enrollment fall 2025 against CDS 2025-26 B1: "(fall 2025)" is printed on the nu and nlac list captures. Correct.
- College other figures cannot tell (no year printed): correct.
- Law GPA, LSAT, acceptance 2025 entrants: GPA quote truncated ("of all 2025 full-..."), school page label "for all program entrants" fits All50th. Correct.
- Law first-time bar cannot tell: outcome correct. The NOTE is wrong against the capture: "US News's method names a two-year average of the 2023 and 2024 classes". In grad_method that average is attached to "Outcomes 10 months after graduation" (employment), not to bar passage. The printed figure equals the ABA 2024-graduate rate in 11 of 11.
- Law ultimate bar: see the differences above.

## 3. Copy
No semicolons, no digits in headings, no AI statements in our copy. No adjectives or causes found in our copy.
- "as US News states it averages them" (11 ultimate-bar notes) and "US News's method names a two-year average of the 2023 and 2024 classes" (11 first-time-bar notes) put words to US News that no capture holds.
- Penn display line "Only item B1 could be read from the college posting" is false. Penn's CDS was not read at all (Box sign-in), and the enrollment row correctly says not found.
- College display lines print "agrees" or "differs" beside figures we score cannot tell. They are labelled after the data and not scored, but "differs" reads like a finding. Better: print the two figures and the CDS year only.
- Corrections lead says "removed, withdrawn or computed again". Emory's quote says corrected data was used in this year's computation. That is not a recompute of a published rank, and the sealed plan scopes this section to cases where "its US News rank changed". cases.json itself says "no change to a published rank stated".

## 4. Blue Ribbon
Award years: SWW 2018 is on the National Archives webharvest copy of the Department's 2018 national.pdf (re-read, page lists the school). Gwinnett 2016 is in a GaDOE release held by the Digital Library of Georgia. TAG 2022 is in a TEA release. All three re-read 200 and confirmed. "Cannot tell (category not stated)" is right: each source explains the two categories but does not give each school's category.
WRONG: the page says the Department pages "returned 'Page not found'". curl on 2026-11-10 got HTTP 403 "Service unavailable. The request is blocked." at nationalblueribbonschools.ed.gov/, /awardwinners/, the ed.gov awards page and www2.ed.gov/programs/nclbbrs/2018/national.pdf. The desk's own records (hs_public.json, internal/BLOCKED) also say 403. No file records "Page not found". Not worked around.
Minor: "no award record was found in the sources read" for the other schools. Leads exist but were not read: Central Magnet 2020 (TN release 403) and Signature 2014 (ED application PDF 403, Congressional Record snippet). Better: "no award record was read".

## 5. Corrections
Re-read 4 primary URLs (Berkeley, UW-Madison, GW node/2281, Emory). Every quote is verbatim. Data-item lines are faithful to cases.json. Word counts: Temple 9, USC 19, Berkeley 22, UW 24, Emory 18. GW is 25 words, which is not under 25.

## 6. Copyright
The page shows rank, name, place, the method's indicators and weights, and the figures checked, with list, method and source links. No US News table beyond the top-ten rows and the figures checked. Fine.

## Refusals
usnews.com law methodology: curl connection failed (status 000), not retried. ed.gov Blue Ribbon: 403 bot block. Caltech CDS PDF text unreadable (font encoding), substituted Yale and Duke.

## Fixes, in order
1. Law ultimate bar (11 rows): capture the US News law method text on bar passage in the owner's browser. If it names the 2021 and 2022 graduates (and how it averages), add it to raw/ and keep MATCH, quoting it. If not, change to CANNOT_TELL (year not printed), show the 2021+2022 reading as display only, and drop "unweighted" and "as US News states it averages them". Law counts then read 33 match, 0 mismatch, 22 cannot tell.
2. Law first-time bar notes (11): delete "US News's method names a two-year average of the 2023 and 2024 classes", or quote the bar passage sentence from the same re-capture. Today's capture attaches that average to employment outcomes.
3. Blue Ribbon: change "returned 'Page not found'" to "refused our reader (HTTP 403, request blocked)", unless a browser capture of "Page not found" is added to raw/.
4. Penn display line: change to "No Common Data Set 2025-26 was read".
5. Emory: drop the row, or add a dated addendum to PLAN.md widening the scope and change the lead to say "or the next ranking was computed on corrected data".
6. GW quote: trim it below 25 words.
7. Optional: HS lunch and enrollment year label (full quote or data-matched label). Note the 2023 or 2022 graduation fallback. College display: print figures only, no agrees or differs. Blue Ribbon: "no award record was read".
