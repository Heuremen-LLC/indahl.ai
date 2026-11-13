# Referee report: Bluesky section (stated label counts against the signed label stream)

Referee: read-only refuting pass, 10 November 2026 UTC. After the replay was completed (step 1 below), nothing in `social_index/bluesky/` was edited.
Inputs read: PLAN.md with Addendum 1, git history and the uncommitted diff of bsky_tick.py, heuremen_kit.py, data/stated.json, data/source/ (both report pages, SHA256SUMS, the Ozone and social-app copies), data/labels.sqlite (complete replay), data/bsky.json, summary_bluesky.json, section_bluesky.html, data/tick.log, data/replay_run1.log, data/replay_run2.log.

The referee's code is in `bluesky_referee/code/`. It is independent of bsky_tick.py and heuremen_kit.py, and neither is imported.
- `recount.py` works out which rows are served from the stored keys themselves (the highest seq per src, uri, cid, val), without using the desk's `sup` flag. It then rebuilds R1 to R7, the in-order test, S(t), G(Y), every share, the classification, the expiry counts and the daily series. Output: `code/out/recount.json`.
- `wire_check.py` is the referee's own websocket client, CBOR decoder, canonical DAG-CBOR encoder and secp256k1 ECDSA, written in pure Python. It reads slices of the live stream and compares every served frame, field by field, with the row the desk stored. Outputs: `code/out/wire_check_pre.json` and `code/out/wire_check_post.json`.
- `quotes_check.py` checks that every stated quote is an exact substring of the fetched source and that every source file matches SHA256SUMS.
- `html_check.py` checks every table cell on the page against the recount, and runs the copy-rule scan.
- `seq_used_check.py` checks the per-day "sequence numbers used" column.

## Step 1: replay completeness

PLAN.md commits to a replay from cursor 0 to the live head ("It stops at the live head"). The 2025 readings need the full year, the US Pacific year up to 1 January 2026 08:00 UTC, S(2026 start), and every negation dated after the year (R5). All of these need the stream read to the present.

State after the reboot. There was one run, with `runs.ended` NULL and `stop` NULL. The last stored seq was 24,946,605 (cts about 28 November 2025), with 24,076,519 rows stored, equal to frames received. `PRAGMA quick_check` returned ok, the odd table was empty and there were no superseded rows. About 20.8M sequence numbers short of the head (45,765,596 at 01:53 UTC) were missing. That covers December 2025, so 2025 was incomplete, along with the Pacific-year edge, S(2026) and every 2026 negation used by R5.

Rerun. First, backups: summary_bluesky.json, section_bluesky.html, data/bsky.json, data/did_doc.json, data/did_audit.json and data/labels.sqlite (after a WAL checkpoint), each to `*.bak-20261110-reboot`. Then `python3 bsky_tick.py` from the desk folder, which is the desk's own incremental resume from the highest stored seq, unchanged. Log: data/replay_run2.log. The planted world passed again. Run 2 read 18,830,106 frames with 0 reconnects and `stop: live head`. Last seq 45,785,475. The full-store superseded pass (it triggers on a broken earlier run) marked 7 rows. Frames received equal rows stored at 42,906,625, with 0 odd frames. The signature sample was 42,743 checked and 42,743 passed, with the known-good passed. The same run rebuilt bsky.json, summary_bluesky.json and section_bluesky.html at 10 Nov 2026 12:20 UTC. No rule, code or window was changed.

One note: the desk ran with the bsky_tick.py on disk, which carries an uncommitted diff over commit 0135cc4 (the `BESIDE` notes and a longer bench-note). That diff changes no rule (see B2).

## Verdict

**FIX THEN SHIP.** Every number and outcome reproduces from raw. The stream as stored matches the live wire field by field, and every signature the referee checked verifies with the referee's own ECDSA. Outcomes are CANNOT_TELL 25 and BELOW 1, the same on both sides. The four outcomes are kept apart. On the page, 25 of 26 table rows match the referee exactly. The one difference is the upper edge of one interval, by 3 labels, and comes from a documented judgment call (N1). Two blocking items remain, and neither changes a number:

- **B1. The data link on the page has no publish entry.** The page says "quoted with its source line in bluesky.json" and links `/social/bluesky.json`. SHIP_PLAN.md §3 adds copies.json entries for DSA and ad spend only, so the link would be dead. Fix: add to `ledger/copies.json` (backup first, as SHIP_PLAN §3 says)
  `"social-bluesky-rows": {"canonical": "social_index/bluesky/data/bsky.json", "copies": ["cloudflare-workers/heuremen-door/public/social/bluesky.json"], "live": ["https://indahl.ai/social/bluesky.json"], "_note": "SOCIAL, Bluesky section: written by bluesky/bsky_tick.py."}`
  data/bsky.json holds no subject identifier. The only DID in it is the labeler's, checked by regex.
