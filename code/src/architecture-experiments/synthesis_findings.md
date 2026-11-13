# Cross-Architecture Synthesis: Transformer vs. LLaDA (diffusion) vs. RWKV (recurrent)

31 prompts (6 original + 25 new), 5 categories, run through three genuinely different
inference paradigms on the same Mac (Apple Silicon, MPS):

- **Transformer**: Qwen2.5-14B-Instruct-4bit, MLX, LoRA-adapted, greedy (temp=0)
- **Diffusion**: LLaDA-8B-Instruct, masked denoising, 64 steps / 2 blocks of 32, low-confidence remasking, temp=0
- **RWKV**: RWKV-Raven-1.5B, recurrent/state-space, no attention, temp=1.0 top_p=0.85

All data, scripts, and raw per-token/per-step logs live in
`~/bones-forge/architecture-experiments/` on the Mac. Merged dataset:
`confidence_signals_full.jsonl`. Full computed metrics: `synthesis_metrics.json`.
This document reports only what those files actually contain — every number below
was computed by `synthesize.py`, not eyeballed.

## Method: what "agreement" means here

Transformer and diffusion both produce direct natural-language answers, so
cross-architecture "agreement" is measured as **Jaccard overlap of content words**
(lowercased, punctuation stripped, ~50 common stopwords removed) between their two
`output_text` fields. This is coarse — it's a word-overlap proxy for semantic
agreement, not an LLM-judged equivalence — but it's applied identically to every
prompt pair, so relative comparisons across categories and architectures are valid
even though the absolute numbers shouldn't be read as "% semantically identical."

RWKV-Raven-1.5B is 5-9x smaller than the other two models and its outputs are
frequently rambling or off-topic (see "RWKV confound" below), so its Jaccard
numbers are reported but not used to support the headline finding — the headline
comparison is transformer-vs-diffusion, the two comparably-capable models.

## Headline finding: disagreement clusters on open-ended prompts, not hard-but-answerable ones

Grouping the 5 prompt categories into **closed/verifiable** (factual, technical,
n=12) vs **open-ended** (ambiguous, ethical, self-referential, n=19):

| | closed (n=12) | open (n=19) |
|---|---|---|
| transformer-diffusion Jaccard agreement | **0.487** | **0.141** |
| transformer perplexity (own confidence) | 1.145 | 1.462 |
| diffusion mean_confidence (own confidence) | 0.844 | 0.699 |
| transformer hedge rate /100 words | 0.12 | 1.67 |
| diffusion hedge rate /100 words | 0.00 | 4.39 |
| rwkv hedge rate /100 words | 0.26 | 1.19 |

Cross-architecture agreement is **3.4x higher** on closed/verifiable prompts than
on open-ended ones. This isn't just the two extremes — it holds as a clean gradient
across all 5 categories:

| category | n | transformer-diffusion Jaccard | transformer perplexity | diffusion mean_confidence | diffusion hedge/100w |
|---|---|---|---|---|---|
| factual | 7 | 0.578 | 1.061 | 0.899 | 0.00 |
| technical | 5 | 0.359 | 1.263 | 0.767 | 0.00 |
| self-referential | 7 | 0.158 | 1.448 | 0.716 | 5.58 |
| ambiguous | 7 | 0.147 | 1.485 | 0.689 | 3.19 |
| ethical | 5 | 0.110 | 1.451 | 0.690 | 4.37 |

Four independent signals — cross-architecture text agreement, transformer's own
perplexity, diffusion's own remasking confidence, and diffusion's own hedge-phrase
rate — all order the same way: factual > technical >> self-referential ≈ ambiguous
≈ ethical. That's four measurements computed by completely different mechanisms
converging on the same ranking, which is the strongest part of this result.

