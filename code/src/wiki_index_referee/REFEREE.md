# WIKI desk (HERMES): referee report

Read-only refuting referee. Read 10 Nov 2026 UTC (9 Nov HST). Nothing in ~/bones-forge/wiki_index/ was edited.

Inputs read in full: PLAN.md (commits 49250d0, 9dd1754, e4fecd5), wiki_tick.py, build_page.py, lint_copy.py, heuremen_kit.py, wiki.html, summary_wiki.json, CHECKS.md, data/wiki.json, data/wiki_live.json, data/state.json, data/raw/ (claims, World Bank and UIS releases, Section 2 delivered files, stated pages, DSA wikitext and XLS, Wayback texts, http.log), and research_wiki/SCOUT_WIKI_20261110.md for what was known before the plan.

Own code (does not import wiki_tick.py): /Users/heuremen/bones-forge/wiki_index_referee/code/. Run order: `python3 -I recount.py` (writes out/ref_rows.json.gz), then sens.py, trunc.py, placebo.py, uis.py, notable2.py, norel.py, s2check.py, live_rows.py. Live reads (house User-Agent, one at a time, paced): 47 for the seeded and notable rows (Wikidata wbgetclaims, World Bank current and archive calls, UIS calls), 3 query-service counts, 8 Wayback (index and captures), 2 Analytics API probes, 3 reads of the DSA page history. Receipts: /Users/heuremen/bones-forge/wiki_index_referee/receipts/.

Verdict at the end: FIX THEN SHIP. Two items block shipping as the page stands. Both are small fixes.

---

## What holds

### Section 1 recount from raw (own code)

Every bin, size outcome, default-row count, set-aside count, Wilson interval and median reproduces exactly. Row by row, all 17,429 rows agree on key, bin, current value, size outcome, default flag and written unit. The only differences are UIS release labels (format only, 173 rows).

| Group | Rows | Current | Older | No release | Nothing | Above | Below | Within 1% | Cannot tell |
|---|---|---|---|---|---|---|---|---|---|
| Population | 8,967 | 1,274 | 7,662 | 16 | 15 | 2,302 | 3,594 | 3,054 | 17 |
| GDP | 1,407 | 703 | 700 | 2 | 2 | 60 | 252 | 1,081 | 14 |
| Gini | 186 | 123 | 58 | 4 | 1 | 13 | 6 | 145 | 22 |
| Unemployment | 203 | 92 | 109 | 2 | 0 | 71 | 31 | 31 | 70 |
| Life expectancy | 3,490 | 684 | 56 | 2,749 | 1 | 881 | 840 | 1,764 | 5 |
| Fertility | 3,176 | 739 | 117 | 2,320 | 0 | 965 | 970 | 1,011 | 230 |
| All | 17,429 | 3,615 | 8,702 | 5,093 | 19 | 4,292 | 5,693 | 7,086 | 358 |

All match the page and summary_wiki.json. Set aside: more than one point in time 36, no point in time 4, deprecated 1 (matches). The country-resampled intervals from my own bootstrap (different seed and order) fall within 3 points of the page's in every cell. The release-year table matches. The frame re-listed live from the query service today: population 186 items and 8,967 statements, GDP 199 and 1,411, life expectancy 205 and 3,525, all as the desk read them.

### Ten seeded rows, end to end, live

Draw: `random.Random(20261109)`, stratified 3 population, 2 GDP, 1 Gini, 1 unemployment, 2 life expectancy, 1 fertility, from rows sorted by item, year, value. Each was read live: the statement by id (wbgetclaims: value, point in time, rank, reference), and the source value the bin claims (World Bank current call, the named archived release, or UIS).

