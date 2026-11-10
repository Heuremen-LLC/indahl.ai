# ADSPEND: Google's stated political ad spend against FEC filings. Plan, written before any comparison.

Written 9 November 2026 (HST), 10 November UTC. Section 4 of the SOCIAL desk. Before this plan we read only schemas, field
vocabularies and file completeness (listed under "Reads before the plan"). No committee's Google figure was set beside its FEC figure.

## Claim read
Google states, for every advertiser verified to run election ads, how much the advertiser spent on election ads, in total and per week
(Political Advertising on Google, keyless bundle). US federal political committees report every payment they make, including payments
to Google, to the FEC. Question: per committee, per two-year cycle and per quarter, do the payments a committee reported to Google agree
with the spend Google states for that advertiser?

## Data (all keyless)
- Google bundle: https://storage.googleapis.com/political-csv/google-political-ads-transparency-bundle.zip. Files used:
  google-political-ads-advertiser-stats.csv (Advertiser_ID, Advertiser_Name, Public_IDs_List, Regions, Spend_USD),
  google-political-ads-advertiser-weekly-spend.csv (Advertiser_ID, Week_Start_Date, Spend_USD), google-political-ads-updated.csv.
  The creative file (2.96 GB) is not unzipped. The weekly file carries the timing and the creative file states spend only in ranges.
- FEC bulk files, https://www.fec.gov/data/browse-data/?tab=bulk-data, cycles 2020, 2022, 2024 and 2026:
  oppexp (Schedule B operating expenditures: Form 3 line 17, Form 3P line 23, Form 3X lines 21(a) and 21(b)),
  independent_expenditure_YYYY.csv (Schedule E and Form 5), cm (committee master), webk (PAC and party summary: coverage end date,
  party coordinated expenditures), weball (candidate summary: coverage end date). Header file: oppexp_header_file.csv, cm_header_file.csv.
- Never read: individual contributor files. 52 U.S.C. 30111(a)(4) forbids using contributor names for solicitation or commercial purposes.
  The treasurer field of the committee master is never read into any output. Payee names are stored only for Google rows. Rows paid to
  individuals (entity type IND) enter the pools as sums only, never with a name.

## Matching rule (Google advertiser to FEC committee)
Only advertisers whose Regions field is exactly US are read. Others are counted apart.
- Tier A (id): Public_IDs_List carries one or more "FEC ID C########" and every listed ID exists in a cm file of 2020 to 2026.
  An advertiser listing several FEC IDs joins those committees into one group. Groups merge transitively (any two IDs ever listed
  together are one group). A group is one row. Its Google figure is the sum over every advertiser mapped into it and its FEC figure the
  sum over its committees.
- Tier B (name): no FEC ID listed, and the normalized advertiser name equals the normalized name of exactly one committee in the cm files
  of 2020 to 2026. Normalized: uppercase, "&" to AND, every character that is not a letter or digit to a space, spaces collapsed.
- UNMATCHED, counted by reason with the stated spend of each bin: FEC ID listed but not in any cm file; name equal to two or more
  committees (ambiguous); no FEC ID and no exact name.
- Rows carry the tier. Outcome counts are reported by tier, because a name is a weaker key than an ID.

