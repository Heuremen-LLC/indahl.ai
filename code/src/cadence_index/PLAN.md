# CADENCE: stated update cadence against delivered (28 Oct 2026, his word)
Written and committed before any portal was read for this purpose.

## What is stated
Each dataset's own accrualPeriodicity in the portal's standard data.json (Project Open Data / DCAT): an ISO 8601 repeating interval such as R/P1D or R/P1M, or a word such as daily, weekly, monthly, quarterly, annually. Portals read: data.cms.gov, data.cdc.gov, healthdata.gov, data.va.gov, www.energy.gov, www.dol.gov, www.fema.gov, data.healthcare.gov and data.bls.gov. Each portal's data.json is fetched at most once every 24 hours on HST ticks, with our user agent naming this site. NASA's file is an aggregate of tens of thousands of records and is left out of this plan.

## Interval table (fixed here)
PT?M, PT?H, P?D, P?W, P?M (30 days), P?Y (365 days) as written; daily 1 day, weekly 7, biweekly 14, monthly 30, bimonthly 61, quarterly 91, semiannual 182, annually 365, biennial 730. irregular, continuously, as needed, never, unknown and anything not in the table are not read and are counted as CANNOT_TELL with the reason.

## What is delivered
The dataset's own modified date in the same data.json. Age is the time between the fetch and modified. Dates without a time are read as the end of that day UTC, and the interval used for any rule is at least two days so a date-only field cannot create a false miss.

## Per dataset outcome (fixed here)
CONSISTENT if the age is at most twice the stated interval. BELOW if the age is more than twice the interval, meaning delivered updates fall short of the stated cadence. CANNOT_TELL if the cadence is not in the table or the modified date is missing or unparseable. ABOVE is not assigned.

## Limits
modified is what the publisher reports. A dataset can be touched without new data, or updated in a place the field does not see. On a random sample of 200 datasets per portal that publish a download link, the file's own HTTP Last-Modified header is read with one HEAD request and the agreement with modified is published beside the main table. Datasets whose download needs a login or returns an error are counted, not dropped.

## Output
Per portal: datasets stating a readable cadence, the share BELOW with a Wilson 95% interval, and the same by cadence class (daily or faster, weekly, monthly, quarterly, yearly). The twenty datasets furthest past their stated cadence, by age divided by interval, each with agency, stated cadence, last modified date and link. A vendor-response path for each portal. No ranking of agencies.

## Addendum 1 (28 Oct, after the first portal read, before any outcome was published)
The first read of one portal (CMS) showed that it lists every historical release as its own record, with a date in the title and the same stated cadence, for example one record per weekly release. An archived release cannot be updated, so reading each as a dataset would count old snapshots as overdue. Records that share a landing page are therefore one series, and the series is read through its newest record: its modified date against its stated cadence. Records with no landing page are their own series. The counts of records and of series are both published. A series counts once. This was decided from the structure of the file, after seeing counts but before any outcome was read or shown.

## Addendum (29 Oct 2026, after publication): Wilson interval corrected
The local Wilson function in this corner omitted the division of the half-width by d = 1 + z squared over n, so published 95% intervals were wider than the Wilson interval this plan names (up to 38% wider at n = 10, about 5% at n = 100). It was found on a read of the code while moving corners onto the shared kit, whose function is tested against planted worlds. The corner now uses the kit function and the page was republished. No verdict changed: CADENCE outcomes use the age rule and not an interval; only the displayed share intervals changed (for example the CDC behind share interval was 18 to 34 percent and is now 19 to 33 percent; the CMS interval is unchanged at 7 to 17 percent after rounding).


## Note (29 Oct, from the internal audit)
This plan did not state its unit and what it does not claim in one place. Stated now, with no change to any rule, read or outcome. Unit: a dataset series on a portal that states a cadence. Not claimed: that a late modified date is a failure to inform, since a dataset can be touched without new data or updated where the field does not see, as the Limits section already says. No ranking of portals or agencies.

## Note 2 (29 Oct, from the internal audit)
1. The plan says age is the fetch time minus the modified date. The code used the current clock, with the fetch branch switched off, so every stored portal file grew older by itself between reads and a dataset could move from CONSISTENT to BELOW with no new read. The code now follows the plan: age is the portal file's fetch time minus modified.
2. The counts of why a series reads CANNOT_TELL are kept in each portal's output and are not dropped. FEMA is one of the nine portals the plan names and is not in the output, because its data.json could not be read on the first pass. That is stated here and on the page's source list.
3. Stated and not fixed: the verdicts use the publisher's own modified date from the same file as the cadence claim, and the side check against a second field agrees in only a small share on two portals. Series from one publisher are treated as independent in every Wilson interval, and two portals are dominated by bulk-stamped daily series. The modified-date sample draws records and not series.

## Note (30 Oct 2026, from the site pass)
The page now states the two-day floor on the interval and the date-only rule that this plan already fixed, and it states that the series rule was decided after the first portal read (Addendum 1). The column that was headed times its cadence is the age divided by the interval used, which is at least two days. Each landing page in the table of series furthest past their cadence is opened once a day with our user agent, and a 404 or 410 is marked beside the link. No rule changed.

## Addendum 2 (10 Nov 2026, from our newsletter audit, after the data)
Two parsing rules were never written down, and both were found after the counts had been published.
1. Decimal durations. ISO 8601 lets the last number of a duration carry a decimal. CMS states R/P3.5D on 1,426 records. The code accepted whole numbers only, so those records read CANNOT_TELL as a cadence not in the table, which made 4 CMS series unreadable. From 10 Nov a duration may carry a decimal number (a comma is read as a point), so R/P3.5D is 3.5 days. The two-day floor on the interval still applies.
2. Ties inside a series. Addendum 1 reads a series through its newest record. When several records share the landing page and the newest date and state different cadences, the code took whichever came first in the file. That decided at least one Veterans Affairs series, so a count could change with the order of the publisher's file. From 10 Nov such a series is read against the longest interval its newest records state, so it reads BELOW only when it is behind every cadence they state.
On the stored portal files of 10 Nov, the series behind their stated cadence across the eight portals read are 633 of 1,229 under these rules, against 633 of 1,219 under the rules the code ran until 10 Nov. Veterans Affairs monthly series read 60 of 60 behind, where the old rules gave 62 of 62. The page prints the old count beside the new one. The per-dataset rule, the interval table and the two-day floor are unchanged.
Note to Addendum 2 (10 Nov 2026, from our referee). The code's word list has long read annual, yearly, bi-weekly, semiannually and biennially, which the interval table above does not list. They are kept, since each names a regular interval the table already holds under another spelling. On the table's own words alone the readable count is 1,221 under the new rules and 1,211 under the old, and the behind count is 633 either way.