| Row | Cited | Bin | Live statement and reference | Live source value |
|---|---|---|---|---|
| San Marino pop 2010 | 30,861 | older, newest 2015 Jul | 30861, 2010, normal, stated in World Bank Open Data | 2015 Jul release 30,861 (current 33,270) |
| Morocco pop 1965 | 14,092,269 | older, 2015 Jul | same pattern | 2015 Jul 14,092,269 (current 13,239,171) |
| Brunei pop 1991 | 264,332 | older, 2015 Jul | same pattern | 2015 Jul 264,332 (current 262,596) |
| Austria GDP 1983 | 71,838,528,420 | current | URL indicator/NY.GDP.MKTP.CD, retrieved 2025-04-09 | 71,838,528,420.4075 |
| Burkina Faso GDP 1961 | 350,247,234 | current | same | 350,247,234.260712 |
| France Gini 2008 | 33.08 | older, 2017 Sep | URL donnees.banquemondiale.org/indicateur/SI.POV.GINI, retrieved 2016-12-20 | 2017 Sep 33.08 (current 33) |
| Belgium unemployment 2019 | 5.36 | current | URL indicator/SL.UEM.TOTL.ZS | 5.364 |
| Finland life exp. 2014 | 81.18049 | current | stated in UIS, URL data.uis.unesco.org DEMO_DS | 81.18049 |
| Guam life exp. 2012 | 78.689 | no release | same | UIS now 76.237 |
| Guinea fertility 2000 | 6.082 | no release | stated in UIS, URL queryid=239 | UIS now 5.918 |

10 of 10 agree on value, year, rank, reference, source value and bin.

### Notable rows, verified live

- South Sudan population 2017: 12,575,714, preferred rank, stated in World Bank Open Data with URL SP.POP.TOTL, retrieved 2019-04-08. World Bank 2019 Apr release 12,575,714 (also carried 2018 Jun to 2019 Apr, nine releases). Current 10,259,154. Gap +22.6%. Page correct.
- Puerto Rico GDP 2021: 217,800,000 with the US-dollar unit, normal rank (best rank, Puerto Rico has no preferred GDP statement), URL NY.GDP.MKTP.CD, retrieved 2023-08-26. Current 106,426,600,000. Nearest release value 106,368,900,000 (2023 July). No release read, gap -99.8%. Page correct.
- Argentina Gini 2020: 423, normal rank (best rank), URL SI.POV.GINI. Releases carried 42.3 (2022 Apr to 2023 Dec, 10 releases) and 42.7 (2024 Mar to 2026 Jul). No release read, +890.6%. Page correct and names no cause.
- Germany Gini: 1995 reads 287 (normal rank, not best rank since 2019 is preferred), no release read, +900%, in the data and correctly not listed. 2019 reads 31.7 (preferred), matches 2024 Jul, current 32.2, -1.6%, below the listing cutoff. Correct.
- South Sudan life expectancy 2016: 56.811, preferred, stated in UIS with URL data.uis.unesco.org DEMO_DS, no retrieval date. UIS versions carry 55.544 (Sept 2024 to Apr 2025) and 36.72 (Sept 2025 on). The World Bank carried exactly 56.811 in its releases of April 2018 to June 2019 (12 releases). The bin "no release read" is literally right for UIS (see F2 for what the page leaves out).
- DHY and XKS: 15 Republic of Dahomey population rows (1960 to 1974, stated in World Bank Open Data) all match an older World Bank release under BEN (2013 Jul to 2017 May or 2022 Sep). Kosovo GDP 2021 and 2022 match under XKX (2022 Dec to 2024 May, and 2023 July to 2023 Oct). Kosovo Gini 2017 (29) matches under XKX (2019 Mar to 2025 Apr), current 44.2. "All 18 match an older World Bank release" is correct. Read live: BEN 1974 in the 2017 May release is 3,184,547, XKX GDP 2021 in the 2024 May release is 9,412,034,299.23.
- No other legacy codes need mapping. Codes present in the archives but not in the current release are aggregates or territories with their own codes (YUG, CSK, YMD, ANT, GLP, MTQ, REU, MYT, GUF, CNI).

### Section 2 numbers

Recomputed from data/raw/s2 with own code. All match the page.

