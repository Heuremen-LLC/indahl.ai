# FIDELITY desk: outside referee report (11 Nov 2026)

Read-only. Nothing in fidelity_index/ was edited. Scripts in this folder: nchs_pos.py, recount.py, spot.py, rates.py, swapcheck.py (outputs my_rows.json, nchs_pos.json, two crop PNGs).

## Verdict: FIX THEN SHIP

The numbers are right. Every row recounts. The problems are in what the page says, not what it counts: one wrong sentence (same-sex), one inaccurate sentence (which states do not report), a headline that hides how much the sex choice moves the divorce reading, and a count-vs-rate disagreement in NCHS that the page does not disclose. Fixes are listed at the end.

## 1. Recount from raw (own code, no make_rows.py import)

- NCHS: re-parsed both PDFs by word position with PyMuPDF (columns assigned by x to the year headers), not by text order. 52 entries x 24 years x 2 tables, 0 differences from data/nchs_counts.json.
- Rebuilt all 1,428 rows from data/raw/acs_*.json. 0 row differences in outcome, reason, sex_split flag or NCHS value.
- Counts match the builder's exactly. Divorce 25 above, 265 below, 303 inside, 121 cannot tell (51 no stated count, 69 does not report, 1 no ACS interval = Delaware 2018, API returns null), 246 splits. Marriage 95 / 313 / 253 / 53 (51 + 2), 85 splits.
- Destination cells match. Nevada divorce 6 above, 7 inside, 1 cannot tell. Nevada+Hawaii marriage 26 above, 2 cannot tell. Excluding destination: divorce 19 / 265 / 296, marriage 69 / 313 / 253.
- Gate 2 rate check reproduced: 1,183 of 1,242 within 0.1 (59 fail). The 59 are not listed anywhere, see Finding C.
- Floor at zero never fires. No row has estimate minus margin below 0. No NCHS count sits exactly on an interval edge.

## 2. Spot checks (10, from the live Census API and the NCHS PDF image)

ACS API re-pulled today with the key (not printed), all equal to data/raw: Texas 2022 divorce 89,194 +/- 6,115 (men 84,520 +/- 6,154), Louisiana 2022 divorce 16,228 +/- 2,462, Nevada 2015 marriage 22,691 +/- 2,319, Georgia 2019 divorce 39,301 +/- 3,682, Hawaii 2017 marriage 10,229 +/- 1,520, Ohio 2013 marriage 74,772 +/- 4,377, Vermont 2021 divorce 2,151 +/- 855, Illinois 2016 divorce 36,296 +/- 2,852, Florida 2023 marriage 164,445 +/- 7,975, Delaware 2018 divorce null (no interval, correct as CANNOT_TELL).
NCHS: rendered the PDF page and read Texas (2022 = 56,269, 2021 = 40,107) and Louisiana (2022 = 3,393, 2023 = 4,120, dashes 2000-01 and 2004-12) off the image. They match the parse. Variable labels confirmed from the API: B12503_010 = Female, ever married, divorced last year. B12501_010 = Female, married last year.

## 3. Attacks on the frame

