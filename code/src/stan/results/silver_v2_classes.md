# STAN v2 silver class mix (12 Nov 2026)

Source: results/silver_v2_classes.json, built by scripts/silver_v2.py from data/silver_v2/silver_all.jsonl. Seed 1112. Counts are by status. The valid slice is 29 of 141 papers (20.6 percent), split by paper.

| code | before cap | after cap | train | valid | plurality status (train) | plurality rate on valid | constant-CT rate on valid | flag |
|---|---|---|---|---|---|---|---|---|
| F1 | P 42 | none | 0 | 0 | none | n/a | n/a | gone: one status only |
| F2 | P 55, A 39, NA 2 | P 41, A 39, NA 2 | P 37, A 29, NA 2 (68) | P 4, A 10 (14) | PRESENT | 0.286 | 0.000 | NA has 2 rows |
| F3 | CT 14, NA 10 | CT 10, NA 10 | CT 6, NA 8 (14) | CT 4, NA 2 (6) | NA | 0.333 | 0.667 | under 15 train |
| F4 | CT 28 | none | 0 | 0 | none | n/a | n/a | gone: one status only |
| F5 | CT 39, NA 23 | CT 23, NA 23 | CT 18, NA 20 (38) | CT 5, NA 3 (8) | NA | 0.375 | 0.625 | valid has 8 rows |
| F6 | NA 3 | none | 0 | 0 | none | n/a | n/a | gone: one status only |
| F7 | CT 8, NA 96 | CT 8, NA 8 | CT 5, NA 6 (11) | CT 3, NA 2 (5) | NA | 0.400 | 0.600 | under 15 train |

Pooled valid slice (33 rows): CT 12, NA 7, A 10, P 4. Pooled constant-CT rate 0.364. Per-code plurality predictor, pooled over codes that have rows: 0.333. Pooled train rows 131.

Codes with fewer than 15 train rows: F1, F4, F6 (0, nothing survives the status cap), F3 (14), F7 (11).

Rows cut by the status cap (data/silver_v2/unused_cap.jsonl, 195): F1 P 42, F2 P 14, F3 CT 4, F4 CT 28, F5 CT 16, F6 NA 3, F7 NA 88. A code with one status has others = 0 and is cut to zero.
