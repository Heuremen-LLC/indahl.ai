# SOCIAL section 3: TikTok by country, report against filings. Plan, written before any comparison was computed.

Written 10 Nov 2026 (UTC), 9 Nov HST. Desk owner: section 3 of the SOCIAL desk (indahl.ai/social). Bones assembles and ships.

## The question
TikTok states, every quarter, how many videos it removed for breaking its Community Guidelines, per market, and how many of
those removals were automated. TikTok also files a statement of reasons for each moderation decision in the EU's DSA
Transparency Database. Do the two filings agree, quarter by quarter, for the EU markets TikTok breaks out, and for the EU as a whole?

## Data
Stated side: TikTok Community Guidelines Enforcement Report (CGER) data, one zip per quarter, long CSV
(columns Metric, Period type, Period, Policy type, Issue [Issue policy in 2023Q4], Task type, Task, Location, Market, Result).
Files and URLs (all keyless, fetched 10 Nov 2026, sha256 in data/sources.json):
- 2023Q4 https://sf16-va.tiktokcdn.com/obj/eden-va2/uhsllrta/Q4_2023_CGER/2023Q4CGER_English.zip
- 2024Q1 https://sf16-va.tiktokcdn.com/obj/eden-va2/uhkklyeh7othpu/Q1_2024_CGER/2024Q1_CGER_English.zip
- 2024Q2 to 2025Q4 https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/ljhwZthlaukjlkulzlp/<YYYYQn>_CGER/<YYYYQn>_CGER_English.zip
- 2026Q1 https://sf16-va.tiktokcdn.com/obj/eden-va2/zkyhviozhk_YLNJ/ljhwZthlaukjlkulzlp/2026Q1/2026Q1_CGER_English.zip
- 2026Q2 https://sf16-va.tiktokcdn.com/obj/eden-va2/zkyhviozhk_YLNJ/ljhwZthlaukjlkulzlp/2026_Q2/26Q2USexcl/2026Q2_CGER_English.zip
The older links were found in archived copies of TikTok's report pages (web.archive.org); the 2026Q2 link is the "Download data"
button on https://www.tiktok.com/safety/en/transparency/cg-report. Every file carries the full history back to 2020, so each
quarter appears in its own release and in every later one.

Delivered side: the Commission's complete monthly aggregates of the DSA Transparency Database, CC BY 4.0,
https://d3vax7phxnku8l.cloudfront.net/agg/pqt/data/tdb_data/global___full/aggregations/aggregated-complete-YYYY-MM-01-parquet.zip
with a .sha1 beside each. One file per month of submission (created_at_month). The complete version groups statements by every
non-free-text field, including territorial_scope (dsa-tdb writes it as a string: AT_FR_ES, or EU, EEA, EEA_no_IS for the full sets),
application_date and content_date (both truncated to the day), automated_decision, automated_detection, source_type, content
types and decision types (pivoted to booleans), content_language, decision_ground. Months read: 2023-09 to the latest available.
Only rows with platform_name = 'TikTok' are kept (the only TikTok name seen in June 2026). Zips are deleted after the TikTok rows
are extracted; the .sha1 files are kept as receipts.

Codebooks read before any filter: the database's API documentation (https://transparency.dsa.ec.europa.eu/page/api-documentation,
saved in data/raw/codebooks/), the dsa-tdb data sources page (aggregation and territorial scope rules), TikTok's ReadMe and
CGER_README in each zip, and the notes inside TikTok's dashboards. Definitions used below are quoted from them.

## What we had seen before writing this plan (stated in full)
- The scout's proof run (SCOUT_20261110.md): 17,864,150 videos removed in the 25 listed EU markets in Apr-Jun 2026 against
  18,928,826 TikTok statements with video content and a removal decision submitted Apr-Jun 2026. A hint, not a result. Redone from files below.
- Global TikTok figures, used as known-goods only: Apr-Jun 2026 total 188,298,141, Automation 163,084,298, AI Moderation 20,260,409
  (97.37%, TikTok's page says 97.4%); Jan-Mar 2026 total 184,012,576 (96.74%, TikTok's narrative says "more than 96%").
- June 2026 TikTok rows in the database: territorial scope EEA or EEA_no_IS for every statement with a removal decision and video
  content; content_language empty on all of them; the crosstab of decision ground by removed/disabled/video.
- Which EU markets each release lists, from the column counts. No EU sum and no market value was compared with any database count.

