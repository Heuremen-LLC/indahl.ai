# SOCIAL section 1: two filings, one platform. Plan, written before any comparison count.

Written 9 November 2026 (HST), 10 November UTC. Committed to git in this folder before the first count of the database by platform.

## Claim read
Each very large online platform (VLOP) publishes a harmonised DSA transparency report in the template of Commission Implementing Regulation (EU) 2024/2835 (Annex I, CSV files). For each half-year it states how many content moderation measures it took, how many of them were solely automated and how many were not, how many it took on its own initiative (split by illegality and by terms and conditions), and how many actions it took on notices.
The same platform files one statement of reasons per decision to the EU DSA Transparency Database.
Question: for the same platform and half-year, how does the number of statements in the database compare with the number the report states?

## Data
Stated side: each platform's report files (zip of CSV, or XLSX with the same sheets). Periods read: 2025-07-01/2025-12-31 (the first harmonised period) and 2026-01-01/2026-06-30. Every file is kept under data/raw/reports/<platform>/<period>/ with source_url.txt, and data/sources.json lists URL, sha256, publication date (verbatim from 1_report_identification) and version. Where a platform published an updated version, the latest version is read and the earlier one is listed.
Delivered side: the Commission's monthly aggregates of the database, "complete" version, CC BY 4.0, keyless:
https://d3vax7phxnku8l.cloudfront.net/agg/pqt/data/tdb_data/global___full/aggregations/aggregated-complete-YYYY-MM-01-parquet.zip
for created_at months 2025-07 through the newest month published (2026-11, partial, at the first read). Each zip is checked against its published .sha1. The configuration file (aggregated-complete.configuration.yaml) lists the grouping columns, which include platform_name, automated_decision, automated_detection, source_type, decision_ground, territorial_scope, application_date (day), created_at (day) and content_date (day). The column count is the number of statements in the group. The "simple" aggregates are downloaded for known-good KG2 only.
Coverage: the VLOPs that file to the database. Google Search and Bing are search engines, which do not file statements of reasons, and are not read.

## Codebooks (read before this plan)
Database (API documentation, data/raw/docs/tdb_api_documentation.txt):
- source_type: SOURCE_ARTICLE_16 "Notice submitted in accordance with Article 16 DSA", SOURCE_TRUSTED_FLAGGER "Notice submitted by a trusted flagger", SOURCE_TYPE_OTHER_NOTIFICATION "Other type of notification", SOURCE_VOLUNTARY "Own voluntary initiative".
- automated_detection: "Yes" or "No", "decision taken in respect of automatically detected means".
- automated_decision: AUTOMATED_DECISION_FULLY "Fully automated", AUTOMATED_DECISION_PARTIALLY "Partially automated", AUTOMATED_DECISION_NOT_AUTOMATED "Not automated".
- decision_ground: DECISION_GROUND_ILLEGAL_CONTENT, DECISION_GROUND_INCOMPATIBLE_CONTENT.
- application_date: "the date that this decision starts from". created_at: when the statement entered the database.
- territorial_scope: EU and EEA country codes. In the aggregates it is one string joined by "_", with EU, EEA and EEA_no_IS for the full sets, and the empty string when none was given.
Template (Annex II instructions, data/raw/docs/ir2024_2835/annex_II_instructions.txt):
- 8_automated_means, "Number of measures solely taken by automated means": "the number of measures that were taken following an order, notice, or on own initiative that were solely processed by automated means". "Number of measures not taken by automated means": the same "that were not processed by automated means". Scope "Total number" is read.
- 5_own_initiative_illegal and 6_own_initiative_TC, column F "Number of measures taken at the provider's own initiative". Own initiative means "the decision to impose a restriction on an account or certain content has not been preceded by an order from a Member State authority or a notice submitted through a notice and action mechanism as referenced in Article 16". Sheet 5 is "on the basis of illegality", sheet 6 "on the basis of incompatibility with the provider's terms and conditions". The TOTAL row is read.
- 4_notices, TOTAL row: "Number of actions taken on the basis of the law" and "Number of actions taken on the basis of the terms and conditions of the service", and the same two columns for Trusted Flagger notices.
- 3_member_states_orders, TOTAL row, scope TOTAL: "Number of specific items of information included in the total number of orders to act against illegal content".
- Reports "shall include information on any content moderation in which they have engaged during the relevant reporting period". The template has two automation classes, solely and not. The database has three. "Partially automated" has no report field.
Law (Regulation (EU) 2022/2065, data/raw/docs/dsa_2022_2065.txt), verbatim:
- Art. 17(2): "Paragraph 1 shall only apply where the relevant electronic contact details are known to the provider." and "Paragraph 1 shall not apply where the information is deceptive high-volume commercial content."
- Art. 17(5): "This Article shall not apply to any orders referred to in Article 9."
- Art. 24(5): platforms "shall, without undue delay, submit to the Commission the decisions and the statements of reasons referred to in Article 17(1)".
So the database may hold fewer statements than the report holds measures, for three kinds of measure. Nothing in the law adds statements beyond the measures.

