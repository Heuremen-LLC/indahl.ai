# Read in full: Q3_K_M session 1 (31 Oct 2026, before any rate was computed)
- 10 completions sampled by read_bridge.py --sample (seed 7): items 11, 133, 80, 56, 17, 155, 47, 57, 78, 139 (cold, cold2 and warm passes),
  each read in full at its end beside both scorers' answers.
- 10 of 10: the Table 7 scorer and the run-time rule both return the answer the reply states on its "####" line. In item 78 the "####"
  sits mid-line ("Vincent saves #### 6.00") and both read 6.00.
- Item 155 (warm), which in Q4_K_M session 1 ended in bold text that no Table 7 pattern matched, here ends with a "####" line and is read.
- Every sampled completion ended with finish reason stop (no truncation at the length limit).
Verdict: the Table 7 scorer reads these replies as it reads hers; no parse slip found in the sample.
