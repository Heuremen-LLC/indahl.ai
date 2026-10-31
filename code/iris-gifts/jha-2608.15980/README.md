# Jha, arXiv 2608.15980: a recount and readings

Our recount of "Whose Gold? Annotator-Pool Disagreement Is Large at the Item Level, and Hidden by Small Leaderboards" by
Anik Jha (arXiv 2608.15980), from the released MultiPref file
(allenai/multipref at 12910233, MultiPref-Train.jsonl) and the paper's public repository anik-jha/whose-gold. The plan was committed before
the readings, with dated addenda after each referee pass. One addendum was committed a minute after its reading ran, as PLAN.md.text
records. GIT_LOG.txt lists the commits with their times. This folder holds no
prompt or completion text, only counts.

## What rebuilds

From MultiPref-Train.jsonl, with our own code: 10,461 comparisons, of which 2,885 have both crowd labels in agreement and both expert labels
in agreement. On those the two majorities differ on 680 of them (23.6%) and name opposite winners on 265 (9.2%). Labels are collapsed to A, Tie and B by prefix.

Table 3. The arXiv v1 column (0.28, 0.86, 0.9997 at 6, 10 and 20 models) is close to treating adjacent swaps as independent events: with
the printed 2.6-point standard deviation that closed form gives 0.274, 0.864 and 0.9996 (readings.text, J1). The camera-ready in the repository already replaces it with 0.29, 0.92 and 1.00. Our own simulation with independent per-model shifts, at a
per-model standard deviation of 2.6/sqrt(2) so that a pair differs with the paper's 2.6 points, gives 0.287, 0.918 and 1.000.

## Readings

Every reading below was defined after the data, as PLAN.md.text records.

- A mixed-pairing baseline. Pairing each crowd annotator with an expert on the same item, under the same unanimity rule, and pooling both
  ways of doing so (j3p.text): the two pairs' majorities differ on 1,209 of 5,619 (21.5%) and name opposite winners on 490 (8.7%), against
  23.6% and 9.2% for crowd against expert. The 2,205 items where all four annotators agree count the same under every pairing, so the
  readings differ only in how they divide the 1,889 items that split two against two. Majorities differ 2.0 points more often with the pools
  held apart: [+0.4, +3.7] by resampling items, [-1.7, +5.8] by deleting one annotator at a time. Opposite winners differ by 0.5 points,
  [-0.8, +1.7] and [-1.9, +2.8].
- The rulers (rulers.text). With annotator ids shuffled within each pool, deleting one annotator at a time reads 2.0 times the item-level
  width and an annotator bootstrap 3.9 times, because each item sits under four annotators. We print the annotator-deletion interval as an
  upper bound on the width, not as the width.
- Annotator order. Within each pool the first listed annotator labelled before the second on most items, so a single mixed split depends
  on which annotator is listed first. readings.text keeps the two single splits (20.8% and 22.2%). The pooled pairing above does not depend
  on order.
- Single annotators (readings.text, J2). Disagreement within the crowd pool is 0.489, within the expert pool 0.501 and across pools 0.504.
  The interval printed there resamples items only. The annotator-deletion upper bound on the 0.010 difference is [-0.006, +0.025].

## Run it

src/fetch_theirs.py downloads MultiPref-Train.jsonl at the pinned revision (FILES.tsv) and checks its hash. Then run src/readings.py,
src/rulers.py and src/j3p.py with python3 and numpy from this folder. Nothing of theirs is run. CHECKS.md.text holds our checks.

Heuremen LLC
