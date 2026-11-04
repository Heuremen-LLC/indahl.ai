# YO Read: checks of the paper-reading adapter

YO Read is a LoRA adapter on Qwen3-1.7B trained to answer three questions about a quantum-hardware paper: does it print the dates of its own hardware runs (DATES), does it link its own data or code (LINK), and does it say its data are available on request (REQUEST). It is scored on 148 held-out papers.

- `results_rescore.text`: YO Read seeds 61-63 against always answering NO, exact McNemar, Holm across 9.
- `shuffled/`: the shuffled-label check. Plan and five addenda, each OpenTimestamped (`*.ots`) and confirmed in Bitcoin block 974519 before training began. Three adapters (seeds 71-73) trained on the same papers with YES/NO answers shuffled within each question. Result: `shuffled/results_shuffled.text`.
- `shuffled/selflabel/`: the self-label check (Addenda 2-5). The base model's own answers replace the real ones; three adapters (seeds 74-76). The base-rate report was written before training (`BASE_RATES.text`), and the scorer was committed before any reply existed. Result: `shuffled/selflabel/results_selflabel.text`.
- `eval_rescore_*.jsonl`: every reply from every adapter, per paper and question.

Results as stamped: three adapters trained on shuffled answers did not reproduce the gain. On DATES and LINK the gain is not shown to need the real answers (three seeds may be too few). Paths inside configs are the paths on the machine that ran them.

- `fresh/`: the fresh test. Plan OpenTimestamped before any adapter answers a fresh item; the driver refuses to run until the plan is in a Bitcoin block. Item prompts quote sentences from the papers and are not published; their hash is in `DATA_YO_FRESH.sha256`, and `yf_build.py` rebuilds them from the List.
