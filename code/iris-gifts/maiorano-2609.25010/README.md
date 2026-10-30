# Maiorano, arXiv 2609.25010: record readings

Our reading of "Do Synthetic Personas Predict Real Audience Response? A Sim-to-Real Study Where a No-Persona Baseline Beats Persona-Based
Copy Simulation" by Alexandre Cristovão Maiorano (arXiv 2609.25010), from his GitHub release at commit 7c1ab46. Per-test scores are withheld
in the release, so these readings compare his report files and code with his text. The plan was committed before each reading was
computed. GIT_LOG.txt lists the commits with their times.

## What matches

Every value in Table 1 and every row of Table 2 equals his report files (baseline_comparison.json, replication.json). The baseline's n is
one or two short of the panel's in four splits (398 against 399 in Table 1), because only packages with every variant scored are kept.

## Readings

Every reading below was defined after reading the paper. Outputs are in readings.text.

- The Reddit row. In replication.json the Reddit row has top-1 40.3% [36.3, 44.3] for the panel against 30.2% [26.5, 34.1] for the
  baseline, and lift 0.45 [0.41, 0.49] against 0.33 [0.30, 0.37]. Table 2 prints that lift as 0.45/0.33. "Captures more than the panel in
  every dataset" and "beats or matches the persona panel everywhere" therefore hold on tau only for that row (-0.026 against -0.009,
  intervals overlapping).
- The rank coefficient. compute_validity.py computes (C - D)/(C + D) with tied pairs left out, which is Goodman and Kruskal's gamma rather
  than Kendall's tau-b, and returns None when every pair is tied. baseline_ties.json counts 71 of 398 baseline packages where every variant
  gets the same score. His code leaves such packages out of the tau mean, while n counts them. With the 71 counted as 0, the baseline's mean
  would be about 0.30 (rho about 0.29), against 0.084 (rho 0.104) for the panel. This is a sensitivity, not a correction, and the
  conclusion holds either way.
- The GPT-4.1 rerun. crossfamily_gpt41.json records 10 baseline draws per variant, against the panel's 10 personas times 3 draws, and 395
  baseline packages against 399. The smaller budget runs against the baseline. tier2_crossmodel.py sends no seed, while the paper says
  seeds are pinned and recorded per prediction.
- Seed spread. The stored SDs (0.025 for tau, 0.008 for top-1) equal the population formula on the three seeds. The sample SDs are 0.031
  and 0.010.

## Run it

src/fetch_theirs.py downloads the report files and scripts read here from his repository at a pinned commit (FILES.tsv) and checks their
hashes. Then run src/readings.py with python3 from this folder (standard library only). Nothing of his is run. CHECKS.md.text holds our
checks.

Heuremen LLC
