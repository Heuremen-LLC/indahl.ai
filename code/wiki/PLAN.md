# WIKI: cited figures against their source, and the Foundation's numbers against its own data. Plan, written before any comparison is read.

Written 10 Nov 2026 (UTC), 9 Nov HST. Desk of the HERMES division. Two sections on one page.

## Known before this plan (stated so the plan is not read as blind where it is not)
1. The scout's proof runs of 9-10 Nov (research_wiki/SCOUT_WIKI_20261110.md) were read before this plan: population (P1082) of sovereign states citing World Bank Open Data against 29 World Bank releases (1,102 of 8,155 values matched the current figure, 7,034 an older release), and the Foundation homepage figures against the Analytics API (views, edits, volunteers, articles, Commons files) and the DSA filings. Those counts are known. This plan fixes the rules for the desk's own reading, which re-pulls everything with its own code, widens the frame, and reads every archived release.
2. Discovery before this plan read only frame counts and schemas, never a cited value against a source value: which properties carry World Bank or UIS references on items with an ISO 3166-1 alpha-3 code (data/raw/discovery/), the reference URL patterns, units, ranks and qualifiers; the World Bank archive's list of 142 releases; the UIS API's 15 versions; the stated pages (homepage, projects page, annual report 2024-2025, DSA userbase page, the two harmonised DSA reports for Wikipedia).

## Section 1: cited figures against their source

### Frame (fixed now)
Items: every Wikidata item with a best-rank ISO 3166-1 alpha-3 code (P298). A statement is in the frame when its property and one of its references fall in one of these groups:

| Group | Property | Reference that puts it in the frame | Source series read |
|---|---|---|---|
| WB-POP | P1082 population | stated in (P248) World Bank Open Data (Q21540096), or a reference URL on worldbank.org or banquemondiale.org | World Bank WDI SP.POP.TOTL |
| WB-GDP | P2131 nominal GDP | same | NY.GDP.MKTP.CD (GDP, current US$) |
| WB-GINI | P1125 Gini coefficient | same | SI.POV.GINI |
| WB-UNEMP | P1198 unemployment rate | same | SL.UEM.TOTL.ZS |
| UIS-LE | P2250 life expectancy | stated in UNESCO Institute for Statistics (Q3152127), or a reference URL on uis.unesco.org | UIS SP.DYN.LE00.IN |
| UIS-TFR | P4841 total fertility rate | same | UIS SP.DYN.TFRT.IN |

Series rule: when a reference URL names an indicator code (for example data.worldbank.org/indicator/NY.GDP.MKTP.CD), that code must be the group's series, or the statement is set aside and counted as "reference names another series". A World Bank reference with no code in its URL takes the group's series.
Set aside and counted, by reason, never scored: deprecated rank; no point in time (P585); more than one point in time; a qualifier that changes what is measured (P21 sex, P518 applies to part, P642 of, P1013 criterion, P1001 applies to jurisdiction); a value with a unit other than the group's (WB-GDP: US dollar Q4917 or no unit; WB-POP, WB-GINI, UIS-TFR: no unit or "1" Q199; WB-UNEMP: percent Q11229 or "1"; UIS-LE: year Q577 or annum). WB-GDP values with no unit are scored, because the reference names a US-dollar series, and are reported apart from values that carry the US-dollar unit.
Unit of reading: a distinct cited figure, keyed by (item, series, year, value). Two statements with the same key are one row. Two different values for one country-year are two rows.
Country code: the item's ISO3 code. Legacy codes in older World Bank releases are mapped before matching, fixed now: ROM to ROU, ZAR to COD, TMP to TLS, ADO to AND, IMY to IMN, KSV to XKX, WBG to PSE. Any other legacy code found in the data is added only by a dated addendum marked defined after the data.

### Delivered side (fixed now)
World Bank: the current WDI release from the indicator API (api.worldbank.org/v2/country/all/indicator/CODE, source 2), read on every run, and every one of the 142 releases in the WDI Database Archives (source 57, April 1989 to July 2026), read once and kept with their SHA-256. UIS: the API's default version and every published version (15, September 2024 to May 2026). The UIS API keeps no release before September 2024, so a UIS figure imported earlier can match only a release still carrying it. Keyless reads, one request at a time, a pause between requests, the house User-Agent.

