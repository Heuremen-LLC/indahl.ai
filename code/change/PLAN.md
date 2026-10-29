# CHANGE: the shutdown dates vendors announce, kept over time. Plan, written before the first snapshot is read.

## Claim read
A vendor's deprecation page states a date when a model, API or feature stops working, and often the date it was deprecated. Stated: this thing ends on this date. Record: the same page, read again and again. A date that holds, a date that moves, and a row that disappears are all visible without any account.

## Sources (fixed now)
Anthropic: the model deprecations page on platform.claude.com (the table of API model names with Deprecated and Tentative retirement date columns, and the dated tables of retirements). OpenAI: the deprecations page on developers.openai.com (tables of shutdown date, model or system, replacement). Google: the Gemini API deprecations page on ai.google.dev (table of model, release date, shutdown date, replacement). Cloudflare: developers.cloudflare.com/deprecations (each entry gives a deprecation date and an end of life date). Open weight models are not covered by a vendor shutdown date and are not in this version.

## Read (fixed now)
Each source is fetched with a user agent naming this site, every 24 ticks of Nova's clock. Rows are parsed into: vendor, name, deprecation date (if stated), shutdown date (if stated), whether the shutdown is stated as "not sooner than" (a tentative earliest date, kept as a date with that flag), and the source URL. No date or "to be announced" stays empty. Every snapshot is saved whole, and every change between snapshots is a row in data/changes.jsonl with the time it was seen.
Row keys are vendor plus name. A change is one of: NEW (a row not in the previous snapshot), MOVED_LATER or MOVED_EARLIER (the shutdown date differs), REMOVED (a row no longer on the page), DATE_ADDED (an empty shutdown date got a value).

## What is reported
1. The next shutdowns in the following 60 days with days left, the deprecation date and the notice given (shutdown minus deprecation in days, when both are stated).
2. Notice given by vendor over current rows with both dates: the median, the shortest, and the share under 30 days. Descriptive.
3. Changes seen since the first snapshot, counted by kind and listed with both values. Descriptive.
4. The test. Unit: a row with a stated, non-tentative shutdown date that passes after the first snapshot was taken. HELD if the date never changed while we watched, MOVED if it changed at least once before it passed, REMOVED_EARLY if the row left the page before its date. The share not HELD with a Wilson 95% interval. Outcome against the claim that a stated date holds (zero not held): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 rows in the test: CANNOT_TELL, which is where this starts.

## Hand check (fixed now)
Every MOVED and REMOVED_EARLIER row is opened on the vendor's page by hand and the reason, if the page gives one, is written beside it before it is listed as a finding. A parse error is fixed by a dated addendum and the snapshot is read again.

## Known-good
Before each snapshot the parser is run on saved fixtures of each source and must return the row counts and three named rows it returned on the day the plan was written. A parser that returns fewer than 80% of the rows of the previous snapshot stops the pass and publishes nothing.

## Not claimed
That a vendor should give any notice. That a moved date is a fault: a later date can be a kindness and an earlier one a security response. That a model disappears when its date arrives: we read the announcement, not the service.

## Addendum 1 (29 Oct, after the first snapshot, before anything was shown)
The parser put Google's Release date column into the deprecation date field, so the first notice table counted lifespan as notice. Google's table states a release date and a shutdown date and no deprecation date. The release date is now kept as its own field. The notice table covers only rows that state a deprecation date (Anthropic and Cloudflare). A second descriptive table gives the stated lifespan for rows with a release date and a shutdown date (Google): the median in days, the shortest, and the share under 180 days. It carries no outcome. The first snapshot is discarded and read again. No rule of the test changed.

## Addendum 2 (29 Oct, from the internal audit)
1. The plan promised a fixture gate and a stop when the parser returns fewer than 80 percent of the previous rows. The code saved fixtures but did not check them, and after a stopped pass it still wrote the summary and published it, so a stale snapshot looked fresh. The gate is now run: every saved page must parse to at least the row count and contain the three named rows recorded in fixtures/EXPECTED.json (written on 29 Oct from the pages as they stand), or the pass stops. A stopped pass publishes nothing, and the page stamp is now the time of the last completed pass.
2. Stated and not fixed. The test counts only dates that pass after the first snapshot and keeps their last state, so a date pushed later again and again leaves the test while it keeps moving, which favours HELD. HELD also means unchanged while we watched, and rows are watched for between one and many days. REMOVED_EARLY merges a vendor withdrawal, a renamed row (the key is vendor and name) and a parser loss. The notice table shows Cloudflare only because Anthropic's table states no deprecation date for the rows read so far. The page already says the test fills as dates pass.
