# BLUESKY LABELS: stated label counts against the signed label stream. Plan, written before any count of 2024 or 2025.

## Claim read
Bluesky's 2025 Transparency Report, published by Bluesky on 29 January 2026, read from Bluesky's own pages only:
- Overview: https://bsky.social/about/blog/01-29-2026-transparency-report-overview
- Full report: https://bsky.social/about/blog/01-29-2026-transparency-report-2025

Both pages were fetched on 10 November 2026 (UTC) and kept as fetched in data/source/ with SHA-256 sums. Every stated figure used here is quoted verbatim in data/stated.json, and each quote was checked as an exact substring of the fetched text. Press coverage is not a source.

Stated figures read against the stream (the rows):
1. Labels applied in 2025: 16.49M. Labels applied in 2024: 5.5M.
2. Labels applied in 2025 by value, from the report's "Top Labels" table: adult 10.79M, suggestive 3.42M, spam 761.77K, nudity 389.44K, needs-review 370.14K, rude 295.38K, sexual-figurative 152.58K, graphic-media 127.46K, !hide 68.26K, intolerant 60.20K, self-harm 20.92K, threat 15.86K.
3. "14.2M labels for adult content detection alone".
4. "In 96.57% of cases, we label specific content rather than marking entire accounts."
5. Content-level shares: intolerance 98%, threat 100%, rude 99%. needs-review "works exclusively at the account level".
6. Takedowns: 2,446,334 items removed in 2025. Account takedowns 1.02M in 2024 and 2.08M in 2025. Temporary suspensions 13,192 in 2025.
7. Read but not measurable from the stream: 95.34% of labels from automated systems, the "% Applied Manually" column, and 9.97M user reports.

## Data
Delivered: wss://mod.bsky.app/xrpc/com.atproto.label.subscribeLabels?cursor=0, the label stream of Bluesky's moderation service (did:plc:ar7c4by46qjdydhdevvrndac, moderation.bsky.app). No key. The user agent names this site. Read only.

Schema read on 10 Nov 2026 (first 3,036 sequence numbers, 13 to 29 April 2023, outside every counted year): one label per frame, body {seq, labels}, label fields ver, src, uri, cid (optional), val, neg (present only when true), cts, sig. Every label in the read carried ver 1 and a signature. 3,000 frames over 3,036 sequence numbers, so 36 sequence numbers were not served. The live head at 10 Nov 2026 01:53 UTC was seq 45,765,596.

How the stream keeps history. Bluesky's published Ozone source (github.com/bluesky-social/atproto, main branch, read 10 Nov 2026, copies in data/source/) writes every label with an insert that, on conflict on (src, uri, cid, val), sets id to the new sequence value and overwrites neg, cts, exp and sig. A negation, or the same label applied again to the same subject, therefore moves the row to a new sequence number. A replay from cursor 0 serves one row per (src, uri, cid, val) at the sequence number of its latest write. Earlier writes of that row are not served and leave gaps. Each frame is {seq: row id, labels: [one label]}. Labels without a current signature are signed when served. The server limits replay to 2,000 events per second by default, shared by all subscribers.

Store: data/labels.sqlite (git-ignored, never published, holds subject identifiers). One row per frame: seq, subject DID (interned), collection (0 for an account-level label), record key, an 8-byte hash of the cid (0 when absent), value, neg, cts and exp in milliseconds UTC, src, ver, signature present. Raw signed label bytes are kept for the signature sample. Each run resumes from the highest stored seq. A frame for a (src, uri, cid, val) already stored at a lower seq marks the older row superseded. Superseded rows are kept and flagged, so writes we read before they were overwritten stay in our record. The counting rules below use served rows only (superseded rows excluded), so a count reproduces what a fresh replay serves.

## Counting rules (fixed here, before any count of 2024 or 2025)
Label: a served row whose src is the moderation service DID. Rows with another src are counted apart and not used.
Value scope of the label totals: every value except !takedown and !suspend. The report counts takedowns apart from labels, and its own top-labels table (12 values) sums to 16.47M of the 16.49M total, which leaves no room for takedown labels. The two takedown values are used only in the takedown rows.
Stated names matched to stream values by exact name, with two exceptions: adult is porn and suggestive is sexual. The labeler declares no value named adult or suggestive. The Bluesky app shows porn as "Adult Content" and sexual as "Sexually Suggestive" (social-app src/lib/moderation/useGlobalLabelStrings.ts, copy in data/source/). Any served value literally named adult or suggestive is added to those rows. Other values the app shows under the same name (gore is also shown as "Graphic Media") are reported beside the row and not added.
Adult content detection (14.2M): porn plus sexual. The report does not name the values. Its own adult and suggestive rows sum to 14.21M. This definition is taken from the stated side, before our count.
Account-level: uri starts with did:. Content-level: uri starts with at:// (any collection, profile records included). Other uri forms are counted apart.
Expired labels (exp in the past) count as applied. Their number is reported.
Years: UTC calendar year first. Alternative: US Pacific calendar year, 1 January 08:00 UTC to the next 1 January 08:00 UTC.
Time of a row: cts first. Alternative: sequence position. Served rows in seq order are cut into blocks of 1,000. A row is in order when its cts is within 24 hours of its block's median cts. S(t) is the smallest seq among in-order rows with cts at or after t. A row falls in year Y by sequence position when S(Y start) <= seq < S(next year start). The number of out-of-order rows is reported.
Unserved sequence numbers of a year: G(Y) = S(next year start) - S(Y start) - (served rows of any value with seq in that range). These are writes of year Y that the replay no longer serves (overwritten or deleted). Their values are unknown.

