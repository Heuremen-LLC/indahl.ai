# CREDIT: what the CFPB and card issuers state about consumer credit, set against the public record. Plan, written before any stated figure was set beside a delivered one.

Desk of indahl.ai under HERMES. Heuremen LLC. Byline Wayfinder and Bones. Aggregate company-level data only. No complaint narrative, ZIP code, state, tag or anything about a person is read into any output. Companies are named as the database names them.

## Stated rules and figures read (quoted from the primary source, fetched 10 Nov 2026, copies in data/raw/docs)

S1. The expectation for a company response. CFPB complaint process page (consumerfinance.gov/complaint/process/), step 3: "Companies generally respond in 15 days." and "In some cases, the company will let you know their response is in progress and provide a final response in 60 days."
The CFPB's annual Consumer Response reports define the database flag: "Complaints in which a company did not provide a response within 15 calendar days of the complaint being sent to the company—or within 60 days if it requested more time—are reflected in the Consumer Complaint Database as not having received a timely response." (2025 report, footnote 24, 2024 report, footnote 28). The 2023 report: "within 15 calendar days of the complaint being sent to the company. If a complaint could not be closed within 15 calendar days, the company provided an interim explanation to the consumer and the CFPB and then a final response within 60 calendar days of the complaint being sent to the company."
The database field reference (consumerfinance.gov/complaint/data-use/): "Timely response? Whether the company gave a timely response. For example, "Yes" or "No."" and "Date sent to company The date the CFPB sent the complaint to the company." and "Company response to consumer This is how the company responded. For example, "Closed with explanation.""
The statute behind it, 12 U.S.C. 5534(b): "A covered person subject to supervision and primary enforcement by the Bureau pursuant to section 5515 of this title shall provide a timely response, in writing where appropriate, to the Bureau, ... concerning a consumer complaint or inquiry". The statute sets no number of days.

S2. The CFPB's printed share of timely responses, one per year, from its Consumer Response Annual Report:
- 2021 (March 2022): "Companies provided a timely response to 99% of the approximately 752,800 complaints sent to them for review in 2021."
- 2022 (March 2023): "Companies provided a timely response to 99% of the approximately 819,800 complaints sent to them for review in 2022."
- 2023 (March 2024): "Companies provided a timely response to 99.6% of the 1,348,200 complaints sent to them for review in 2023."
- 2024 (May 2025): "Companies provided a timely response to 99.7% of the approximately 2,829,400 complaints sent to them for review in 2024."
- 2025 (March 2026): "Companies overwhelmingly provided timely responses, providing a timely response to 99.6% of the more than 5.9 million complaints sent to them for review in 2025."

S3. The CFPB's printed share for its own forwarding, 2025 report: "Of those complaints sent to companies, the Bureau sent 97% to a company in a day or less."

S4. Credit reporting disputes, 15 U.S.C. 1681i(a)(1)(A) (Fair Credit Reporting Act section 611): if the consumer disputes an item and "notifies the agency directly, or indirectly through a reseller, of such dispute, the agency shall, free of charge, conduct a reasonable reinvestigation ... before the end of the 30-day period beginning on the date on which the agency receives the notice of the dispute from the consumer or reseller." (B): "the 30-day period described in subparagraph (A) may be extended for not more than 15 additional days if the consumer reporting agency receives information from the consumer during that 30-day period that is relevant to the reinvestigation." Text from the Cornell LII copy of the US Code (law.cornell.edu/uscode/text/15/1681i).

S5. The CFPB's printed Table 1, "How companies have responded to consumer complaints", by product, in the 2024 and 2025 reports (closed with monetary relief, with non-monetary relief, with explanation, admin response, company reviewing, no timely response). Shown beside the database shares. Not a ruler (see Q1b).

S6. Card plan terms. The CFPB Terms of Credit Card Plans (TCCP) survey, one file per half year (consumerfinance.gov/data-research/credit-card-data/terms-credit-card-plans-survey/), one row per plan an issuer reports, with "Purchase APR min", "Purchase APR median", "Purchase APR max", the credit tier APRs, "Issued by Top 25 Institution", and fees.
The Federal Reserve G.19 Consumer Credit release, Terms of Credit, commercial bank credit card plans: "For credit card accounts, the rate for all accounts is the stated APR averaged across all credit card accounts at all reporting banks. The rate for accounts assessed interest is the annualized ratio of total finance charges at all reporting banks to the total average daily balances against which the finance charges were assessed (excludes accounts for which no finance charges were assessed)." Quarterly, from the G.19 history table cc_hist_tc_levels.

## Questions
Q1a. What share of complaints in the database are flagged not timely, by company, set beside the CFPB's own printed all-company share?
Q1b. How did the three nationwide credit bureaus close complaints, against all other companies? Descriptive.
Q1c. Can the database measure the 30-day reinvestigation period of 15 U.S.C. 1681i?
Q1d. Does the database's own date pair agree with the CFPB's printed "97% in a day or less" for 2025?
Q2. Do the purchase APRs issuers state in the TCCP survey sit beside the G.19 averages in a way that can be compared?