## Name mapping (fixed now, exact platform_name)
Facebook = "Facebook". Instagram = "Instagram". TikTok = "TikTok". YouTube = "YouTube". X = "X". LinkedIn = "LinkedIn". Snapchat = "Snapchat". Pinterest = "Pinterest". Amazon Store = "Amazon". AliExpress = "AliExpress". Temu = "Temu". Shein = "Shein". Zalando = "Zalando". Booking.com = "Booking.com". Apple App Store = "App Store". Google Maps = "Google Maps". Google Play = "Google Play". Google Shopping = "Google Shopping". Pornhub = "Pornhub". XVideos = "XVideos". XNXX = "XNXX". Stripchat = "Stripchat". WhatsApp Channels = "WhatsApp Channels".
Not counted for any VLOP: "Other Meta Platforms Ireland Limited-offered Products", "Threads", "Apple Books (ebooks)", "Apple Podcasts Subscriptions".
Wikipedia: no platform_name containing "wiki" exists in any month of the window (names checked, no counts read). Its delivered value is 0 statements under any such name, and the row says so.

## Measures and matching rule (fixed now)
For platform p and period [t0, t1]. "Filed" below means statements with platform_name of p.
| Measure | Stated field | Delivered filter | Added to the upper edge of the band |
|---|---|---|---|
| total | 8: solely + not, scope Total number (summed by us, both quoted) | all filed | none |
| solely | 8: solely, Total number | automated_decision FULLY | PARTIALLY |
| not | 8: not, Total number | automated_decision NOT_AUTOMATED | PARTIALLY |
| own | 5 TOTAL col F + 6 TOTAL col F | source_type VOLUNTARY | OTHER_NOTIFICATION |
| own_illegal | 5 TOTAL col F | VOLUNTARY and ground ILLEGAL | OTHER_NOTIFICATION with ground ILLEGAL |
| own_tc | 6 TOTAL col F | VOLUNTARY and ground INCOMPATIBLE | OTHER_NOTIFICATION with ground INCOMPATIBLE |
| own_auto | 5 TOTAL col G + 6 TOTAL col G | VOLUNTARY and FULLY | see below |
| notice | 4 TOTAL: actions on the basis of the law + of the terms and conditions | ARTICLE_16 or TRUSTED_FLAGGER | OTHER_NOTIFICATION |
| notice_tf | 4 TOTAL: the same two Trusted Flagger columns | TRUSTED_FLAGGER | none |
OTHER_NOTIFICATION is on the upper edge of both own and notice because the template counts a non-Article 16 report as own initiative, while a platform may file it as "Other type of notification".
own_auto: column G's header says "after detection with solely automated means" and its instruction says "solely using automated means". Both database fields are admitted: lower edge min(VOLUNTARY and FULLY, VOLUNTARY and detection Yes), upper edge max(VOLUNTARY and FULLY or PARTIALLY, VOLUNTARY and detection Yes).
Stated values are read from the TOTAL row (sheets 3 to 6) or the Total number scope (sheet 8) of the row whose Service matches p (case-insensitive match on the service name or the database name; a file that names one service only is read for the platform it was published for). A report whose stated period (1_report_identification) is not one of the two periods above is listed and not read. If that cell is blank and the category rows are filled, the stated value is the sum of the STATEMENT_CATEGORY_ rows, marked "summed by us". If a TOTAL cell and its category sum disagree, both are recorded and TOTAL is used. A blank field with no category values: no stated value, outcome CANNOT_TELL, "the report leaves this field blank". Numbers are read after removing thousands separators and spaces. Every stated value carries the verbatim CSV row, the file name inside the zip, and the zip's URL, sha256 and publication date.