- Views (billions a month), last 12 months Nov 2025 to Oct 2026: Wikipedia human 11.36 to 13.98 (mean 12.48), Wikipedia all agents 18.78 to 23.29 (20.90), all projects human 12.36 to 14.73 (13.40), all projects all agents 22.62 to 27.91 (25.33). July 2024 to June 2025: 12.52 to 16.19 (14.42), 20.54 to 23.72 (21.78), 13.29 to 16.87 (15.10), 22.83 to 26.42 (24.23).
- Edits a minute, last 12: with bots all pages 300.2 to 393.2 (348.7), without bots 213.8 to 234.5 (224.5), with bots content 220.9 to 300.6 (254.2), without bots content 159.9 to 182.3 (171.6). FY: 298.0 to 345.8 (323.1), 225.1 to 253.0 (236.2), 222.8 to 265.3 (234.5), 177.1 to 194.0 (184.1). Editor types add up (all minus user, anonymous and both bot types is 0).
- Articles 68,737,713 open and 68,737,743 with closed editions. Editions 348 and 364. Commons files 150,427,922.
- Volunteer bounds, last 12, all open wikis: 110,903 to 329,245 (1+ edits), 38,123 to 122,836 (5+). Wikipedias only: 110,903 to 251,741, and 38,123 to 85,931. The Analytics API refuses all-projects and all-wikipedia-projects for the editors metric (HTTP 400, probed today), so "no count of people deduplicated across wikis" holds.
- Pre-first-capture means: Wikipedia human views Nov 2024 to Oct 2025 14.06 billion, edits with bots 322.7. Correct.
- Every outcome follows from the plan's band and containment rules. The 9 cannot-tell readings are honest. The issue is the moment for annual report counts (B1).

### Wayback readings

All 72 cached homepage captures were scanned. Every first-with and last-without pair is a real change on the page, not a broken capture. Before 7 Aug 2025 18:46 UTC the homepage was the older design ("written in over 300 languages", "270,000+ editors", "113+ million media files"). From then to 7 Nov 2025 it read "more than 15 billion views", "nearly 260,000 volunteers", "342 new edits", "over 64 million articles". On 7 Nov 2025 20:57 it changed to 265,000, 324, 65 million and "built by nearly 250,000". On 10 Nov 2025 16:30 "more than 15 billion" became "nearly 15 billion". On 20 Jul 2026 23:57 "65 million" became "67 million". All four later captures checked for each figure carry the phrase.

### DSA

- Rounding: 250 cells (11 families by 8 windows, 27 member states by 6 windows). One is not a whole thousand: Wikispecies, Aug. 2024 to Jan. 2025, 159,490. The rounding remark ("These estimates have been rounded to the nearest '000 (e.g. '1499' rounds to '1000'. '1500' rounds up to '2000').") sits directly under the families table that holds this cell, so the page's reading applies.
- Finland 2,960,000 in Jan to June 2025, July to Dec 2025 and Jan to June 2026. The windows are consecutive, non-overlapping half-years. Latvia repeats once (587,000, Jan to Jun 2024 and July to Dec 2024). No other repeat. Correct.
- EU total against the 27 member-state rows (sheet 10_AMAR): July to Dec 2025 total 155,663,000, sum 155,663,000, difference 0. Jan to June 2026 total 157,313,000, sum 157,313,000, difference 0. 27 member rows each (codes EL and SP stand for Greece and Spain). The total equals the sum exactly. Cross-filing: 27 of 27 equal the DSA page's column for the same half-year in both reports, and the page columns sum to the same totals.
- Bound: largest stated EU share of global family devices 78% (smaller families, Aug 2022 to Jan 2023). Wikipedia 20% to 23%. No cell above the bound. Correct.

---

## Findings

Severity: blocks ship (the page as built would state something false or misleading about a named party, or print a number the data do not hold), fix before ship (the page misdescribes its method or omits a disclosure the house rules require), note (optional).

