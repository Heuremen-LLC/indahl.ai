# STAN A full-text teacher re-baseline, gold dev only

Source rows: teachers_ft/outputs.jsonl. All numbers: teachers_ft/summary.json (made by teachers_ft/score_ft.py). Prompt: teachers_ft/prompt_template.txt. Gold flags: data/gold_items.json codes field (recount flags). Ceiling labels: ceiling_ft/judgments.jsonl (all-keys rule). Intervals are Wilson 95 percent.

A flagged pair is gold PRESENT. An unflagged pair is "not flagged", not absent. Recall is the share of flagged pairs the teacher called PRESENT. False-flag rate is the share of unflagged pairs the teacher called PRESENT. Grounding is the share of PRESENT and ABSENT calls whose quote is verbatim (whitespace normalised) in a retrieved chunk. No call was converted; statuses are as written.

## gemma

### F1 (92 papers)
- Recall on flagged pairs: 19/24=0.79 [0.59,0.91]
- False-flag rate on unflagged pairs: 59/68=0.87 [0.77,0.93]
- Recall, ceiling IN pairs: 11/13=0.85 [0.58,0.96]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 7/8=0.88 [0.53,0.98]
- Grounding of PRESENT/ABSENT calls: 20/91=0.22 [0.15,0.32] (named chunk 16, other retrieved chunk 4, not found 71)
- PRESENT and grounded, flagged / unflagged: 4/24=0.17 [0.07,0.36] / 16/68=0.23 [0.15,0.35]
- CANNOT_TELL rate: 0/92=0.00 [0.00,0.04]; ABSENT rate: 13/92=0.14 [0.08,0.23]
- Parse failures: 0; call errors: 0; wall seconds: 897
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.22, 0.142] -> no pass

### F2 (92 papers)
- Recall on flagged pairs: 35/35=1.00 [0.90,1.00]
- False-flag rate on unflagged pairs: 57/57=1.00 [0.94,1.00]
- Recall, ceiling IN pairs: 14/14=1.00 [0.79,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 18/18=1.00 [0.82,1.00]
- Grounding of PRESENT/ABSENT calls: 7/92=0.08 [0.04,0.15] (named chunk 6, other retrieved chunk 1, not found 85)
- PRESENT and grounded, flagged / unflagged: 2/35=0.06 [0.02,0.19] / 5/57=0.09 [0.04,0.19]
- CANNOT_TELL rate: 0/92=0.00 [0.00,0.04]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 804
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.14, 0.108] -> no pass

### F6 (92 papers)
- Recall on flagged pairs: 27/29=0.93 [0.78,0.98]
- False-flag rate on unflagged pairs: 62/63=0.98 [0.92,1.00]
- Recall, ceiling IN pairs: 8/9=0.89 [0.56,0.98]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 14/15=0.93 [0.70,0.99]
- Grounding of PRESENT/ABSENT calls: 46/89=0.52 [0.41,0.62] (named chunk 39, other retrieved chunk 7, not found 43)
- PRESENT and grounded, flagged / unflagged: 12/29=0.41 [0.26,0.59] / 34/63=0.54 [0.42,0.66]
- CANNOT_TELL rate: 0/92=0.00 [0.00,0.04]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 3; call errors: 0; wall seconds: 927
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.323, 0.091] -> no pass

### F3 (92 papers)
- Recall on flagged pairs: 20/22=0.91 [0.72,0.97]
- False-flag rate on unflagged pairs: 69/70=0.99 [0.92,1.00]
- Recall, ceiling IN pairs: 10/10=1.00 [0.72,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 9/11=0.82 [0.52,0.95]
- Grounding of PRESENT/ABSENT calls: 25/89=0.28 [0.20,0.38] (named chunk 21, other retrieved chunk 4, not found 64)
- PRESENT and grounded, flagged / unflagged: 8/22=0.36 [0.20,0.57] / 17/70=0.24 [0.16,0.35]
- CANNOT_TELL rate: 0/92=0.00 [0.00,0.04]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 3; call errors: 0; wall seconds: 813
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.08, 0.344] -> no pass

## llama

### F1 (92 papers)
- Recall on flagged pairs: 1/24=0.04 [0.01,0.20]
- False-flag rate on unflagged pairs: 3/68=0.04 [0.01,0.12]
- Recall, ceiling IN pairs: 0/13=0.00 [0.00,0.23]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 1/8=0.12 [0.02,0.47]
- Grounding of PRESENT/ABSENT calls: 0/4=0.00 [0.00,0.49] (named chunk 0, other retrieved chunk 0, not found 4)
- PRESENT and grounded, flagged / unflagged: 0/24=0.00 [0.00,0.14] / 0/68=0.00 [0.00,0.05]
- CANNOT_TELL rate: 58/92=0.63 [0.53,0.72]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 819
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.053, 0.138] -> no pass

