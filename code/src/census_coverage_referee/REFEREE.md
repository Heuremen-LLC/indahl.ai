# Referee: CENSUS COVERAGE desk (outside, read-only)

VERDICT: FIX THEN SHIP. The numbers are right. The component section and some wording are not ready.

## Recount (own code: recount.py, extra.py; raw read from the desk's data/raw, desk code not imported)
- 51 areas: BELOW 6 (AR FL IL MS TN TX), ABOVE 8 (DE HI MA MN NY OH RI UT), CONSISTENT 37, CANNOT_TELL 0. Zero differences.
- Puerto Rico null row excluded, 51 in frame. US PES -0.24 SE 0.25, interval -0.651 to 0.171, CONSISTENT. Same.
- DA Table 1 (CB22-CN.02) in the raw release HTML: 2020 row 0.22 / -0.35 / -1.21, PES -0.24 SE 0.25. Same. Range holds zero.
- Components vs national (omissions 5.8 SE 0.24, duplicates 1.6 / 0.04, other 0.6 / 0.03): omissions 8 BELOW 7 ABOVE 36 C; duplicates 16/8/27; other 10/3/38. Same. H_STATES NCE equals G_STATES NCE for all 51.
- PLAN.md sha256 equals the sealed hash 04aaab1b and equals the file at ed9e74d.

## Spot-checks against the Census PDF (PES20-G-02RV, raw .txt of the PDF)
I parsed Appendix Table 3 for all 51 areas, not 8: count, NCE, SE equal the API for every area (0 mismatches). The asterisk set (14) equals the flagged set exactly, each on the right side. Table 4 hand-read for FL, HI, LA, UT, NY (omissions, duplication, other, SE) equals H_STATES. DA numbers match.