### B1. Annual report counts are read at a moment that reverses their outcome. Blocks ship.

Rows: "66 million Wikipedia articles" (page: below), "135 million freely usable media files on Wikimedia Commons" (page: below), "More than 66 million articles." (page: consistent).

The plan reads counts "today" (10 Nov 2026), 16 months after the report's year ended. The page itself says annual report figures are read against the report's own year. The counts grew fast enough to flip the direction:

| Moment | Commons files | Wikipedia articles (sum) |
|---|---|---|
| End of the report's year | 121,579,203 (Commons Main Page, Wayback 26 Jun 2025 06:40 UTC) | 65,140,053 (en.wikipedia "List of Wikipedias" table, Wayback 1 Jul 2025 14:39 UTC, 365 rows summed) |
| A week before the report's first capture | 138,512,663 (10 Apr 2026 00:16 UTC) | 67,168,425 (23 Apr 2026 08:15 UTC, 368 rows) |
| Today (desk) | 150,427,922 | 68,737,713 |

The Commons Main Page states "a collection of N freely usable media files", the same words the report uses, and N is the same site statistic the desk reads. The article sums are a proxy from a table fed by site statistics. The desk should source its own.

At the end of the report's year all three stated bands lie above the count: 135 million (134.5 to 135.5 million) against 121.6 million is ABOVE, 66 million (65.5 to 66.5 million) against 65.1 million is ABOVE, more than 66 million against 65.1 million is ABOVE. At the first capture and today they read below, below, consistent. The page prints "below" against a named organisation's figures when the report's own moment reads the opposite way.

