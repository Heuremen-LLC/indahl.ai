# Gupta, arXiv 2610.31657: a recount and readings

Our recount of "Cost-Aware Abstention for LLM-Based IT Ticket Classification" by Sachin Gupta (arXiv 2610.31657), from the author's
Zenodo supplement. The plan was committed before each reading was computed. GIT_LOG.txt lists the commits with their times.

## What rebuilds

From his per-ticket files, with our own code, accuracy for every prompted run equals the stored value and his Table III (readings.text).

## Readings

Every reading below was defined after reading the paper and code. Model names follow his configuration: GPT-4o-mini (alias, queried
22 May 2026), Claude Haiku 4.5, Qwen2.5-7B-Instruct-Turbo and Meta-Llama-3-8B-Instruct-Lite on Together, which the provider documents as
FP8 and INT4.

- Confidence and the examples. Every few-shot example in his prompt template shows "confidence": 1.0. With those examples, model-reported
  confidence is exactly 1.0 for GPT-4o-mini on 1,000 of 1,000 tickets, for Llama on 849 of its 849 parsed replies, and for Qwen on 853 of
  1,000. Without them (zero-shot) the counts are 0, 1 and 8. Claude Haiku 4.5 reports 1.0 on 19 of 1,000 with the examples, so the pattern
  is not uniform. This is an association with the prompt, and no cause is named.
- Ranking signal. The correctness AUROC of model-reported confidence in the few-shot runs is 0.500 for GPT-4o-mini, 0.509 for Qwen and
  0.664 for Claude Haiku 4.5. For Llama it is 0.601 over all tickets and 0.500 over its parsed replies, so its signal comes from the 0.0
  the pipeline assigns to the 151 parse failures.
- Intervals for accuracy. Wilson 95% intervals for every run, and the paired few-shot minus zero-shot change per model with an exact
  McNemar p. Llama's change (-0.123) includes its 151 parse failures, scored wrong as the paper scores them.

## Run it

src/fetch_theirs.sh downloads the Zenodo supplement, checks its hash, and unpacks it into theirs/unz. Then run src/readings.py with
python3 from this folder. Versions are in VERSIONS.txt. CHECKS.md.text holds our checks.

Heuremen LLC
