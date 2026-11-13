# Recount plan: arXiv 2610.24999v1 (PIAtlas SoK; Damianakis, Psounis, USC), committed before computing
Ack read: no funder statement in the PDF. Eligible free row.
Data: calib/b1a, b1b, b4, b8 .jsonl (64 records; LLM technique labels at batch sizes 1, 1, 4, 8), calib/decision.json.
## A. Recount decision.json agreement: micro-F1 over technique-code sets and class sets (class = code before ".T"), b1a vs b1b, b4 / b8
   vs each b1. Printed: technique 0.968 b1a-b1b; 0.947 / 0.933 (b4), 0.951 / 0.937 (b8); class 0.985 / 0.966 / 0.958 / 0.966 / 0.951.
## B. Pricing: BATCH CARRIER. For each batched run, agreement with the two b1 runs minus the b1a-b1b agreement (the run-to-run floor),
   record bootstrap (20,000, seed 20261025), micro-F1 recomputed per draw. ABOVE / CONSISTENT / BELOW.