## Data (all public, keyless)
- CFPB Consumer Complaint Database, the full file https://files.consumerfinance.gov/ccdb/complaints.csv.zip, downloaded 10 Nov 2026 (file time 10 Nov 2026 10:15, 364,972,185 bytes, sha256 db66181722a6a49b6010b73fe32425bca393d718c8f45af40d84cadb2f4c1d9f). Columns read: Date received, Product, Company, Date sent to company, Company response to consumer, Timely response?, Complaint ID (for the duplicate check only). The ZIP code, State, Tags, Issue, Sub-issue and Company public response columns are never read into any output. This file carries no narrative column.
- The CFPB public search API (consumerfinance.gov/data-research/consumer-complaints/search/api/v1/) for the known-good gate only.
- CFPB Consumer Response Annual Reports 2021 to 2025 (PDF, files.consumerfinance.gov).
- TCCP survey files 2022 H2 to 2025 H2 (seven xlsx files) and the user guide.
- G.19 history table https://www.federalreserve.gov/releases/g19/HIST/cc_hist_tc_levels.html.
Terms: CFPB data are US government works, public. Federal Reserve data are public. Requests one at a time, paced, user agent heuremen-credit/0.1 (+https://indahl.ai/credit).

## Frame (fixed now)
- Window: complaints with Date received from 1 January 2021 to 31 December 2025, the last five complete years. Each calendar year is also read alone.
- A row is one complaint. A row with a Timely response? value other than Yes or No is counted apart and left out of Q1a.
- Duplicate Complaint IDs: counted. The first is kept.
- The three nationwide credit bureaus: the Company values "EQUIFAX, INC.", "Experian Information Solutions Inc." and "TRANSUNION INTERMEDIATE HOLDINGS, INC." (the only Company values in the file holding Equifax, Experian or TransUnion, read in the schema pass). Every other company is "all others".
- Product families, fixed now from the Product values in the file:
  credit reporting = "Credit reporting", "Credit reporting, credit repair services, or other personal consumer reports", "Credit reporting or other personal consumer reports"
  debt collection = "Debt collection"
  credit card = "Credit card", "Credit card or prepaid card", "Prepaid card"
  checking or savings = "Checking or savings account", "Bank account or service"
  mortgage = "Mortgage"
  student loan = "Student loan"
  vehicle loan = "Vehicle loan or lease"
  money transfer = "Money transfer, virtual currency, or money service", "Money transfers", "Virtual currency"
  personal or payday loan = "Payday loan", "Payday loan, title loan, or personal loan", "Payday loan, title loan, personal loan, or advance loan"
  debt or credit management = "Debt or credit management"
  other = "Consumer Loan", "Other financial service" and any value not listed
- Not timely share = rows with Timely response? = No over rows with Yes or No.

## Clustering and intervals (fixed now)
Complaints cluster by company and month: one company's process, staffing or a wave of filings moves many complaints at once. Every interval is a 95 percent percentile interval from a block bootstrap whose block is one company-month (all complaints of one Company value with Date received in one calendar month). For a one-company cell the blocks are that company's months. For a pooled cell the blocks are all company-months in it. 2,000 resamples with replacement, the statistic is the ratio of summed counts, fixed seed 20261110. The page says complaints may also cluster across companies in the same month (a filing wave) and that this is not covered.

## Rules (fixed now)
Q1a, ruler one (pooled, against S2). For each year 2021 to 2025, the timely share of all rows of that year. The printed figure is read as the band its rounding allows: "99%" is [98.5, 99.5), "99.6%" is [99.55, 99.65), "99.7%" is [99.65, 99.75). ABOVE: the whole interval is above the band. BELOW: the whole interval is under it. CONSISTENT: the whole interval is inside it. CANNOT_TELL: otherwise. The printed figure counts every complaint sent to companies that year. The database holds the complaints published by the download date, so the two bases differ, and the page prints both counts. 2025 also reads against "more than 99%" as the band (99, 100], display only.
Q1a, ruler two (each company, against S2). For each company with at least 1,000 rows in a year and rows in at least 10 of its months, the not timely share with its company-month interval, against the not timely share the printed figure leaves (2025: [0.35, 0.45) percent). Same four outcomes. The CFPB printed figure is an all-company average, not a per-company limit, and the page says so. A company with fewer rows or months reads CANNOT_TELL and is counted, not listed. The same rule for each company and product family pair in 2025, and for each bureau over the whole window against the window's rows-weighted printed share (display only).
Q1a, the expectation itself (S1). S1 says "generally" and the flag records whether each complaint met 15 or 60 days. No share is stated, so no outcome is drawn against S1 alone. Each company's count and share not timely is printed.
Q1b (descriptive). For each year and for the window: the share of rows in each Company response to consumer category for the three bureaus pooled, each bureau, and all others, with company-month intervals. No outcome. The S5 Table 1 credit reporting row is printed beside for 2024 and 2025 with outcome CANNOT_TELL, because Table 1 counts complaints with an admin response (10 percent of credit reporting in 2025 by the table) that the database does not publish, so the bases differ.
Q1c. The database records the date the CFPB received the complaint and the date it sent it to the company. It records no date of company response, and no date a bureau received a dispute notice under 1681i. A complaint to the CFPB is not by itself the dispute notice the statute counts from. So the 30-day period cannot be measured from the file. Outcome fixed now: CANNOT_TELL, with that reason. Shown beside, decides nothing: for credit reporting complaints at the three bureaus, the days from received to sent, and the not timely share under the CFPB's 15 and 60 day flag.
Q1d (against S3). The share of 2025 rows with Date sent to company minus Date received of 0 or 1 day, against the band [96.5, 97.5) that "97%" allows. Same four outcomes, company-month interval. A row with sent before received is counted apart and left out.
Q2. For each TCCP file: plans, plans with a purchase APR, the median across plans of "Purchase APR median" (all plans, and plans of a Top 25 institution), the 10th and 90th percentiles, the lowest "Purchase APR min" and highest "Purchase APR max". Beside it the G.19 all accounts and accounts assessed interest for the quarter holding the file's report date (June 30: Q2, December 31: Q4). Outcome fixed now: CANNOT_TELL, not like for like. The survey states APRs offered on plans, one row per plan with no account weight, including credit unions and smaller issuers. G.19 averages APRs held on all accounts at reporting commercial banks, weighted by account (all accounts) or by balance (assessed interest). Display only: whether each G.19 figure falls between the 10th and 90th percentiles of the top 25 plan medians. Fees issuers state (late fee, annual fee) are printed with no delivered counterpart and no outcome.
Q3. The New York Fed Household Debt and Credit report is set aside for this release.

Headline (fixed now): Q1a ruler one for 2025: the database timely share with its interval against the printed 99.6 percent, its outcome, then the three bureaus' 2025 not timely shares, and the count of companies reading each outcome under ruler two in 2025.

## Nothing returned, counted apart and never folded
- Rows with a Timely response? value other than Yes or No, rows with an unreadable date, rows outside the window.
- Rows with sent before received (Q1d).
- A TCCP file that cannot be read, a plan with no purchase APR, a G.19 quarter not in the table.

## Both alternatives
A. The database share sits inside the printed figure, companies sit inside it, the forwarding share matches. CONSISTENT or CANNOT_TELL.
B. The database share or a company sits above or below the printed figure. ABOVE or BELOW.
Either is printed the same way. No cause is named for any reading.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL and keeps the original)
1. Format. The header holds the 15 fields read in the schema pass. Every row has 15 fields. Timely values are Yes or No.
2. Reader. For four cells (EQUIFAX, INC. 2023 not timely, the whole of 2024 not timely, Experian Information Solutions Inc. 2025 all rows, and 2022 all rows), our count from the file equals the hit count the CFPB search API returns for the same filter, within 0.5 percent (the API is live and the file is a 10 Nov copy).
3. Rule. Synthetic readings come out ABOVE, BELOW, CONSISTENT and CANNOT_TELL as planted, the block bootstrap of a planted cell covers the planted share, and heuremen_kit's self-test passes.
4. Privacy. Every written output is scanned for the keys and column names ZIP code, State, Tags, Issue, Sub-issue, Company public response and narrative. Any hit stops the run before anything is written to the site.

## Set aside
- Complaint narratives, ZIP codes, states, tags, issues, company public responses.
- Consumer disputed? (retired by the CFPB in 2017, not in this file).
- The Philadelphia Fed Y-14 large bank card series (not read for this release).
- The New York Fed report.
- Any cause of any reading, and any reading about whether a complaint was right.

## Reading done before this plan was written
- The CFPB pages, the five annual reports, the statute pages, the TCCP page and the column names of the 2025 H2 TCCP file, the G.19 current release notes and the history table layout.
- A schema pass over the complaint file (scout/schema_pass.py, scout/schema.json): the header, rows by year of Date received, the value sets of Product, Company response to consumer, Timely response? and Submitted via, and the Company values that hold a bureau name. No share of any value by company, product or year was computed, and no timely or response count was read.
- The rows by year (2021 495,940, 2022 800,245, 2023 1,292,043, 2024 2,734,252, 2025 5,442,927) were seen in the schema pass, next to the printed counts of complaints sent in S2.
- The G.19 card rates in the current release table were seen on the page while reading its notes.
No stated figure was set beside a delivered one.
