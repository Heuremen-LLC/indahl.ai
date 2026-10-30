# Nakayashiki and Watanabe, arXiv 2607.29274: readings

Readings of the released results behind "Language Models Agree With Each Other, Not With Readers" by Kazuki Nakayashiki and Keisuke
Watanabe (arXiv 2607.29274), from the authors' arXiv ancillary files. The plan was committed before each reading was computed. GIT_LOG.txt
lists the commits with their times.

## What rebuilds

From panel-agreement.json, with our own code, the 153 model-to-model agreements and each model's agreement with readers, including the
range from +0.006 (Granite 4.1 8B) to +0.047 (Gemini 3.1 Pro) (readings.text).

## Readings

Every reading below was defined after reading the paper.

- Each model beside itself. For each of the 18 models, the mean of its agreement with the other 17 runs from +0.023 to +0.150, and is 3.0
  to 7.9 times its agreement with readers, which is the paper's title model by model. Across the 18 models the two columns rank the models
  almost the same way (Spearman +0.94, Pearson +0.91). Both columns come from the same per-model excess computation, so the release cannot
  tell whether the shared factor is the model or something each model's output carries into both, such as how many sentences it returns
  (the authors' own HARNESS-DEFECTS.md, D1). The rankings needed to test that are not released. The paper reports the group version of this
  pattern (newer models closer both to readers and to each other).
- Two printed medians. The analysis takes the upper of the two middle values when a group has an even count. Table 2's "both closed"
  +0.174 is +0.172 as an exact median, and "same country" +0.090 is +0.089. The cross-border comparison keeps its direction.

## Run it

src/fetch_theirs.py downloads the two files read here from the arXiv ancillary listing (FILES.tsv) and checks their hashes. Then run
src/readings.py with python3 from this folder. The arm table is read out of panel-agreement.py as text, and nothing of theirs is run.
Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
