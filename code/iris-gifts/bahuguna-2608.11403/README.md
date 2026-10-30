# Bahuguna, arXiv 2608.11403: a recount and a reading

Our recount of one interval in "When Self-Consistency Backfires: Majority Vote Hurts the Majority of Hard Science Problems for Small
LLMs" by Utkarsh Bahuguna (arXiv 2608.11403, version 3), from the derived data on Zenodo (10.5281/zenodo.21933418). The plan was
committed before the reading was computed. Nothing in this folder contains benchmark question text.

## What rebuilds

The registered replication run in Section 8 (Qwen/Qwen3.5-9B, cap 6,144) has 1,253 samples over 79 problems, 1,119 with an extracted
answer (0.8931) and 364 truncated (0.2905), as printed. 230 truncated samples still carry an extracted answer (b1.text).

## Reading

Defined after reading the paper. The printed interval for that answer rate, [0.8747, 0.9090], matches a sample-level Wilson interval to
four places. Disclosure 24 moves two other answer-rate intervals to the paper's problem-level convention. Under a problem-level cluster
bootstrap this one is about [0.85, 0.93], and b1.text gives it under both bootstrap setups the paper states. The registered 0.995 line
sits above both intervals, so the paper's verdict does not change. The 79 problems are the budget-stopped slice the paper describes, so
neither interval speaks for the benchmark.

## Run it

src/fetch_theirs.py downloads the one file read here from Zenodo (FILES.tsv) and checks its hash. Then run src/b1.py with python3 from
this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