Fix: treat the moment as a candidate definition (end of the report's year, first capture of the report page, today), label it defined after the data with a dated plan note, and apply the plan's own rule that disagreeing candidates give cannot tell. All three rows become cannot tell, with the three readings printed beside them. "300+ Languages on Wikipedia" stays consistent at every moment.

### B2. A page number does not match the data. Blocks ship.

The page says "Figures that match a World Bank release: ... total fertility rate: 2,320 of 2,320". The data (section1 UIS-TFR wb_secondary) hold 2,302 matching an older World Bank release, 1 matching the current release, and 17 matching no World Bank release. The right figure is 2,303 of 2,320. My recount gives the same 2,302, 1 and 17.

Cause: build_page.py line 181 counts any key whose second part starts with `MATCHES_`, and `MATCHES_NO_RELEASE_READ` starts with it. Fix: count only `MATCHES_CURRENT` and `MATCHES_AN_OLDER_RELEASE`. Also, "life expectancy at birth: 2,749 of 2,750" puts the Rwanda 2025 row (nothing returned at either source) in the denominator of "figures that match no UIS release". Say 2,749 of 2,749.

### F1. The match is a tolerance, not "the precision the figure is written in", and GDP bins depend on the extra term. Fix before ship.

The rule as committed: half a unit of the last written digit (never coarser than three significant digits), plus |r| x 2^-24 (about 6 in 100 million of the release value), plus 1e-9. The page says only "agree at the precision the figure is written in".

For population the extra term decides 1 row (Mali 2020) and the three-digit floor 1 row (Bermuda 1975 "53000", current 53,129). The population headline holds.

For GDP written to the dollar, the extra term is larger than the half-unit on every figure above about $8.4 million (0.5 x 2^24). Without it, 395 of 1,407 GDP bins change: 245 from current to no release, 37 from current to older, 113 from older to no release. Half-unit-only GDP bins would be 421 current, 624 older, 360 no release, 2 nothing, instead of 703, 700, 2, 2.

- 357 of the 395 are the source's value cut (not rounded) at the written digit. Example: Belarus 1990, cited 17,389,558,232, current 17,389,558,232.9317 (off by $0.93, more than half a dollar). The term catches these, so the bins are right in spirit.
- 38 rows read "current" only because the term covers a later revision. Example: Kenya 2021, cited 109,703,659,313, which an older release carried to the dollar, current 109,703,658,904.994 ($408 apart). At the written precision, even allowing truncation, these match an older release, not the current one.
- The plan justifies the term by single-precision storage in some archived releases (April 1999). The current release comes from the API in double precision (17389558232.9317), so the rationale does not cover the current-release matches the term decides.

Fix: keep the committed rule, and describe it on the page: half a unit of the last written digit, at least three significant digits, plus about 6 in 100 million of the source's value (about $1,000 on a $17 billion GDP). Print the GDP sensitivity: 395 bins depend on that term, 357 of them are the source value cut at the written digit, and 38 would read as an older release.

### F2. The UIS rows imply the figures are unsourced. Fix before ship.

The page has no sentence saying the figures are wrong. The layout implies it, and the brief requires that it must not.

- 3,481 of 3,490 life expectancy figures cite UIS.Stat (http://data.uis.unesco.org/Index.aspx?DataSetCode=DEMO_DS). 3,164 of 3,176 fertility figures cite http://data.uis.unesco.org/index.aspx?queryid=239. That is the database UIS ran before its API. 3,472 and 3,158 carry no retrieval date. The dated ones were retrieved in Oct 2018 (18) and Feb 2018 (16). The API's own changelog: "2024-09-11, Version 1.0.0, Initial release of the UIS Data API".
- All 2,749 life expectancy figures that match no UIS release equal a World Bank release of the same indicator code. The newest World Bank release carrying them is from 2019 for 2,350, 2022 for 281, and other years for 118. For fertility, 2,303 of 2,320 match (2017 for 1,395, 2019 for 508, 2022 for 336).
- What the page shows: 78.8% and 73.0% "Matches no release read" in the main table, beside World Bank rows read against 142 releases. In the listing, "No release read" on all 41 UIS rows with gaps up to +54.7%. The caveat sits in a note under the "All" row and in a paragraph after the listing. The intro says "both still publish their older releases", which is not true of UIS before September 2024 through the API.

Fix:
(a) Intro: "The World Bank publishes its releases back to April 1989. The UIS data API keeps its releases from September 2024 on."
(b) Directly under the bins table, for the two UIS rows: nearly all of these figures cite UIS.Stat, the database UIS ran before its API, and nearly all that match no UIS release equal a World Bank release of the same indicator code (counts as above).
(c) In the listing, for UIS rows, replace "No release read" with "No UIS release kept (API from Sept 2024), equals World Bank release [newest]". This is the plan's own second reading, descriptive, not called the cited source.
(d) Correct the count (B2).

### F3. A match on unemployment carries little information about which release a figure came from. Fix before ship.

Placebo (referee's own reading): read each cited figure against every release's value for the same country two years earlier and two years later, years it does not describe.

| Group | Matches some release for the wrong year |
|---|---|
| Population | 0.1% (24 of 17,577 tries) |
| GDP | 0.0% (1 of 2,766) |
| Life expectancy | 0.2% |
| Fertility | 4.2% |
| Gini | 8.0% (6 of 23 for whole-number figures) |
| Unemployment | 43.8% (167 of 274 for whole-number figures, 61%) |

For population, GDP and life expectancy a match is strong evidence. For unemployment it is close to a coin flip. The page names a "newest release that carried it" for 82 listed unemployment rows and says "A figure that matches an older release carries that release's value". Also, 30 of the 31 unemployment figures within 1% are one country (Belgium). The country interval [0.0, 36.9] shows it, the text does not.

Fix: say "carries a value an older release carried, at the precision the figure is written in". For unemployment, add one sentence that a whole-percent figure also matches some release for a neighbouring year in most tries, labelled defined after the data, or drop the named release for whole-number rows. Optionally note that 30 of the 31 within-1% rows are Belgium.

### F4. The median column is not labelled absolute. Fix before ship.

CHECKS.md (III) says "The median gap is labelled absolute". The page header reads "Median gap, figures not matching the current release", beside a signed gap column. Fix: "Median absolute gap, figures not matching the current release". Correct CHECKS.md.

### F5. What was known before the plan is under-stated on the page. Fix before ship.

The scout file (SCOUT_WIKI_20261110.md, line 82, written before PLAN.md commit 49250d0) already reported "Finland is stated at 2,960,000 in three half-years in a row ... except Latvia, which repeats once". Discovery also read the DSA page before the plan (dsa_userbase_20261110.wikitext, identical to the scored copy, including the 159,490 cell). The repeats and rounding checks were written with those figures in view. The page says only "A first scout reading of population and of the homepage figures came before it".

Fix: add "and of the DSA member-state table (the Finland repeat)" there, and in the Repeats paragraph say the repeat was first seen in the scout reading before the plan.

### F6. Known-good 3 was run differently from the plan. Fix before ship (a plan note).

The plan says 10 rows "across groups" opened in wbgetentities, with value, year, rank and reference to agree. The code (hand_check_s1) reads the query service and compares the value only, with seed 11 and a uniform draw. It landed on 6 population, 3 fertility and 1 life expectancy rows, with no GDP, Gini or unemployment. The page describes what was done, so it is truthful, but the deviation needs a dated plan note. The substance holds: my live check of 10 stratified rows on value, year, rank, reference, source value and bin passed 10 of 10.

### F7. Headline scope. Fix before ship.

"population figures in Wikidata that cite the World Bank" means figures on items with an ISO 3166-1 alpha-3 code: 186 countries, territories and one historical state (Republic of Dahomey). Fix: "population figures for countries and territories in Wikidata that cite the World Bank".

### F8. The data feed is referred to but not linked. Fix before ship.

The volunteers note says "in the data feed" and the listing code can print "see data". The visible page links neither /wiki/live.json nor the full data file (live.json appears only in the head). Fix: add a visible link where "figures say where they live".

### F9. Volunteers: annual report bounds missing and a quote without its subject. Fix before ship.

The bounds table shows the last 12 months only. The defined-after-the-data sentence also covers the annual report figures, which were placed against July 2024 to June 2025 bounds. Those bounds are: Wikipedias only 114,822 to 272,487 (1+ edits), upper 88,451 (5+). All wikis 114,822 to 344,752 (1+), upper 120,494 (5+). They are not shown.

The quote "numbering more than 250,000" drops its subject. The source reads "Volunteer contributors add the knowledge on Wikipedia, and they live in almost every country of the world, numbering more than 250,000." The subject is what tells the reader which scope applies.

Fix: add the FY rows to the table. Quote the full sentence. Say which scope each figure is placed against (homepage "supports nearly 265,000" against all wikis, the three Wikipedia figures against Wikipedias only).

### Notes

- N1. Wikidata's own stated bounds (upperBound and lowerBound) sit on 145 rows: 126 unemployment rows at plus or minus 1 on whole percentages, 17 GDP rows equal to half a written unit, and 2 population rows. Using them would move 21 unemployment rows from older to current, and nothing else. The plan chose the written form (Addendum 1). This could be shown as a sensitivity.
- N2. Truncated copies in the small series: a rule that also accepts a value with its digits cut would move 35 rows. That is 12 unemployment rows from older to current. Fertility: 12 from no release to current, 6 from no release to older, 3 from older to current. Life expectancy: 2 rows.
- N3. The code widens the size interval by 2^-24 on each side, which the plan's size rule does not. That changes 3 outcomes. Bolivia GDP 1962 and 1971 go from below to cannot tell. Greece fertility 2009 (1.49 against 1.5) goes from within 1% to cannot tell. Either note it or align with the plan. Also, "Cannot tell means the figure is written too coarsely to say, or the source has no current figure" misses the Bolivia GDP rows for 1960 to 1971, whose gap sits on -1.0% itself.
- N4. Views: both view figures name Wikipedia. By the plan's own rule ("when the Foundation states the definition, that definition decides") the all-projects candidates should drop for those two. The outcome is unchanged (Wikipedia human: cannot tell, all agents: below, so still cannot tell).
- N5. Quotes from figure cards: 9 of 16 quotes join separate page elements (lead-in, big number, caption). Example from the homepage HTML: "Wikipedia receives nearly" / "15 billion" / "views each month." The words and order are verbatim. Say "as shown on the page's figure card" or render the break. The languages row shows the 2026 sentence ("over 67 million articles") beside a first-seen date of 7 Aug 2025, when the sentence read "over 64 million articles". Show the phrase "300+ languages" alone there. The homepage quote also stops before its subject (", Wikipedia is the home of trusted information online").
- N6. "These are the values most likely to be read by other sites and tools" is not supported by anything on the page. Use "These are the values a plain query returns."
- N7. "under CC0, through the Wikimedia Analytics API and each wiki's site statistics": CC0 is stated for the Analytics API, not for site statistics. Reword.
- N8. "The history dumps published since the November 2025 snapshot carry a global user id": the schema page in discovery shows event_user_central_id but no date. Source the date or drop it.
- N9. Politeness: the plan says Wikimedia requests stay under 200 a minute. http.log shows 6 minutes above 200 across Wikimedia hosts (peak 203). The pacer is per host and steps ran in parallel (site statistics: 367 requests in 103 seconds across 365 hosts). Add to Note 1.
- N10. Repeats context: the DSA page's own note (a) says the Jan to June 2025 column was re-analysed. Revision 546664 (15 Jan 2026) changed Finland's Jan to June 2025 figure from 2,961,000 to 2,960,000 (receipts/dsa_oldid_546663.wikitext and 546664). Showing that is descriptive. It is better than the closing line "The per-country device counts behind these figures are not published", which reads as a hint.
- N11. Readings added after the data but not labelled on the page: the whole-percent unemployment count (Note 1.2), "two distinct sets" of UIS figures (Note 1.1), and the All-row UIS share. They are descriptive, so either label them or accept them as descriptive.
- N12. "Each country links to the statement": the links go to the item's property section (for example #P1082), not to the statement.
- N13. Seven listed unemployment rows read "Current release" with gaps over 10% (Bhutan "3" against 2.63, +14.1%). That follows the rule (plus or minus half a point) and the whole-percent note covers it.
- N14. The planted known-good rows sit on AFE (an aggregate). They work but exercise population only.
- N15. "countries" in table cells includes territories and one historical state.
- N16. CHECKS P9 says the lint holds, but lint_copy.py exits 1 with 13 review prompts (12 for "editor" inside definition names, 1 for "because" in a method sentence). None is a real breach. ship.sh does not run it.
- N17. "consistent (rounding to the nearest thousand allows up to 13,500)" is right. "Equal (difference 0)" is plainer and is what the files show.

---

## Section 2: what each stated figure is

The Foundation states no definition for any of these. "Fits" is the referee's reading of which candidate the data match. It is not for the page.

| Figure (page) | Scope named | What the data fit | Page outcome | Referee |
|---|---|---|---|---|
| "Wikipedia receives nearly 15 billion views each month." (home) | Wikipedia | Human traffic: Nov 2024 to Oct 2025 mean 14.06 bn sits in 13.5 to 15 bn. All agents 19 to 23 bn does not fit. | cannot tell | Honest |
| "The Wikimedia Foundation supports nearly 265,000 volunteers every month." (home) | all projects | No deduplicated count. All-wiki 1+ edit bounds 110,903 to 329,245. | cannot tell | Honest |
| "Every minute 324 new edits are made to Wikipedia." (home) | Wikipedia | With bots, all pages. 12-month means ending Feb 2025 to Dec 2025 ran 320.5 to 325.4 (Jun 2024 to May 2025: 323.9). Without bots: 224 to 236. | cannot tell | Honest. A plain figure (plus or minus 0.5) can never be inside a monthly range. |
| "With over 67 million articles, in 300+ languages" (home) | Wikipedia | Sum of article counts 68.74 m. 348 open editions. | consistent, consistent | Right moment (present tense) |
| "Wikipedia is built by nearly 250,000 volunteers" (home) | Wikipedia | Includes people who "fix code". No deduplicated count. | cannot tell | Honest |
| "114 million images, photographs, videos and music files and counting" (projects) | Commons | File count | consistent | Right ("and counting") |
| "More than 340 edits every minute." (report) | Wikipedia (context: "By any measure, Wikipedia is extraordinary") | FY with bots mean 323.1, peak month 345.8. The same report also says 324. | cannot tell | Honest |
| "More than 66 million articles." (report) | Wikipedia | 65.1 m at the year end, 67.2 m at first capture, 68.7 m today | consistent | Moment flips (B1) |
| "66 million Wikipedia articles" (report) | Wikipedia | as above | below | Moment flips (B1) |
| "300+ Languages on Wikipedia" (report) | Wikipedia | 348 open editions | consistent | Robust at every moment |
| "135 million freely usable media files on Wikimedia Commons" (report) | Commons | 121.6 m at the year end, 138.5 m a week before first capture, 150.4 m today | below | Moment flips (B1) |
| "324 edits to Wikipedia every minute" (report) | Wikipedia | With bots, FY mean 323.1 | cannot tell | Honest |
| "250,000 volunteer editors of Wikipedia around the world" (report) | Wikipedia editors | FY Wikipedias-only 1+ bounds 114,822 to 272,487 | cannot tell | Honest |
| "numbering more than 250,000" (report) | Wikipedia contributors (subject dropped, F9) | same | cannot tell | Honest |
| "Nearly 15 billion views on Wikipedia every month" (report) | Wikipedia | Human traffic: FY mean 14.42 bn is inside the band | cannot tell | Honest |
| DSA figures | stated method | EU devices are not public | cannot tell | Honest |

Quotes are verbatim and each carries its page URL and the read date (10 Nov 2026). The stored HTML hashes match pages_read.json: home 26ac89a9, projects 47c88cc6, report 3ba23bd6.

---

## Copy check (item 6)

- Semicolons: none in the main text.
- Adjectives about Wikidata editors or the Foundation: none.
- Cause named: none for any gap. "because the reference names that series" and "since the figures for one country come from one source series" are method statements. The Finland closing line reads as a hint (N10).
- Intervals: every share says Wilson 95% or countries 95%, and the note explains both. Delivered ranges say "monthly low to high". The median is not labelled absolute (F4).
- Figures say where they live: rows link to Wikidata, the source record and the archived release. Stated figures link to their page and captures. The data feed is not linked (F8).
- Post-hoc labels: the alias reading and the volunteer placement are labelled. Three descriptive after-data notes are not (N11). B1's fix needs the label.
- Attribution: Wikidata, the Analytics API, the World Bank (CC BY 4.0), UIS (CC BY-SA 4.0, confirmed in the UIS OpenAPI licence block), the Foundation pages and the Wayback Machine are named, plus "courtesy of the Wikimedia Foundation".
- Page numbers against the data: all match except "2,320 of 2,320" (B2).

---

## Verdict: FIX THEN SHIP

The core of the desk holds. Section 1 recounts exactly from raw with independent code. Ten seeded rows and every notable row check out live. Section 2 numbers, Wayback readings and DSA checks all reproduce.

Before shipping:
- B1: make the three annual report count rows cannot tell, with the year-end, first-capture and today readings shown, under a dated plan note.
- B2: fix the fertility count (2,303 of 2,320) and the life expectancy denominator.
- F1 to F9: copy, label and plan-note fixes. The largest are describing the match tolerance and the GDP dependence on it (F1), and putting the UIS history and World Bank equality next to the UIS rows (F2).

No item needs new data collection beyond the moment readings for B1.
