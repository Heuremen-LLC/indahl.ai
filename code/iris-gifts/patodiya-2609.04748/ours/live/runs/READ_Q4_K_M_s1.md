# Read in full: Q4_K_M session 1 (31 Oct 2026, before any rate was computed)
- 10 completions sampled by read_bridge.py --sample (seed 7), each read in full at its end beside both scorers' answers.
- 9 of 10: the Table 7 scorer returns the answer the reply states (a "####" line or a boxed number); the run-time rule returns it only
  where "####" is used, as her run-time rule does.
- 1 of 10 (item 155, warm pass): the reply ends with the answer in bold followed by a word, which no Table 7 pattern matches, so it scores as
  no answer. That is her scorer's rule (rebuilt exactly on her own logs in known_good_reader.text), applied the same way to her runs and ours.
- Every sampled completion ended with finish reason stop.
Verdict: the Table 7 scorer reads these replies as it reads hers; the one miss is her rule, not a parse slip of ours.