### Matching rule (fixed now)
Written precision of a cited value: for a value written with d decimal places, the unit u is 10^-d. For a whole number with s significant digits and k trailing zeros, u is 10^k when s is 3 or more, otherwise 10^(k - (3 - s)) and never below 1, so a figure is never treated as coarser than its first three significant digits.
A release value r matches a cited value v when |v - r| <= u/2 + |r| x 2^-24 + 1e-9. The middle term allows for releases stored in single precision (the April 1999 release stores 1,210,000,128 for 1.21 billion). It is about 6 in 100 million of the value.

### Bins (fixed now), one per row
- MATCHES_CURRENT: the current release has a value for that country and year, and it matches.
- MATCHES_AN_OLDER_RELEASE: not the above, and at least one older release read matches. The row names the newest release that carried the value and the first.
- MATCHES_NO_RELEASE_READ: at least one release read has a value for that country and year, and none matches.
- SOURCE_UNREADABLE (NOTHING_RETURNED): no release read has a value for that country and year in that series, or the series could not be read. The reason is kept.
Shares per group and over all groups, each with a Wilson 95% interval over rows. Rows of one country share an import and a source series, so they are not independent: beside each Wilson interval a second 95% interval comes from resampling countries with replacement (2,000 resamples, seed 7, percentile interval). The outcome rules below use neither interval. Both are shown and labelled.