## Date basis
The report counts measures taken in the period. The database groups by created_at (the day the statement was submitted) and by application_date (the day the decision starts from). Two delivered counts are made for every measure:
- D_app: application_date in [t0, t1], summed over every created_at month from 2025-07 to the newest month, so late filings submitted up to the newest month are included.
- D_cre: created_at in [t0, t1].
D_app is the central delivered value, since application_date is the field closest to the date of the decision. Statements filed after the newest month published are not in either count.

## Interval (scope-alignment band), fixed now
The counts are exact. There is no sampling interval. The interval is the band the known scope differences allow.
- Delivered band: lower edge D_lo = min(D_app, D_cre) minus the statements whose territorial_scope names only IS, LI or NO (no EU member state), counted on the application basis. Upper edge D_hi = max(D_app, D_cre) of the filter plus the "added to the upper edge" rows.
- Stated band: upper edge S_hi = S. Lower edge S_lo = S - O - M for total, solely and not, and S - M for own, own_illegal, own_tc and own_auto, floored at 0. O = the report's items of information in orders (3, TOTAL). M = the measures in rows of sheets 5 and 6 whose description of the sub-category "Other" matches spam or high volume (case-insensitive). These are the order and deceptive high-volume commercial content measures the law does not require in the database. Measures on recipients without known contact details cannot be sized from either source and are named in the reason of every BELOW row.
- Ruler: ratio delivered over stated. Central r = D_app / S. Interval [r_lo, r_hi] = [D_lo / S_hi, D_hi / S_lo] (r_hi is unbounded when S_lo is 0). Signed gap D_app - S is printed in counts, said as signed. Magnitude |D_app - S| is printed only where the text says magnitude.
- Item by item: for the total, the solely and not gaps and the partially automated count are printed before the netted total gap.

## Outcomes, fixed now
Agreement band for the ratio: 0.90 to 1.10 (within a tenth of the stated figure, beyond the scope band). Residual differences we cannot size, such as a decision made on the last day of a period and applied the next, are expected to be small.
- ABOVE: r_lo > 1.10. The database holds more statements than the report states measures, beyond every scope difference we can size.
- BELOW: r_hi < 0.90. The database holds fewer statements than the report states measures, beyond every scope difference we can size. The reason names the difference we cannot size (recipients without known contact details). No cause is named.
- CONSISTENT: 0.90 <= r_lo and r_hi <= 1.10.
- CANNOT_TELL: anything else, including a band that crosses 0.90 or 1.10, a blank stated field, and any failed known-good check.
- Stated value 0: CONSISTENT if D_hi is 0, ABOVE if D_lo > 0 and the band does not reach 0, otherwise CANNOT_TELL.
- NOTHING_RETURNED: the report file for that platform and period was not found keyless, is not in the template, or did not parse; or the aggregates for a month in the window did not download or did not match their sha1.
Where the two agree the row says so in the same words as where they differ.

## Second reading A: the two automation fields inside the database
Per platform (the list above) and created_at month, 2025-07 to 2026-10 (2026-11 printed as partial): statements; shares with automated_decision FULLY, PARTIALLY and NOT; share with automated_detection Yes; share with FULLY and detection No; share with NOT and detection Yes. No stated figure exists for these and no outcome is given. The page prints the shares as a description of the filings.

