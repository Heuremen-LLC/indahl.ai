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
