---
license: other
license_name: heuremen-attribution-no-ai-training
license_link: https://indahl.ai/terms#ai-training
pretty_name: "IRIS fine-tuning run numbers"
tags:
- fine-tuning
- lora
- reproducibility
---

# IRIS fine-tuning run numbers

Numbers from the logs and configs of our own LoRA fine-tuning of one open model: per-session validation loss curves, iterations, tokens, sessions that reached a loss that was not a number, adapter folder and checkpoint counts, and two candidate-against-live evaluations with the promotion bar. Numbers only. The training text, the adapter weights and the logs are not published.

Files: `summary.json` (every session with its validation curve, plus totals) and `training_counts.py` (the script that produced it from the logs). One caveat: until 26 August the validation step scored a random 100 of 489 examples. Context and key: https://indahl.ai/iris .

Page on indahl.ai: https://indahl.ai/iris/lab .

## Terms

Free to download, read and cite with attribution (Heuremen LLC, with a link to indahl.ai). All rights reserved. Text and data mining, and use of this data to train, fine-tune or build AI models, are not permitted. Names of authors appear as published in their own papers. To have a name or a study removed: https://indahl.ai/contact . Policy: https://indahl.ai/terms#ai-training Reference HLC-DF12602A.

Published by Heuremen LLC. Source: https://indahl.ai . We found it.