## Second reading B: the platform's own automation share against its filings
Stated share s = solely / (solely + not) from sheet 8, Total number. Stated band: with E = O + M excluded measures, s_a assumes all E were solely automated, s_b assumes none were; the band is [min(s, s_a, s_b), max(s, s_a, s_b)].
Delivered share band: lower edge min over the two date bases of FULLY / all filed, upper edge max of (FULLY + PARTIALLY) / all filed. Central: FULLY / all filed on the application basis.
Ruler: delivered minus stated, in percentage points, signed, interval [d_lo - s_hi, d_hi - s_lo].
Outcomes: ABOVE if the interval's lower edge is above +5 points, BELOW if its upper edge is below -5 points, CONSISTENT if the interval lies inside -5 to +5 points, CANNOT_TELL otherwise. Same NOTHING_RETURNED rule.

## Known-good, before the full read (any failure turns every outcome into CANNOT_TELL, original kept)
- KG1, aggregate reader against the Commission's own daily totals: for three days listed on the download page (19, 25 and 31 October 2026), the sum of count over all platforms with created_at on that day matches the published "Statements of reasons" total within 1%.
- KG2, two aggregations of the same dumps: for every mapped platform and created_at month, the simple aggregate total equals the complete aggregate total (difference under 0.01%).
- KG3, report parser: YouTube's 2026-01-01/2026-06-30 file 8_automated_means.csv reads 34496297 for "Number of measures solely taken by automated means", scope Total number, and 1_report_identification reads publication date 2026-08-28.
- KG4, dump coverage: the dates file lists every day from 2025-07-01 to the newest day, each day with one dump sha1. Missing days are listed and every reading touching them is CANNOT_TELL.

## Seen before this plan (disclosure)
The scout note (research_social/SCOUT_20261110.md) printed, before this plan: YouTube 2026H1 report solely 34,496,297, not 1,931,541; database statements created January to June 2026 for YouTube 24,141,114 fully, 16,216,323 not, 2,580,414 partially, 42,937,851 in all; October 2026 statements per platform (Facebook 34,175,412, TikTok 17,056,103, Instagram 8,109,875, YouTube 5,029,409, X 722,059); October 2026 automation shares for Facebook, Instagram, X and TikTok. We also printed the head of YouTube's 2026H1 8_automated_means.csv while reading the template (own initiative solely 34,244,896, not 1,760,859, notices 251,401 and 170,659, trusted flagger 0 and 376, and the per-country rows). The bands and thresholds above were set after these were seen. No other platform's report or database count was read before this plan.

## Outputs
data/dsa.json: one row per platform x period x measure: stated value, verbatim quote, file, URL, sha256, publication date; delivered D_app, D_cre, band, the filter in words; ratio, interval, signed gap; outcome; reason. Second reading A in data/automation_monthly.json, B as rows with measure "share".
summary_dsa.json: counts by outcome, known-good results, coverage.
section_dsa.html: description, rows, sources with links, how we read it. Plain HTML, classes from launch.html and style.css.
dsa_tick.py: rerunnable build, refreshes the aggregates when a sha1 changes, never installs a timer.

## Addendum 1 (10 Nov 2026 UTC, after the known-good run, before any comparison row was computed)
1. KG2 failed on 43 of 386 platform-months, all in February and May 2026. Per-day totals over all platforms locate it to six days (9, 10, 11 and 12 February, 30 and 31 May 2026). On those days the simple aggregate holds about twice the complete aggregate and carries two or three append jobs per day against one. The Commission's published daily totals (download page, all 23 pages read 10 Nov 2026 UTC, data/raw/docs/download_page/daily_totals_published.json) match the complete aggregate on all six days. For example, 9 February: published 16,027,977, complete 16,027,977, simple 32,055,954. The failure is in the simple aggregate, which no reading uses.
   Under the plan as committed, this failure turns every outcome into CANNOT_TELL. Every row keeps that as outcome_plan_as_committed.
   From this addendum on, KG2 is replaced by KG1-all: for every day from 2025-07-01 to the newest day, the complete aggregate's total over all platforms matches the published daily total within 1%. Days that fail are listed, and readings whose created_at window contains a failed day are CANNOT_TELL.
