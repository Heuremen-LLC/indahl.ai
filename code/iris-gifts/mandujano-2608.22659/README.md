# Mandujano Reyes, arXiv 2608.22659: a recount and readings

Our recount of "Statistical Methods for Multiple Language Model Comparison on a Shared Evaluation" by Juan Francisco Mandujano Reyes
(arXiv 2608.22659, version 2). It uses his released data and the MMLU-Pro outputs his data was drawn from. The plan was committed before
each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From his mmlu_pro_real_data.csv, with our own code, every value in his Tables 1, 3 and 5, the shown rows of Table 4 and his Friedman test
rebuild to the printed digits (known_good.text). Table 4 is rebuilt through the identity the paper reports, a contrast standard error of
the square root of twice the question-blocked residual mean square over n. His file matches TIGER-Lab's released per-item outputs on every
reply that gave an answer letter (k2_provenance.text).

## Readings

Every reading below was defined after reading his paper. Intervals are 95%. Outputs are in readings.text.

- Pairing under correction. Holm over the 15 pairs keeps 3 comparisons with paired tests and 1 with unpaired tests. Without a correction,
  both keep 5.
- The near miss. Mistral-7B-v0.1 against Yi-6B has raw p .0034 under the paper's Eq. 3 model. That misses Bonferroni's .00333 and clears
  Holm's third step, .05/13 = .00385. Under Bonferroni the paired test keeps it (p .0027) and the Eq. 3 contrast does not. Under Holm,
  the paired tests, the Eq. 3 contrasts and an exact McNemar test keep the same three comparisons.
- Distance to the line. The same comparison crosses its line after one or two single-item score changes under every rule we ran.
- Replies with no answer letter. TIGER-Lab's outputs hold no extracted letter for 10.8% to 22.8% of each model's questions in this
  subsample. The released file scores each of those as wrong. The benchmark's own scorer (save_res in TIGER-Lab's evaluate_from_local.py)
  gives them a random guess among the item's options, and those guesses are not stored in the released outputs. For
  Mistral-7B-v0.1 against Qwen1.5-7B-Chat, 98 of the 441 discordant questions have a letter from one model only, 73 of them missing on
  Qwen's side. On the 1,058 questions where both models gave a letter, the difference is +0.0066 (p .71). On the 811 questions where
  all six models gave a letter, Holm keeps 1 of the 15 comparisons.

## Run it

src/fetch_theirs.sh downloads the files read here into theirs/ at pinned commits and checks their hashes. Then run each script in src
with python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds the checks we ran on each reading before it was filed.

Heuremen LLC