### Sex splits (the largest issue)
- The two sexes are not interchangeable for divorce. Across 14 years the women/men estimate ratio has median 1.10 (range 0.53 to 2.92) for divorce and 0.985 for marriage. Nationally (reporting states), NCHS / ACS women divorced = 0.80 to 0.87, against the men's estimate 0.89 to 0.97. So the sealed choice of women is the choice that reads most BELOW.
- Scored divorce rows (593) read under each rule: women 25 above / 265 below / 303 inside. Men only 78 / 140 / 375. Both sexes below in 111 rows, both inside in 225, both above in 11. Range spanning both intervals (lowest lower end to highest upper end): 11 above, 111 below, 471 inside.
- So "265 below" is a women-only number. Under men it is 140. 136 of the 246 splits are women BELOW / men INSIDE. A reader of the lead sees only the women's count.
- Marriage is much steadier. Women 95 / 313 / 253, men 95 / 332 / 234, both below 294, both above 81, both inside 201. 85 splits, all one step apart (never above vs below).
- Divorce has 18 rows where women read BELOW and men read ABOVE (NCHS sits between the two sexes' intervals), meaning the two sexes disagree with each other by more than either margin. Marriage has no such row, all 85 marriage splits are one step apart.
- Recommendation: keep women as the scored reading (sealed, and changing it after the data would break the seal). Add to each headline table a men's column and a "below in both / inside in both / above in both" line, plus the sentence that the divorce BELOW count drops from 265 to 140 under the men's estimate. The conclusion that survives every choice: Texas, Illinois, Massachusetts, Iowa, Kansas and similar states read BELOW under both sexes. The conclusion that does not survive: "NCHS is below in 45 percent of divorce rows." Do not turn this into a share (plan forbids it anyway).

### Is women-married/divorced-last-12-months a fair one-per-event conversion?
Roughly for marriage, loosely for divorce. Marriage: ratio of the two sexes sits near 1, a good sign. Divorce: ACS counts a person who reports divorcing in the past 12 months, so it includes divorces decreed out of state, people who remarried, and recall errors (a person reporting a divorce that finished 13 months ago). Nationally the NCHS total is 13 to 20 percent under the women's total even in reporting states, which is the size of the definitional gap alone. State BELOW readings should be read against that baseline, not against 1.0. The page should say this baseline in the lead (median NCHS/ACS women, reporting states, 2022 = 0.80).

### Same-sex sentence is wrong
Page: "Same-sex events are counted once per partner of the respondent's sex, which makes the women's estimate a small undercount of events in the same-sex share." Two-woman divorces and marriages are counted twice by the women's estimate (an overcount), and two-man events are not counted at all (an undercount). The net sign is not known. Replace with that.

### Occurrence vs residence, rolling window, other definitions
- Occurrence/residence: handled and prominent. Destination states are counted apart. Note the page's own table shows the effect is not only Nevada and Hawaii: Florida marriage 12 of 13 above, Arkansas and New York 10 above (ratio 1.12 to 1.20). That supports the page's "every state has some" line.
- Rolling 12 months vs calendar year: stated. ACS interviews run all year, so the window averages two calendar years with half weight each. A state with a falling count (Texas 2021 to 2022) reads high.
- Petitions vs decrees, annulments: stated on the page. NCHS includes some petitions and legal separations in some counties and states, so this pushes NCHS up, not down, which makes BELOW harder to explain by it.
- ACS universe: all persons 15+ resident. Includes military posted in the state, excludes those in group quarters differently. Not material to the reading.

### Is Texas BELOW plausibly a definitional artefact?
Partly. Texas NCHS/ACS women = 0.67 median across 13 years, against a national 0.80 to 0.87 for reporting states. So definitional gap explains roughly the national baseline, and about a third of Texas's gap is left over. Texas also reads BELOW under the men's estimate in all 13 years (0.67 and 0.80). The Texas NCHS series itself is unstable: 63,674 (2017), 74,126 (2018), 61,350 (2019), 43,233 (2020), 40,107 (2021), 56,269 (2022). A 2021 cliff and 2018 spike are more consistent with how and when Texas reports than with a change in divorces. So the reading can say: NCHS count sits below ACS in all 13 years and is further below than the national baseline. It cannot say records are missing, nor that ACS is right. The page already refuses to name a cause. Keep that. Also: do not call the table column "Gap in events" without saying it is ACS estimate minus NCHS count, in persons read as events. Nevada marriage 3.8x above is the same reading in the other direction and is already covered by the destination paragraph.

### Is the 90 percent margin used correctly?
Yes. Census publishes MOE at 90 percent, MOE = 1.645 x SE. The interval estimate +/- MOE is the 90 percent interval as published. Flooring at zero is harmless (never fires in this frame). The 1.96/1.645 scale is display only. One limit worth a sentence: the margin covers sampling error only. It does not cover the NCHS side, the conversion, or nonresponse bias, so an inside reading is "not distinguishable at this margin", and the page says no more than that. Treating NCHS as exact is fine because it is a count, not a sample.

### Louisiana and Georgia blanks
Real non-reporting, not a parse artefact. Dashes are in the count PDF and the rate workbook ("Data not available") for the same years. Georgia divorce: counts 2000-03, blank 2004-16, then 2017-23. Louisiana divorce: blank 2000-01 and 2004-12, then counts 2013-23. Georgia marriage: 2013 and 2014 blank in the rate workbook while counts exist, check that the 3 Georgia marriage CT rows are the intended ones (they are: 2013, 2014 and 2024).
Two things the page does not disclose:
- Louisiana divorce counts that are printed are not stable: 9,995 (2021) then 3,393 (2022) and 4,120 (2023), rates 2.2 then 0.7 and 0.9. Louisiana at 0.21 (page's biggest gap) is this cliff, not a steady gap. Georgia jumps 36,464 (2017) to 26,327 (2018), rate 3.5 to 2.5. Both are printed by NCHS so they stay scored, but each should carry a note on the page, and Louisiana 2022 and 2023 should either be labelled "printed count falls by about two thirds in one year" or turned to CANNOT_TELL. I recommend a note, not a CANNOT_TELL, because changing the reason after seeing the data is the thing the seal prevents. A note is allowed, a re-class is not unless the plan allows it.
- "California, Hawaii, Indiana, Minnesota and New Mexico do not report divorces" is inaccurate as written. Hawaii reported 2000-02, Minnesota 2000-04, New Mexico 2000-15. New Mexico has 6 scored divorce rows. Say "do not report in some or all years in the frame."

### Finding C: NCHS count table and rate table disagree in places
The 59 gate-2 misses are not random. Marriage 2023: about 45 of the 51 jurisdictions miss because the printed 2023 rate was not computed on the ACS B01003 population (Utah 9.9 printed vs 11.19 from count, Hawaii 14.4 vs 12.47). That is a population base difference, harmless. Divorce 2016 and 2017: count columns for Iowa, Kansas, Maryland, Maine and Louisiana look swapped against the rate table. Example Iowa 2016 count 6,178 gives 1.97 per 1,000 and the printed rate is 1.30, while the 2017 count 3,933 gives 1.25 and the printed rate is 2.00. The swapped assignment fits to 0.1 in all ten state-years. Texas and Illinois 2016 differ too, but both rates are footnoted as revised. Across all states and years the columns line up overall (divorce 2016 fit 38 of 45, 2017 41 of 46, other years 45 to 46 of 46), so this is limited to about seven states. If the count PDF is the wrong one, two rows move (Kansas 2017 INSIDE to BELOW, Maine 2017 INSIDE to BELOW), the rest keep their reading. This is an NCHS file inconsistency, not a desk error. The page should say it (list the 14 state-years, say outcomes were read from the count table as printed, and that two rows would change under the other assignment).

### Was the plan sealed before the first comparison?
Mostly yes, with two things to fix.
- PLAN.md blob 1b571f2, committed 11:22:31 -05:00 (16:22:31Z). SHA-256 of the working PLAN.md equals the plan_sha256 in data/plan_seal.json and equals the committed blob. first_comparison is 16:23:26Z, 55 seconds after the commit. No plan text changed after that (git log shows 3 commits, PLAN.md touched once).
- make_rows.py, CHECKS.md, known_good_rows.json, the summary and the rows were committed at 11:24:48, after the first comparison. The rule is fixed in PLAN.md text, and my independent code (written from that text) reproduces every outcome, so the rule was implemented as sealed. But the code itself was not sealed. Say that.
- The ACS pulls (data/raw/acs_*.json, 16:21:34Z to 16:21:50Z) and the NCHS parse (11:21) all predate the seal commit by about 40 to 60 seconds. PLAN.md states ACS data for all years "were pulled after this paragraph was written and not read." The disclosure paragraph has no timestamp of its own, so a reader cannot verify the order. The pull was not read before the seal (the first comparison is later), so the substance holds. Reword on the page and in PLAN-derived text to "pulled in the minute before the plan was committed and not read before it", and keep PLAN.md unchanged.
- The scout (SCOUT.md) had already shown women and men for TX, FL, NY and PA 2022-23 before the women's estimate was "chosen before comparing anything". The plan discloses the 16 scouted rows. The page says "We chose women over men before comparing anything". That sentence is not exactly true given the scout. Replace with "before the full comparison, after a scout of 16 state-year-events that the plan lists."
- Gate P10: the reader-gate tolerance first ran at 0.15, then set to 0.1. Disclosed in CHECKS.md only. Put one line on the page.

## 4. Cold read of fidelity.html

Passes: Census attribution line present and exact, CDC credit in Sources, lint_copy.py gives 0 hits (no semicolons, no AI statements), no heading carries a count or digit, CANNOT_TELL is a separate column in every table and in the lead, nobody is called wrong (the first sentence says the opposite), no share or test is printed over rows, destination states are counted apart.

Fix list for the page:
1. Same-sex sentence (see above).
2. "do not report divorces" sentence (see above).
3. "We chose women over men before comparing anything" (see above).
4. Lead has only the women's counts. Add the men's counts and the both-below / both-inside / both-above line for each event, and the national baseline sentence.
5. Table title "Gap in events": rename to "ACS estimate minus NCHS count" or add the note under the table that these are point estimates and persons read as events.
6. Add the Louisiana and Georgia series note and the 2016-17 count/rate note.
7. "Hawaii marriage: 13 above" and "Nevada 3.81" are destination effects and are labelled, but the lead's "Without the destination cells" line still shows 69 marriage rows above. Add that Florida, Arkansas and New York also read above in most years so the reader does not take the destination line as the whole explanation.
8. "counts are provisional and have no final series" rests on the scout, not on a page I could re-open. Cite the NCHS file header text ("Rates are based on provisional counts of divorces by state of occurrence") instead of asserting it. Verified in the sd.pdf header. The same file has the footnotes "Includes annulments" and "Includes divorce petitions filed or legal separations for some counties or States", which is the exact wording to quote.
9. Pennsylvania note in SCOUT.md (Philadelphia divorces possibly missing from the 2023 state report) is unverified and not on the page. Leave it off unless checked.

## 5. What the reading can and cannot mean

Can mean: for this state-year and this conversion, the CDC count is above, below or within the ACS interval. In divorce, NCHS sits below the women's ACS interval in 265 of 593 scored rows and in 140 under the men's estimate. National totals alone sit 13 to 20 percent below the women's total.
Cannot mean: that any state's records are incomplete, that ACS is closer to the truth, that a state under-reports, or that a destination state over-counts. It cannot rank states against each other, since the definitional gap is shared and unknown by state.

## Fix list (concrete, in order)

1. Add men's counts and both-sexes agreement line to the lead and the headline tables. Add the national NCHS/ACS baseline sentence (2022 women 0.80, men 0.89).
2. Correct the same-sex sentence.
3. Correct "do not report divorces" to "do not report in some or all years".
4. Replace "before comparing anything" with the scout-aware sentence. Add the pull-time sentence and the one-line note that code was committed after the first comparison and that the tolerance was first run at 0.15.
5. Add a note for Louisiana 2022-23 and Georgia 2017 (printed count breaks) and for the 14 divorce state-years 2016-17 where count and rate tables disagree, with the two rows that would flip. Do not re-class any cell.
6. Rename "Gap in events".
7. Quote the NCHS header footnotes instead of the unsourced "provisional, no final series".
8. Publish the list of the 59 gate-2 misses in data/ (not on the page body) so the 95.2 percent has a visible tail.
