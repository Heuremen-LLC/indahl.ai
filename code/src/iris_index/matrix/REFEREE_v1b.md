# Referee v1b (read-only Sonnet, 25 Oct 2026): the six models not in REFEREE_v1a (gemma3, granite3.3, olmo2, falcon3, smollm2, deepseek-r1)
Recomputed every M1/M3/M5 value from raw: all 12 match; intervals match within bootstrap noise.
Real errors found (all fixed under PLAN.md addendum 3, old values kept in MATRIX.pre-add3.md):
1. Footer counted unread (CANNOT_TELL) carrier cells: 18 / 0.9 -> resolved cells only 16 / 0.8.
2. deepseek-r1 M1 printed as resolved on 92/116 and 132/184 usable (77 of 300 NepPlural replies truncated, content-conditional drop) -> CANNOT_TELL (partial).
3. deepseek-r1 known-good "FAIL 0.000" read as disagreement; cause was <150 usable pairs (empty truncated replies) -> reason printed; n clause stated in plan.
4. granite3.3 batch drop reason misdescribed (item-keyed dict, not missing list) -> renamed; dict-parsed bound printed (M4 0.40, M6 0.92), outcome stays CANNOT_TELL.
5. First-letter answer rule read words as letters ("box"->B, "attic"->A; falcon option words dropped) -> strict letter or exact option text; falcon M3 0.157->0.160, M5 0.145->0.151, outcomes unchanged.
6. Bootstrap rng advanced across calls (intervals order-dependent; json/md disagreed) -> reseeded per cell; json outcomes masked as in MATRIX.md.
Checked and fine: formats of all six; gemma3/granite/olmo2/falcon3/smollm2 cells; reverse-order construction; terminations columns; four outcomes only; same-letter flip pattern holds for the new models.
