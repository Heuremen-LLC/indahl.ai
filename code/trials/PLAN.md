# TRIALS: results due vs results posted (ClinicalTrials.gov). Plan, written before any collection.

## Claim read
FDAAA 801 / 42 CFR 11: the responsible party of an applicable clinical trial submits results no later than 12 months
after the primary completion date (certified delay can extend it). Stated: results due within one year. Delivered: results posted on the record.

## Data
ClinicalTrials.gov API v2, public, read at collection time, one pass per run, page size 1000.
Query: StudyType INTERVENTIONAL, IsFDARegulatedDrug or IsFDARegulatedDevice true, primary completion date type ACTUAL,
primary completion from 2018-01-01 to the date 13 months before the read (one month of grace for posting lag), status COMPLETED or TERMINATED.
Fields: NCTId, LeadSponsorName, LeadSponsorClass, Phase, PrimaryCompletionDate, ResultsFirstPostDate, HasResults, DelayedPosting (certification).

## Why this is only a screen
Applicable-clinical-trial status is a legal call the registry does not store. The FDA-regulated flags plus interventional plus
actual date are the closest public proxy. Phase 1 drug trials are outside the law, so Phase 1 and Early Phase 1 drug-only records are excluded.
Device pilot/feasibility trials also fall outside and have no phase marker, so device-only records are reported apart from drug records.

## Rule (fixed now)
Per record: POSTED if HasResults true. NOT POSTED if false and no certified delay on the record. DELAY_CERTIFIED if the record
shows a delayed-posting field or a results-first-submit date with no post date (under QC review): both counted as CANNOT_TELL, never as late.
Per sponsor class (INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER) and per lead sponsor with at least 20 qualifying records:
share NOT POSTED with a Wilson 95% interval.
Outcome per group against the law (law says 100% posted after allowances): ABOVE means not-posted share lower bound above 0.25,
CONSISTENT means upper bound below 0.10, otherwise CANNOT_TELL. Thresholds are fixed here and not tuned after the read.
Floor: records with primary completion 13 to 15 months back are shown separately as the lag zone, not scored.
No sponsor ranking sentence, no adjectives. Sponsors are named as the registry names them, with counts and intervals.

## Known-good
Check the collector against 5 hand-picked records with known state read from their public pages before the full run.

## Tick bus
Rider every 24 ticks re-reads the totals by sponsor class (counts only, one API call per class) and publishes KV trials_live.
Full per-sponsor pass weekly (every 240 ticks).

## Addendum 1 (28 Oct, before any collection run)
The v2 API has no delayed-posting or certification field. Checked on a 2-record probe: only resultsFirstSubmitDate, resultsFirstSubmitQcDate,
resultsFirstPostDateStruct and hasResults exist. So a record with no results can be a missed deadline or a certified delay and the registry does not say which.
Changes: the label NOT POSTED reads "no results on the record". DELAY_CERTIFIED is dropped. A record with a submit date and no post date is IN_REVIEW (CANNOT_TELL, not counted either way).
The outcome rule per group is unchanged but is read as "share with no results on the record", never as "late" or "in violation".
Qualifying set at probe time: 30,405 records before the Phase 1 drug-only exclusion.
Known-good: NCT03515551 (results posted 2022-03-11, Immunocore) must read POSTED; NCT04537429 (Lundbeck, completed 2022-10-20, no results) must read NO_RESULTS, and is excluded here as Phase 1 drug-only unless a device flag is set.

## Addendum 2 (28 Oct, before the rider's first run)
The full pass is 31 requests, so the rider re-reads the whole set every 48 ticks (about 5 hours) instead of the per-class counts and weekly pass written above. Same rule, same thresholds.
Lead sponsors classed INDIV are not listed by name. The sponsor table lists organisations only.
