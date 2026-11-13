# STAN A: full-text plan, revision 2 (for Sage, 12 Nov 2026, about 14:40)

Revises PLAN_A.md against Sage's eight breaks (V2_REQUIREMENTS.md, "Sage on PLAN_A", 18:43). Nothing below has run except where
it says so. The teacher keep line in section 6 was written while the full-text teacher re-baseline was still running. Before
writing it, Bones had seen a dry run of score_ft.py on about a quarter of the rows (14:25). That is declared here, and the line is
written to the standard's question, not to those numbers.

## 1. Ceiling (break 1): done, pre-registered, declared deviations
PLAN_A_CEILING.md was written before retrieval ran. Results are in ceiling_ft/SUMMARY.md, with deviations in ceiling_ft/DEVIATIONS.md
(all-keys matching rule set by the judging agent, keys written after retrieval existed).
- Pass at IN/(IN+OUT) of at least 0.60: F1 and F2.
- F6 sits at the line (9 of 15) and is exploratory.
- F3 is retrieval-limited (10 of 20).
- F4, F5 and F7 are untested (fewer than 10 decided pairs).
Over all 196 flagged pairs, IN is 52 (27 percent). NOT_IN_TEXT is 45 (23 percent): evidence that lives outside the paper.
BM25 is not swapped out for any code.
The decided split per code is sealed in results/decided_split.json (sha256 in results/decided_split.sha256). It was built from the
committed judgments only.

## 2. Cells (break 2): derived from the standard, ABSENT defaults to not quotable
The "expected" line in PLAN_A.md is deleted. It was a post hoc guess from v1.
QUOTABLE_FT.md is written from the standard's text alone, by this rule, fixed here:
- A status is quotable from the retrieved chunks when its Test can be completed from one passage of the paper body.
- It is not quotable when the Test needs (a) a released file outside the PDF, (b) a recomputation or new run, or (c) a statement
  about every item in the paper.
- ABSENT is not quotable unless the code's own Test or ABSENT line names a place where the absence is visible (for example "the
  reference is described as ..."). Six chunks without a thing do not show it is absent from the paper.
The cell list is hashed separately from this plan. Only cells that are quotable and pass the ceiling (section 1) go on to
training. Today that can be at most F1 and F2 PRESENT, plus whichever ABSENT cells the rule allows. If the answer is two cells,
that is the finding.

## 3. Hand gate (break 3): bigger, two readers, a stated limit
- Per surviving cell: 30 rows, seeded from this file's sha256. Pass when at least 22 of 30 quotes support their label (Wilson 95
  lower bound 0.56 at 22/30; a 50 percent cell passes with probability 0.008, a 70 percent cell 0.43, an 80 percent cell 0.87).
- Two readers, blind to each other: Bones, and a blind model pass with a saved prompt, checked first on a positive control of 10
  supported and 10 unsupported quotes. Wayfinder builds that control (or picks from the marks page), not Bones. Disagreements
  go to Wayfinder in batches of about 10.
- Stated limit: "quote supports label" cannot catch a retrieved quote that an unretrieved passage contradicts.
- The number of surviving cells is reported, including zero.

## 4. Keep rule and power (break 4)
Power, simulated (paired bootstrap, 95 percent, independent errors, which is conservative). Read each cell as "chance of a pass".

| Constant right | STAN right | 40 calls | 80 calls | 150 calls |
|---|---|---|---|---|
| 0.70 | 0.90 | 0.60 | 0.86 | 0.99 |
| 0.70 | 0.85 | 0.41 | 0.58 | 0.87 |
| 0.77 | 0.90 | 0.30 | 0.54 | 0.88 |

So 40 fresh papers cannot carry a per-code keep test. The revision:
- Fresh recounts: at least 150 papers, drawn as in PLAN_A (seed from the plan hash, excluding every paper in pool, silver, gold
  or twins, including the 5 version-drift twins in results/twins_hand_read.md). Recounts are the bottleneck. They are made in
  batches, and nothing reads them until all are frozen.
- The keep decision is one pooled test over the surviving cells: STAN against the per-cell constant predictor on committed
  calls, paired bootstrap over papers (so calls on one paper move together). Per-cell results are descriptive.
