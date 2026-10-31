# Santillana, arXiv 2610.02142: a recount and readings

Our recount of "Keyword Harnesses Fail Open: A Cheap Diagnostic Ladder for Tool-Use Claims in Small Language Models" by Juan S. Santillana
(arXiv 2610.02142), from the Hugging Face releases at pinned revisions. The plan was committed before the runs, with dated addenda after the
data and after the referee pass. One addendum was committed a minute after its reading ran, as PLAN.md.text records. GIT_LOG.txt lists the
commits with their times. This folder holds token ids, counts and probabilities, and no prompt or completion text.

The model code in the release carries no license, so the decoder here is our own, written from the architecture his model file describes
(RMSNorm, SwiGLU, rotate-half RoPE with theta 1e6 and none on every fourth layer, grouped-query attention, tied embeddings). It runs greedy
in fp32 on the CPU with a key-value cache. The prompt is the row text through <|assistant|>, encoded with his tokenizer.json and no BOS. We
stop at <|end|> or </s> or 256 new tokens, where his limit is unstated.

## What rebuilds

On the 269 corpus rows of section 6.8 (247 that expect a call, 22 that expect none), with two runs for each of the three main models
(identical token for token) and one run per factorial arm:
- 600M: 249 of 269 (his 0.926), exact copies 56 of 238 (0.235).
- Pre-remediation 1B: 27 of 269 (0.100), with 5 parseable calls, 3 of them exact.
- Repaired 1B: 258 of 269 (0.959), exact copies 243 of 246 (0.988).
- The five factorial arms of section 6.9: 269, 269, 268, 269 and 268 of 269, and exact copies 247 of 247 except diverse/low at 246 of 247.
- First-token probability of <|tool_call|>, median over the call rows: 1.6e-13 for the 600M (it opens with a newline, as section 6.7 says),
  7.7e-5 for the pre-remediation 1B, 0.996 for the repaired 1B.
- Section 6.6, repaired 1B against its parent: mean absolute drift 9.44e-6, max 5.98e-3, Frobenius norm 635.162769 to 635.163016, 97.7% of
  table entries unchanged.

## Readings

Every reading here was defined after reading the paper or after the data, as PLAN.md.text records.

- What the 6.8 rate counts (verbatim.text L1b, readings_c.text L1c). The rates rebuild only as a pass rate: a well-formed call on a row that
  expects one, or no call on a row that expects none. The printed intervals are the 2.5% and 97.5% binomial quantiles of those numerators
  (249 gives [0.892, 0.955], 27 gives [0.067, 0.138], 258 gives [0.933, 0.981]). Counted as calls on the 247 call rows only, the three
  models emit a well-formed call on 238, 5 and 246. The pre-remediation 0.100 is 5 calls and 22 correct no-calls. The two factorial arms at
  0.9963 are well-formed on all 247 call rows, and their one miss is a call opened on a row that expects none.
- The row-8 cosine (cos_rulers.text, readings_c.text F2b and F2c). The printed 0.99999583 and the norms 3.6246328 to 3.6246383 are what
  PyTorch's fp32 cosine_similarity and norm return. In fp64 the cosine is 0.99999539. Ranked in fp64 against all 32,768 rows, row 8 is more
  moved than 95.2% of them. By the printed pair (0.99999583 against the baseline mean 0.99999678) row 8 also moved slightly more than the
  baseline rows, so "marginally less moved than an average row" reads the other way. The change itself stays small, 1 minus the cosine being
  about 4.6e-6.
- The factorial arms against the same parent (drift.text, readings_c.text F2b). In every arm the <|tool_call|> row keeps a cosine of 0.9999947
  or higher, and its norm shrinks by 0.02% to 0.12%. Ranked in fp64, the share of rows less moved than row 8 is 54.8% and 73.2% in the two
  narrow arms, 45.9% in diverse/low, and 13.6% and 14.0% in the two diverse/high arms.

## Run it

src/fetch_theirs.py downloads the tokenizer and the corpus at pinned revisions (FILES.tsv) and checks their hashes. Then
src/read_verbatim.py --rates rebuilds every completion from the token ids in runs/ and prints verbatim.text (Python, tokenizers). To rerun the
decoder or the drift readings, src/fetch_weights.py downloads the eight weight files in WEIGHTS.tsv (about 30 GB) and checks them against the
hub's hashes. Weights are read with src/pt_safe.py, which parses the checkpoint without running anything from it. src/run_verbatim.py needs
PyTorch, and an hour or so on a laptop CPU for all eight checkpoints. CHECKS.md.text holds our checks.

Heuremen LLC
