# Read in full: Q8_0 session 1 (31 Oct 2026, before any rate was computed)
- 10 completions sampled by read_bridge.py --sample (seed 7), each read in full at its end beside both scorers' answers.
- 10 of 10: the Table 7 scorer returns the answer the reply states (a "####" line or a boxed number); the run-time rule returns it only where
  "####" is used. Every sampled completion ended with finish reason stop.
Verdict: no scorer slip in what was read.