Readings, each an exact count, for a value set V and year Y:
- R1 standing now, by cts, UTC year (printed first): served rows with val in V, no neg, cts in Y.
- R2 as R1 with the US Pacific year.
- R3 as R1 by sequence position.
- R4 every served row dated in Y: R1 plus served negation rows of V with cts in Y.
- R5 same-year net: R1 plus served negation rows of V with cts after Y, each credited with one application in Y. A negation of a record whose key is a timestamp identifier (TID) dated after Y is not credited, since that record did not exist in Y.
- R6 distinct subject and value: R1 with rows that share uri and value (different cid) counted once.
- R7 upper reading: R3 plus G(Y), every unserved sequence number of the year credited to V. Writes of V in Y cannot exceed it unless the sequence skipped numbers, which only makes it looser.
The delivered interval is the minimum to the maximum of R1 to R7. It is the spread across counting rules, not a sampling interval. Counts are exact.
Shares (content against account): each reading's share. R7 gives two shares, with every unserved write counted as account-level and as content-level. The interval is the minimum to the maximum.

Stated range: the printed figure's rounding range. 16.49M is 16,485,000 to 16,495,000. 98% is 97.5% to 98.5%. "Exclusively" is exactly 100%. An exact integer is itself.
Outcome, the shared kit's classify: ABOVE when the whole delivered interval is above the stated range (the stream holds more than stated). BELOW when the whole interval is below it. CONSISTENT when the whole interval lies inside it. CANNOT_TELL otherwise. NOTHING_RETURNED when R1 to R6 are all zero.
Wider scope: takedowns and suspensions can be carried out on Bluesky's servers outside this label stream, so the stated figure may cover more than the stream. For those rows only ABOVE is read (a wider figure cannot be smaller than the stream if both are right). Otherwise the row is CANNOT_TELL with that reason.
Not in the stream: the stream does not record whether a person or a system applied a label, and it carries no reports. Those rows are CANNOT_TELL with the reason.
Takedown rows: items are served !takedown rows (any uri). Account takedowns are served !takedown rows on did: uris. Temporary suspensions are served !suspend rows. Same readings R1 to R7.
Every row also shows whether the stated figure lies inside the interval (agreement within the rule spread), the gap of R1 against the stated figure, and the gap interval.

## Signature check
A deterministic random sample: a served row is sampled when the first 4 bytes of BLAKE2b-8 of its seq, read as an integer, fall below 2^32 / 1000 (about 1 row in 1,000, spread over the whole stream). For each sampled label: DAG-CBOR encoding of the label without sig (ver kept), SHA-256, ECDSA on secp256k1 against the #atproto_label key in the labeler's DID document (did:key:zQ3shmV1BNcX17coaDbfen6zArEad6SCLT3jVWCbC6Y9iinTa, present in the PLC log since 5 March 2024, never rotated). The low-S rule of atproto is checked and reported apart. A failure is retried against every other key in the PLC audit log. Reported: sample size, pass count and share, low-S count, unsigned count.
Known-good before reading the sample: one sampled label passes, the same label with one byte of its value changed fails, and five sampled labels are also checked with OpenSSL's ECDSA (an independent implementation). If the known-good fails, the signature result is CANNOT_TELL.

## Known-good for the counter
Before the first count: (a) a planted world of synthetic rows with known applications, negations, overwrites, re-labels, timezone edges and gaps is run through the counting code and must return the planted value for every reading. (b) Within each connection seq is strictly increasing, and stored rows equal frames received. (c) Re-encoding of every sampled label reproduces the bytes as received (canonical DAG-CBOR). If (a) fails, every outcome is CANNOT_TELL.

## Live series
Served rows per UTC day by cts from the first row, applications and negations apart, and sequence numbers used per day, S(next day) - S(day). The latest full UTC day and the partial current day are marked. A past day's served count can fall later, since a label negated or applied again moves to the day of the new write. Our store keeps what we read before it moved.

## Rerun
bsky_tick.py is incremental from the highest stored seq. It installs no timer. It stops at the live head: when a frame dated within 60 seconds of the present arrives, or after 30 seconds without a frame once within 10 minutes of the present. A dropped connection resumes from the highest stored seq.

## Addendum 1 (10 Nov 2026, 02:09 UTC, before any count of 2024 or 2025, replay under way)
1. The in-order test changes from blocks of 1,000 rows to a rolling window. The schema read shows about 190 labels a day in April 2023, so a block of 1,000 rows there spans about five days and its median sits days away from most of its rows. A row is now in order when its cts is within 24 hours of the median cts of the 21 served rows centred on it in seq order (fewer at the two ends of the stream). Nothing else in the sequence-position rule changes.
2. Known-good (a) was run before the replay: the counting code returned exactly what a separate, slow implementation of the same rules returned for every reading on a planted world of about 54,000 writes with overwrites, negations, re-labels, sequence skips, backdated rows, another src and takedown values, and the planted gross count fell inside R3 to R7 for every value. Timezone edges read 32 rows in the UTC year and 33 in the Pacific year, as planted. The signature known-good passed on a 30,000-frame smoke read (36 sampled labels passed, one changed byte failed, OpenSSL agreed).
3. A frame or label that cannot be decoded is skipped and logged with its seq, not retried, so one bad frame cannot stall the replay. The number skipped is reported.