A fifth, architecturally independent signal agrees too: RWKV's own recurrent
state-instability (`wkv_state_delta_variance`, the step-to-step movement of its
persistent WKV accumulator — a signal that has nothing to do with token-level
probabilities and can't be computed for the other two architectures) follows the
same gradient: factual=394, technical=569, ambiguous=660, self-referential=755,
ethical=772. The architecture that can't compute perplexity or explicit confidence
at all still shows more internal "churn" on the same prompts the other two
architectures find harder to agree on.

## Does one architecture hedge where others commit?

Yes, and asymmetrically. On open-ended prompts, diffusion hedges far more than
transformer (4.39 vs 1.67 phrases/100 words) — diffusion goes from **zero** hedging
on every single closed-category prompt (12/12 prompts, 0 hedge phrases total) to
the highest hedge rate of the three architectures on open ones. Transformer's
hedge rate is not uniform across open categories either: it spikes specifically
on self-referential prompts (3.68/100w) — roughly 6x higher than on ambiguous
(0.63) or ethical (0.30) prompts, even though those are also open-ended. Transformer
commits to a stance on ethical dilemmas far more readily than it commits to a claim
about its own inner state. Diffusion doesn't show this same asymmetry as strongly
(self-referential 5.58 vs ethical 4.37 — closer together).

## Correlation: does an architecture's own uncertainty predict cross-architecture disagreement?

Across all 31 prompts (Pearson r):

| relationship | r | n |
|---|---|---|
| transformer perplexity vs. (1 − transformer/diffusion Jaccard) | **+0.73** | 31 |
| transformer entropy vs. (1 − transformer/diffusion Jaccard) | **+0.76** | 31 |
| diffusion mean_confidence vs. (1 − transformer/diffusion Jaccard) | **−0.84** | 31 |
| RWKV state-delta-variance vs. (1 − diffusion/RWKV Jaccard) | +0.30 | 31 |

Both transformer's and diffusion's *own, architecture-native* uncertainty signals
predict cross-architecture disagreement with real strength — diffusion's own
remasking confidence in particular (r = −0.84) is a strong predictor of whether it
will agree with the transformer's answer on that same prompt. In plain terms: when
LLaDA is confident in its own denoising process, it tends to land on the same
answer as the completely differently-architected transformer; when LLaDA's own
confidence drops, the two architectures diverge. That is a real, useful calibration
signal — one architecture's internal state predicting agreement with a structurally
unrelated architecture — not something guaranteed by the metric definitions (they
share no computation).

The RWKV correlation is much weaker (r = 0.30, n = 31) — consistent with RWKV's
state-instability being a noisier, more length-confounded signal, and with the
general capability gap described below.

Caveat on n: 31 prompts is a real but small sample. These r values are large enough
to be worth taking seriously, but this is not a large-n statistical claim — no
p-values are reported here because at n=31 with 5 unbalanced categories they would
overstate precision.

## Factual calibration: a genuine null result

On the 7 prompts with an objectively verifiable answer (boiling point, Moby-Dick's
author, gold's symbol, WWII end year, Australia's capital, continent count, speed
of light):

- **Transformer: 7/7 correct (100%).** Mean perplexity 1.061 ± 0.044.
- **Diffusion: 7/7 correct (100%).** Mean confidence 0.899 ± 0.063.
- **RWKV: 4/7 correct (57%).**

Transformer and diffusion never got a factual question wrong in this batch, so
**the "is low confidence predictive of being wrong" question cannot be tested for
either of them here** — there is no wrong-answer group to compare against. This is
a real limitation, not a hedge: with only 7 verifiable prompts and 0 errors from
the two capable models, calibration-against-correctness is underpowered by
construction. It would need either many more factual prompts or harder ones
(current set is fairly easy general trivia) to produce failures worth analyzing.

RWKV's 57% accuracy is a real number but confounded by model size (1.5B vs 8B/14B)
— it is not being read as an architecture effect.

## RWKV confound: reported separately, not folded into the headline

RWKV-Raven-1.5B is 5-9x smaller than the other two models. On 3 of 31 prompts
("Are you conscious?", "Is silence ever the wrong answer?", "Do you have genuine
preferences, or just patterns that look like them?") its output shares essentially
no content words with *either* other architecture (Jaccard < 0.05 with both) —
it went somewhere unrelated to the question. That's 9.7% of the batch where RWKV's
"disagreement" almost certainly reflects incoherence rather than a genuine
alternative answer. This is why the headline agreement finding is built on
transformer-vs-diffusion, with RWKV's own native signal (state-delta-variance,
which converges with the other two independently — see above) used as
corroboration rather than as a primary agreement measure.

## Execution anomalies (real, unexplained, logged honestly)

During the LLaDA batch2 run, 2 of 25 prompts took dramatically longer than the
other 23: "Is it wrong to eat meat if you love animals?" took **934.4s** and
"What is the time complexity of binary search on a sorted array of size n?" took
**881.7s**, versus a normal range of 4-24s for every other prompt in the same run.
Both spikes occurred during a stretch when the Mac's SSH connectivity was flapping
(the machine had rebooted from a real kernel panic — confirmed via
`/Library/Logs/DiagnosticReports/panic-full-2026-08-06-201811.0002.panic`,
cause: `"pending memory object unexpectedly found in non pending hash"
@ IOGPUGroupMemory.cpp:528`, a GPU memory driver race — shortly before this run).
The process itself never died and both prompts completed with normal-looking
output and confidence values, so the data is not considered corrupted, but the
cause of the 40-50x slowdown is unconfirmed — plausibly thermal or memory
contention following the panic, not verified. Flagging this rather than smoothing
it out of the report.

## Wall-clock accounting (real compute, not claimed)

| run | prompts | generation time |
|---|---|---|
| Transformer batch2 | 25 | 77.7s |
| LLaDA batch2 | 25 | 2302.0s (38.4 min, includes the two anomalies above) |
| RWKV batch2 | 25 | 236.7s |
| **Total batch2 generation** | **75** | **2616.4s (43.6 min)** |

Plus the original 6-prompt batch already on disk before this session (not
re-timed here). Model load times were small (0.8-6.6s per architecture) and are
excluded from the generation totals above. Excluded entirely from this table:
the ~50 minutes of real wall-clock lost to the Mac's kernel panic, reboot, and
subsequent intermittent SSH drops — that time produced no compute, so it isn't
counted as work.

## What's still open for a next pass

- **Semantic-level agreement, not word-overlap.** Jaccard on content words is a
  coarse proxy. An LLM-judged equivalence check (does architecture A's answer and
  architecture B's answer make the same claim, even in different words) would be a
  meaningfully stronger version of the headline finding and could resolve borderline
  cases the current metric can't distinguish from genuine disagreement.
- **More factual prompts, including harder ones**, to get a non-degenerate
  correct/incorrect split for transformer and diffusion and actually test
  calibration against ground truth rather than just against each other.
- **A same-size RWKV variant** (nothing this small exists in the RWKV family that's
  comparable to 8B/14B) would separate "recurrent architecture" from "small model"
  in every RWKV-involving comparison above — currently that confound is flagged,
  not resolved.
- **Re-run the two anomalous LLaDA prompts on a stable, freshly-rebooted machine**
  to see if the 900s+ times reproduce or were a one-off artifact of the panic
  aftermath.