2. KG4 failed: 1 and 2 November 2026 are missing from the dates file, and the download page lists no dump for those two days. Neither day is inside a period's created_at window. On the application basis, statements created on those two days with an application date in the period are absent. The upper edge of every delivered band is raised by twice the larger of the counts of such statements (same platform, same upper-edge filter) created on 31 October and on 3 November 2026. With that allowance KG4 no longer gates the readings.
3. Database counts seen before this addendum: the KG2 failures (mapped platform totals for February and May 2026 from both aggregates) and per-day totals over all platforms. No report value other than YouTube's (disclosed above) and no comparison row had been read.

## Addendum 2 (10 Nov 2026 UTC, after KG1-all, before any comparison row was read)
1. KG1-all checked 493 days. 490 match the published daily totals within 1% (most exactly). Three do not: 30 September 2026 (published 139,200,845, aggregate 127,201,030), 1 October (44,630,353 against 46,481,663) and 2 October (23,631,610 against 15,631,983). Over 24 September to 8 October the aggregate holds 18,148,136 fewer statements than the published totals, so this is not a shift between neighbouring days. The two days before were backlog days (113 and 139 million statements).
2. None of the three days is inside a period's created_at window. The application basis counts statements created on any day up to the newest, so it reaches them. Under Addendum 1 as written, every reading would therefore be CANNOT_TELL.
3. Rule from here: the Commission's raw daily parquet for those three days (https://d3vax7phxnku8l.cloudfront.net/raw/pqt/data/tdb_data/global___full/daily_dumps_chunked/sor-global-YYYY-MM-DD-full.parquet.zip) is read part by part for the mapped platforms and reduced to the same keys as the aggregate. Per platform, period and filter, the statements in those dumps with an application date in the period, minus the same count in the aggregate for those created days (floored at 0 per key), are added to the upper edge of the delivered band. They are not added to the central value, because the dumps may hold statements the aggregate removed on purpose.
4. KG1-all then gates only readings whose own created_at window contains a failed day (none at present). If the raw dumps cannot be read, every reading is CANNOT_TELL as in point 2.

## Addendum 3 (10 Nov 2026 UTC, before any comparison row was read)
1. The raw daily parquet for 2 October 2026 holds 15,631,983 rows. That equals the aggregate for that day and is 7,999,627 fewer than the published total for the CSV dump (23,631,610). The parquet dumps and the aggregate come from the same conversion, so the method of Addendum 2 cannot size the shortfall. It is replaced by point 2. The raw parquet for 1 October is read as a second check of this equality.
2. Rule from here: the download page also lists daily totals per platform (its platform filter). For each mapped platform, the shortfall is the sum over 30 September, 1 October and 2 October 2026 of max(0, published per-platform daily total minus the aggregate's count for that platform and created day). The shortfall is added to the upper edge of every delivered band of that platform, in both periods, because the application dates and fields of the missing statements are unknown. It is not added to the central value. 29 September and 3 October are read as control days. A platform whose control days differ by more than 1% is flagged in the row.
3. Addendum 1.2 (the allowance for 1 and 2 November) stays. KG1-all gates only readings whose own created_at window contains a failed day.

## Addendum 4 (10 Nov 2026 UTC, defined after the data)
1. The raw parquet for 1 October 2026 holds 46,481,663 rows, the same as the aggregate and more than the published CSV total (44,630,353). The two products of the Commission differ in both directions on those days. Addendum 3 stands.
2. Reading the contextual information that platforms attach to the stated rows used here (data/context_notes.json, every note read by hand), some notes state that a field counts things the database does not hold as separate statements, or leaves out things the database holds. The plan's bands do not carry these. Rule, defined after the data:
   - A note stating the field includes items that are not restrictions (content approvals, warnings without a restriction, notices, auto-closed cases), counts one decision as more than one measure, or counts actions outside the EU: the stated figure can exceed the database count for that reason alone. BELOW and CONSISTENT become CANNOT_TELL. ABOVE stands.
   - A note stating the field leaves out measures the database can hold, or counts several items as one action: ABOVE and CONSISTENT become CANNOT_TELL. BELOW stands.
   - The outcome the plan's rule gives is kept on the row as outcome_rule. The platform's own words are quoted on the row.
3. Applied to: Snapchat sheet 8, both periods (content approvals; in 2026H1 the not-automated figure also includes human-processed notices); Snapchat sheet 6, 2025H2 (warnings without removal) and 2026H1 (a removal with an account lock counted as two measures); Snapchat sheet 4 trusted flagger actions (one action can cover several items); X sheet 6 column G (auto-closed moderation cases and advertising review decisions); Amazon sheets 5 and 6 (all actions reported under terms and conditions, illegal content included); Booking.com sheet 4 (removals reported on a global scale).
4. Notes whose difference is far inside the agreement band do not change an outcome (Facebook and Instagram leave out French Guiana and the Aland Islands). Notes that match the plan's bands need no change (Pinterest counts hybrid enforcement as solely automated, TikTok's not-automated figure is human action after automated review; both sit inside the partially automated band).

