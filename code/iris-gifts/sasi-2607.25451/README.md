# Sasi, arXiv 2607.25451: a recount, readings and a live reference run

Our recount of "Bits and Memories: Measuring Verbatim Extraction Across LLM Quantization" by Akshay Sasi (arXiv 2607.25451), from the
result files and sampled sequences in the Hugging Face dataset AkshaySasi/bits-and-memories at aa3db05. The plan was committed before each
reading was computed. GIT_LOG.txt lists the commits with their times. Sequences are handled as token ids only, and no training text is
printed anywhere in this folder.

## What rebuilds

All 16 rows of Table 1 rebuild from the result files to the printed digits, using the Pile perplexity files for c and s (readings.text, K).

## Readings

Every reading below was defined after reading the paper. Intervals are 95%.

- Intervals. Wilson intervals for every extraction rate at n 500, and unpaired Newcombe intervals for each difference from the reference,
  since the files hold counts only (a paired interval from per-sequence outcomes would be narrower if outcomes agree across precisions).
  Every four-bit drop clears zero, for example 410M NF4 0.228 [0.193, 0.267], minus the reference -0.606 [-0.652, -0.554]. FP16 and INT8
  differ from the reference by at most 2.4 points, and every one of those intervals includes zero.
- The larger samples. The release holds two further 410M samples of 2,000 sequences (seeds 1 and 2) at FP16 and NF4 that the paper does not
  cite. Memorization lost against FP16 is 0.723 at n 500 and 0.739 and 0.747 on the larger samples, in line with "nearly three-quarters".
- Two sentences. The 0.718 behind "over seventy percent of memorized sequences" is the NF4 extraction rate over the FP16 rate (0.596 over
  0.830). Of the 500 sampled sequences, 0.596 are extracted. Selectivity for 1B NF4 is 6.97 with WikiText and 7.97 with Pile perplexity
  (Table 1 prints 8.0).
- The reference itself. The paper describes the samples as sequences the full-precision model reproduces greedily, and the references
  extract 0.756, 0.834 and 0.830. We reran the reference on our Mac CPU in FP32 with the same weights by revision, the same sampled sequences
  and the same generate call (src/live). We get the same counts, mean prefix and token accuracy as his 160M and 410M FP32 references, and the
  same exact-match rate and prefix as his 1B FP16 reference. Two repeats differ on none of the 500 sequences per model. So 122, 83 and 85 of
  the 500 sampled sequences are not reproduced under this protocol on his GPU (FP32 at 160M and 410M, FP16 at 1B) and on our CPU (FP32). No
  released file says why. Per-sequence agreement with his runs cannot be checked, since his files hold aggregates.

## Run it

src/fetch_theirs.py downloads the result files and sampled sequences at the pinned revision (FILES.tsv) and checks their hashes. Then run
src/readings.py and src/live/read_l1.py with python3 from this folder (standard library). src/live/run_l1.py reruns the reference and needs
torch and transformers (VERSIONS.txt, src/live/SETUP_L1.md). CHECKS.md.text holds our checks.

Heuremen LLC