- **B2. The shipped numbers were built by uncommitted code.** Fix: in `social_index/bluesky/`, run `git add bsky_tick.py && git commit -m "BLUESKY tick: beside notes for porn(self), sexual(self), nudity(self), rude:1714644703844 and gore, longer bench-note; no rule change"`. The point is that the commit which made the page is the commit on record. The diff was read in full. It adds `beside` entries (all 0 in 2025 except gore at 164) and lists the seven readings in the bench-note. No count, rule or outcome depends on it.

After B1 and B2 the section can ship without another referee pass.

---

## 1. Recounts from raw

### Store against wire

The referee read 9,000 frames from the live stream, 1,500 at each of six cursors (0, 5,000,000, 20,000,000, 26,655,000 at the 2026 boundary, 35,000,000 and 45,770,000). All 9,000 frames match the stored row on did, collection, rkey, cid hash, value, neg, cts, exp and src. Nothing served was missing from the store, and nothing stored in those ranges went unserved. All 9,000 signatures verify against `did:key:zQ3shmV1…iinTa` with the referee's ECDSA, and all are low-S. Each frame carries exactly one label.

### Store-level figures (desk / referee)

| Figure | Desk | Referee |
|---|---|---|
| Head seq | 45,785,475 | 45,785,475 |
| Served rows (labeler, with cts) | 42,906,618 | 42,906,618 (served set from keys, identical to desk's sup = 0) |
| Older copies not served | 7 | 7 |
| Other src / no cts / other uri form | 0 / 0 / 0 | 0 / 0 / 0 |
| Out of order (rolling 21, 24 h) | 2024: 3 | 2024: 3 |
| S(2024), S(2025), S(2026) | 995,066 / 7,076,870 / 26,656,482 | same |
| G(2024), G(2025) unserved seq | 250,807 / 722,621 | same |
| 2025 labels with expiry / expired | 170,839 / 170,839 | same |
| Daily series, last 7 full days (served, negations, seq used) | page table | identical on all 21 cells |
| Served labels by year (2024, 2025) | 5,510,697 / 15,892,830 | same as R1 |

### Recount against builder, every row

The readings are R1 to R7, as in PLAN.md. Every reading of every row was diffed. Only R5 differs, in four rows, by 2 or 3 labels (N1).

| Row | Stated | Desk R1 | Referee R1 | Desk interval | Referee interval | Desk | Referee |
|---|---|---|---|---|---|---|---|
| Labels applied 2025 | 16.49M | 15,892,830 | 15,892,830 | 15,889,143 – 16,615,451 | same | CANNOT_TELL | CANNOT_TELL |
| Labels applied 2024 | 5.5M | 5,510,697 | 5,510,697 | 5,508,625 – 6,394,196 | 5,508,625 – 6,394,193 | CANNOT_TELL | CANNOT_TELL |
| Adult detection (porn + sexual) | 14.2M | 13,849,748 | 13,849,748 | 13,846,715 – 14,572,369 | same | CANNOT_TELL | CANNOT_TELL |
| adult (porn) | 10.79M | 10,656,225 | same | 10,653,790 – 11,378,846 | same | CANNOT_TELL | CANNOT_TELL |
| suggestive (sexual) | 3.42M | 3,193,523 | same | 3,192,925 – 3,916,144 | same | CANNOT_TELL | CANNOT_TELL |
| spam | 761.77K | 732,384 | same | 732,313 – 1,455,005 | same | CANNOT_TELL | CANNOT_TELL |
| nudity | 389.44K | 381,303 | same | 381,114 – 1,103,924 | same | CANNOT_TELL | CANNOT_TELL |
| needs-review | 370.14K | 200,473 | same | 200,473 – 923,094 | same | CANNOT_TELL | CANNOT_TELL |
| rude | 295.38K | 293,077 | same | 292,705 – 1,015,698 | same | CANNOT_TELL | CANNOT_TELL |
| sexual-figurative | 152.58K | 150,471 | same | 150,471 – 873,092 | same | CANNOT_TELL | CANNOT_TELL |
| graphic-media | 127.46K | 121,463 | same | 121,406 – 844,084 | same | CANNOT_TELL | CANNOT_TELL |
| !hide | 68.26K | 57,822 | same | 57,795 – 780,443 | same | CANNOT_TELL | CANNOT_TELL |
| intolerant | 60.20K | 59,491 | same | 59,404 – 782,112 | same | CANNOT_TELL | CANNOT_TELL |
| self-harm | 20.92K | 19,873 | same | 19,847 – 742,494 | same | CANNOT_TELL | CANNOT_TELL |
| threat | 15.86K | 15,663 | same | 15,662 – 738,284 | same | CANNOT_TELL | CANNOT_TELL |
| Content share, all | 96.57% | 97.72% | same | 93.47% – 97.82% | same | CANNOT_TELL | CANNOT_TELL |
| intolerant on content | 98% | 98.62% | same | 7.50% – 99.90% | same | CANNOT_TELL | CANNOT_TELL |
| threat on content | 100% | 99.96% | same | 2.12% – 100.00% | same | CANNOT_TELL | CANNOT_TELL |
| rude on content | 99% | 99.61% | same | 28.74% – 99.89% | same | CANNOT_TELL | CANNOT_TELL |
| needs-review on accounts | 100% (exclusively) | 99.57% | same | 21.62% – 99.91% | same | BELOW | BELOW |
| Items removed (!takedown) | 2,446,334 | 2,398,393 | same | 2,397,046 – 3,121,014 | same | CANNOT_TELL (wide) | CANNOT_TELL |
| Account takedowns 2025 | 2.08M | 2,038,206 | same | 2,036,869 – 2,760,827 | same | CANNOT_TELL (wide) | CANNOT_TELL |
| Account takedowns 2024 | 1.02M | 166,744 | same | 166,744 – 417,551 | same | CANNOT_TELL (wide) | CANNOT_TELL |
| Temporary suspensions (!suspend) | 13,192 | 0 | same | 0 – 722,621 | same | CANNOT_TELL (wide) | CANNOT_TELL |
| Automated share | 95.34% | not in stream | | | | CANNOT_TELL | CANNOT_TELL |
| User reports | 9.97M | not in stream | | | | CANNOT_TELL | CANNOT_TELL |

The one decided row holds under every reading. In 2025, 857 needs-review labels sit on `app.bsky.feed.post` records, against 199,616 on accounts in R1. Every share reading is below 100%, and the highest is R7 with every unserved write counted as account, at 99.91%. "Exclusively" is read as exactly 100%, as the plan fixed before the count.

## 2. Stated figure named correctly (definition, period, denominator)

All 14 quotes are exact substrings of the fetched report and overview. All 12 source files match SHA256SUMS. On period, the report's "In 2025" is read as the calendar year, with UTC first and Pacific as a reading. That is in the interval. On "Applied" against standing labels: the stream serves only the latest write of each key, so R1 counts labels standing now and R7 credits every unserved write. That spread is what makes the totals CANNOT_TELL. It is stated on the page.

- The total's scope leaves out !takedown and !suspend. This is justified from the stated side: the 12-value table sums to 16.47M. In the stream, the 12 mapped values give 15,881,768 of 15,892,830 R1 labels in 2025. The other 11,062 are other values (!warn 4,790, impersonation 3,172, misleading 2,339, sensitive 344, gore 164 and smaller ones) and are counted in the total. That is consistent with the report's 0.02M gap.
- adult = porn and suggestive = sexual. The mapping is taken from Bluesky's own app strings (copy in data/source). No served value is literally named adult or suggestive.
- For adult detection (14.2M) the plan takes porn + sexual, the report's own adult + suggestive at 14.21M. This was fixed before the count.
- needs-review: the stated "370.14K accounts" is compared with all needs-review labels, including the 857 on posts (N5). The outcome is the same either way.
- Takedowns and suspensions: the report says takedowns include content "removed from public access and our infrastructure before human moderators or users view it". The wide-scope rule (only ABOVE is read) fits that.

## 3. Outcomes kept apart

The table has ABOVE 0, BELOW 1, CONSISTENT 0, CANNOT_TELL 25 and NOTHING_RETURNED 0. Nothing is folded. The suspension row has R1 = 0 but R4 = 9,468 and R5 = 11,946, so it is correctly not NOTHING_RETURNED. Every interval that reaches both sides of a stated range reads CANNOT_TELL. The 2024 account-takedown row lies wholly below the stated figure (417,551 against 1.02M). It reads CANNOT_TELL under the wide-scope rule, and the reason is printed in bsky.json and summarised under the table.

## 4. What each filter drops, by side

- Stated side: nothing is dropped. The two quoted figures not in the stream (95.34% automated and 9.97M reports) are rows that read CANNOT_TELL with a reason.
- Stream side, for all rows: 7 older copies of keys read twice (not served), 0 rows from another src, 0 without cts, 0 in other uri forms, and 0 undecodable frames.
- Stream side, label rows: !takedown and !suspend are left out of the totals. In 2025 that is 2,398,393 !takedown labels standing, plus 34,199 served !takedown negations. R1 also leaves out the 522,101 served negations of label values dated 2025, which R4 adds back.
- Stream side, R5: 127,986 later negations on post records whose TID is dated after 2025 are not credited to 2025, and 365,907 are not credited to 2024, by the plan's TID rule.

## 5. Page against recount, and copy rules

`html_check.py` compared all 26 table rows (stated, first reading, range and outcome). 25 match exactly. The labels_2024 upper edge reads 6,394,196 on the page and 6,394,193 in the referee recount (N1). Every prose number matches the recount: head seq 45,785,475, the signature sample of 42,743 with 42,743 passed, the latest full day 2026-11-09 at 48,367 labels and 411 negations, unserved 722,621, expiry 170,839 and 170,839, and first day 2023-04-13. So do the 21 cells of the seven-day table (sequence numbers used checked with `seq_used_check.py`), the year table rows for 2024 and 2025, and the outcome tally "below 1, cannot tell 25".

Copy rules:
- There are no semicolons in visible text. The only semicolons on the page are the ends of HTML entities such as `&rsquo;`.
- Headings carry no count of our own things.
- There is no AI statement.
- There is no cause claim about any gap. The "since" and "so" clauses explain the method or the stream's published mechanism ("since every count is exact", "since takedowns can be made outside the stream", "its published code moves that row…, so a replay serves the latest write"). They do not explain why Bluesky's figure differs, which is acceptable.
- Sentences are plain.

## Non-blocking items

- **N1. R5 and three record keys that are not plausible TIDs.** Three served negations (seq 11,155,853, 27,402,724 and 45,734,193) have 13-character keys that decode to the years 2190 to 2303. The desk's tid_ms treats them as not TIDs and credits them. The referee's strict reading treated them as TIDs dated after the year and did not credit them. The desk's reading is the sensible one. The effect is 2 or 3 labels in R5 of labels_2025, labels_2024, adult_detection and val_suggestive. Only the labels_2024 interval edge shows on the page. No outcome changes. Optional: one plan line saying a key is a TID only when it decodes to a date between 2017 and 2059.
- **N2. Suspension row.** The first reading prints 0, but the stream serves 21,757 !suspend negations (9,468 dated 2025) and 196 standing !suspend labels (all from 27 October 2026 on). A reader could take the 0 as "no suspensions in the stream". Suggested sentence under the table: "Every !suspend label of 2025 that the stream still serves is a negation, since a suspension that ends is negated. The stream serves 9,468 of them dated 2025."
- **N3. gore beside graphic-media.** The plan says gore (164 in 2025) "is reported beside the row". It is in bsky.json but not on the page. Optional clause on the graphic-media row or under the table.
- **N4.** "drawn at random across the whole stream" describes a fixed hash of the sequence number. Suggested: "drawn by a fixed hash of the sequence number, about one in a thousand, across the whole stream".
- **N5.** The needs-review count row compares the stated "370.14K accounts" with needs-review labels on any subject (857 of the 200,473 R1 labels are on posts). The outcome is the same either way.
- **N6. Design note, no change asked.** R7 credits all 722,621 unserved 2025 sequence numbers to every row. Count rows can therefore read only ABOVE or CANNOT_TELL, and a small value's range spans up to 47 times its R1 (threat runs from 15,662 to 738,284). This is the committed rule. The page's list "The stated figure lies inside our range for: …" (22 rows) is true but could read as agreement. Optional rewording: "The stated figure lies inside our range, which reads cannot tell, for: …". For the record, R5 for labels_2025 is 16,489,948, which is inside the stated 16.49M rounding range. That is a fact about one reading, not a finding, and the page does not claim it.
- **N7.** runs.ended for run 1 stays NULL in bsky.json `meta.runs` (the reboot). Harmless. The resume and the full superseded pass handled it as designed.

## Verdict

**FIX THEN SHIP.** B1: add the `social-bluesky-rows` copies.json entry so `/social/bluesky.json` exists. B2: commit bsky_tick.py as it ran. Neither changes a number or an outcome, and no further referee pass is needed after them.