## Addendum 5 (10 Nov 2026 UTC, defined after the data): bounds from the restriction columns
1. Three notes describe the sheet 6 TOTAL as a sum over the restriction columns H to U: TikTok ("We sum all of the enforcement actions reported under the other columns."), X ("Represents the sum of all own initiative measures taken and identified in columns H through on the bases on terms of service.") and Snapchat 2026H1 (a removal with an account lock counted as two measures, to align the total with the sum of the subcategories). A sum over columns can count one decision more than once. A decision appears at most once in each column, so the number of decisions is at least the largest single column.
2. For those rows the stated band runs from the largest restriction column of the TOTAL row (for own, the largest column of sheet 5 plus the largest of sheet 6) to the stated TOTAL. Snapchat 2025H2 says its TOTAL also holds warnings outside columns H to U. Its band runs from the largest column to the sum of columns H to U. These bands replace the Addendum 4 treatment of Snapchat sheet 6. The outcome then follows the plan's ratio rule with the new band, and the rule's own outcome without the bound is kept as outcome_rule.
3. X sheet 6 column G (auto-closed cases) keeps the Addendum 4 treatment, since column G has no column split.

## Addendum 6 (10 Nov 2026 UTC, defined after the data): the referee's fixes
Written after the outside referee's read-only pass (social_index/dsa_referee/REFEREE.md, verdict FIX THEN SHIP). Every rule below is defined after the data. Each row keeps the outcome the plan's comparison rule gave before these changes as outcome_rule.

6.0 Provenance. data/tick_log.txt (21:11:41 local, 02:11 UTC) records a full build run after Addendum 1 and before Addenda 2 and 3. Its gate failed, so it printed every row as CANNOT_TELL. heuremen_kit.apply_gate kept each computed comparison as outcome_before_gate in data/dsa.json, so a file of computed comparisons existed when Addenda 2 and 3 were written. We read only the printed counts and the KG1-all result from that run, not the rows. Addenda 2 and 3 only widen bands.

6.1 Ads. YouTube, Google Maps and Google Play publish ads moderation in separate template files (8_automated_means_Ads, 6_own_initiative_TC_Ads). For these three services the main template is compared with statements whose CONTENT_TYPE_AD is false, and the Ads template with statements whose CONTENT_TYPE_AD is true, on separate rows named "<service> (ads)". Ads rows read all measures, solely, not automated, own initiative on terms and conditions and the automation share. The orders deduction stays on the main rows. The Addendum 1.2 and 3 allowances go on both the main and the ads rows. No other report has an ads template, and their ad-flagged statements stay in their counts (Google Shopping's note says its metrics include ads).

6.2 Notices. Actions on notices are compared with statements labelled Article 16 or trusted flagger only under two further rules. (a) Unit: the upper edge of the stated band is the larger of the actions and the report's own count of notified items (sheet 4, column H; for trusted flagger rows, column I). (b) Label: the two filings label notice sources differently (one platform's report moves user reports to own initiative, others file user reports as Article 16 notices). So the delivered band runs from zero to every statement the platform filed, on the same date bases and allowances. An outcome survives only if it holds against that band, which in practice leaves only a below reading where every statement the platform filed is still fewer than the notice actions.

