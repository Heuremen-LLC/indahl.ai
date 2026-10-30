# Lail, arXiv 2609.06444: a recount and readings

Our recount of "Decomposing LLM-Judge Uncertainty to Target Expert Labels" by Ryan Lail (arXiv 2609.06444, v3), from the author's GitHub
release (composo-ai/judge-uncertainty-decomposition at 49f876e) and the community ChaosNLI mirror on Hugging Face (earino/chaosnli at
bf8d66a), since the original download link returns File Deleted. The plan was committed before each reading was computed. GIT_LOG.txt lists
the commits with their times.

## What rebuilds

From judge_cache.jsonl and the mirror, with our own code: the judge's mean Manhattan error against all 100 labels (0.458), mean stated
confidence (90.3), the Spearman correlations of error with stated confidence (-0.13) and prediction entropy (0.11), and the half-split
noise ceiling (0.158). All 9,339 stored distributions equal their raw replies (known_good.text).

## Readings

Every reading below was defined after reading the paper and code. Intervals are 95% over items. Outputs are in readings.text.

- The distance feature. In build_features, each item's distance to the nearest labelled item is computed against a labelled set that
  includes the item itself, so the value is 0 for every labelled item (to 2e-15, under any reveal draw). fit_dcm fits on labelled items
  only, so inside the fit that column is constant and moves with the intercept. The likelihood is flat along it, and its coefficient is
  not set by the data, yet the column varies over zero-label items and the coefficient scales their trust. The 10-nearest density column
  includes the item's own zero for labelled items only. We did not rerun Table 2 under other values of that coefficient.
- Five labels against the judge. On Manhattan error against a 50-label half, the judge's prediction scores like about three raw fresh
  labels from the same pool (0.465 against 0.469 for three), and five fresh labels beat it by 0.095 [0.085, 0.106]. Against all 100 labels
  the judge is level with the original five annotators overall (-0.003 [-0.020, +0.012]). That panel is the one ChaosNLI selected its
  items by, with exactly three of five agreeing on every item, and the overall tie is two opposite gaps: the judge is closer by 0.144 on
  SNLI and further by 0.129 on MNLI. The five pseudo-labels in Section 5.3 is a fitted concentration, a different quantity.
- Appendix C. It says self-update "loses to" conjugate updating. On the printed errors, where lower is better, self-update (0.258) is below
  conjugate updating with the familiarity channel (0.262) and without it (0.307).

## Run it

src/fetch_theirs.py downloads the files read here at pinned revisions (FILES.tsv) and checks their hashes. Then run src/known_good.py and
src/readings.py with python3 and numpy from this folder. Nothing of the author's is run. CHECKS.md.text holds our checks.

Heuremen LLC
