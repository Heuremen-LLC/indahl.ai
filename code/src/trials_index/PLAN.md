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

## Addendum 3 (29 Oct, before the cancelled-trials read): two years of stopped trials
New block, same page, same registry. Population: interventional studies with a start date from 2024-10-29 to 2026-10-29 (the start date can be anticipated for a withdrawn study). Denominator: all of them. Stopped: overall status WITHDRAWN, TERMINATED or SUSPENDED. Counts are by sponsor class and phase, with the share of the population, and a cohort table by start quarter. The cohort table is descriptive: a recent quarter has had less time to be stopped, so shares are not compared across quarters.
Reasons: the whyStopped text of each stopped record, sorted by first match into funding or sponsor decision (funding, funder, financial, budget, business, strategic, sponsor, portfolio, priorit, commercial), recruitment (enrol, enroll, recruit, accrual, participants, feasib), safety or efficacy (safety, adverse, toxic, futility, efficacy, benefit), regulatory or supply (regulat, FDA, approval, supply, drug availability, manufactur), investigator or site (investigator, PI left, site, staff, moved), completed or other (anything else with text), and BLANK (no text). Descriptive, no outcome. The words were fixed before the read.
Two tests against the registry's own rules, outcome rule as above (ABOVE if the lower end of the Wilson interval is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL, fewer than 30 records CANNOT_TELL):
1. The registry asks for a reason for every withdrawn, terminated or suspended study. Share of stopped records with a blank whyStopped.
2. A withdrawn study is one that enrolled no participants. Share of WITHDRAWN records whose enrollment count is above zero.
Every record read as failing a test is checked against its public page by hand for a sample of ten before the share is shown, and the ten are listed with what the page says. Known-good: NCT05935592 (terminated, reason stated, 40 enrolled) must read terminated with a reason; the count query for the population must match the API's totalCount.

## Addendum 4 (29 Oct, from the internal audit, after seeing the first read)
The reasons block of addendum 3 sorted free text into five classes and a bin called Other text that held 31 percent of the stopped records. A bin with no positive definition is where several different reasons hide, and the audit refused it. Sampling 28 of its 523 texts by hand showed reasons that fit definable classes. Defined after seeing the data and labelled so: six classes are added after the original five, tried in this order after them (so no record already in a class moves): never started or never approved (never start, not start, never initiat, not initiat, never approved, not approved, no participants, never opened), registration replaced or withdrawn (registration, registered, duplicate, ISRCTN, another registry), pandemic or logistics (covid, pandemic, logistic), sponsor or partner decided (partner, company, collaborator, decided, decision, discontinu, no longer, not to pursue, not proceed), resources or staff (resource, staff, personnel, faculty, human, lack of, insurance, unable to provide, fund and funds), and design or outcome changed (design, protocol, outcome measure, standard of care, inapplicab, amend). A record that matches none of the words is shown as Matches none of the words, with its count, and the unmatched texts are published in data/unmatched_reasons.txt so anyone can read them. The tests of addendum 3 are unchanged.


## Note (29 Oct, from the internal audit)
This plan did not state its unit and what it does not claim in one place. Stated now, with no change to any rule, read or outcome. Unit: one registry record. Not claimed: that a record with no results on it breaks the law, since certified delays are not in the registry data, that a sponsor complies or does not, that a stopped study is at fault, or any ranking of sponsors.

## Note 6 (29 Oct, from the internal audit)
The plan's known-good records were never run by the tick. The tick now reads NCT03515551 (results posted) and NCT04537429 (no results) from the registry before publishing, and publishes nothing if either reads otherwise. Stated and not fixed: the intervals treat the records as independent although sponsors and programs cluster, so the widths on the share with no results are narrower than the units justify. CANNOT_TELL labels both an unresolved group and a resolved 21.9 percent share that falls between the thresholds, and the page says which.

## Correction (30 Oct 2026, site pass H-14)
1. The collector ends the window at the last day of the month 14 months before the read month (31 Aug 2025 for a read in October 2026), so every record is at least 13 months past its primary completion date. The page said 13 months ago and now says 14 months before the read.
2. Addendum 3 says ten records of the first stopped-trial test are opened by hand and listed with what the page says. That was not done before the first read. It was done on 30 Oct 2026: ten were drawn once (seed 7, sorted ids, data/hand_sample.json), each was opened on its registry record, and the notes are in data/hand_checked.json and listed on the page. All ten were records of one lead sponsor, and 24 of the 25 records of the test have that sponsor, which the page now says.
3. Note 6 says the page states which kind of cannot tell a row is. The page now writes in the Outcome cell whether the whole interval sits between the two thresholds, the interval reaches a threshold, or there are fewer than 30 records. Addendum 4 says the six added reason classes are labelled as defined after the data, and the page now labels them. The rule of the two stopped-trial tests (above when the lower end is over 10 percent, consistent when the upper end is under 5 percent) and the independence note are printed on the page. No rule or threshold changed.

## Addendum 5 (10 Nov 2026, from our newsletter audit, after the data)
1. The floor in the Rule section was never built. Records with primary completion 13 to 15 months before the read are the lag zone and are not scored, but trials_summary.py said the query end left none, and the query ends about 13 months back. On the 10 Nov read, 395 records sat in the lag zone and were scored, 244 of them with no results. The floor is built now: a record whose primary completion date falls after the read date minus 15 months is shown apart as the lag zone and not scored. On the same read the share with no results moves from 5,019 of 22,580 (22.2 percent, Wilson 21.7 to 22.8) to 4,775 of 22,185 (21.5 percent, Wilson 21.0 to 22.1). The 2025 completion year moves from 890 of 2,007 (44 percent) to 646 of 1,612 (40 percent). No threshold or outcome rule changed, and the headline outcome stays CANNOT_TELL.
2. Note 6 says the intervals treat records as independent although sponsors cluster. Beside the plan's Wilson interval the page now prints a sponsor-clustered interval for the headline share (ratio estimator, cluster-robust standard error, lead sponsors as units). It was defined on 10 Nov 2026, after the data, and is labelled so. The outcome is still read on the plan's Wilson interval. On the 10 Nov read the clustered interval is 19.6 to 23.5 percent, which also sits between the two thresholds.
3. The registry class OTHER_GOV covers state, local and non-US public bodies. In this set it is mostly public universities and hospitals outside the US. The page names the class that way and never as government sponsors in general. Its row now shows how many distinct sponsors stand behind its records, since a few sponsors hold many of them.
