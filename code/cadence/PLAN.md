# CADENCE: stated update cadence against delivered (28 Oct 2026, his word)
Written and committed before any portal was read for this purpose.

## What is stated
Each dataset's own accrualPeriodicity in the portal's standard data.json (Project Open Data / DCAT): an ISO 8601 repeating interval such as R/P1D or R/P1M, or a word such as daily, weekly, monthly, quarterly, annually. Portals read: data.cms.gov, data.cdc.gov, healthdata.gov, data.va.gov, www.energy.gov, www.dol.gov, www.fema.gov, data.healthcare.gov and data.bls.gov. Each portal's data.json is fetched at most once every 24 hours on Nova's ticks, with our user agent naming this site. NASA's file is an aggregate of tens of thousands of records and is left out of this plan.

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
