# Chen, arXiv 2609.00363: a recount and readings

Our recount of "Deterministic LLM Inference Across GPU Kernels: Power-of-Two INT8 Quantization Scales and the Limits of Tolerance-Based
Conformance" by Teng-Ruei Chen (arXiv 2609.00363), from the public repository luka-krixvon/deterministic-int8-llm-inference at 689cc52
(tag v1.0.1). The plan was committed before the readings, with a dated addendum after the referee pass. GIT_LOG.txt lists the commits
with their times. Nothing of theirs is run. Their checkpoints are unreleased and the kernels are CUDA only, so every reading here is on
their recorded files.

## What rebuilds

With our own code, the fault-injection scorecard (8,232 cells against the pinned matrix), Table IV, Table V (8 of 196 and 10 of 252
layers identical under the checkpoints' own scales, all identical after requantizing, 0 of 8 against 8 of 8 sequences at each size), and
the companion's Tables II and III. The layers have K of 2,048 and 6,144, not "1,042 to 12,288".

## Readings

Every reading after the first set was defined after the data, as PLAN.md.text records.

- Prefill against decode, with counts (readings.text K1, readings_b.text K1b and K1c). On the 8-prompt grid, CUTLASS prefill's top-1 token
  differs from its own decoded token at 44 of 512 positions (8.6%, Clopper-Pearson [6.3, 11.4]). Seven of the 44 are exact log-probability
  ties, which the harness breaks toward the higher token id. Leaving those out and leaving out position 0 (the prefill pass) gives 37 of 504.
  Both teacher-forced files use the CUTLASS greedy output as the rail, so the Triton figure, 55 of 512, is Triton prefill against the CUTLASS
  decode. No released file holds a Triton-railed run. On the 64 x 256 grid (its rail is tokens64_CUTLASS.json, matched by hash to the
  manifest), the two arms differ from the rail at 766 and 834 of 16,384 positions, a Triton excess of 0.42 points [+0.09, +0.73] by
  prompt-cluster bootstrap. The CUTLASS rate falls by position: 7.6%, 5.5%, 3.4% and 2.2% across the four 64-token windows.
- Where the two kernels part (K2). Under the checkpoints' own scales, the first token at which CUTLASS and Triton greedy sequences differ
  has a median index of 2.0 at 1.7B, 2.5 at 8B and 7.0 at 14B (8 prompts each, ranges 0 to 33, 0 to 36 and 0 to 41). Over the companion's 64
  prompts the median is 5.5 and 9 of 64 differ at the first generated token. Eight prompts per size cannot order the sizes.
- The same kernel across two runs (K2b). The 8 prompts of the 8-prompt run also appear, with the same prompt lengths, in the 64-prompt run.
  Within the first 64 tokens, CUTLASS agrees with itself across the two runs on 0 of 8 sequences (first differing index median 10) and Triton
  on 0 of 8 (median 8.5). The repeats inside the 8-prompt run are identical for both kernels.
- Scorecard intervals (K3). In the real-scale regime, F1, F2, F3 and F4 move the output in 439, 448, 205 and 478 of 588 cells each, and no
  applicable check fires on any of them (95% upper bounds 0.8%, 0.8%, 1.8% and 0.8%). F5 moves one cell, not detected, as the repository's
  corrections note says.

## Run it

src/fetch_theirs.py downloads the 28 artifact files from the repository at the pinned commit (FILES.tsv) and checks every hash. Then run
src/readings.py and src/readings_b.py with python3, numpy and scipy from this folder. CHECKS.md.text holds our checks.

Heuremen LLC
