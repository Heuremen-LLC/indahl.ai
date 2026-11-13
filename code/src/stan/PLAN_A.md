# STAN A: full-text plan (draft for Sage, 12 Nov 2026). Nothing in it has run.

## Why
Abstract-only STAN is closed (results/v2_prep.md, results/f2_hand_read.md). The abstract carries little of what the standard asks,
and local teachers agreeing on abstracts did not produce valid F2 labels (about 1 in 12 ABSENT and at most 2 in 12 PRESENT quotes
supported their label).

## Inputs, frozen here
- Corpus: open-access full text only. Gold coverage 185 of 197 (dev 93 of 98, test 92 of 99), data/fulltext_coverage.json. The 12
  missing are listed there and stay out; 08c4a2608cbe (254 characters extracted) stays out.
- Extraction: pypdf 6.21.1, page text joined with a form feed, no OCR. A paper under 2,000 characters is out.
- Chunking: 1,200 Qwen3 tokens per chunk, 150-token overlap, chunk ids carry page numbers.
- Retrieval per code: BM25 (rank_bm25, version pinned at install) over the paper's own chunks. The query is the code's Test and
  PRESENT/ABSENT lines from the standard plus fixed cue lists written in QUOTABLE_FT.md before any label is read. Top 6 chunks,
  in page order. Total input capped at 8,192 tokens; if over, drop the lowest-ranked chunk.
- Output order: quote, chunk id, status, reason. A quote must be a verbatim substring of the named chunk (ws() normalisation).
  An ungrounded call is recorded with its flag and original status. Nothing is converted.

## Cells
QUOTABLE_FT.md will re-derive, from the standard's text alone and before any full-text label is read, which code/status cells a
quote from the paper body can show. Same rule as QUOTABLE.md, with the paper body in place of the abstract: not quotable when the
Test needs (a) a released file outside the PDF, (b) a recomputation or new run. Expected (to be confirmed in that file, not here):
F1, F2, F3 and F6 both ways; F4 PRESENT only for the "method not stated well enough" clause; F5 and F7 not quotable.

## Labels
- Teachers: the same three local models (Llama 3.1 8B, Mistral 7B, Gemma 3 4B), temperature 0, seed 0, on the retrieved chunks.
  Round 1 blind. No round 2 crosstalk: v1 forensics showed round 2 led agreement (80 of 89 CT agreed only after seeing others).
- Silver: three-way grounded agreement on a quotable cell. CT is silver only when all three chose it.
- Gate before any training: a hand read by Bones of a seeded sample of 12 rows per surviving cell. A cell trains only if at least
  8 of 12 quotes support their label by the rule. Cells that fail are reported, not trained.
- Cap by status per code. Codes under 15 train rows are reported as untested.

## Training and selection
Base Qwen3-1.7B, LoRA rank and steps as v1. Grouped 5-fold by paper over silver for selection; the stopping step is fixed in
advance at the fold-mean minimum of a pre-run schedule (100, 200, 300, 400). Status-token diagnostic on held-out silver: P(status)
must vary by true class (named test: per class mean P, and a permutation test over rows) before anything reads gold.

## Gold
- Reused gold (the 197) is spent for confirmation. Any reading on it is labelled a second look; the strongest verdict is
  "not rejected".
- Fresh gold: about 40 new recounts from full text, chosen by seed from the QIA List pool excluding every paper already in pool,
  silver, gold or twins, recounted and signed off by Bones row by row, frozen with a sha256 and an OTS stamp submitted before any
  teacher call on them. The keep rule for STAN A is read once on these.
- Keep rule, pre-registered: on fresh gold, per quotable cell, STAN's committed calls beat both the per-code constant predictor and
  a named lexical baseline (cue present in the retrieved chunks), paired, 95 percent bootstrap over papers, the whole interval above
  zero. Recall against recount flags reported descriptively per code.

## Order
1. QUOTABLE_FT.md frozen. 2. Fresh 40 chosen and recounted, frozen. 3. Retrieval built and checked on 5 dev papers by hand (does
the retrieved text contain the recount's evidence?). 4. Teachers on the training pool. 5. Hand-read gate. 6. Train. 7. Diagnostic.
8. Read fresh gold once.
