# SUPPORT: stated support windows against release activity. Plan, written before any cycle is scored.

## Claim read
A vendor states how long each release cycle is supported (a support end date and an end-of-life date). Stated: the cycle is supported until then. Delivered: releases of that cycle keep coming while it is supported, and stop around the stated end.

## Data
endoflife.date, public (https://endoflife.date/api/all.json and /api/PRODUCT.json). Per cycle it records the vendor's stated support and end-of-life dates, the latest release of the cycle and its date. Its dates are collected by its maintainers from the vendors' own pages and release feeds. We take them as that source gives them and do not check them against the vendors.
One read of the product list and one request per product, one request per 0.7 seconds, user agent naming this site. Re-read every 7 days.

## Test (fixed now)
A cycle is SUPPORTED when its end-of-life date is in the future or none is stated, and its stated support end (if any) is not past. For a SUPPORTED cycle released more than 400 days ago, SILENT means its latest release is more than 365 days old at the read time.
Share SILENT = silent / SUPPORTED cycles tested, overall and by product, Wilson 95% interval.
Outcome against the claim that a supported cycle is still being released (zero silent): ABOVE if the lower end of the silent share is above 0.10. CONSISTENT if the upper end is below 0.05. Otherwise CANNOT_TELL. Fewer than 30 cycles tested: CANNOT_TELL. Thresholds fixed here.
Descriptive, no outcome: for cycles whose end of life has passed, where the last release falls against the stated date: before it, within 90 days after, 90 to 365 days after, more than a year after.
Cycles without a latest release date, and products with no cycle dates, are counted apart and not tested.

## Known-good
Before each pass, two cycles are read through the same code and must come out as follows. python 3.8: end of life passed and its last release is not after that date (stated 2024-10-07, last release 2024-09-06). python 3.15: SUPPORTED and not SILENT (released this year). If either reads differently from the endoflife.date record at the time of reading, the pass is not published and the page says the instrument failed its gate. The two values above were read by hand from the API on 29 Oct 2026 before this plan was committed.

## Not claimed
That a silent cycle is abandoned: some vendors release in other channels. That endoflife.date is complete or correct. Anything about the quality of support.

## Addendum 1 (29 Oct, after the first read, before anything was published)
The first read reported about half of the tested cycles SILENT, and the silent list began with Microsoft Exchange 4.0 (last release 1998) and Jira 1.0 (2002). In endoflife.date the eol field is a date, or the boolean true (the cycle has ended, no date given), or the boolean false (not ended, no date given). The code treated any value that was not a date string as "no end stated", so ended cycles with eol true were counted as SUPPORTED. The state EOL_NO_DATE is added: eol true. It is counted apart and not tested. eol false still means no end stated. The support field is read the same way: only a date string counts as a stated support end. No threshold, outcome rule or known-good changed. The first read's numbers were never shown anywhere; the page is built only after the corrected read has been hand checked.