## Payee rule (what counts as a payment to Google)
A Schedule B or Schedule E row is a Google row when the uppercased payee name matches
`GOOGLE|YOUTUBE|YOU ?TUBE|ADWORDS|DOUBLECLICK|ALPHABET INC|\bG ?-?SUITE\b|\bGSUITE\b` and is not on the exclusion list
`TOP OF GOOGLE`. A payee that also names another company (`FACEBOOK|\bFB\b|\bMETA\b|TIKTOK|\bWIX\b|YAHOO|\bBING\b|MICROSOFT|AMAZON|TWITTER`)
is a mixed Google row and never counts as an ad row.
Each Google row on Schedule B gets one class:
- AD purpose: `ADVERTI|ADVERTIZ|\bADS?\b|\bAD-|AD ?BUY|MEDIA BUY|PLACEMENT|PAID MEDIA|DIGITAL MEDIA|ONLINE FUNDRAISING|ACQUISITION|LIST BUILDING|DIGITAL ADVOCACY|ELECTIONEERING|PROMOTION|PROMOTED|MARKETING|YOUTUBE|PRE-?ROLL|\bSEM\b|\bPPC\b|PAY PER CLICK`
- NONAD purpose: `SOFTWARE|SUBSCRIPTION|E-?MAIL|HOSTING|WEB ?SITE|WEB SERVICE|DOMAIN|G-?SUITE|GSUITE|WORKSPACE|CLOUD|STORAGE|COMPUTER|\bIT\b|TECHNOLOGY|TECH SUPPORT|OFFICE|PHONE|VOICE|INTERNET SERVICE|INTERNET UTILITY|UTILIT|DATA ?BASE|DATA SERVICE|LICENS|\bAPPS?\b|PRODUCTIVITY|ORGANIZATIONAL TOOLS|DIGITAL TOOLS|PAYROLL|EQUIPMENT|SUPPLIES|WIRE SERVICE|SERVER|VOTER FILE|FIBER|CATERING|TRAVEL|RECRUIT|EMPLOYMENT|REFUND`
- NONAD payee product: `WORKSPACE|G ?-?SUITE|GSUITE|SUITES?\b|CLOUD|DOMAINS?|FIBER|\bFI\b|F1 PHONE|VOICE|\bPLAY\b|STORE|STORAGE|PHOTOS|\bNEST\b|GMAIL|\bTV\b|YOUTUBETV|PREMIUM|\bPRO\b|\bAPPS?\b|\bAPS\b|\bPAY\b|WALLET|LOOKER|CHATGPT|OTTER|CLASH|FOOTBALL|PHONE|MERCHANDISE|CATERING|OPERACIONES`
- AD payee product: `\bADS?\b|ADWORDS|\bADX\b|ADVERTIS|\bAD SERVICES|LEADS|DOUBLECLICK|YOUTUBE` (YouTube only when no NONAD product word).
Class: mixed payee: UNCLEAR. Purpose AD and not NONAD: AD, unless the payee is a NONAD product (then UNCLEAR). Purpose NONAD and not AD:
NONAD, unless the payee is an AD product (then UNCLEAR). Purpose both: UNCLEAR. Purpose neither: AD if the payee is an AD product,
NONAD if a NONAD product, UNCLEAR otherwise. Every Schedule E Google row is an ad row (an independent expenditure is a public communication).

## FEC side of each row (dates are FEC transaction dates)
- D_lo = Schedule B Google rows classed AD + Schedule E Google rows after deduplication (per committee, for each key of date, amount,
  payee, candidate and support or oppose, the largest count found within any single file number; this removes 24 and 48 hour notices
  repeated in later reports and amendments).
- D_hi = every Schedule B Google row (AD, UNCLEAR, NONAD, mixed) + Schedule E Google rows without deduplication.
- A (pool that could have reached Google through others) = Schedule B rows to payees that are not Google whose purpose matches the AD
  purpose pattern or `DIGITAL|MEDIA|ONLINE|INTERNET|\bWEB\b|SOCIAL|SEARCH|VIDEO|STREAMING|\bCTV\b|\bOTT\b|PROGRAMMATIC|CONNECTED TV`,
  + every Schedule E row to a payee that is not Google, + for party committees (type X or Y) the cycle's party coordinated expenditures
  from webk (Schedule F payees are not in any bulk file). Consulting, salary and travel without those words are not in A.
- Memo rows count: they are almost all credit card itemizations (see reads). A memo row whose parent (same committee, file number and
  BACK_REF_TRAN_ID) is itself a Google row is dropped and counted.
- Amendments: a key of committee, report year, report type and transaction id found under more than one file number keeps the highest
  file number. Drops counted.
- Negative amounts are kept and net within their class. Each row keeps the count and sum of positive and negative items per class.
- Rows dated outside every window, and rows with a bad date or field count, are counted.

