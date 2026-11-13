# RANK graduate-school referee (outside, own code: rescore.py in this folder)

## Verdict: FIX THEN SHIP

The two MISMATCH rows are the problem. Pittsburgh stands. The Booth MISMATCH does not stand as written. The US News capture also dropped every two-digit value, which left 17 rows unscored or missing. No MATCH row changed. No row that stays CANNOT_TELL needs a different outcome except the ones listed.

## Differences (desk vs referee)

| School | Figure | Desk | Referee | Why |
|---|---|---|---|---|
| Chicago Booth | New entrants, full-time | MISMATCH (695 vs 635) | CANNOT_TELL (definition), or show both numbers | Booth's own page (saved and live, read with curl) prints 635 as the headline "Full-Time MBA Students", prints 60 "Joint Degree Students" beside it, and says percentages are "calculated out of 695 students". 635 + 60 = 695 equals US News. The page prints 695, so a same-quantity MISMATCH is not supportable. Row must at least quote 695 in the note. |
| Caltech (eng) | Tenured or tenure-track faculty | CANNOT_TELL (not printed), usn None | CANNOT_TELL (year or definition), usn 95 | US News prints "Full-time faculty (tenured or tenure-track) 95" and "95 full-time faculty". Public is 80 (70 tenured, 10 not tenured), no year. Capture bug, see Fix 2. |
| 10 education schools | Tenured or tenure-track faculty | no row (only Wisconsin 131, Teachers College 133) | rows added: Northwestern 40, Florida 60, Michigan 45, Vanderbilt 90, Harvard 39, NYU 79, Berkeley 30, UCLA 47, UT Austin 96, Virginia 71 | US News prints all twelve. Dropped because they are two digits. Public: Vanderbilt 189 "Full-time Faculty" (not tenure-track, so CANNOT_TELL definition). The other nine not found, and the saved faculty files for those schools are 404 pages. |
| 6 education schools | Students who took a licensure assessment | no row (rows only for Wisconsin 141, Michigan 127, NYU 168, TC 243, UT 335, Virginia 107) | rows added: Northwestern 19, Florida 72, Vanderbilt 95, Harvard 54, Berkeley 32, UCLA 93 | Same cause. US News year is printed: "during 2024-2025". The desk row says "not printed". |
| Mayo Clinic | Acceptance rate | CANNOT_TELL (not found) | CANNOT_TELL (year) | Mayo's saved page prints "The 2026 acceptance rate ... was 3.5%" (6,061 applications, 215 offers). US News is 3.5% for the 2025 entering class. The figure was found, the year differs. Counts move from not_found to year. |
| Kellogg, Stern, Sloan | Two-year average (DISPLAY) | pub 86.3, 77.0 and 85.3, 81.9 | pub 86.4, same, 81.8 | The desk worked these from rounded rates. From counts: Kellogg 367 of 429 and 369 of 423 gives 86.4. Sloan 223 of 256 and 223 of 289 gives 81.8. The page now shows a difference from US News that is a rounding artefact. Also these three rows have no Source link. |
| Education, all 12 | Row label "Acceptance rate (doctoral)" | label says doctoral | label "Acceptance rate as printed" | US News prints "Acceptance Rate" unqualified and locks "Acceptance rate (Ph.D.)" separately. The chart counts (Northwestern 416 of 1,035 = 40.2%) are not labelled doctoral. All 12 stay CANNOT_TELL. |
| Baylor | Full-time faculty | shows 3,629 from a search excerpt | remove from page | The 3,629 figure (2023-24) is marked UNVERIFIED against the saved file in the public JSON and appears in visible copy. A figure not in a saved file should not be shown. |

Everything else agrees (26 MATCH, 2 MISMATCH minus the Booth change, rest CANNOT_TELL).

## Numbered fixes, in order

