# NIGHT ladder (13 Nov 2026): rows written by night_decide.py after each eval

base: hand 9/27 pos, 1/30 neg; pipeline 6/23 pos, 0/39 neg

| time | model | test_hand | test_pipeline | route |
|---|---|---|---|---|
| 15:29 | lora_v3 | 0/27 pos, 0/30 neg | 0/23 pos, 0/39 neg | collapse | next lora_v4: data_short, lr 1e-5, 600 iters
| 16:22 | lora_v4 | 19/27 pos, 5/30 neg | 15/23 pos, 4/39 neg | partial | next lora_v5: data_bal, lr 2e-5, 1200 iters
| 17:57 | lora_v5 | 0/27 pos, 0/30 neg | 0/23 pos, 0/39 neg | collapse | next lora_v6: data_short, lr 2e-5, 1200 iters
| 19:32 | lora_v6 | 20/27 pos, 6/30 neg | 17/23 pos, 4/39 neg | partial | ladder stopped
| 19:41 | (Bones) | | | added by hand on Wayfinder's "hit a training loop or two" | next lora_v7: data_short, lr 1e-5, 1200 iters (between v4 and v6) |
| 20:49 | (Bones) | paper vote, defined after the data | v6 k>=1: 19/23 papers caught, 5/10 clean flagged (hand); k>=2: 1/23, 1/10 | errors sit in one chunk, so a vote kills recall; next: score-based threshold (eval with yes/no probabilities) after v7 |