## Google side of each row (the stated figure, with its interval)
Google states weekly spend in whole hundreds of dollars. Per listed week we allow 100 dollars either way (a week listed at zero is
0 to 100). Payments may fall up to P days before the ad week starts and up to Q days after it ends. Week s covers days s to s+6.
For an FEC window [a, b]:
- G_lo = sum over weeks with s >= a + P and s + 6 + Q <= b of max(0, v - 100) (spend that must have been paid inside the window).
- G_hi = sum over weeks with s + 6 + Q >= a and s - P <= b of (v + 100) (spend that could have been paid inside it).
- G_pt = sum over weeks starting inside [a, b] of v (the plain figure, shown, never used for an outcome).
Primary ruler: P = 31, Q = 92 (prepayment used within a month; invoices and card statements paid within about three months).
Second ruler beside it: P = 92, Q = 183. A row whose outcome differs between the two is marked timing-sensitive.
In a calendar quarter P + Q + 6 exceeds the quarter's length, so G_lo is 0 and quarter rows can read only ABOVE or CANNOT_TELL. They
are kept to show where the timing falls.

## Windows
- Cycle rows: a = 1 January of the odd year, b = 31 December of the even year, cut earlier at the committee's coverage end date
  (webk CVG_END_DT for PACs and parties, weball CVG_END_DT through the candidate id for candidate committees) when that is earlier.
- 2026 is cut at the last complete month of the itemized file: the last month m whose row count by transaction date is at least
  0.7 times the mean of the three months before it, counting forward from January 2025. On the 9 November files we expect June 2026.
- Quarter rows: calendar quarters inside each cycle window.

## Outcomes (sizes fixed now)
Size that matters: a gap of at least 1,000 dollars and at least 10 percent of Google's bound (G_hi for ABOVE, G_lo for BELOW).
- ABOVE: D_lo - G_hi >= size. The committee's reported ad payments to Google exceed the most Google's stated spend allows.
- BELOW: G_lo - (D_hi + A) >= size. Every reported Google payment plus the whole pool is short of the least Google's stated spend allows.
- CONSISTENT: G_lo <= D_lo, D_hi <= G_hi, and G_hi <= 2 G_lo (the timing and rounding band spans at most a factor of two).
- CANNOT_TELL with a reason: scope (committee type I, C, E or Z, whose reports carry no operating expenditures), agency (D_hi < G_lo
  <= D_hi + A), band (G_hi > 2 G_lo), purpose (the D interval crosses a band edge), near (outside the band by less than the size).
- NOTHING_RETURNED: Google states spend in the window and the FEC files hold no Schedule B row, no Schedule E row and no summary record
  for the committee in that cycle.
- No row is made when Google's possible window holds no listed week and the FEC shows no Google row.
Both alternatives are tested on every row: the ABOVE test and the BELOW test are stored with their margins.

## Known-good (run before the first full read, and on every run)
1. Google internal check: for every US advertiser the weekly sum lies within the advertiser total plus or minus (100 x listed weeks + 100).
   If more than 1 percent fall outside, the rounding band is wrong and every outcome is CANNOT_TELL.
2. Planted rows: synthetic committees built to read ABOVE, BELOW, CONSISTENT, CANNOT_TELL (agency), CANNOT_TELL (band) and
   NOTHING_RETURNED go through the same functions. Any mismatch: every outcome is CANNOT_TELL.
3. Parser: every oppexp line has 26 fields (25 named plus a trailing empty field). Other lines are dropped and counted. If more than
   0.1 percent are dropped, every outcome is CANNOT_TELL.
4. FEC completeness: monthly row counts per cycle are stored. The 2026 cut follows the rule above.

## Party and naming
The committee name is CMTE_NM as filed in the cm file of the row's cycle (else the latest cm file holding the ID). The party field is
CMTE_PTY_AFFILIATION as filed. It is stored and never used to group, sort or describe.

## Limits stated now
- Google's library holds only ads Google classes as election ads. Other ads a committee buys from Google sit only in the FEC column.
  Ads paid from accounts that do not report to the FEC (state or non-federal accounts) sit only in Google's column.
- Disbursement lines outside oppexp (Form 3 line 21, Form 3P line 29, Form 3X line 29) and itemized Schedule F are not in the bulk files.
- The FEC itemized file is processed data and lags the filings.
- A name match can attach the wrong committee. Ambiguous names are dropped and counted.
- The match gate keeps advertisers that gave Google an FEC ID or whose name equals one committee. The unmatched spend is reported.

