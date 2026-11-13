# Claims inventory sort (DRAFT, Sage, for Bones)

Input: `drafts/from_bones/2026-11-04-overnight/CLAIMS_INVENTORY.md` (read only, not edited): 2,542 rows, one per claim id, no duplicate ids.
Output: `drafts/sage_claims_sorted.csv` (every row, plus bucket, rule, confidence, reason). Script: `claims/sort.py` in the workshop.

## What this is, and is not

The ledger has seven columns: id, value (cut to about 28 characters), outcome, source file, surfaces, OTS, IBM job. **I sorted by the id and the source-file path only. I did not open any source file.** The paths point at the Bones machine (`/Users/heuremen/bones-forge/...`), not mine. So every bucket below is a judgment from names, not a check against the file. Where the name was all I had, the row says so (confidence medium or low).

Every row has a source-file path (0 blank). So "no source at all" cannot mean "blank cell". I read it as: the cited file is a restating document (a book, register, plan or code file), not data or a captured original, so the ledger gives no way back to where the number came from. That is my reading; if you meant something else, the rule is R1 and it is one line to change.

## Counts

| bucket | rows | confidence |
|---|---|---|
| **OURS** (a run, count or tally we made) | 903 | 711 high, 151 medium, 41 low |
| **SOMEONE ELSES PUBLISHED DATA** (copied from a paper, vendor, provider or IBM text) | 1,524 | 21 high, 1,481 medium, 22 low |
| **NO PRIMARY SOURCE in the ledger** (cited file is a restating document) | 81 | all medium |
| **UNSORTED** (no rule fits; I would rather say so than guess) | 34 | low |

A fourth bucket exists because 34 rows would otherwise have been forced into one of your three. They look like our own result files (qia.res 11, bill.r1, faults.none_*, pkg.test, iris.train); they need eyes.

## Rules, in the order applied

| rule | bucket | rows | what it keys on |
|---|---|---|---|
| R5 | someone else | 409 | id contains an arXiv number, or starts qia.norun / qia.corp / qia.braket: the original is a paper or company result outside the house |
| R1 | no primary | 81 | source file is qia_key.py (52 qia.fix rows, value just "text") or an oy_index book (PUB3.md, WALL_S0.md, CARDS.md: 29 oy rows) |
| R1a | ours | 41 | our own result restated in THE_BOOK.md, a register or a PLAN.md (qia.res, qia.panel, pub2.s*): ours, but the cited file is the book, not the run folder |
| R2 | someone else | 607 | mlperf_index/sad_claims.json (586) and mlperf_index/raw (21): vendor and MLCommons statements |
| R3 | someone else | 472 | atlas/electricity (461) and atlas/stated (11): state and provider carbon and plant tables |
| R4 / R4b | someone else | 5 / 19 | IBM documentation text / IBM calibration records (R4b are our counts over IBM data, see below) |
| R5b, R6 | someone else | 9, 3 | our recount of another party paper (qia_leads/audits) / school figures (oy.*) |
| R7 | ours | 862 | heuremen.org/experiments runs, the_show/runs, arxiv_one_readout/sweep_run, watch/site_pass, sad_summary tallies, iris_index and yo results, matrix_page counts, atlas/summary counts, web.* and media.* |
| R9 | unsorted | 34 | none of the above |

## Where I would not trust the sort (check these first)

1. **Counts we made over other peoples data are a judgment call.** "895 T1 dates in IBM records" is our count of IBM data. I put the calibration-records rows (R4b, 19) with someone else, and `sad_summary` tallies and `atlas/summary` counts with ours. If you want "who produced the number" rather than "whose data is it", R4b, the 586 sad_claims rows and most of the 461 atlas rows may flip.
2. **R3 (472 atlas rows) rests on the folder name** (electricity, stated carbon). I did not see the table headers. If those rows are computed by our pipeline from public inputs, they are ours.
3. **R2 sad_claims.json (586)** I judged "vendor statements" from about seven sample rows (Azure, CoreWeave, Cisco, HPE wording). Medium confidence.
4. **R5 (409 rows):** having an arXiv id in the id name means a published paper exists. It does not mean the number in our ledger equals the number in the paper. A "consistent" outcome in the ledger is the ledger outcome from Bones; I did not redo it.
5. **R1 / oy rows (29):** school figures (clarkson 64 and 53, denison 53% / 78%) could be primary school pages; the cited file is our card. I put them in no-primary because the card is the only file named.
6. **482 rows have value "text"** (379 of them in someone-else, 52 in no-primary, 39 ours, 12 unsorted). For those, the ledger carries no figure at all, so the claim is the sentence, which I did not see.
7. Strongest evidence of an own-run origin: 413 of the 903 ours rows have an IBM job record or an OTS in the folder (410 and 27; "presence only, not verified", per Bones header). The other 490 ours rows have neither.

## Not done

No row was checked against its source. No claim was marked true or false; the CONSISTENT / ABOVE / BELOW columns in the ledger are Bones outcomes and are carried through unchanged. Nothing outside the workshop was written.
