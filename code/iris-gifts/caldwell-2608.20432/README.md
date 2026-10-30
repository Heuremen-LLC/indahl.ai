# Caldwell, arXiv 2608.20432: a recount and readings

Our recount of "ProofJudge: Tool-Grounded LLM Evaluation of Formal Proof Quality in Mathlib" by Shane Caldwell (arXiv 2608.20432), from the
released eval traces on Hugging Face (SJCaldwell/proofjudge-eval-traces at 2fe14f4) and the GitHub repository (SJCaldwell/ProofJudge at
5c335ca). The plan was committed before each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From the six trace files, with our own code, Table 1 alignment matches to the last digit for gemini-3.7-flash (75.2), gpt-5.4-mini (68.7)
and deepseek-v4-flash (63.5), the three judges with no missing trajectories. For claude-sonnet-5, muse-glimmer-30b and inkling-small, which
lose 6, 2 and 1 pairs to omitted runs, we get 80.7, 70.4 and 69.2 against the printed 80.8, 70.2 and 69.3. Counting lost pairs as misses
gives muse-glimmer-30b's 70.2 but not the other two (known_good.text, readings.text C4).

## Readings

Every reading below was defined after reading the paper. Intervals are 95%. Outputs are in readings.text.

- The sign test with the declaration as the unit. With a declaration counted as aligned when at least 2 of its 3 replicates are, every
  judge stays below 10^-5 by exact two-sided sign test, deepseek-v4-flash at 2.9e-7 (147 of 218). Table 1's percentages are over
  declaration and replicate pairs. Per declaration they run from 82.1% (claude-sonnet-5) to 67.4% (deepseek-v4-flash). A single replicate
  alone does not reach 10^-5 for deepseek-v4-flash (replicates 1 and 2) or inkling-small (replicate 2) when ties count as misses.
- Ties. Ties are 3.9% to 8.9% of pairs, and Table 1 counts them as misses. make_frontier.py line 158 says ties are "vanishingly rare".
  With ties counted as misses, the chance line for alignment is 45.6% to 48.1% rather than 50%, so the 50% line is conservative.
- Order of the judges. Paired by declaration (declaration-clustered bootstrap, replicates nested in declaration), the gaps between
  muse-glimmer-30b, inkling-small and gpt-5.4-mini span zero under every tie rule, and their order changes when ties are left out.
  claude-sonnet-5 sits above gemini-3.7-flash with ties as misses (+5.5 points [+0.3, +10.6]) but not with ties halved (+3.2 [-1.4, +7.8])
  or left out (+1.8 [-3.0, +6.7]).
- Cost. Table 1's 0.136 per pair for gpt-5.4-mini equals the released token totals at 0.75 and 4.50 USD per million tokens with no cache
  discount (0.1355). make_frontier.py lists 0.25 and 2.00 for the same model, which gives 0.046.

## Run it

src/fetch_theirs.py downloads the six trace files and make_frontier.py at pinned revisions (FILES.tsv) and checks their hashes. Then run
src/known_good.py and src/readings.py with python3 from this folder (standard library only). CHECKS.md.text holds our checks.

Heuremen LLC