## Reads before the plan (schema, vocabulary and completeness only)
- Google advertiser-stats: 23,316 advertisers, 18,039 with Regions US only. Public_IDs_List forms among US advertisers: EIN 9,443,
  FEC ID 3,303, empty 1,258, state registrations the rest. All Spend_USD values are multiples of 100.
- Google weekly: 325,852 rows, no repeated advertiser and week, weeks start on Sunday, 2018-05 to 2026-11. Per US advertiser the weekly
  sum equals the total for 6,634, is above it for 8,804 and below it for 2,601. All 18,039 lie within total - (100 x weeks + 100) and
  total + (100 x weeks + 100) except 450 that fall below total - 100 by a few hundred dollars across many weeks.
- FEC oppexp: 8,268,689 lines in four files, every line 26 fields, SUB_ID unique across files. In the 2024 file 79 of 57,207 reports
  appear under two file numbers and 572 of 2,246,396 transaction ids repeat across them.
- Google payee vocabulary: 180 distinct payee strings, 84,146 rows. Memo rows 33,306: parent payee another company for 30,823
  (credit cards), no parent found for 2,482, parent Google for 1.
- Schedule E Google rows: 2020 1,148 rows, 2022 1,812, 2024 1,553, 2026 587, with repeated keys.
- oppexp26 rows by report: Q1 222,118, Q2 224,665, Q3 78,939. Rows by transaction month fall from June (121,022) to July (72,393).

## Addendum 1 (10 Nov 2026 UTC, before the first comparison)
1. The FEC's description of the independent expenditure file (read today at
   https://www.fec.gov/campaign-finance-data/independent-expenditures-file-description/) says: "This file contains 24-hour and 48-hour
   reports of independent expenditures filed during the current election cycle." Independent expenditures reported only on periodic
   Schedule E are therefore not in it. Change: for PACs and parties, the pool takes the larger of the file's non-Google rows in the
   window and the cycle's total "Independent Expenditures Made" from webk (field 24 of 27). Quarter rows take the cycle total.
   Schedule E Google rows in D still come from the file only. That can lower D but the cycle total in the pool keeps the BELOW test a bound.
2. The FEC's description of the operating expenditures file confirms the lines read: "Form 3, Line 17 for House and Senate committees,
   Form 3P, Line 23 for Presidential committees, Form 3X, Lines 21(a)(i), 21(a)(ii), and 21(b) for PAC and Party committees". Memo code:
   "'X' indicates that the amount is NOT to be included in the itemization total."