### Size reading (fixed now)
Size that matters: 1 percent of the source's current figure, for every group.
Gap of a row: g = (cited - current) / current, with an interval from the written precision: [(v - u/2 - c)/c, (v + u/2 - c)/c].
Four outcomes per row (country-year), the stated figure relative to the delivered one:
- ABOVE: the whole interval is above +1 percent (the cited figure is more than 1 percent above the source's current figure).
- BELOW: the whole interval is below -1 percent.
- CONSISTENT: the whole interval lies within plus or minus 1 percent. This is a bound, printed as within 1 percent, never "the same".
- CANNOT_TELL: the interval crosses plus or minus 1 percent, or the source has no current value for that country and year (counted apart by reason), or the current value is zero.
Shares of the four outcomes per group with Wilson 95% intervals and the country-resampled interval. Also descriptive, without outcome: the median absolute gap among rows that do not match the current release.

### Sub-readings fixed now
1. Defaults: rows whose statement has the best rank for that item and property (the value a plain query returns, wikibase:BestRank). Bins and size outcomes reported for defaults apart.
2. Listing rule for notable rows: per group, the 10 default rows with the largest absolute gap, and every default row whose gap is beyond 10 percent. Each listed row is opened by hand first (hand check below).
3. UIS second reading, descriptive, no outcome: UIS rows that match no UIS release read are also read against the World Bank's releases of the indicator code they carry (SP.DYN.LE00.IN, SP.DYN.TFRT.IN). UIS does not state the upstream source of these two series in its API, so this is never called the cited source.
4. By release: for MATCHES_AN_OLDER_RELEASE rows, the count by year of the newest release that carried the value.

### Known-good (fixed now)
1. Planted rows run through the same matcher before the real rows: a value equal to the current release must read MATCHES_CURRENT; a value equal to a value only an older release carried must read MATCHES_AN_OLDER_RELEASE naming that release; a value 0.5 percent away from every release must read MATCHES_NO_RELEASE_READ; a country code no release carries must read SOURCE_UNREADABLE. A planted gap of +2 percent must read ABOVE, -2 percent BELOW, +0.5 percent CONSISTENT, and +1 percent with a precision wide enough to cross the line CANNOT_TELL. A failure stops the run and every outcome is printed CANNOT_TELL.
2. Two reads of one release: our pull of each of the 29 releases the scout pulled on 9 Nov must equal the scout's file value for value.
3. Live hand check: 10 rows chosen by a seeded draw (seed 11) across groups are opened in the live Wikidata entity JSON (wbgetentities) and in the World Bank or UIS single-country call. The value, year, rank and reference must agree with the frame. A disagreement is reported and the row is marked.

### Hand check (fixed now)
Every row listed under the listing rule is opened by hand in Wikidata and in the source before it is shown.

## Section 2: the Foundation's numbers against its own data

### Stated side (fixed now)
Each stated figure is quoted verbatim with its URL and the date read, from the live page read on each run (HTML, text and SHA-256 kept): the Foundation homepage (wikimediafoundation.org), the projects page (wikimediafoundation.org/what-we-do/wikimedia-projects/), the 2024-2025 annual report (wikimediafoundation.org/annualreports/2024-2025-annual-report/), the DSA userbase statistics page (foundation.wikimedia.org, Legal: ... Digital Services Act Userbase Statistics) and the harmonised DSA reports for Wikipedia (Commission template, XLS, reporting periods July to December 2025 and January to June 2026).
How long each figure has stood: from the Wayback Machine capture index (CDX, status 200, collapsed by digest), the first capture whose text carries the verbatim phrase and the last earlier capture that does not, found by bisection over the captures. Read one at a time with a pause.
Out of scope, stated: "one of the top 10 most visited websites", "~8 million donors", "185 Wikimedia affiliates". Wikimedia's own public data do not deliver them.

### What each figure is (fixed now)
The Foundation's pages do not define these figures. Where no definition is stated, the candidate definitions are run side by side:
- Views: V1 Wikipedia, every edition in the site matrix (open and closed), human traffic (agent user); V2 the same, all agents (user, spider, automated); V3 all Wikimedia projects, human; V4 all projects, all agents. Monthly page views from the Analytics API (CC0).
- Edits a minute: E1 all Wikipedias, every editor type including bots, all pages; E2 registered and anonymous editors without bots (user plus anonymous); E3 every editor type, content pages; E4 without bots, content pages. Monthly edits divided by the minutes in that month.
- Articles: A1 sum of each open Wikipedia's article count (site statistics, read today); A2 the same with closed editions.
- Languages: L1 number of open Wikipedia editions; L2 with closed editions.
- Commons files: C1 Commons file count (site statistics, read today). One definition.
- Volunteers: the Analytics API counts editors per wiki only. It has no count of people deduplicated across wikis. Every volunteers figure is CANNOT_TELL by this rule, with that reason. Shown beside it, descriptive: for registered editors with 1 or more and with 5 or more edits in a month, a lower bound (the largest single wiki that month) and an upper bound (the sum over wikis, which counts a person once per wiki), for all open wikis and for Wikipedias only.
- DSA figures: the DSA page states its definition (EU unique devices averaged over six months, divided by 2.4 devices per person). EU device counts are not published, so the figures themselves are CANNOT_TELL by this rule. The checks that public data allow are listed below.

### Windows (fixed now)
Homepage and projects page figures are in the present tense and are read against the latest 12 complete months (November 2025 to October 2026 at the first run; the window moves with each run). Annual report figures are read against the report's own year, July 2024 to June 2025. Counts (articles, languages, files) are read today. Descriptive, no outcome: each homepage rate is also shown for the 12 complete months before the month of the first capture carrying it.

### Word rules (fixed now)
- "nearly X": the band [0.9X, X].
- "over X", "more than X": the band above X, open at the top.
- "X+", "X and counting": the band from X up.
- a plain figure "X": X plus or minus half a unit of its last written significant digit (324: 323.5 to 324.5; 250,000: 245,000 to 255,000; 66 million: 65.5 to 66.5 million; 135 million: 134.5 to 135.5 million).

### Outcomes (fixed now), the stated figure relative to the delivered value
Delivered interval per definition: for a rate stated "each month" or "every minute", the lowest and highest monthly value in the window; for a count read today, the single value.
- ABOVE: the stated band lies wholly above the delivered interval.
- BELOW: the stated band lies wholly below it.
- CONSISTENT: the delivered interval lies wholly inside the stated band.
- CANNOT_TELL: otherwise (they overlap without containment), or no data.
Across definitions: when the Foundation states the definition, that definition decides. When it does not, the figure takes the outcome its candidate definitions share. When they disagree (they straddle the stated figure), the figure is CANNOT_TELL, and each definition's reading is printed beside it.
Second ruler, descriptive, beside each definition: where the 12-month mean sits against the band (inside, above, below).

### DSA checks (fixed now)
1. Rounding: the DSA page says its figures "have been rounded to the nearest '000". Count the cells of both tables that are not whole thousands. CONSISTENT when there are none. Otherwise the count and the cells are printed.
2. Sums: in each harmonised report, the EU total against the sum of its 27 member-state rows. CONSISTENT when they differ by no more than 13,500, the most that 27 roundings to the nearest thousand can add. Otherwise ABOVE or BELOW.
3. Cross-filing: each harmonised report's member-state rows against the DSA page's member-state column for the same half-year, row by row (equal or not).
4. Bound: for each project family and six-month window on the DSA page, the stated EU devices (recipients x 2.4) against the global unique devices of that family averaged over the same six months (Analytics API, all sites). ABOVE when the stated EU devices exceed the global devices. Otherwise CONSISTENT with the bound, printed with the implied EU share. CANNOT_TELL when the global series is missing for any month of the window.
5. Repeats, descriptive: member-state figures repeated exactly in consecutive half-years are listed. No cause is named.

## Not claimed
Anything about the people who write Wikidata or Wikipedia. That an older release's figure is wrong, or that the current one is true: the source revises its own history, and a row that carries an older release's figure is a copy of that release. Why any figure differs: the desk measures gaps, never their cause. Any reading of a figure whose definition the Foundation does not state, beyond the candidate definitions run side by side.

## Politeness and terms
User-Agent "HeuremenLLC-research/1.0 (https://indahl.ai)" on every request. One request at a time. Wikimedia REST and Action APIs under the published 200 requests a minute for a compliant User-Agent; the Wikidata Query Service under its 60 seconds of processing a minute, with Retry-After honoured on 429 and 5xx. World Bank and UIS reads paced at about one a second. No account, no key, no edit anywhere. Licences: Wikidata and Analytics data CC0, World Bank WDI CC BY 4.0, UIS CC BY-SA 4.0, Foundation pages CC BY-SA 4.0. Wikimedia, the World Bank and UIS are attributed on the page.

## Addendum 1 (10 Nov 2026, before any comparison was read): reading details
1. Statements are read from the live Wikidata API (wbgetclaims, one call per item and property). The query service is used only to list the items whose statements carry a frame reference. The API keeps each amount as written ("+2.10"), while the query service stores a decimal that can drop trailing zeros, and the written precision rule needs the written form.
2. Point in time: a date with month or day precision is read as its year. A date coarser than a year is set aside and counted ("point in time coarser than a year").
3. Default (sub-reading 1) is computed over all of the item's statements of that property, not only frame statements: a frame statement is a default when it has preferred rank, or normal rank and the item has no preferred statement of that property.
4. A World Bank current-release row with an empty country code is skipped (aggregates). UIS geoUnit codes are ISO3 and are read as they are.
5. Section 2 page views for V1 and V2 sum every Wikipedia edition in the site matrix that is not private. An edition with no page view rows in a month adds zero and is counted.
6. The run reads the harmonised DSA reports with the xlrd package. Run with the desk's venv python (venv/bin/python). Without xlrd the two sums and the cross-filing checks print CANNOT_TELL with that reason.

## Note 1 (10 Nov 2026, after the first reading): what the data showed that the plan did not anticipate. No rule changed.
1. UIS. The API's 15 versions hold two distinct sets of values for each of the two series: one from September 2024 to April 2025, one from September 2025 on. A UIS figure that matches an older UIS release names a version from the first set.
2. Unemployment. 137 of the 203 unemployment figures are written as whole percentages ("7"), so the written precision rule matches them to the nearest point. The size reading reads 54 of those 137 as CANNOT_TELL (70 of all 203). The page says so.
3. Codes, defined after the data. The 18 World Bank figures that returned nothing are held under codes the World Bank does not use: 15 population figures on the Republic of Dahomey (ISO 3166-3 code DHY, 1960 to 1974, a territory the World Bank files under BEN) and 3 figures on Kosovo (Wikidata code XKS, the World Bank's XKX). Read under the World Bank's codes, all 18 match an older World Bank release. This is shown on the page and in the data as a reading defined after the data. The bins are unchanged, and the plan's legacy list is unchanged.
4. Wayback. The projects page and the annual report page have no capture at their present address before 7 August 2025 and 17 April 2026, so "how long it has stood" for their figures is "since the first capture of this page". For every figure, four evenly spaced later captures were read and all carry the phrase.
5. Volunteers, defined after the data. With one or more edits in a month, every stated volunteers figure lies between the lower and upper bounds. With five or more edits, every stated figure lies above the upper bound. The outcome stays CANNOT_TELL by rule.
6. Listing rule. It lists 218 rows (75 GDP and 82 unemployment rows have a gap beyond 10 percent). The page shows 10 per figure in its table and the rest in a collapsed block. All rows are in the data feed.
7. DSA rounding. One of the 250 figures on the DSA page is not a whole thousand (Wikispecies, August 2024 to January 2025, 159,490). Per the rule, the count and the cell are printed with no outcome label.
8. Politeness. The Wikidata API answered 429 four times at about four requests a second, and the Wayback Machine refused some connections at one request every three seconds. Both were retried after their Retry-After. The paces are now about 0.6 seconds and 6 seconds.

## Note 2 (10 Nov 2026, after the outside referee's report, FIX THEN SHIP). Items marked defined after the data were written after the data were read.
1. Annual report counts (referee B1), defined after the data. The report does not state the moment its counts describe. "66 million Wikipedia articles", "More than 66 million articles.", "135 million freely usable media files on Wikimedia Commons" and "300+ Languages on Wikipedia" are read at three moments as candidate definitions: the end of the report's year (30 June 2025 23:59:59 UTC), just before the report page's first Wayback capture (17 April 2026 14:45:19 UTC), and today. Past counts come from the revision of Commons "Data:Wikipedia statistics/data.tab" in force at that moment (CC0, posted by a bot from each wiki's site statistics): revision 1050891402 of 30 June 2025 21:47 UTC and revision 1198958058 of 17 April 2026 13:12 UTC. Today stays the direct site statistics read. The table's revision at the time of our direct read differs from it by 225 articles and 3,889 files, about two hours apart. Disagreeing moments give CANNOT_TELL by the plan's own rule. Articles: 65,137,525, 67,110,817, 68,737,743. Commons files: 121,944,090, 139,312,316, 150,427,922. Editions: 356, 361, 364. The three count rows are CANNOT_TELL (ABOVE at the year end, BELOW or CONSISTENT later). "300+" is CONSISTENT at every moment.
2. Known-good 3 (referee F6). The first run read the Wikidata Query Service (value only) with a uniform seed-11 draw (6 population, 3 fertility, 1 life expectancy rows). It was rerun as the plan specifies: the live entity JSON (wbgetentities) for value, year, rank and frame reference, and the source's single-country record for the release the bin names. The draw is stratified, seed 11, quota 3 population, 2 GDP, 1 Gini, 1 unemployment, 2 life expectancy, 1 fertility, a quota defined after the first run. 10 of 10 agree on all six checks. The first run stays in the data.
3. Size rule (referee N3). The code widened the size interval by 2^-24 on each side, which the plan's size rule does not. It now follows the plan. Three outcomes change: Bolivia GDP 1962 and 1971 read below (were cannot tell), Greece fertility 2009 reads within 1 percent (was cannot tell). Defined after the data: twelve Bolivia GDP figures (1960 to 1971) sit on the 1 percent line, each gap -1.0000 percent, and their outcome turns on the ninth digit (2 below, 10 cannot tell). The page says so.
4. Views scope (referee N4), defined after the data. Both view figures name Wikipedia, so by the plan's rule that a stated definition decides, the Wikipedia candidates decide their outcome and the all-projects candidates are shown for reference. Outcomes unchanged.
5. Volunteers (referee F9), defined after the data. Each figure is placed against the scope it names, in its own window: the homepage's "supports nearly 265,000 volunteers" against all wikis, the three figures about Wikipedia against Wikipedias only. Bounds for both windows are shown. The outcome stays CANNOT_TELL by rule. "numbering more than 250,000" is now quoted as its full sentence, and its Wayback reading is unchanged.
6. Match tolerance (referee F1), descriptive, defined after the data. The page states the committed rule exactly. With half a written unit alone, 395 of the 1,407 GDP bins change (245 current to no release, 113 older to no release, 37 current to older): 357 are the source's value with its digits cut, not rounded, at the written digit, and 38 are figures an older release carried to the dollar that the current release revised by less than the term. Half-unit GDP bins: 421, 624, 360, 2. Population: 1 bin. Other figures: none. The plan justified the term by single-precision storage in archived releases. The current release is read in double precision, so for current-release matches the term acts as a tolerance, and the page says so. The bins stay as committed.
7. Wrong-year chance match (referee F3), descriptive, defined after the data. Each figure is read against every release's value for the same country two years earlier and two years later. Population 24 of 17,577 tries (0.1%), GDP 1 of 2,766, Gini 16 of 199 (8.0%), unemployment 177 of 404 (43.8%, whole percents 167 of 274), life expectancy 16 of 6,976, fertility 267 of 6,347 (4.2%). The page prints it for unemployment, and that 30 of the 31 unemployment figures within 1 percent are for Belgium.
8. UIS (referee F2), descriptive, defined after the data. 3,482 of 3,490 life-expectancy figures and 3,164 of 3,176 fertility figures cite a URL on data.uis.unesco.org (UIS.Stat, the database before the API). 3,472 and 3,158 carry no retrieval date. Of the figures that match no UIS release, all 2,749 life-expectancy figures and 2,303 of 2,320 fertility figures equal a World Bank release of the same code (sub-reading 3). The listing names that release for UIS rows. The intro no longer says both sources still publish their older releases.
9. Page count (referee B2). The page counted "matches no release read" as a match in sub-reading 3 and printed 2,320 of 2,320 for fertility. It now counts current and older matches only, over the figures that match no UIS release (2,303 of 2,320, and 2,749 of 2,749).
10. DSA (referee N10, F5), descriptive. Revision 546664 of the DSA page (15 January 2026, "Update Jan - June 2025 data following improvements to automated traffic detection") changed Finland's January to June 2025 figure from 2,961,000 to 2,960,000. The page shows it with the page's own note on that column. The scout's reading before this plan already reported the Finland repeat and the 159,490 cell, and the page says so.
11. Politeness (referee N9). In the first run six minutes went above 200 requests a minute across Wikimedia hosts (peak 203), because the pacer was per host and steps ran in parallel. The pacer is now shared across Wikimedia hosts at no less than 0.31 seconds, and Wikimedia steps are run one after another.
12. Known-good 1 (referee N14). The planted rows now sit on a country in the frame (Afghanistan 1990), not an aggregate. Passed.
13. Page wording (referee F4, F7, F8, N5, N6, N7, N8, N11, N12, N15, N17). The median is labelled absolute. The headline says countries and territories. The data feed is linked. Figure cards are labelled and sentences are quoted in full. Descriptive counts made after the data are labelled. Site statistics are not called CC0 (the statistics table is). The history-dump date is dropped. Country links are described as the item's statements for the property. Equal sums read "equal (difference 0)".
14. Not taken: N1 (Wikidata's own stated bounds as a tolerance) and N2 (cut copies in the small series), both optional sensitivities. N16: the copy lint prints review prompts that are not breaches, and the check block now says so.