6.3 Addendum 4, applied evenly.
- Snapchat 2025H2 sheet 4: "EU user reports of Community Guidelines violations, previously included here, have been reclassified to the "own initiative" fields to align with the DSA template." Rule two (the field leaves out measures the database can hold) on both notice rows of that half.
- Facebook and Instagram sheet 6, both halves: "Visibility restriction removal contains some actions for Facebook and Instagram combined due to technical and product limitations." and "The data in this column contains actions for Facebook and Instagram combined due to technical and product limitations." The note does not say which service carries the shared actions, so both directions apply. Every Facebook and Instagram row of all measures, solely, not automated, own initiative, own initiative on terms and conditions, own initiative solely automated and the automation share becomes CANNOT_TELL. A combined row "Facebook and Instagram" sums both reports and both services' statements for those measures.
- Apple sheet 6: account terminations "include terminations of App Store developers, Apple Media Services customers and Apple Ads advertisers", and removals include reviews removed "before and after publication". Recorded. No Apple outcome moves: the largest restriction column (11.4 million and 8.1 million) still exceeds the statements filed many times over.
- Notes handled with no effect: WhatsApp ("violations ... for either service can result in account termination for both services") sits on a blank column. Meta's note that its age-restricted, interaction-restricted and labelled columns are "not taken on the basis that the content is illegal or violates our terms" covers blank columns. Snapchat's "Other" restriction column (14,285 and 8,619) is too small to move a reading. Facebook and Instagram leave out French Guiana and the Aland Islands (Addendum 4.4).

6.4 Addendum 5, applied by arithmetic. The bound fires for every sheet 5 or 6 TOTAL that equals the sum of its restriction columns H to U exactly, and still for the three notes of Addendum 5. The stated lower edge is the largest restriction column (sheet by sheet; for own initiative the two sheets' edges are added), minus spam rows. This applies to main rows, ads rows (the Ads sheet 6) and the combined Meta rows (lower edge: the larger of the two services' largest columns).

6.5 Sheet 8 built from those TOTALs (the judgment call). Where a report's sheet 8 total (solely plus not) equals its sheet 5 and 6 TOTALs, plus its notice actions and, where they fit, its order items, to within 0.1%, and at least one of those TOTALs is a column sum, sheet 8 is read as built from them and inherits the same lower edge: the sheet 5 and 6 edges of 6.4 plus the notice actions (and order items where they were part of the identity). The amount removed is spread over solely and not automated in unknown proportion, so each loses up to the whole amount. The automation share widens the same way. Decided before computing which rows it moves, and applied by arithmetic to every report.

6.6 Ground and source allowances. Own-initiative statements of the other ground go on the upper edge of each ground split (own illegal, own on terms and conditions). Statements labelled Article 16 or trusted flagger beyond the report's notified items (column H) go on the upper edge of own, own illegal and own on terms and conditions (same ground where split).

6.7 Opposite readings on one split. Where, after 6.1 to 6.6 and 6.8, one half of a split (solely or not automated; own illegal or own on terms and conditions) reads ABOVE and the other BELOW for the same platform and half-year, both become CANNOT_TELL with the reason "the two filings label this split differently". A row of its own type records the pair with the reading "labelled differently in the two filings". It carries the counts and no outcome.

6.8 Minimum count. ABOVE needs the database count to clear the 1.10 edge by at least 100 statements (with a stated zero, at least 100 statements). BELOW needs it to fall short of the 0.90 edge by at least 100 statements. Otherwise the row is CANNOT_TELL.

6.9 Names. "X (formerly Twitter)" (1,469 statements created 19 November 2025, the same profile as X) is counted as X.

6.10 Copy. The below reason names every difference neither source sizes: recipients whose contact details are unknown, how a filing counts one decision (per item, per account, per restriction type, a TOTAL built as a column sum), content filtered at upload that a report counts, and statements filed after the newest aggregate. The above reason names how each filing attributes EU relevance and one decision filed as more than one statement. The page says that under the plan as committed every row would read cannot tell. Read dates print in HST. Ratios print four significant figures within 0.005 of an edge.

