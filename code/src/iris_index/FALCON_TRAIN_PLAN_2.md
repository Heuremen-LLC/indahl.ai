# Public update 1, round 2: does the trained Falcon hold on fresh evaluation sets (28 Oct 2026, his word)
Written and committed before any reply to the new sets exists.

## Question
Round 1 trained Falcon3 3B Instruct on the Faults and Guards (true labels) and with mixed labels, and read both on evaluation sets A and B. Against the mixed-label model the true-label model was ahead on Forced verdict and Best of n in both sets. Does that, and the 40% left on Unchecked equals sign, hold on two evaluation sets the models have never been read on?

## Arms
The same three models as round 1, nothing retrained: the untouched model, the model trained on the Faults and Guards (adapters_true), the model trained with mixed labels (adapters_mixed). Adapters are frozen as committed in round 1. Settings, scorer, gates and the three reply arms (bare, repeat, guard) are unchanged.

## New evaluation sets
Set C: seismic detectors, seeds 20273001 and 20273002. Set D: wind turbine controllers, seeds 20274001 and 20274002. New stories, never used in training or in rounds 1 to 13. Built by make_eval.py C D, which refuses to rebuild a set that exists. Code hashes in each folder's CODE.sha256.

## Reading (the plan 1 rule, unchanged)
Per family, the paired fault difference trained minus untouched and trained minus mixed, bootstrap of 2,000, seed 7. AHEAD, BEHIND, CONSISTENT, CANNOT_TELL, gates as in round 1. A result is called replicated for a family only where trained is ahead of mixed in sets C and D and was ahead in sets A and B. Where it was cannot tell in round 1 the round 2 reading stands alone. Rates are published side by side, never pooled with round 1. Parser hand-check on ten replies per family for two models before any score is read; any repair is a dated addendum.

## Release
The replies, the scores, the scripts and the plan, with the vendor-response path open. Weights stay unreleased until the license text is quoted in release notes.
