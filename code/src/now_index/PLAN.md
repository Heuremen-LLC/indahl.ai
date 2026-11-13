# NOW (with FORTUNE): stated predictions against the record. Plan, written and committed before any entry was collected or read.

10 November 2026. Desk under HERMES at indahl.ai/predictions (the path /now is the site's live landing page, so the desk takes this path). Byline Wayfinder and Bones. Heuremen LLC.

## What is stated
A public prediction by a named person or organisation, or a public community forecast, that is dated, names an event that can be checked, and has a deadline. The prediction is the exact words, read from a primary source. A primary source is, in this order: the predictor's own text (a post, paper, letter, filing, press release, shareholder letter, book page or transcript the predictor's organisation published), a contemporaneous report that quotes the words (named outlet and date), or a platform's own record (a forecasting platform's API or page). The kind of source is stored with every entry and shown.

## What is delivered
The record at the deadline: a public, dated document that shows whether the named event happened by the deadline. Each reading names its evidence with a link and an archived copy.

## The log (append-only)
- data/log.jsonl. One JSON row per line. Kinds: entry, outcome, due, correction. Nothing is edited or deleted. A correction is a new row naming the entry id, the field, the new value and why. The newest correction of a field wins on the page, and every correction is shown.
- Every row carries a sequence number, the time it was written (UTC) and the sha256 of the previous row, so the rows form a chain. A changed or removed row breaks the chain and the page says so.
- Every time rows are appended, a copy of the log is stamped with OpenTimestamps (data/stamps/log_<first 16 hex of sha256>.jsonl and its .ots), the same tool and calendars ledger/stamps.py uses for releases. The tick-bus rider upgrades pending stamps. The stamp proves the log existed in that form no later than the Bitcoin block that confirms it.
- Every source and evidence URL is sent to the Internet Archive (Save Page Now, paced), and the capture URL is stored. Where a capture cannot be made, an existing capture is used and its date stored, or the entry says no capture was made.

## Every entry holds
id, who, who_kind (person / organisation / community forecast), the exact quote, source URL, source kind, archive URL, the date said, the deadline, the event in plain words, the resolution criterion written by us in plain words, the time the criterion was written, whether that time is before the deadline, the probability if one is stated (a number from 0 to 1, or a range kept as stated), and the topic (AI, energy, space, transport, technology, other).
A deadline given as a year means the end of that year (31 December, 23:59 UTC). "Within N years" from a dated statement means N years after that date. A deadline we cannot fix from the words means the entry is not logged in NOW (it can appear in FORTUNE).

## Readings
Binary claims (no probability stated): at the deadline each entry reads one of
- RIGHT: the record shows the event happened by the deadline, as the criterion states it.
- WRONG: the record shows it did not happen by the deadline.
- CANNOT_TELL: no public record decides the criterion, or the criterion's words do not fix a test the record can answer. The reason is stated.
A reading cites its evidence. A reading never names a cause and never judges the predictor.

Probability claims: each entry's event reads HAPPENED, DID_NOT_HAPPEN or CANNOT_TELL by the same rules. Calibration is read per source, never pooled across sources:
- Bins of stated probability: 0 to 0.1, then each tenth up to 0.9 to 1 (a value on a boundary goes to the higher bin, 1 goes to the top bin).
- Per bin: n entries read, mean stated probability, observed share that happened, Wilson 95 percent interval (heuremen_kit.wilson).
- Bin outcome: ABOVE if the whole interval lies above the mean stated probability (it happened more often than stated), BELOW if the whole interval lies below it, CONSISTENT if the mean stated probability is inside the interval, CANNOT_TELL while n is under 30.
- Brier score (mean of (stated minus result) squared, result 1 or 0) once 30 or more entries from a source have read HAPPENED or DID_NOT_HAPPEN. Beside it, the Brier score of stating the source's observed base rate for every entry, and the skill 1 minus the ratio, with a 95 percent interval from 2,000 bootstrap draws over entries (seed 20261110).

AI-risk probability statements ("p(doom)" and the like): logged only with the exact quote verified word for word from a primary source. They read CANNOT_TELL by design and the page says why in a plain sentence: one outcome cannot test a probability. They never enter a calibration bin.

## Sources read
1. Long Bets (longbets.org): every prediction and bet with a stated deadline. The quote is the prediction text as Long Bets prints it. Concluded bets keep Long Bets' published result beside our reading, and our reading is checked against the record.
2. On-record statements by executives, researchers and organisations with a date and a deadline (AI capability timelines, transport and autonomy, space, energy, technology adoption). Only words read in a primary source. Nothing is attributed from memory. A statement whose exact words cannot be found in a primary source is not logged.
3. Manifold (api.manifold.markets), a community forecasting platform. Two fixed sets:
   - Resolved set (gives calibration on day one). Binary markets in the topic with slug "ai" (checked before any market was read: it exists, named "AI"), resolved YES or NO (other resolutions are counted and not read), with at least 50 unique bettors, whose reference time falls from 1 January 2025 to 31 October 2026. The reference time is the earlier of the market's close time and its resolution time. The stated probability is the market probability 30 days before the reference time: the probability after the last bet placed before that moment. A market created less than 30 days before its reference time, or with no bet before that moment, is counted and not read. The event is the market question as written, and the market's own resolution is the record. Our criterion for each is: the market resolves as its creator resolves it under the market's own description.
   - Open set (logged today, read at the deadline). Binary markets in the same topic, open on 10 November 2026, with at least 50 unique bettors and a close time from 17 November 2026 to 31 December 2027. The stated probability is the market probability when we read it, with the time read. At the deadline the rider reads the market's resolution. A market not resolved 30 days after its close reads CANNOT_TELL (not resolved).
4. Metaculus is not read: its API answers only to an account token (checked 10 November 2026). Metaculus questions may be logged as on-record statements by their page text if a later addendum says so.

## Day-one outcomes
Entries whose deadline has already passed are logged with their reading. For these the criterion is written after the deadline, from the quote alone, and the entry says so (criterion_before_deadline false). They are counted apart from entries whose criterion was written before the deadline.

## FORTUNE (history)
Famous historical predictions, read in two steps.
1. Was it said? One of: SAID (the words are in a primary source, earliest found given), SAID_DIFFERENTLY (a primary source has a statement the popular version alters, both given), NO_PRIMARY_SOURCE_FOUND (the earliest source found is given with its date, and its distance from the claimed date), CONTRADICTED (a primary source by the same person says otherwise).
2. For SAID entries with a deadline or a checkable claim: how it landed, RIGHT / WRONG / CANNOT_TELL with the record. Entries with no deadline say "no deadline stated" and are not scored.
Nostradamus has one entry: not scoreable, because the verses give no date, no named event and no probability. Stated plainly, with no adjective.

## Rider (tick bus, about daily)
now_tick.py --publish: reads the log, finds entries whose deadline has passed and that have no outcome row, writes outcome rows for Manifold entries from the platform's resolution, writes one due row for any other entry until a reading with evidence is added, verifies the chain, stamps the log when rows were appended, upgrades pending stamps, rebuilds the summary and puts it in the site KV for /predictions/live.json.

## Known limits, stated up front
- The entries are those we found. They are not a random sample of predictions, and the share RIGHT says nothing about predictions in general.
- Long Bets entries are predictions people chose to put on the record, often with a stake.
- A Manifold market's probability is a price set by traders. It is read as a stated probability. Markets in one topic are not independent.
- A criterion written after the deadline is labelled as such everywhere it is shown.

## Not claimed
No ranking of people. No claim about any predictor's skill from one entry. No cause is named for any reading.
