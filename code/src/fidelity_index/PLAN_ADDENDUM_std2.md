# FIDELITY: plan addendum for Faults and Guards 2.0, 12 November 2026

This addendum is written before any reading under the new outcome rule. PLAN.md is not edited and its seal is unchanged. The data, the sources, the ACS conversion, the known-good gates and the row rule are unchanged. Only the way a cannot tell is named and the counts printed beside the headline change. Outcomes recorded on 11 November stand under the rules the plan named.

## Rows are exact reads
A row compares one published NCHS count with one published ACS interval, the women's estimate plus and minus its published 90 percent margin, lower end not below zero. There is no sampling in that read, because the count is a published value and the interval is the published margin as published. Under owner decision O1 it is an interval of zero width and is read with heuremen_kit read_exact against the band from the lower end to the upper end, edges included as in PLAN.md. Inside is CONSISTENT, above is ABOVE, below is BELOW. No resampling, so no draws and no seed. The 95 percent scale and the men's estimate stay displays and score nothing.

## How the desk's own causes of CANNOT_TELL map
Each cause gives CANNOT_TELL with reason NO_INTERVAL_FORMABLE, because no value or no interval exists to be compared. The plain cause is kept beside the code.
- State does not report: no stated count exists.
- No stated count, the 2024 rows: NCHS publishes rates only, so no stated count exists.
- No ACS interval: the margin is missing or coded.
- Gate failed: a known-good gate failed, so no row is read.

## The jurisdiction and year labels
The plan labels a jurisdiction, a year or an event as above, below or inside when at least 5 of its rows are scored and one outcome holds at least 80 percent of them, and as mixed otherwise. That label is a plain summary of how the exact row reads fall. It carries no interval and it is not a share read against a figure, and it stays as the plan wrote it. The counts beside it are the reading. A label over fewer than 5 scored rows is below the desk's minimum sample, so it reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE under owner decision O3. A label over no scored row reads CANNOT_TELL with reason NO_INTERVAL_FORMABLE.

## Failed reads and the counts beside the headline
A failed fetch or parse of a source is NOTHING_RETURNED, a status of the read, listed apart and outside every count. The desk reads copied files, and a failed read stops a gate, so the count of failed reads is zero when the gates pass. The headline is Texas divorces read below under both sexes. Beside it the page prints the REQ-13 line for the Texas divorce rows: the NOTHING_RETURNED count, then the CANNOT_TELL share split by reason.

## What flips
No outcome of any row flips and no count moves. The cannot tell rows now carry the reason NO_INTERVAL_FORMABLE. The labels over fewer than 5 scored rows carry TOO_WIDE_TO_RESOLVE or NO_INTERVAL_FORMABLE on the page.
