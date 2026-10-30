# Sarkar, arXiv 2608.14329: a recount, readings and a live embedder arm

Our recount of "A Four-Axis Trustworthiness Benchmark for LLM-as-Judge in Principle-Based Regulation" by Dipankar Sarkar (arXiv
2608.14329), from the author's GitHub release at commit a2e47ae. The plan was committed before each reading was computed. GIT_LOG.txt lists
the commits with their times.

## What rebuilds

From his run files, with our own code: the LLM judge (gpt-oss:120b) is right on 35 of 47 Consumer Duty originals (0.74) and 3 of 11
keyword-stuffed Consumer Duty items (0.27), and on 48 of 50 and 12 of 13 for COBS, each scenario scored on its own principle. Every row of
judge_agreement.csv rebuilds, including Consumer Duty adversarial kappa 0.157 on 23 scenarios (known_good.text).

## Readings

Every reading below was defined after reading the paper. Intervals are 95%. Outputs are in readings.text and s4.text.

- The drop on matched items. On the 11 Consumer Duty adversarial items with a scored source, the judge was right on 9 of the sources and 3
  of the stuffed versions. Six went right to wrong and none went wrong to right (exact McNemar p .031). The matched drop is 0.545, with a
  paired Newcombe interval of [0.195, 0.731]. Five of the six are flip_positive items, which alone go 5 to 0 (p .0625). The printed
  47-point drop (35 of 47 against 3 of 11) has an interval of about 15 to 68 points, so it excludes zero but not a drop of about 15
  points. Of the judge's 8 wrong stuffed verdicts, 5 pass a non-compliant promotion and 3 escalate a compliant one.
- Kappa on that split. The second judge (kimi-k2.6) escalated all 10 Consumer Duty adversarial scenarios that both judges assessed, so
  kappa on the principle's own scenarios is 0 by construction, and an always-escalate rule is also right on 8 of the 10. The pooled 0.157
  also scores 13 COBS scenarios against Consumer Duty. It equals the highest kappa the two judges' escalation rates allow (15 and 22 of
  23), with a bootstrap interval of [0.00, 0.51]. Directly, the second judge was right on 5 items the first judge missed and on none the
  other way, all five flip_positive. That points the same way as the paper's claim, and exact McNemar gives p .0625 on 10 items.
- How often each judge escalates. On Consumer Duty originals the first judge escalates 36 of 47 and the second 40 of 48. Both are right on
  all 24 escalate-expected originals, and on 11 of 23 and 8 of 24 comply-expected ones.
- Live embedder arm. The MiniLM and BGE-base similarities in his released runs reproduce from the public weights (all-MiniLM-L6-v2 at
  1110a243, bge-base-en-v1.5 at a5beb1e3) on CPU, with normalised embeddings and no prefix, to within 6e-7 over 2,688 values each. Two
  repeats on our machine are identical. Every embedder verdict is escalate in his files and ours, so the verdicts do not test the
  reproduction. mxbai-embed-large was not run.

## Run it

src/fetch_theirs.py downloads the files read here from the author's repository at a pinned commit (FILES.tsv) and checks their hashes.
known_good.py, readings.py and read_s4.py run with python3 and the standard library from this folder. run_s4.py needs sentence-transformers
(versions in VERSIONS.txt) and writes src/runs. SETUP_S4.md records the weights by revision and file hash. CHECKS.md.text holds our checks.

Heuremen LLC