3. The 2026 cut walks forward from April 2025 and stops at the first month that fails the 0.7 test. The cut is the end of the month
   before it. (The plan's wording "the last month ... counting forward" means this.)
4. The fragment's sentence on unmatched advertisers states only what their Public_IDs_List holds, counted by form.

## Addendum 2 (10 Nov 2026 UTC, after the first run printed its aggregate outcome counts, before any row was read)
The first run printed one line of cycle outcome counts (ABOVE 53, BELOW 110, CONSISTENT 40, CANNOT_TELL 6,066, NOTHING_RETURNED 214).
No row was opened. A read of the match gate's unmatched ID forms then showed two rule gaps in the ID field itself:
1. About 130 US advertisers list an FEC candidate ID ("FEC ID H8OH01043", "FEC ID S4AZ00139", "FEC ID P40016024") or a committee ID in
   lowercase ("FEC ID c00810044"). Change: IDs are read case-insensitively and uppercased. A candidate ID maps to the candidate's
   principal campaign committee (cm CAND_ID equal and CMTE_DSGN P) in any cm file of 2020 to 2026. More than one such committee joins
   them as a group. Tier label "candidate id". A candidate ID with no principal committee, or a malformed ID ("COO795948",
   "CC2000407"), is UNMATCHED (id not in cm).
2. Tier B (name) is not applied to an advertiser whose Public_IDs_List carries a state registration ("Registered in US-XX"), which
   marks a state-level committee. Such advertisers are UNMATCHED (state registration).
The first run's files are kept as data/adspend_run1_superseded.json and data/summary_run1_superseded.json.

## Addendum 3 (10 Nov 2026 UTC, after reading 7 quarter rows that read BELOW)
The plan says quarter rows can read only ABOVE or CANNOT_TELL. Run 2 gave 7 quarter rows reading BELOW. We read those 7 rows: in every
one Google states 0 to 5,800 dollars, G_lo is 0, and the pool is negative (refunds from other vendors reported as negative disbursements,
-3,056 to -30,745 dollars). A negative pool is not an upper bound on money that could have reached Google. Change, which can only move
rows out of BELOW: the pool counts positive items only, and the BELOW test uses the positive part of D_hi:
BELOW when G_lo - (max(D_hi, 0) + pool of positive items) >= size. D_lo, D_hi and the ABOVE and CONSISTENT tests keep netting.
Run 2's files are kept as data/adspend_run2_superseded.json and data/summary_run2_superseded.json. Run 2 cycle counts before this change:
ABOVE 49, BELOW 103, CONSISTENT 41, CANNOT_TELL 6,013, NOTHING_RETURNED 191. No cycle row had been read.

## Addendum 4 (10 Nov 2026 UTC, defined after the data: after reading the BELOW, ABOVE and CONSISTENT cycle rows of run 3)
Read: run 3's decided cycle rows set beside each committee's own summary totals. Several BELOW rows rest on committees whose
disbursements the itemized file barely holds: V-PAC 2026 summary disbursements 47,573,794 dollars and no itemized row, RSLC PAC 2026
12,729,101 and no row, Republican Party of Florida 2022 implied operating disbursements 39,583,692 against 1,183,992 itemized.
Their Google payments can sit in reports the processed file does not yet hold, or on lines the bulk file leaves out (Form 3X line 29
other disbursements and line 30 federal election activity, Form 3 line 21). A BELOW cannot rest on money we cannot see, and neither can
a CONSISTENT. Changes, which can only move rows out of BELOW and CONSISTENT:
1. unseen = max(0, implied operating disbursements from the summary - itemized non-memo Schedule B total of the committee in that cycle
   file). Implied from webk: total disbursements - transfers to affiliates - refunds - loan repayments - contributions to other committees
   - independent expenditures - party coordinated expenditures. Implied from weball (candidate committees, through the cm candidate id,
   counted once per candidate): total disbursements - transfers to authorized committees - loan repayments - refunds. Summary totals run
   to the committee's latest coverage date, so for 2026 the term also holds July to October money. That only widens the bound.
2. BELOW when G_lo - (max(D_hi, 0) + pool + unseen) >= size. CONSISTENT needs D_hi + unseen <= G_hi as well. New CANNOT_TELL reason
   "unseen": money in the summary that the itemized file does not show could decide the side.
3. Scope (types I, C, E, Z) takes precedence over NOTHING_RETURNED, because those filers never report operating expenditures.
4. Public rows matched by name only say so.
Run 3's files are kept as data/adspend_run3_superseded.json and data/summary_run3_superseded.json.

## Addendum 5 (10 Nov 2026 UTC, defined after the data: after reading the rows Addendum 4 moved out of CONSISTENT)
Read: 34 run-3 CONSISTENT rows became CANNOT_TELL (unseen) in run 4. Most carry unseen money of a few hundred to a few thousand dollars
against operating disbursements of hundreds of thousands to millions (Carl DeMaio for Congress 2020: unseen 1,419 of 3,036,979). That
remainder is mostly unitemized spending, and the itemization rule caps how much of it can be Google. 11 CFR 104.3 (eCFR, current on
1 Nov 2026): (b)(3)(i), committees other than authorized committees, itemize "Each person to whom an expenditure in an aggregate amount or
value in excess of $200 within the calendar year is made ... to meet the committee's operating expenses"; (b)(4)(i), authorized
committees, "in excess of $200 within the election cycle". So unitemized money can hold at most 400 dollars of payments to Google
(one payee) in a two-year cycle. Change:
1. Per committee, unseen counts in full when the committee is a party committee (type X or Y, whose line 30 federal election activity
   can carry ad buys outside the itemized file), or when the itemized file holds less than 0.9 of the committee's implied operating
   disbursements (reports missing or money on other lines). Otherwise unseen counts as min(unseen, 400).
2. The threshold 0.9 is ours and is defined after the data. Every row keeps outcome_unseen_full, its outcome with unseen in full as in
   Addendum 4, and rows whose outcome differs are marked unseen_rule_sensitive and counted in the summary.
Run 4's files are kept as data/adspend_run4_superseded.json and data/summary_run4_superseded.json.

## Record of runs (10 Nov 2026 UTC)
Files read: Google bundle Last-Modified 9 Nov 2026 23:45:03 GMT, report data updated 2026-11-09 14:04:54 PT. FEC bulk files as listed in
data/raw/manifest.json (oppexp24 Last-Modified 8 Nov 2026 21:40:06 GMT, oppexp26 8 Nov 2026 18:10:14 GMT).
- Run 1 (plan + addendum 1): cycle ABOVE 53, BELOW 110, CONSISTENT 40, CANNOT_TELL 6,066, NOTHING_RETURNED 214. Superseded.
- Run 2 (+ addendum 2): ABOVE 49, BELOW 103, CONSISTENT 41, CANNOT_TELL 6,013, NOTHING_RETURNED 191. Superseded.
- Run 3 (+ addendum 3): ABOVE 49, BELOW 99, CONSISTENT 41, CANNOT_TELL 6,017, NOTHING_RETURNED 191. Superseded.
- Run 4 (+ addendum 4): ABOVE 49, BELOW 35, CONSISTENT 7, CANNOT_TELL 6,136, NOTHING_RETURNED 170. Superseded.
- Run 5 (+ addendum 5, current): ABOVE 49, BELOW 38, CONSISTENT 26, CANNOT_TELL 6,114, NOTHING_RETURNED 170 over 6,397 cycle rows.
  Quarter rows 19,688: ABOVE 108, CANNOT_TELL 19,434, NOTHING_RETURNED 146. Decided cycle rows 113: timing-sensitive 36, dependent on
  the itemization rule 22, matched by name only 13, robust (ID match, neither flag) 53.
Known-good on run 5: planted rows passed, Google internal check 0 of 18,039 advertisers outside the band, oppexp parser 15 of 8,268,689
lines dropped (bad date), 2026 cut at 30 June 2026.
Independent recount (separate script, raw files, no shared code), matched the tick to the cent:
Trump Save America JFC 2022 (19 rows "ONLINE ADVERTISING" to GOOGLE LLC, 10,405,151.72; Google weekly 7,590,600),
Warren for President 2020 (22 rows "DIGITAL MEDIA SERVICES", 4,845,804, plus 26 "SUBSCRIPTION" rows; Google 3,050,100),
Biden Victory Fund 2020 (6 rows "DIGITAL ADVERTISING", 14,530,082.57; Google 15,932,100),
Harris Victory Fund 2024 (20 rows "ONLINE FUNDRAISING", 82,202,290.88; Google 82,116,000),
CCAGW PAC 2024 (no Google row; webk24 total disbursements 640; Google 133,600), Carl DeMaio for Congress 2020 (49 memo rows "ONLINE ADS",
54,000.00; Google 54,000).
/tp core pass over every row: every stored outcome re-derives from its stored numbers, no quarter row reads BELOW or CONSISTENT.

## Addendum 6 (10 Nov 2026 UTC, record of departures found by the outside referee, before the rerun)
The referee (social_index/adspend_referee/REFEREE.md, verdict FIX THEN SHIP) rebuilt all 6,397 cycle rows from the raw files with its
own code and found these places where the tick departs from the plan text. None moves an outcome in the referee's variant runs.
1. AD payee words, kept and recorded: the tick's AD payee pattern adds `\*ADS|GOOGLEADS|ADS\d|ADWRDS|\bADDS\b` and treats `YOU TUBE`
   like `YOUTUBE`. These are Google ad descriptors as they appear in card memos ("GOOGLE *ADS2583901760", "GOOGLEADS", "GOOGLE ADDS").
   A payee that is both an AD product and a NONAD product counts as neutral (then the purpose decides). The comment in the code that
   called these "PLAN.md, verbatim patterns" was wrong and is corrected. Effect: one D_lo value (Bowman & Bowman 2024, 1,265 against
   1,000 under the plan's words), no outcome.
2. Schedule E mixed payees, now as the plan says: a Schedule E Google row whose payee also names another company counts in D_hi only.
3. Amendment rule, now before the Google and pool filter: a key of committee, report year, report type and transaction id found
   under more than one file number keeps the highest file number, applied to every row of a matched committee. The itemized total
   behind unseen is summed after it. Effect: America Leads Action 2024 pool falls by 1,522.50 ("WEB SERVICES" amended to "BANK FEES").
4. Schedule E deduplication, extended: before the key rule, rows sharing a committee and transaction id keep only the highest file
   number, so an amended 24 or 48 hour entry is not counted twice (Way to Lead PAC 2020, transaction VVAZQAQ6VM5).
5. The tick is committed with each addendum from now on. The code behind runs 1 to 4 was not committed. Run 5's code is commit 9242f45.

## Addendum 7 (10 Nov 2026 UTC, defined after the data: the outside referee's blocking and fix-before-ship items)
Read: the referee's report on run 5 (social_index/adspend_referee/REFEREE.md). It found Below rows that compare a federal committee with a
Google advertiser that is another entity or another account (House Republican Campaign Committee 2020, 2022 and 2024, Uniting Missouri
PAC 2020, Greg for Montana 2020, Middle Ground 2026, Justice 2020, McKayla Wilkes for Congress 2020, Preserve Protect and Defend PAC 2020,
and three committees whose FEC summary record is empty), a Nothing returned test that counted Google spend outside the window, Above
rows where Google lists no spend in the window, and Above rows resting on Schedule E amounts the filer marked as estimates. Every rule
below is ours, was set after reading those rows, and can only move a row out of a match or out of a decided outcome. Flags never move one.
1. Name-match validity. A name match (Tier B) is unmatched, counted by reason in the gate, when any of these holds:
   a. collision: another US advertiser in Google's file with the same normalized name carries a state registration;
   b. geo: at least two thirds of the advertiser's US spend in Google's state file (google-political-ads-advertiser-geo-spend.csv) sits in
      one state, and that state is not the committee's home state (the candidate's office state from the cn file for House and Senate
      committees, none for presidential committees, the committee's filed address state otherwise);
   c. first activity: the advertiser's first week of stated spend is more than 90 days before the committee's first itemized FEC row
      (Schedule B or E, any purpose, any file read), when that first row is on or after 1 April 2019; or more than 90 days before 1 January
      of the first cycle whose committee file holds the committee, when that cycle is 2022 or later.
   The thresholds (two thirds, 90 days) were chosen against the referee's rows: Justice 2020 has 75.0 percent of its spend in West Virginia
   against a DC address, the 2020 Preserve Protect and Defend PAC advertiser 78.6 percent in Kentucky against DC, Uniting Missouri PAC's
   spend starts 145 days and Middle Ground's 268 days before the committee's first itemized row.
2. Candidate-cycle committee and cycle guard. A row reads Cannot tell (cycle) when no member committee is in that cycle's committee file,
   or when every registered member is a candidate committee whose candidate the cycle's candidate file (cn) lists as not yet a statutory
   candidate (status N) for a later election. For a group matched by name only, any status other than C (statutory candidate) or F
   (statutory candidate for a future election), or no cn record, also counts. Only CAND_ID, CAND_ELECTION_YR, CAND_OFFICE_ST, CAND_OFFICE,
   CAND_STATUS and CAND_PCC are read from cn files, never names or addresses.
3. A name match cannot decide Below on its own (the referee's rule): a row that reads Below reads Cannot tell (name) when the band built
   without the name-matched advertisers does not reach Below. Name matches keep deciding Above and Consistent.
4. An empty summary record (no coverage date and every total zero) counts as no summary.
5. Nothing returned, as the plan says: Google states spend inside the window (weeks starting in it), and the FEC files hold no Schedule B
   row, no Schedule E row and no summary for the committee in that cycle. A group matched by name only reads Cannot tell (name) instead.
6. Above needs Google spend stated in the window. Otherwise the row reads Cannot tell (no Google spend). For quarter rows the test is
   spend stated anywhere in the quarter's possible window.
7. Schedule E rows whose purpose says estimate (pattern ESTIMAT) count in D_hi and not in D_lo. A row that would read Above or Consistent
   only with them reads Cannot tell (estimates).
8. Flags, outcome kept: Below rows where card payments or reimbursements in the window (Schedule B, non-memo, payee not Google, purpose
   matching the referee's card and reimbursement families) exceed the gap less the size; Above rows that rest on ad rows whose own purpose
   text says not candidate-specific, no express advocacy, not an independent expenditure, or nonfederal; Above rows where another
   advertiser whose name equals the committee's or an advertiser's name, apart from PAC, INC, LLC, CORP, THE, FEDERAL and CO, states spend
   in the possible window.
9. The page links the slim public file (cycle rows only), drops the per-quarter claim (quarter rows stay in the full data file), and
   takes the referee's copy fixes.
The referee's own proposed rules (scripts/proposed.py) give Above 28, Below 26, Consistent 26, Nothing returned 23. Ours differ in
method (validity rules in place of hand relabels) and are compared row by row in the record of runs.

## Record of runs, continued (10 Nov 2026 UTC)
- Run 7 (addenda 6 and 7, code commit 16ea552; the public file's layout was then slimmed, rows unchanged): 6,160 cycle rows. The 237 rows
  fewer than run 5 belong to groups whose only advertisers the name-match checks set aside, and every one of them reads Cannot tell under
  the referee's own proposed rules. ABOVE 28, BELOW 26, CONSISTENT 26, CANNOT_TELL 6,056, NOTHING_RETURNED 24. By cycle (Above, Below,
  Consistent, Cannot tell, Nothing returned): 2020 12, 3, 11, 1,091, 6. 2022 8, 8, 7, 1,627, 8. 2024 8, 10, 8, 1,624, 7. 2026 0, 5, 0,
  1,714, 3. Quarter rows 19,287: ABOVE 30, CANNOT_TELL 19,221, NOTHING_RETURNED 36. Name matches set aside: 210 (geo 143, collision 29,
  first activity 38), leaving 800 of 1,010. Flags: card payments or reimbursements 8, purpose text 5, related advertiser 1.
- Against the referee's proposed rules (scripts/proposed.py: 28, 26, 26, 6,294, 23): the same 80 decided rows. Nothing returned differs by
  11 rows. Six more here because the empty-summary rule (the referee's fix 4) applies to every row, where proposed.py applies it to Below
  rows only: Solid Blue Strategies 2020, Pima County Republican Party 2020, Not One Step Back PAC 2022, The Leadership Fund 2022, Place
  America First 2024, HUD PAC 2026. Five fewer because the candidate-cycle rule reads them Cannot tell (cycle): McClellan for Congress 2022
  and Harvey Wizard for President 2026 (ID matches whose candidate the cycle's cn file lists as not yet a candidate, for a later election;
  the referee's own scan flagged McClellan), Travis Oler for US Senate 2020, Simpson for America 2022 and Kelly for Senate 2022 (name-only
  matches whose candidate was not a current or future candidate in that cycle).
- Referee scripts rerun on run 7's outputs: page_check.py, 38 table rows, no problems. cmp_all.py, 237 rows only in the plan-rules recount,
  none only here, outcome differences only where the new rules act. recount_rows.py stops with a KeyError at Middle Ground 2026, a row
  Addendum 7 removed. The nine rows it printed before that carry run 7's outcomes. variants.py, match_audit.py, below_detail.py and
  audits.py analyse the referee's plan-rules recount and reproduce the report. variants.py's two-row check shows America Leads Action 2024's
  pool at the plan reading and Bowman & Bowman 2024's D_lo at 1,265 under the payee words Addendum 6 records.
- Filed party field of the decided rows (stored, never used): Above blank 12, DEM 12, REP 4. Below blank 16, REP 5, DEM 4, IND 1.
  Consistent REP 13, DEM 10, blank 3. The same split as the referee's proposed rules.