1. Booth new entrants: change to CANNOT_TELL (definition) with a note quoting 635, 60 joint degree students and "calculated out of 695". Tallies: Business 24 match, 0 mismatch, 56 cannot tell. (If the owner prefers to keep MISMATCH, it needs a reason Booth's own 695 is a different quantity. I found none.)
2. Fix the US News capture parser: it dropped values below 100. Re-run for education faculty (10 rows) and assessment (6 rows), and Caltech faculty 95. New education tally: 0 match, 0 mismatch, 68 cannot tell (was 56). Engineering stays 1 match, 0 mismatch, 49 cannot tell.
3. Mayo acceptance: reason year with the 3.5% shown and "2026 incoming" as the public year. Medicine: 1 match, 1 mismatch, 94 cannot tell (unchanged), but the reason counts move.
4. Rework the six Kellogg, Stern, Sloan display figures from counts (not rounded rates) and add Source links to the three rows that lack them.
5. Relabel the education acceptance row. Fix the assessment year to 2024-2025.
6. Remove or verify the Baylor 3,629 faculty figure from visible copy.
7. Update the "Figures checked so far" line to the new counts after fixes 1 and 2, in the ledger first.

## Judgement calls

- Medicine total enrollment CANNOT_TELL (definition): agree. US News method says faculty over "full-time M.D. students" and AAMC B-1.2 counts all MD students on Oct 31 including leave. All 16 AAMC figures are 3 to 36 percent above US News (Yale 570 vs 419). Value-only would be MISMATCH for all 16, which would claim a gap the definitions explain.
- Engineering MIT, Georgia Tech, Carnegie Mellon enrollment and faculty CANNOT_TELL (definition): agree. MIT's own page says 146 faculty are shared with the College of Computing. Georgia Tech acceptance is the weakest: school prints 13,150 applicants against US News 10,462 plus 6,940, and the reason is a count difference. CANNOT_TELL is defensible but could be argued either way.
- Wharton employment CANNOT_TELL (timing not stated): agree. 529 of 608 = 87.0 matches 87 in value only.
- HBS 84%: agree CANNOT_TELL (definition). The page text says 90% received an offer and "out of the 90 that received an offer, 84% accepted", so 84 may be of those with an offer. Under the precision sub-rule 84 would also equal US News 84.4 rounded, so the row would be CANNOT_TELL (precision) if the definition were settled.
- Columbia: agree CANNOT_TELL (definition, sponsored students). Same precision note: 90 equals 90.4 rounded.
- Precision sub-rule (CANNOT_TELL precision if US News rounded to the public precision equals the public figure, else MISMATCH): agree. It avoids calling 90 vs 90.4 a match or a miss. It is not applied anywhere in the data today (Tuck's 87% is replaced by counts, 233 of 268 = 86.9, a MATCH).
- UC San Diego 3,985 MATCH: confirmed. Jacobs page (saved and live) prints 2,631 master's and 1,354 Ph.D. fall 2025, sum 3,985. The same page labels professors "Fall 2026" (276), so the faculty row stays CANNOT_TELL.

## Confirmed

- US News side, all 48 school pages re-read through the owner's Chrome (own tab, closed): every scored value equals the desk capture (MBA 10, engineering 10, education 12, medicine 16) except the dropped two-digit values above. Every page says "<Business|Engineering|Education|Medical> School details based on 2025 data." Every page carries "Unlock these and N other ... data points with U.S. News ... Compass". GMAT shows "UNLOCK WITH COMPASS". GPA, MCAT, NIH, research expenditures and doctoral degrees are absent from the page text on all 48. Education assessment year line reads 2024-2025. No account, purchase or cookie control was touched.
- MBA employment: MIT Sloan prints 91.0 received and 87.1 accepted at three months, 73.8 and 67.2 at graduation (confirmed by the report text "By three months after graduation, 91.0%"). NYU Stern 75.6 at graduation, 86.0 at three months (letter says 86% within three months). Kellogg xlsx: 69.46 and 85.55 give 69.5 and 85.5. Haas 114 and 153 of 182. Stanford GSB 144 and 217 of 268. Tuck 233 of 268. Means versus medians: Stanford 190,109, Kellogg 167,150.56, Sloan 173,132, Stern 168,970 and Haas 164,930 are means. Wharton, Booth, HBS, Columbia, Tuck publish medians only (all CANNOT_TELL).
- Pittsburgh: 317 offers, 11,888 applicants, Class of 2029 (saved and live). 317 / 11,888 = 2.67 percent, rounds to 2.7. US News 3.1. MISMATCH stands (AAMC lists 11,887 applications, consistent).
- Yale 4.4% MATCH: class of 2029 profile prints 4.4% (saved and live).
- Live checks with curl, UA HeuremenRANK-referee/0.1: Booth, Pittsburgh, Yale, Jacobs, HBS and Stanford GSB class pages all returned 200 and still carry the figures above (GSB embed not parsed).
- Recomputation with my own code (rescore.py, half-up at the precision US News prints): all 26 MATCH and both MISMATCH reproduce from the pub and usn strings. Outcome counts in checks_grad.json equal the tallies on the page: Business 24/1/55, Engineering 1/0/49, Education 0/0/56, Medicine 1/1/94 (the 6 display rows are excluded from tallies, as stated).
- Copy on the four sections: no semicolons in visible text, no adjectives about schools or US News, no cause named for any gap, the "Where the data comes from" table present on all four with "not public" where no source publishes per school, source links on every scored row (except the three display rows above), year on both sides for scored rows.
- Missed-figure search of the saved public files: the saved education school pages (Harvard, Northwestern, NYU, Teachers College, Florida, UT, UCLA, Wisconsin, Berkeley) are 404 or challenge pages, and Harvard's file is Fall 2023, so those "not found" rows are right. Medicine: no other school page prints an offers count for the 2025 class besides Pittsburgh, Yale and Mayo (2026).