### F2 (92 papers)
- Recall on flagged pairs: 2/35=0.06 [0.02,0.19]
- False-flag rate on unflagged pairs: 2/57=0.04 [0.01,0.12]
- Recall, ceiling IN pairs: 1/14=0.07 [0.01,0.32]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 1/18=0.06 [0.01,0.26]
- Grounding of PRESENT/ABSENT calls: 1/4=0.25 [0.05,0.70] (named chunk 1, other retrieved chunk 0, not found 3)
- PRESENT and grounded, flagged / unflagged: 0/35=0.00 [0.00,0.10] / 1/57=0.02 [0.00,0.09]
- CANNOT_TELL rate: 23/92=0.25 [0.17,0.35]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 828
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.093, 0.083] -> no pass

### F6 (92 papers)
- Recall on flagged pairs: 2/29=0.07 [0.02,0.22]
- False-flag rate on unflagged pairs: 2/63=0.03 [0.01,0.11]
- Recall, ceiling IN pairs: 1/9=0.11 [0.02,0.43]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 1/15=0.07 [0.01,0.30]
- Grounding of PRESENT/ABSENT calls: 1/4=0.25 [0.05,0.70] (named chunk 0, other retrieved chunk 1, not found 3)
- PRESENT and grounded, flagged / unflagged: 0/29=0.00 [0.00,0.12] / 1/63=0.02 [0.00,0.09]
- CANNOT_TELL rate: 53/92=0.58 [0.47,0.67]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 825
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.085, 0.102] -> no pass

### F3 (92 papers)
- Recall on flagged pairs: 0/22=0.00 [0.00,0.15]
- False-flag rate on unflagged pairs: 4/70=0.06 [0.02,0.14]
- Recall, ceiling IN pairs: 0/10=0.00 [0.00,0.28]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 0/11=0.00 [0.00,0.26]
- Grounding of PRESENT/ABSENT calls: 0/4=0.00 [0.00,0.49] (named chunk 0, other retrieved chunk 0, not found 4)
- PRESENT and grounded, flagged / unflagged: 0/22=0.00 [0.00,0.15] / 0/70=0.00 [0.00,0.05]
- CANNOT_TELL rate: 39/92=0.42 [0.33,0.53]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 814
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.052, 0.149] -> no pass

## mistral

### F1 (92 papers)
- Recall on flagged pairs: 24/24=1.00 [0.86,1.00]
- False-flag rate on unflagged pairs: 67/68=0.98 [0.92,1.00]
- Recall, ceiling IN pairs: 13/13=1.00 [0.77,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 8/8=1.00 [0.68,1.00]
- Grounding of PRESENT/ABSENT calls: 35/91=0.39 [0.29,0.49] (named chunk 20, other retrieved chunk 15, not found 56)
- PRESENT and grounded, flagged / unflagged: 13/24=0.54 [0.35,0.72] / 22/68=0.32 [0.22,0.44]
- CANNOT_TELL rate: 1/92=0.01 [0.00,0.06]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 1122
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.006, 0.423] -> no pass

### F2 (92 papers)
- Recall on flagged pairs: 35/35=1.00 [0.90,1.00]
- False-flag rate on unflagged pairs: 56/57=0.98 [0.91,1.00]
- Recall, ceiling IN pairs: 14/14=1.00 [0.79,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 18/18=1.00 [0.82,1.00]
- Grounding of PRESENT/ABSENT calls: 40/91=0.44 [0.34,0.54] (named chunk 21, other retrieved chunk 19, not found 51)
- PRESENT and grounded, flagged / unflagged: 18/35=0.51 [0.36,0.67] / 22/57=0.39 [0.27,0.52]
- CANNOT_TELL rate: 1/92=0.01 [0.00,0.06]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 1108
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.077, 0.322] -> no pass

### F6 (92 papers)
- Recall on flagged pairs: 29/29=1.00 [0.88,1.00]
- False-flag rate on unflagged pairs: 62/63=0.98 [0.92,1.00]
- Recall, ceiling IN pairs: 9/9=1.00 [0.70,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 15/15=1.00 [0.80,1.00]
- Grounding of PRESENT/ABSENT calls: 44/91=0.48 [0.38,0.58] (named chunk 35, other retrieved chunk 9, not found 47)
- PRESENT and grounded, flagged / unflagged: 10/29=0.34 [0.20,0.53] / 34/63=0.54 [0.42,0.66]
- CANNOT_TELL rate: 1/92=0.01 [0.00,0.06]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 1065
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.382, 0.024] -> no pass

### F3 (92 papers)
- Recall on flagged pairs: 21/22=0.95 [0.78,0.99]
- False-flag rate on unflagged pairs: 70/70=1.00 [0.95,1.00]
- Recall, ceiling IN pairs: 10/10=1.00 [0.72,1.00]
- Recall, ceiling OUT or NOT_IN_TEXT pairs: 10/11=0.91 [0.62,0.98]
- Grounding of PRESENT/ABSENT calls: 38/91=0.42 [0.32,0.52] (named chunk 28, other retrieved chunk 10, not found 53)
- PRESENT and grounded, flagged / unflagged: 8/22=0.36 [0.20,0.57] / 30/70=0.43 [0.32,0.55]
- CANNOT_TELL rate: 1/92=0.01 [0.00,0.06]; ABSENT rate: 0/92=0.00 [0.00,0.04]
- Parse failures: 0; call errors: 0; wall seconds: 1120
- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: [-0.268, 0.169] -> no pass