## Mapping, fixed now
Stated figures (from the quarter's own release, Policy type All, Issue All, Location Market):
- videos_removed: Metric "Total videos removed", Task type All, Task All.
- automated_removals: Metric "Total videos removed", Task type "Task type", Task "Automation", plus Task "AI Moderation" where it
  exists (from Jan-Mar 2026; TikTok: "we are adding videos taken down by AI moderation to the automated removals bar chart").
  TikTok: "Videos that are removed by automation did not require intervention from human moderators."
- automated_share: automated_removals / videos_removed.
- proactive_rate: Metric "Proactive removal rate", Task All. TikTok: "Proactive removal means identifying and removing a video before it's reported."
- within_24h_rate: Metric "Removal rate within 24 hours", Task All. TikTok: "removing the video within 24 hours of it being posted".
- TikTok's market: "the originating country or region where the content was published, or where an account was last active" (ReadMe).
- TikTok's videos "include short-form video content (including image-based videos and stories)" (dashboard note).
- TikTok reports "closed cases for the specified period" (ReadMe).

Delivered figures (TikTok statements in the database):
- Removal decision: DECISION_VISIBILITY_CONTENT_REMOVED = true ("Removal of content"). Disabling access, demotion, age restriction,
  interaction restriction, labelling and other are not removals. Disabled-access video statements are counted and printed as an
  item, never added.
- Video content, point: CONTENT_TYPE_VIDEO = true and CONTENT_TYPE_AD = false (ad removals are a separate TikTok metric).
- Lower allowance: the point set with decision_ground = DECISION_GROUND_INCOMPATIBLE_CONTENT only (CGER counts Community Guidelines removals).
- Upper allowance: removals with CONTENT_TYPE_AD = false and any of VIDEO, IMAGE, SYNTHETIC_MEDIA, or OTHER with no dsa-tdb
  normalised type (ACCOUNT, AD, LINK, STICKER, HASHTAG, PRODUCT, APP, TEXT, AUDIO all false), because TikTok counts image-based
  videos and stories as videos and the database has no field for either.
- Date, point: application_date ("the date that this decision starts from") inside the quarter, UTC days, counting statements
  submitted in any month read (late filings included). Alternatives: created_at (submission) inside the quarter; and the
  application_date window shifted one day earlier and one day later (TikTok's quarter boundary time zone is not stated).
- automated: automated_decision = AUTOMATED_DECISION_FULLY. PARTIALLY and NOT_AUTOMATED are not automated.
- proactive: source_type = SOURCE_VOLUNTARY ("Own voluntary initiative"). ARTICLE_16, TRUSTED_FLAGGER and OTHER_NOTIFICATION are reported.
- within 24 hours: d = application_date minus content_date in days. Both are days, so the share removed within 24 hours lies
  between P(d = 0) and P(d <= 1). Sanity gate: if more than 1% of matched statements have no content_date or d < 0, the row is CANNOT_TELL.

Markets: TikTok market names map to ISO codes (Czech Republic CZ, Greece GR, others by name; EU 27 plus Norway NO, Iceland IS,
Liechtenstein LI for the EEA). A database statement is placed in market m only when its territorial_scope is exactly m. Scopes EU, EEA,
EEA_no_IS or any multi-country list cannot be placed in one market: TikTok's market is where content was published, the database's
scope is where the restriction applies.

## The rows
1. EU total, per quarter, all five measures.
   Stated point S = sum over the EU markets the release lists. Stated interval: lower S; upper S plus an allowance for every
   unlisted market that could be in the database's population: unlisted EU markets, and Norway, Iceland and Liechtenstein
   (we cannot tell whether TikTok files statements for EEA-only users; Norway's listed value is added when listed).
   Allowance per unlisted market = B_q: 49,999 for 2026 quarters (TikTok, Jan-Mar 2026 narrative: "all markets that have had at least
   50,000 removals for the quarter"); for earlier quarters the smallest "Total videos removed" among the markets the release lists
   (TikTok: "the fifty markets with the largest volumes of removed videos").
   Shares: stated point = removal-weighted mean over listed EU markets with a value. Stated interval: unknown mass (unlisted markets
   at B_q each, listed markets without a value at their own count) set to share 0 for the lower end and share 1 for the upper end.
   The interval is the hull over the two populations, EU only and EEA.
   Delivered point D from the point mapping. Delivered interval: minimum and maximum over the date alternatives (three application
   windows and created_at) crossed with the content sets (lower, point, upper). For counts the lower end uses the lower set, the upper
   end the upper set. For shares every combination is computed and the range taken; for within 24 hours the lower end is the smallest
   P(d = 0), the upper end the largest P(d <= 1).
2. Market rows, per quarter, per EU market the release lists, all five measures, plus one videos_removed row per unlisted EU market.
   Delivered query: statements placed in that market. Stated query: the market's value in the release.
3. Revisions (TikTok against TikTok): every EU market value and EU sum in a quarter's own release against the same cell in the
   latest release. Counted and printed, no outcome.

## Intervals: what they are
Both sides are full counts, not samples. No interval here is statistical. Each interval is the range a figure takes across the
matching choices fixed above (unlisted markets at zero or at TikTok's own ceiling, decision date or submission date, a one-day
boundary shift, the narrow or wide content set, the day truncation of dates). Every printed interval says this.

## Outcomes, fixed now
Gap = delivered minus stated. Gap interval: [D_lo minus S_hi, D_hi minus S_lo]. Material size m: 5% of the stated point for counts,
1 percentage point for shares (TikTok prints rates to one decimal, so this is ten of its reporting steps). Both alternatives are tested,
zero and m.
- ABOVE: the whole gap interval is above zero (the database holds more than the report allows under every choice).
- BELOW: the whole gap interval is below zero.
- CONSISTENT: the gap interval contains zero and lies inside plus or minus m. Printed as a bound, never as "the same".
- CANNOT_TELL: the gap interval contains zero and reaches past m, or a side fails a gate, or the database did not exist for the
  whole quarter (it opened in late September 2023, so Jul-Sep 2023 is CANNOT_TELL with both figures printed).
- NOTHING_RETURNED: a side's query returned no figure for the row (an unlisted market on the stated side; no statement placed in the
  market on the delivered side). The reason prints what the other side holds.
Every ABOVE or BELOW also carries material: yes when the whole gap interval is past m, no when it lies inside m, cannot tell otherwise.
For shares the ruler is percentage points. The complement (not automated, reported) is printed beside it as a second ruler; when the
two rulers read differently the row says so in its reason.
The outcome is computed with the quarter's own release. If the latest release differs for that cell, the row also carries the
outcome under the latest figure, and a changed outcome is printed.

## Known-good, run before the rows (KNOWN-GOOD)
- TikTok file: global Apr-Jun 2026 (Automation + AI Moderation) / total rounds to 97.4%, as TikTok's page states; global Jan-Mar 2026
  total equals 184,012,576 in both the 2026Q1 and 2026Q2 releases.
- Database: TikTok's monthly totals in the complete aggregates equal the simple aggregates (the Commission's dashboard feed) for
  Jan to Jun 2026 (sample files on disk), and October 2026 equals 17,056,103 (sor_platform_day_2026-10.csv).
- If a known-good fails, every outcome becomes CANNOT_TELL and the original is kept (heuremen_kit.apply_gate).

## Limits we cannot size (stated on the page as limits, never as causes)
Where TikTok locates an uploader against where a database statement applies. Whether videos removed with spam or fake accounts
("Videos removed from fake accounts", a separate TikTok metric) get statements. LIVE. Duplicate statements for one video. Later
corrections inside the Commission's aggregates (each run records the sha1 it read). TikTok's later restatements.

## Rerun
`.venv/bin/python -I tiktok_tick.py` re-reads TikTok's report page for a new "Download data" link, re-checks every month's sha1,
re-extracts what changed and rebuilds data/tiktok.json, summary_tiktok.json and section_tiktok.html. No timer is installed.
Changes to this plan are appended below as dated addenda, never edited in place. data/plan_receipt.json records the sha256 of this
file before the first comparison run and after each addendum.

## Addendum 1 (10 Nov 2026, before the first comparison run; no stated-against-delivered figure computed yet)
Read from the stated side's structure only (which markets each release lists, how rates are printed):
1. TikTok prints rates to three decimals (France, Apr-Jun 2026: proactive 0.98, within 24 hours 0.916). Each market's rate therefore
   carries plus or minus 0.0005 of rounding. The stated share interval adds it: lower end uses rate minus 0.0005, upper end rate plus 0.0005.
2. A second ceiling for unlisted markets, also TikTok's own: their total cannot exceed the global "Total videos removed" minus the sum of
   every market the release lists. The allowance for unlisted markets is the smaller of (number unlisted times B_q) and that remainder.
   The same remainder caps the unknown mass in the share intervals.
3. Every 2026 release lists 25 EU markets and Norway. Luxembourg, Malta, Iceland and Liechtenstein are not listed. Releases before 2026
   list 50 markets, of which 4 to 8 are in the EU. Every listed EU market carries Automation, proactive and 24-hour rows, and in 2026 an
   AI Moderation row, so no listed market needs the missing-value rule.
4. Jul-Sep 2023 has no release of its own on file. Its stated figures come from the earliest release that carries the quarter (2023Q4).

## Addendum 2 (10 Nov 2026 UTC, after the known-good run, before any comparison row was computed)
1. KG3 failed for February and May 2026. Day by day, TikTok's counts in the two aggregates differ on six days only (9, 10, 11 and
   12 February, 30 and 31 May 2026), and on each of them the simple aggregate holds exactly twice the complete aggregate. Every other
   day of every month read agrees exactly. Section 1 (social_index/dsa, Addendum 1) located the same six days across all platforms and
   found the Commission's published daily totals equal to the complete aggregate on all six. The failure is in the simple aggregate,
   which no reading here uses.
   Under the plan as committed this turns every outcome into CANNOT_TELL. Every row keeps that as outcome_plan_as_committed.
   KG3 is replaced by KG3-days: (a) on every day, TikTok's total in the complete aggregate equals the simple aggregate's, or the simple
   aggregate holds an exact multiple of 2 or 3 of it (a repeated append); (b) on every day that the Commission's published daily totals
   cover (section 1's file data/raw/docs/download_page/daily_totals_published.json, read only, from 11 February 2024), the complete
   aggregate's total over all platforms is within 1% of the published total. A day that fails (a) or (b) makes every EU row whose
   quarter runs from its first day to three months after its last day contain that day CANNOT_TELL.
2. Days the database does not hold at all: 1 and 2 November 2026 (no published dump, section 1 KG4). On the decision-date basis,
   statements created on those days with a decision date inside a quarter would be missing. The upper end of each delivered range
   is raised by twice the larger of the matched counts created on 31 October and on 3 November 2026 with a decision date in the quarter.
3. Submission date leaves the outcome range. Reason, from the delivered side only: TikTok filed no statement at all on 43 days
   (5 to 9 June 2024, 5 September to 9 October 2025, 3 December 2025, and 1 to 2 November 2026 when the database has no dump), and from
   July 2025 to January 2026 it filed up to 94% of a month's video removal statements one to three months after the decision date
   (about 36 million statements of all kinds filed in January 2026 for decisions taken in October to December 2025). In 2026, from
   February on, every video removal statement was filed in the month of its decision. TikTok's report counts "closed cases for the
   specified period", which is the decision date. A submission-date count measures filing delay, not the quarter's removals.
   The outcome range now runs over the decision-date windows (as is, one day earlier, one day later) and the content sets. The
   submission-date count is still computed and printed in every row as a second reading, and outcome_plan_as_committed keeps it in the range.
4. A quarter is read once three full months after its end are in the files (TikTok's longest observed filing lag is three months).
5. Database counts seen before this addendum: TikTok statements per month and per day (all content types) in both aggregates; days with
   no TikTok statement; and video removal counts per decision month by filing lag (from which a quarter's database total can be formed).
   The scout's stated Apr-Jun 2026 figure was known from the start. No stated figure was set against a database figure by us.

## Addendum 3 (10 Nov 2026 UTC, DEFINED AFTER THE DATA; committed outcomes unchanged)
1. KG3-days failed. (a) 11 February 2026: TikTok's simple total is 2,835,390 against a complete total of 1,417,692, twice it plus 6, not an
   exact multiple. (b) 30 September, 1 and 2 October 2026: the complete aggregate's all-platform totals differ from the published totals
   (127,201,030 against 139,200,845, 46,481,663 against 44,630,353, 15,631,983 against 23,631,610), as section 1 also found.
   Under Addendum 2.1 the EU rows of Oct to Dec 2025, Jan to Mar 2026 and Apr to Jun 2026 are CANNOT_TELL. They stay CANNOT_TELL.
2. A second reading, defined after the data and printed beside the committed outcome, never in its place: TikTok's own published daily totals
   (download page, platform filter, platform_id 30, all 24 pages, 1,138 days from 25 September 2023 to 8 November 2026, saved in
   data/raw/dsa_pages/, summary in data/posthoc_daycheck.json) replace the day check. They equal the complete aggregate on 1,091 days,
   including 11 February 2026 (1,417,692 both). For each quarter, over the window of Addendum 2.1: where the aggregate holds more TikTok
   statements than TikTok's total, the excess, capped at the matched statements created that day with a decision date in the quarter, can come
   off the lower end of the delivered range; where it holds fewer, the shortfall is added to the upper end; days with no published total (22
   August 2026) can come off the lower end in full. Shares widen as if that mass were all automated or all not. The outcome rule is unchanged.
   Largest differences: 8 May 2026 (aggregate 1,199,408, published 340,518), 30 September 2026 (3,258,409 against 3,442,533), 2 October 2026
   (271,453 against 359,373), 1 February 2024 (2,255,383 against 2,084,351).
3. The revision check compared floating values exactly and listed ten rate cells that differ only in the 17th digit. It now compares within
   1e-9. No stated cell differs between a quarter's own release and the latest release (397 cells checked).
4. Seen before this addendum: every EU row's committed outcome and gap range.

## Addendum 4 (10 Nov 2026 UTC, DEFINED AFTER THE DATA; referee findings, social_index/tiktok_referee/REFEREE.md)
Every rule here was set after every row's outcome and gap range were known. Each row it moves keeps its earlier outcomes under
addendum_4.before in data/tiktok.json, and summary_tiktok.json lists the rows moved. No figure changes.
1. (B1) Removed before any report against own voluntary initiative is not like for like. TikTok's report counts removal before any user
   report. The DSA counts as own initiative every decision not preceded by an Article 16 notice or an order (Commission Implementing
   Regulation 2024/2835), so a removal after an ordinary in-app report is own initiative, and TikTok's own DSA report note says so.
   Every proactive_rate EU row reads CANNOT_TELL in every column (committed, submission-date range, defined after the data), with the
   reason "The two filings define report differently. TikTok's report counts any user report. The DSA counts only notices under
   Article 16, so removals after other user reports are filed as own initiative." Figures are kept. The table is retitled "Removed before
   any report (TikTok report) and own initiative (database)" and its database column "Database, own voluntary initiative". This moves
   8 committed ABOVE and 10 defined-after-the-data ABOVE to CANNOT_TELL. The earlier summary line that removed before any report read
   ABOVE in 8 quarters is withdrawn.
2. (B2) From 2026 TikTok's report counts AI Moderation as automated. A 2026 automated_share reading that changes direction when the report
   share is taken with Automation alone (same allowance rule) reads CANNOT_TELL, with the reason "Below when AI moderation counts as
   automated, as TikTok's report counts it from 2026, and Above when it does not. The two filings may count AI moderation differently."
   The Automation-only report share is printed beside the row (88.4% Jan to Mar 2026 and 89.0% Apr to Jun 2026, with ranges
   87.5% to 88.5% and 88.1% to 89.2%). Both defined-after-the-data BELOW rows move to CANNOT_TELL.
3. (B4) Limits from the Limits section are carried on the page and on every decided count row: "TikTok's report counts videos removed
   from fake accounts and LIVE sessions apart from videos removed, and gives no market split for either. The database could hold
   statements for them, and one decision filed twice counts twice. We cannot size these, so an Above may include them." This applies
   to the one decided reading left, videos removed Jan to Mar 2026, ABOVE, defined after the data.
4. (B3) Correction to Addendum 2.3, which stays as written above. Under the desk's lag definition (calendar months from decision month
   to filing month), November 2025 video removals (5,351,631 statements) were 97.5% filed one to three months later, and December
   2025 93.8%. "Up to 94%" is corrected to "up to 97%". The figure "about 36 million statements of all kinds filed in January 2026 for
   decisions taken in October to December 2025" does not reproduce. The recount gives 107,859,110 statements of all kinds, 42,173,343
   removals of all kinds and 12,595,443 video removals. The page does not carry that figure.
5. Day line (referee note 2). Addendum 3.2's 1,091 of 1,138 days counts 41 days where neither side holds a statement and counts
   8 November 2026, which the files do not reach. The page now says the published totals match the files on every day both cover
   (1,137) except 46, and that on 41 of the matching days neither side holds a statement.
6. Components. The delivered side's drop list adds video statements that are not removals, age restricted and visibility "other",
   beside disabled (data/components.json).
7. Seen before this addendum: every EU row's outcome in both columns, all gap ranges, and the referee's recount.