## The frame
1. 1.645 x SE: Census states "statistically significant at the 90 percent confidence level (alpha = 0.10) using a two-sided test" and asterisks those. Same level. Census may use unrounded SE or a t value, but it cannot matter here: lowest flagged |NCE/SE| is 1.93 (Delaware), highest unflagged is 1.58 (Louisiana). Any multiplier from 1.59 to 1.93 gives the identical 14. Say that on the page instead of "Census's own rule" (the multiplier is ours, the level is Census's).
2. Floor line "14 vs about 5.1": not wrong, but cut it. Binomial P(14 or more) is 0.0004 under independence. Under a shared-error simulation (equal correlation) it becomes 0.02 at rho 0.2, 0.07 at 0.4, 0.11 at 0.6, so "more than chance" is not safe, and nobody knows rho (no published covariance). Also the all-zero null is not a world anyone proposes (mean z squared is 2.9). The line invites an argument we cannot settle and adds nothing, since the 14 are Census's own asterisks. If kept, one sentence: "Census asterisks the same 14. A 90 percent test flags about 1 in 10 areas when nothing is off, and these errors are not independent, so we do not read the count of 14 as a result."
3. Components against the national value: CUT the duplicates and other-erroneous readings, and cut or demote omissions.
   - Fragility: the published values and SEs are rounded to 0.1. Moving each by 0.05 flips 24 of 51 duplicate readings and 33 of 51 other-erroneous readings (omissions: 3). Those flags are rounding artifacts. Arizona duplicates 1.4 SE 0.1 reads BELOW only because 0.1 is taken as exact.
   - Meaning clash: BELOW/ABOVE mean "count under/over the survey" for net and "rate under/over national" for components. Omissions ABOVE is the undercount direction, net ABOVE is overcount. A reader will cross them.
   - It restates the net reading: 12 of the 15 omissions flags are the same states as the 14 net flags (AR FL IL MS TN TX ABOVE omissions; DE HI MN OH RI UT BELOW). Not independent evidence.
   - Test is also not a clean state-vs-rest test (the national value contains the state, covariance unpublished; conservative for large states).
   Recommend: keep the table of values with SE beside the national value, no reading words, no counts. Note in CHECKS.md that the plan's component readings were dropped for rounding and the meaning clash (a cut after the pre-seal look, say so).
4. DA vs PES: separated well (own heading, "never merged", population difference stated). Fixes: do not label the DA cell with the outcome word CONSISTENT (it is a scenario range, not an interval, and the same word implies the same test). Write "the range holds zero". State that all three series are listed, high series -1.21 is an undercount (page omits it). The "PES estimate sits inside that range" sentence is fine, keep it in words.
5. Seal: the seal covers PLAN.md text and the rule only. Things it cannot cover: the raw data were pulled at 11:21-11:22, before PLAN.md (11:23:23) and before the seal; the full list was seen; the census_flags gate replicates a list already known (a replication, not a prediction); code (census_coverage.py) was committed after the reading (44562fd); all three commits carry the same second (11:23:30), and the seal json says first_computed_reading null in c10bd6f then was edited in 44562fd. The first run failed two gates, which turns every outcome into CANNOT_TELL, so no outcome was seen from the bad parser; the regex fix (counts under a million) changed no rule. Nothing compromises the seal as a rules seal. The page's first claim "sealed before any reading was computed" is too strong next to the disclosed look. Reword: "The rule was sealed before any count of outcomes was computed. The full list had been looked at once before, see the end."
6. Census count vs resident total: the page says household count is smaller than resident total and that the reading applies to the household count. Clear enough in prose, but the table puts the two side by side with no gap guidance and the gap is large (DC 649,000 vs 689,545, 5.9 percent; Alaska 700,000 vs 733,391), which a reader may take as an undercount number. Label the column "Resident total including group quarters and Remote Alaska, not used in the reading", or drop it.

## Cold read of census_coverage.html
- Required line "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau." present twice (body and sources). Good.
- No semicolons in visible text, lint_copy.py 0 hits, no digit in any heading or the title. Counts in the lead are area counts of the data, not counts of our things. OK.
- Nothing says Census is wrong. "Does not judge the count" and "own measure of its own count" are present. Good. CONSISTENT is not folded; CANNOT_TELL shown as 0.
- Lead sentence says "read three ways, and the four counts are printed apart." Three vs four. Fix: "read one of three ways, and CANNOT_TELL is kept as its own count (none here)."
- Plain words missing: standard error, nonsampling error, "90 percent confidence interval" are named, not explained. Add: standard error = how far the survey figure could move from sampling alone, nonsampling error = errors that are not sampling noise (for example people matched wrongly), 90 percent interval = the range that holds the true value 9 times in 10 if the survey method is unbiased.
- Components table shows "6.6 ± 1.1" where 1.1 is the SE, but the reading uses 1.645 x SE and the column says only "percent". Mislabelled for a reader. Moot if readings are cut, otherwise label "± standard error".
- Add a one-line legend under the states table: BELOW = census count under survey estimate (undercount), ABOVE = over (overcount).
- "The rule is Census's own 90 percent rule" -> "uses the 90 percent level Census states". 
- Nothing that implies cause, funding or apportionment. Good.

## Fix list (each concrete)
1. Cut duplicate and other-erroneous readings and the counts sentence; show values and SE beside the national value only. Cut or rename omissions reading (see 3). Log the cut in CHECKS.md.
2. Cut the floor sentence or replace with the one-sentence version in 2.
3. Reword the seal sentence in "The reading rule" (see 5), keep the disclosure at the end.
4. Fix "three ways / four counts" in the lead.
5. Add plain-word glosses for standard error, nonsampling error, 90 percent interval.
6. Legend for BELOW/ABOVE under the states table. Label the "±" as standard error if the component table stays.
7. Relabel or drop the resident-total column.
8. DA cell: say "range holds zero" not CONSISTENT, list the high series as an undercount.
9. Replace "Census's own rule" with "the 90 percent level Census states", and add that no multiplier between 1.59 and 1.93 changes the 14.
After these, SHIP. No recount fix needed, no data fix needed.