## Addendum 6, record of effects (10 Nov 2026 UTC, after computing)
- Original 475 rows under Addenda 1 to 6: 39 ABOVE, 82 BELOW, 35 CONSISTENT, 292 CANNOT_TELL, 27 NOTHING_RETURNED. New rows: 30 ads rows (6 CONSISTENT, 24 CANNOT_TELL), 14 combined Meta rows (all CANNOT_TELL), 9 label-split rows (no outcome).
- Against the referee's expected 39 / 84 / 35 / 290 / 27, six original rows differ, each from a rule as committed. Addendum 6.5 (the judgment call): Amazon 2026H1 all measures and not automated (BELOW to CANNOT_TELL), YouTube 2025H2 share (BELOW to CANNOT_TELL), App Store 2025H2 share (ABOVE to CANNOT_TELL). Addendum 6.7 applied after 6.8: Snapchat 2026H1 own initiative on terms and conditions stays BELOW, because its partner's ABOVE rests on one statement and is floored. Addendum 6.6 on own initiative on terms and conditions: XVideos 2025H2 own initiative on terms and conditions becomes CANNOT_TELL, so the pair is not opposite and own initiative illegal stays ABOVE.
- Addendum 6.5 moves 24 rows in all: the four original rows above, the combined Meta 2025H2 all-measures row (CONSISTENT without it, 1.040 [1.040, 1.097]) and 19 ads rows (CONSISTENT, or one BELOW, without it), because each ads template's sheet 8 total equals its sheet 6 TOTAL, which is a column sum. Without 6.5 the original rows read 40 / 85 / 35 / 288 / 27.
- A code error found while reconciling: the source allowance was first also applied to own initiative solely automated, which 6.6 does not name. It was removed before these counts.
- The referee's scripts, rerun on these outputs: stated side 372 values, 0 differences. Database side 39 differences, all the ads split (checked exact against the referee's own CONTENT_TYPE_AD recount, 72 of 72 rows) or the X alias. Band edges 205 differences, all from 6.1, 6.2, 6.6 or 6.9, none moving a lower edge outside notices, ads and X, none narrowing an upper edge. Page 424 cells, 6 differences, all from printing five figures near an edge (6.10: four figures would print 1.0997 as 1.100).

## Second referee pass, record (10 Nov 2026 UTC)
Verdict FIX THEN SHIP with three copy changes and no further pass (dsa_referee/REFEREE.md, "SECOND PASS"). Changes made, none of which moves an outcome:
- The stated-zero sentence and reason now say that above needs at least 100 statements (Addendum 6.8).
- Ads and combined rows show the reading without the column-sum bound (Addenda 6.4 and 6.5) wherever the bound alone makes them CANNOT_TELL: 26 rows (3 combined, 23 ads), all CONSISTENT without it except Google Play ads July to December 2025 not automated, BELOW. Field outcome_without_column_bound, with the addendum named in the reason.
- The Meta line on the page says the combined row also reads CANNOT_TELL, and why.
- Taken from the optional list: reason strings join rule texts as sentences, without semicolons. The three Google services' notice rows take every statement, ads included, as the upper edge, since sheet 4 has no ads version (12 rows, upper edges only, no outcome moves). The below reason names deceptive high-volume commercial content a report does not label as spam (DSA Article 17(2)).
- Plan text corrections, no code change: Addendum 6.10 prints five significant figures near an edge, not four (four would print 1.0997 as 1.100). Addendum 6.5 as implemented takes the first identity within 0.1% in the order sheets 5 and 6, then plus notice actions, then plus order items. For LinkedIn, Google Play and Google Shopping that lowers some lower edges by the notice actions (484 to 2,730 statements), and the referee found no outcome changes with the closest identity.
- The referee's page check (dsa_referee/code/html_check2.py) on the final page: 527 cells, 0 differences, every comparison row on the page, 9 of 9 label-split rows.
