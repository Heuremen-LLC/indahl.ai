# Cochran, Dodson and Nore, arXiv 2608.28875: a recount and readings

Our recount of "No Detectable Change in Side-Level WER from Prompt-Level Context: A Preregistered Ablation on a Production Oral-History
Corpus" by Theodore O. Cochran, Stephanie Dodson and Keith Nore (arXiv 2608.28875). It uses the authors' OSF release. The plan was
committed before each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From per_side_outcomes.csv, with our own code, the primary result rebuilds for both configurations: gpt-4o-transcribe +0.56 WER points
[-1.14, +1.04], Wilcoxon p .568, and gemini-2.5-flash -0.37 [-2.46, +7.01], p 1.000, against the printed +0.6 [-1.1, +1.0] and -0.4
[-2.5, +7.0] (known_good.text).

## Readings

Every reading below was defined after reading the paper. Outputs are in readings.text.

- Position in the rerun. The main run always ran the arms in one order. The rerun counterbalanced it, and its arm_pos field records the
  position for each side's first audio part. Using residuals centred on each arm's own five-rep median, the last-minus-first difference for
  gpt-4o-transcribe has median -0.49 WER points, with a 95% order-statistic interval of [-2.07, +0.11]. That interval holds zero and also
  reaches effects larger than the primary interval, so the rerun cannot tell either way on a position effect of that size.
- Sign of the effect across runs. For the four rerun sides, the sign of full minus none in the main run repeats in 14 of 20 gpt-4o-transcribe
  reruns and 12 of 20 gemini-2.5-flash reruns. The main run and the reruns also differ in arm order and date.
- Quartile rule. The printed rerun IQR [-1.9, +2.7] uses index quartiles. The paper's other IQRs use the linear rule, which gives
  [-2.65, +1.98] here. Both are valid rules and the conclusion is unchanged.

## Run it

src/fetch_theirs.sh downloads the OSF release zip, checks its hash, and unpacks the two files read here into theirs/release. Then run each
script in src with python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds the checks we ran on each reading.

Heuremen LLC
