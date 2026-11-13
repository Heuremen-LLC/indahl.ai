# Recount Matrix: Language Models - v2 (4-option items + positive control; our seat; internal draft)

Plan: PLAN_v2.md (addenda v2-1..v2-3). Gate: an order cell is read only if the positive control (pick the option listed FIRST) is followed in
>= 80% of items in BOTH orderings and the known-good copy check passes; otherwise CANNOT_TELL with the reason. Flip cells = share of items whose
answer changes under the carrier, minus the exact-copy floor. top-letter = share of answers on the most-used letter (0.25 = uniform).

| model | known-good | positive control acc (A / rev) | top letter | reverse order flip | rotation flip | template B flip | truncated |
|---|---|---|---|---|---|---|---|
| deepseek-r1_1.5b | FAIL 0.011 [0.000, 0.033] n91 | 0.882 [0.765, 0.971] n34 / 1.000 [1.000, 1.000] n37 | 0.35 | 0.438 [0.312, 0.562] n64 CANNOT_TELL (truncated under our settings: 108 of 200 replies hit the length limit) | 0.453 [0.344, 0.563] n64 CANNOT_TELL (truncated under our settings: 108 of 200 replies hit the length limit) | 0.388 [0.245, 0.531] n49 CANNOT_TELL (truncated under our settings: 108 of 200 replies hit the length limit) | 108 of 200 |
| falcon3_3b | pass 0.005 [0.000, 0.015] n195 | 1.000 [1.000, 1.000] n40 / 1.000 [1.000, 1.000] n40 | 0.36 | 0.425 [0.358, 0.492] n193 ABOVE | 0.312 [0.245, 0.380] n192 ABOVE | 0.222 [0.074, 0.407] n27 ABOVE | 0 of 200 |
| gemma3_4b | pass 0.000 [0.000, 0.000] n200 | 0.600 [0.450, 0.750] n40 / 0.600 [0.450, 0.750] n40 | 0.30 | 0.325 [0.260, 0.390] n200 CANNOT_TELL (positive control < 80%) | 0.305 [0.240, 0.365] n200 CANNOT_TELL (positive control < 80%) | 0.113 [0.072, 0.159] n195 ABOVE | 0 of 200 |
| granite3.3_2b | pass 0.000 [0.000, 0.000] n173 | 0.250 [0.125, 0.375] n40 / 0.450 [0.300, 0.600] n40 | 0.32 | 0.398 [0.329, 0.472] n161 CANNOT_TELL (positive control < 80%) | 0.344 [0.268, 0.414] n157 CANNOT_TELL (positive control < 80%) | 0.294 [0.176, 0.431] n51 ABOVE | 0 of 200 |
| llama3.1_8b | pass 0.000 [0.000, 0.000] n200 | 0.750 [0.625, 0.875] n40 / 0.900 [0.800, 0.975] n40 | 0.29 | 0.240 [0.180, 0.300] n200 CANNOT_TELL (positive control < 80%) | 0.185 [0.130, 0.240] n200 CANNOT_TELL (positive control < 80%) | 0.120 [0.075, 0.170] n200 ABOVE | 0 of 200 |
| mistral_7b | pass 0.000 [0.000, 0.000] n199 | 0.875 [0.775, 0.975] n40 / 0.850 [0.725, 0.950] n40 | 0.28 | 0.273 [0.212, 0.338] n198 ABOVE | 0.273 [0.212, 0.338] n198 ABOVE | 0.131 [0.084, 0.183] n191 ABOVE | 0 of 200 |
| olmo2_7b | pass 0.000 [0.000, 0.000] n195 | 0.350 [0.200, 0.500] n40 / 0.525 [0.375, 0.675] n40 | 0.31 | 0.377 [0.314, 0.445] n191 CANNOT_TELL (positive control < 80%) | 0.325 [0.257, 0.393] n191 CANNOT_TELL (positive control < 80%) | 0.208 [0.148, 0.262] n183 ABOVE | 0 of 200 |
| phi4-mini | pass 0.000 [0.000, 0.000] n199 | 1.000 [1.000, 1.000] n40 / 1.000 [1.000, 1.000] n40 | 0.32 | 0.278 [0.217, 0.343] n198 ABOVE | 0.246 [0.186, 0.307] n199 ABOVE | 0.106 [0.056, 0.155] n142 ABOVE | 0 of 200 |
| qwen3_4b | FAIL 0.000 [0.000, 0.000] n9 | 1.000 [1.000, 1.000] n11 / 1.000 [1.000, 1.000] n11 | 0.67 | 0.000 [0.000, 0.000] n3 CANNOT_TELL (truncated under our settings: 191 of 200 replies hit the length limit) | 0.000 [0.000, 0.000] n4 CANNOT_TELL (truncated under our settings: 191 of 200 replies hit the length limit) | 0.000 [0.000, 0.000] n4 CANNOT_TELL (truncated under our settings: 191 of 200 replies hit the length limit) | 191 of 200 |
| smollm2_1.7b | pass 0.000 [0.000, 0.000] n196 | 1.000 [1.000, 1.000] n40 / 1.000 [1.000, 1.000] n40 | 0.36 | 0.500 [0.432, 0.573] n192 ABOVE | 0.477 [0.410, 0.549] n195 ABOVE | 0.300 [0.100, 0.500] n20 ABOVE | 0 of 200 |

Reading so far: where the positive control passes (phi4-mini, mistral, falcon3), answers change with option order and rotation while the most-used
letter stays near uniform -> order sensitivity separated from letter fallback (the v1 limit). Models still running are partial.
Check (25 Oct): mistral reverse and rotation cells are equal (54 of 198 each) by count, not by construction: the two arms use different option
orders on every item and 114 of 200 raw replies differ.
