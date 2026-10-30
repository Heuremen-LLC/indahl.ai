# Arjmandi, arXiv 2608.03297: a reading

A reading of the released results behind "Distractor-Aware Truncation: Disentangling Context-Length Effects from Signal Loss in
Long-Context LLM Benchmarks" by Mohsen Arjmandi (arXiv 2608.03297), from the author's repository at commit 229afe14e36d. The plan was
committed before each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From the released per-sample files, with our own code, the number of items whose score changes in each of his Table 1 contrasts (25%
retention against full context, within each protocol, paired on sample_id), for all 28 contrasts.

## Reading

Defined after reading the paper. At 100% retention the naive and distractor-aware runs send the same prompt (equal prompt_hash on every
item), so the two full-context runs are a repeat of the same request inside his own release. They are separate calls, made 12 minutes to an
hour apart. Items whose score differs between them:

- BABILong: Claude Haiku 4.5 0 of 240, Claude Opus 4.7 10, Claude Sonnet 4.6 4, GPT-5.5 15.
- GraphWalks: Haiku 13 of 50, Opus 1, Sonnet 0, GPT-5.5 6.
- MRCR v2: Haiku 4 of 50, Opus 10, Sonnet 4.
- Oolong: Haiku 0 of 110, Opus 11, Sonnet 3.

Haiku and Sonnet ran at temperature 0, Opus and GPT-5.5 at their API default. Every mean difference is consistent with zero. The Opus MRCR
pair spans 18 May to 10 July, so that floor may include a change of model. Each floor comes from a single repeat, and a floor of zero is
the degenerate case.

Set beside his Table 1, three contrasts change no more items than their model's full-context repeat (GPT-5.5 BABILong and GraphWalks
distractor-aware, Sonnet GraphWalks distractor-aware), and all three are rows he reads as neutral. For GraphWalks and MRCR, whose scores
are continuous, the count at a 0.05 threshold adds a fourth, Haiku GraphWalks distractor-aware, which he reads as a trend. For that cell
the full-context repeat alone moves the mean by -0.044, against his +0.083. These are count comparisons, not tests, and the contrasts above
their floors are consistent with his verdicts.

## Run it

src/fetch_theirs.py downloads the 56 result files read here at the pinned commit (FILES.tsv) and checks every hash. Then run src/a1.py with
python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
