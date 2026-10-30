# Bronder, arXiv 2607.14399: a recount and readings

Our recount of "Instrument Effects in Language-Model Honesty Evaluation: An Auditable Single-System Demonstration" by Justin Bronder
(arXiv 2607.14399), from the logs and files on Zenodo (10.5281/zenodo.21384627) and the repository at tag v1.0-arxiv. The plan was committed
before each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From his closed inspect-ai logs, with our own code: Table 2 on the four anchors (complete 22 to 7, unreachable 16 to 0, incomplete 0 to
28, budget 2 to 5), Table 3 (valid 59 and 58, HALT 43 and 10, false 18 and 0, pin games 4 and 42), and the Gate 2 strong-claim rates for the
meter cell (23 of 60, .383) and the none-lantern cell (9 of 60, .150). No game in either series 2 arm records a win (known_good.text).

## Readings

Every reading below was defined after reading the paper. Intervals are 95%. Outputs are in readings.text.

- The grammar shift by anchor. Strong claims fall on every anchor (9 to 0, 10 to 3, 10 to 3 and 9 to 1 of 10), each Fisher exact p at
  most 0.0031. Pooled, 38 of 40 to 7 of 40 is a drop of 0.775 [0.590, 0.870], with the time confound the Table 2 caption names.
- The disclosure contrast by instance. All six instances carry false verdicts under the hidden criterion (1 to 6 of 9 or 10) and none
  disclosed (exact sign test p .031). The two-sided 95% Clopper-Pearson upper end for 0 of 58 is 0.062. Only 10 of 58 disclosed games
  halted, so the contrast also stands conditional on halting: 18 of 43 against 0 of 10 (Fisher p .011).
- Meter against lantern in Gate 2. The difference is +0.233. Resampling the 12 instances gives an exact bootstrap interval of [+0.067,
  +0.400], beside the game-level Newcombe interval [+0.075, +0.377]. Meter is above on 8 instances and below on 1 (sign p .039). With each
  solvable instance and its unsolvable twin as one unit it is 5 up, 0 down and 1 tied (sign p .0625).
- Fidelity flags. The printed "35/60 games flagged vs heroic 29/60" are flag totals over 60 games. Games with at least one flag are 29 of
  60 (mundane) and 20 of 60 (heroic). Mundane still leads, and the no-skin lantern cell (25 of 60) is also above heroic.
- Narrations. The 5,181 rows in hetero_values.jsonl are 5,176 unique narrations: five first attempts returned empty replies and were run
  again. One more row (mundane, lu-900002u, epoch 4, narration 3) is an error with no retry, so 5,175 carry an extraction. The lantern
  cells hold 4,011 rows and 4,006 unique narrations.
- Gate 2 records. In the five Gate 2 logs no GLM call, in its config or its recorded request, carries a temperature. In Gate 0 and series 2
  every GLM call carries 0.7. No Haiku call carries a temperature in any run. All five Gate 2 cells are dirty=true. Four bind 4de8b8f, which
  adds only scripts/g2_readout.py and docs/PAPER-SKELETON.md to the ratification commit 081586f, and the none-lantern cell binds 081586f.

## Run it

src/fetch_theirs.py downloads logs.tar.zst and hetero_values.jsonl from Zenodo (FILES.tsv) and checks their hashes. src/extract_logs.py
unpacks the logs (Python 3.14 standard library). Then run src/known_good.py and src/readings.py with python3 from this folder. Nothing of his
is run. src/compare_081586f_4de8b8f.min.json is a trimmed copy of the public GitHub compare between those commits. CHECKS.md.text holds our
checks.

Heuremen LLC