- Coverage (committed calls / all calls) is reported beside every number. A STAN that commits on fewer than 30 percent of the
  pairs in a cell has that cell reported as untested, whatever it scores.
- Lexical baseline, defined now: a cell's cue list is the content words of its PRESENT line in the standard (stop words removed,
  lowercased, scripts/common.py code_block). It calls PRESENT when any cue appears in the top 6 chunks for that code, otherwise
  ABSENT. It is reported beside the constant predictor and enters the pooled test as a second comparison.
- Fresh recounts record PRESENT, ABSENT, CANNOT_TELL or NOT_APPLICABLE explicitly for every code. "Not flagged" is not ABSENT.
  ABSENT cells stay unscored on the old gold.

## 5. Silver gate and diagnostic (break 5)
- Silver gate restored: on held-out silver, per code, STAN beats the plurality, always-PRESENT and always-CT constants on committed
  calls. A code that fails is not trained further and is reported.
- Output order is quote first, then chunk id, status, reason. The status-token diagnostic teacher-forces the model's own quote and
  chunk id (from its free decode on that row), then reads P(status) at the status position. Free decode alone is reported beside it.
- Folds: grouped by paper. The stopping-step folds (schedule 100, 200, 300, 400) and the diagnostic hold-out are disjoint sets of
  papers. The hold-out is drawn first, by seed, before any training run.

## 6. Context and teachers (break 6)
- Context: training and inference both at 8,192 tokens. No truncation inside a chunk. If the 6 chunks exceed the cap, the
  lowest-ranked chunk is dropped whole, so a quote is never checked against a cut chunk. The memory and time cost is measured
  on the Armature GPU before the run and written into the run log.
- Teacher re-baseline on gold dev full text: running now (teachers_ft/, 3 teachers x 92 papers x F1 F2 F6 F3). The quote flag
  (grounding) is recorded separately from the status, and nothing is converted.
- Teacher keep line, fixed before the full scores are read. A teacher labels the pool for a code only if, on gold dev, its rate of
  grounded PRESENT on flagged pairs is above its rate of grounded PRESENT on unflagged pairs. The test is a Newcombe 95 percent
  interval for the difference with its lower bound above zero. A teacher that calls PRESENT on nearly everything, or on nearly
  nothing, cannot pass. If no teacher passes for a code, that code has no silver and is reported as "no usable teacher on full
  text".
- If no teacher passes for any code, the teacher-to-silver route is closed. The route left is training on the fresh recounts
  themselves (human labels, with STAN as the sorter), and that needs a plan of its own before anything runs.

## 7. Extraction (break 7)
- Coverage and the 13 exclusions: results/fulltext_extraction.md. All 13 are non-arXiv (13 of 43 non-arXiv gold, 0 of 154 arXiv),
  mostly Zenodo deposits with no PDF, where F4 and F5 flags sit. Claims read "open-access PDF slice only".
- Broken-text measure, defined now: per paper, the share of lines under 3 characters, and the share of characters outside letters,
  digits, spaces and common punctuation. A paper is flagged broken when either share is above the 95th percentile of the arXiv
  papers. Reported per code. F4 and F6 tables are hand-read on 10 papers.
- Version: the version the recount read is recorded against the version fetched. Zenodo concept DOIs drift (5 gold items, results/
  twins_hand_read.md). arXiv versions get checked with the same table.

## 8. Order and witness (break 8)
- This plan, QUOTABLE_FT.md and each addendum are committed under separate hashes.
- The fresh draw seed is the first 8 hex digits of this plan's committed sha256, so the draw comes after the commit.
- The ordering is labelled self-witnessed (git times on one machine).

## Order of work
1. Teacher re-baseline scored against section 6's line.
2. QUOTABLE_FT.md frozen.
3. Broken-text and version tables.
4. Fresh recount draw.
5. Recounts in batches.
6. Teachers on the pool, only for codes that passed.
7. Hand gate with two readers.
8. Train.
9. Silver gate and diagnostic.
10. One read of fresh gold.
