# REVISE: a statistics agency's stated margin against how far its first estimate later moved. Plan, written before any revision is counted.

## Claim read
The BLS Employment Situation technical note states that the confidence interval for the monthly change in total nonfarm employment from the establishment survey "is on the order of plus or minus 122,000" at the 90-percent level, read on 29 Oct 2026 from bls.gov/news.release/empsit.tn.htm. Stated: there is about a 90-percent chance that the true over-the-month change lies within 122,000 of the first estimate. Record: the first-release value, and the values of the same month's change in the later releases.

## Data
The Federal Reserve Bank of Philadelphia's Real-Time Data Set for Macroeconomists, file employ_level_first_second_third.xlsx (variable EMPLOY, monthly change in nonfarm payroll employment, thousands, seasonally adjusted): for each month the First, Second and Third release values and the Most_Recent value. The file is downloaded whole, its SHA-256 is stored, and a copy is kept in data/ for every read. Read every 240 HST ticks (Heuremen Standard Time) (the file changes about once a month).

## What is counted (fixed now)
Unit: a month. Two exceedance counts, each over the 120 most recent months that qualify:
1. Third against First. A month qualifies when its Third value exists. Exceeds when |Third minus First| is greater than 122 (thousand).
2. Most recent against First. A month qualifies when its Most_Recent value reflects the annual benchmark, which means months up to and including March of the year before the file's last update year. Exceeds when |Most_Recent minus First| is greater than 122.
Each is reported as the share of months exceeding with a Wilson 95% interval. Also reported, descriptive and without outcome: the median and the mean of signed revisions (later minus first, in thousands), and the median absolute revision.
Outcome per count against the claim read, which expects an exceedance share of about 0.10 if the stated interval described the revision: ABOVE if the lower end is above 0.10, BELOW if the upper end is below 0.10, CONSISTENT if 0.10 lies inside the interval and its width is 0.12 or less, otherwise CANNOT_TELL.

## What this is and is not
The stated interval is a statement about sampling error of the first estimate against the true change. A revision to a later release also contains late reports and, for the benchmark count, non-sampling error, and the later value has its own error. So the count says how often the first estimate was later moved by more than the interval the agency states. It is not a test of the agency's sampling theory, and it does not say the interval is wrong. The stated figure is today's. Earlier statements may have been different, and the same figure is applied to every month. That choice is defined here, before the data are counted.

## Known-good
Before each read: planted series with revisions of exactly 122, 123 and -123 must count 0, 1 and 1 exceedances; the Wilson interval is the kit's. The file must say Variable ID EMPLOY and the unit thousands. The Most_Recent column for the last 24 qualifying months must match the month-over-month changes of the BLS public API's current level series CES0000000001 to within 1 thousand in every month. A failure stops the pass.

## Hand check (fixed now)
Every month in either count with a revision above 300 thousand is opened by hand against the file's row and the BLS value, before it is listed.

## Not claimed
That the agency's number is wrong. That a later number is truer. Anything about markets, rates or what a number means for any price.

## Note 1 (29 Oct, hand check of the first read, before anything was shown)
Four months have a revision above 300 thousand (March 2020, August, November and December 2021). The first-release value of each in the file was read against the archived Employment Situation release for that month (through the Internet Archive, since bls.gov refuses automated requests): fell by 701,000, rose by 235,000, rose by 210,000, rose by 199,000. All four match the file's First column. The file's Most_Recent column matched the BLS API's current month-over-month changes to within 0 thousand in all 14 months the API returned. The third-release count window includes March to May 2020, as the plan's 120 most recent months require. No rule changed.

## Note 2 (29 Oct, from the internal audit)
1. Dependence. Consecutive months are not independent: the benchmark count shares one revision across each year and the third-release windows overlap. The Wilson interval treats 120 months as 120 independent units. A second interval is added and shown beside it, from a bootstrap over calendar years (4,000 resamples, seed 7). The outcome keeps the fixed rule on the Wilson interval, and the interval over years is shown so the two can be read together. Defined after the first read.
2. Known-good. The plan asked for 24 months of Most_Recent to match the BLS API. The public API without a key returns 14 months, and 14 matched. The code accepts 12 or more. The plan is amended to say so.
3. Hand check. Every large month used to print the same note that its first print matches the archived release, though only four months had been opened. The note is now read from data/hand_checked.json, and a month not in it reads Not yet opened by hand.
4. The stated 122 was read from the BLS note on 29 Oct and is a constant in the code. If the BLS changes its figure the page will not see it. It is shown with its read date at the top of the page.


## Addendum on cadence (29 Oct)
The repeat cadence is now every 36 ticks of the tick bus, about 3.5 hours, so that a change at the source shows within hours. The earlier cadence was a default chosen when the corner was built. Nothing else changes; each pass keeps the same read, the same politeness pauses and the same known-good checks.

## Note 3 (30 Oct 2026, from the site pass)
The outcome keeps the fixed rule on the interval over months. Beside the interval over calendar years the page now shows the outcome the same rule gives for it (above if the lower end is above 0.10, below if the upper end is below 0.10, consistent if 0.10 is inside and the interval is no wider than 0.12, otherwise cannot tell). It is descriptive and was defined after the first read. At the 30 Oct read it gives cannot tell for both counts, where the interval over months gives consistent for the third release and above for the benchmarked value. The months in the table of large revisions link to the Philadelphia Fed file. No rule changed.

## Addendum 1 (9 Nov 2026, source)
The Philadelphia Fed's pages carry no reuse terms, only "All rights reserved". The BLS publishes the same estimates itself, in the public domain, so from this date every value is read from the BLS: the first, second and third over-the-month estimates of total nonfarm employment, seasonally adjusted, from the BLS table "Nonfarm Payroll Employment: Revisions between over-the-month estimates, 1979-present" (bls.gov/web/empsit/cesnaicsrev.htm), and the most recent value from the month-over-month change of the BLS level series CES0000000001, read from the BLS flat file ce.data.00a.TotalNonfarm.Employment (download.bls.gov), the same series the known-good used to read through the API, which allows only 25 keyless requests a day. The reader is bls_source.py. A copy of the BLS table is kept in data/files for every read, with its SHA-256. The benchmark cutoff is set from the table's own "Last Modified Date". The counts, the stated 122 thousand, the windows of 120 months and the outcome rule are unchanged.
Known-good from this date: the table's first estimates for the four months opened by hand in Note 1 (March 2020, August, November and December 2021) must match the archived releases (-701, 235, 210 and 199 thousand), the table must hold at least 500 months, and the flat file must give the current change for every month of the last ten years. The old check of the Philadelphia Fed file's Most_Recent column against the API no longer applies, since the most recent value now comes from the BLS series itself.
Before the switch the two sources were compared month by month (9 Nov 2026, Philadelphia Fed file of 5 October 2026 against the BLS table of 6 November 2026). The first estimates match in 570 of 571 shared months, the second in 567 of 569 and the third in 555 of 567. In the windows that are counted, two values differ: April 2020 (first estimate -20,500 in the file, -20,537 in the BLS table) and February 2020 (third estimate 230 against 251). The second estimate, which is not counted, differs in August 1996 and March 2020. The other third estimates that differ are from 1981 to 2003, outside the windows. The most recent values match within 1 thousand in all 120 benchmarked months. The BLS table also holds third estimates the file lacks (July to September 2025, August 2026), so the third-release window moves from April 2016 to July 2026 to August 2016 to August 2026. Both sources give 13 of 120 months moved by more than 122 thousand at the third release, and 25 of 120 after the benchmark.
