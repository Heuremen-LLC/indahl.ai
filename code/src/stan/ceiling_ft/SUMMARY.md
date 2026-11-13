# STAN A full-text retrieval ceiling (dev only)

Pre-registered in PLAN_A_CEILING.md. Settings frozen (pypdf 6.21.1, 1,200-token Qwen3 chunks, 150 overlap, BM25 rank_bm25 0.2.2, query = Test + PRESENT + ABSENT lines, top 6). Pass line IN/(IN+OUT) >= 0.60, Wilson 95% lower bound beside it, untested under 10 decided pairs.
Judge: Claude Sonnet 5.5, same model family as the abstract-ceiling judge, one reader who sees the note (not blind to the label). Prompt: ceiling_ft/judge_prompt.txt. Bones second read on the seeded 20 (bones_sample_20.json) is NOT yet done, so no disagreement count exists.
Unit: 196 (dev paper, code) pairs from ceiling/judgments.jsonl whose paper has full text of at least 2,000 characters (92 papers). 4 of the 200 abstract-ceiling pairs have no usable full text and are out. Test split not read.

| Code | Pairs | IN | OUT | NOT_IN_TEXT | CANNOT_TELL | IN/(IN+OUT) | Wilson 95% | Reading | Scrambled-paper share of pairs |
|---|---|---|---|---|---|---|---|---|---|
| F1 | 24 | 13 | 6 | 2 | 3 | 0.684 | [0.46, 0.846] | pass | 0.042 |
| F2 | 35 | 14 | 8 | 10 | 3 | 0.636 | [0.43, 0.803] | pass | 0.029 |
| F3 | 22 | 10 | 10 | 1 | 1 | 0.5 | [0.299, 0.701] | fail (retrieval-limited) | 0.000 |
| F4 | 63 | 2 | 5 | 12 | 44 | 0.286 | [0.082, 0.641] | untested | 0.032 |
| F5 | 15 | 2 | 2 | 7 | 4 | 0.5 | [0.15, 0.85] | untested | 0.000 |
| F6 | 29 | 9 | 6 | 9 | 5 | 0.6 | [0.357, 0.802] | pass | 0.069 |
| F7 | 8 | 2 | 2 | 4 | 0 | 0.5 | [0.15, 0.85] | untested | 0.000 |
| ALL | 196 | 52 | 39 | 45 | 60 | 0.571 | [0.469, 0.668] | fail (retrieval-limited) | 0.031 |

NOT_IN_TEXT is the extraction ceiling per code (column above): evidence in a table, figure, released file or the recount own run that the PDF text does not hold. Many are by construction (released files, recount own runs, digitized figure values).

## Extraction

92 papers, 6541834 characters total, median 61862 per paper, min 4552, max 321769. Papers flagged scrambled (paper flagged when lines of >=6 tokens with >=70% numeric tokens hold >=8% of its characters (operational definition set while writing the script)): 3 of 92. Per paper numbers in summary.json.

## Sensitivity (descriptive, not the pre-registered reading)

IN if any one key string (not all) is in the top 6:

| Code | decided | IN any key | share | Wilson 95% |
|---|---|---|---|---|
| F1 | 19 | 14 | 0.737 | [0.512, 0.882] |
| F2 | 22 | 17 | 0.773 | [0.566, 0.899] |
| F3 | 20 | 11 | 0.55 | [0.342, 0.742] |
| F4 | 7 | 2 | 0.286 | [0.082, 0.641] |
| F5 | 4 | 2 | 0.5 | [0.15, 0.85] |
| F6 | 15 | 12 | 0.8 | [0.548, 0.93] |
| F7 | 4 | 2 | 0.5 | [0.15, 0.85] |
| ALL | 91 | 60 | 0.659 | [0.557, 0.748] |

## Limits

CANNOT_TELL is large for F4 because most F4 notes are pure absences (run dates not printed, no circuits released) that name nothing to search. Per the file, those are CANNOT_TELL, so F4 is untested. Several keys were chosen by the judge reading the note (scripts/ft_keys.py); the Bones read on the seeded 20 is the check. Scrambled-text flag is an operational definition set while writing the script.
