# THE REVERSE GRADIENT + DALET GARDEN -- 2026-09-30

Relays each record through the frozen instruments (arrow, clock, split-c) hop by hop. Each hop's record is reduced by what the clock's fitted envelope-and-carrier accounts for (`component = C0*exp(-(t-t0)/tau) * cos(unwrapped Hilbert phase)`, tau from `core.fit_exp_decay` on the Hilbert envelope of the current hop's series -- the SAME frozen exp-decay-fit machinery `three_formulas.py`/`core.py` already use, generalized off autocorrelation to the signal's own envelope so it runs on any window, not just the yeast during-window). Two relay columns, same component each hop:

- **PLAIN SUBTRACTION** (original reverse-gradient rule): `x_next = x - component`.
- **DALET** (Wayfinder's precision, 2026-09-30 mid-task: gradient ASCENT, the untraining direction): `grad = x - component` read as dL/dx for the pointwise loss L(x)=(x-component)^2 the clock fit minimizes (component held fixed -- the only tractable gradient without differentiating through the Hilbert transform + exp-decay-fit chain); `x_next = renorm_unit_var(x + eta*std(x)*grad/std(grad))`, eta=0.10 primary, cutoff test at 0.05/0.20.

8 hops max, or stop when the SUBTRACTION column's residual variance fraction (var(residual)/var(x0)) drops below 1%. Bootstrap errors: 300 draws (case-resample, `core.py`'s frozen `arrow_bootstrap_fast` / `bootstrap_tau_fast` / `split_bootstrap`, N reduced from core's default 1000 to 300 -- 'within real order'). **No shuffle used as judge anywhere in this pass**; arrow's best-k is chosen by max|A| directly (not a shuffle-z search) to keep 9 records x 4 order/direction combos x 2 columns x 8 hops tractable in one numpy-only process -- documented departure from `three_formulas.py`'s per-k shuffle floor, since the gradient relay needs magnitude+sign per hop, not a per-k significance test. `core.py`, `split_v2.py` (`analytic_signal`, `naive_peaks_idx`, `candidate_c`, `running_median_detrend`), `load_horn.py`, `load_buzz.py` imported verbatim, not edited.

BEFORE = textbook-residualize x0 first (yeast: running-median detrend; horn: subtract window median; buzz: subtract fitted linear rotation vs shot index; mice: subtract 24h sinusoid fit), then relay. AFTER = relay the raw record (sub column only, run to its own stopping point), then textbook-residualize that final residual once more (one extra row, `after_fwd_final_textbook`). Reversal = same relay on the time-reversed array (BEFORE-residualized series, reversed).

Records: yeast (during 800-1400s, whole), horn (at-horn window, whole), buzz J2 (seats 80/100/116, whole 4000-shot series, run individually, not pooled -- the pooling in `THE_TABLE_20260930.md` is a THAT report's final step, not repeated here), mice (size1 = SC10.2 whole record, size4-5 = median-pooled SC14.4/SC19.5/SC26.7 whole record). No windowing beyond what's named -- mice/buzz have no separate synchrony window in this task, unlike yeast/horn.

## yeast_during  (family: yeast, units: s, n=460)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=-6.182e+07±4.3e+07 (-) | tau=852.8±1.3e+02 | S=-23.31 P=0.5528±0.6 (n=14) | 0.1352 | -- |
| 1 | k=78.6 A=7.517e+06±2.2e+06 (+) | tau=5179±2.7e+04 | S=-13.69 P=0.5249±0.46 (n=20) | 0.03566 | arrow=Δ6.93e+07(±4.57e+07,OUT) clock=Δ4.33e+03(±2.73e+04,in-err) split=Δ-0.0279(±1.06,in-err) |
| 2 | k=62.9 A=2.509e+06±1e+06 (+) | tau=4730±2.4e+04 | S=-3.352 P=-0.6775±0.36 (n=25) | 0.01312 | arrow=Δ-5.01e+06(±3.28e+06,OUT) clock=Δ-448(±5.13e+04,in-err) split=Δ-1.2(±0.825,OUT) |
| 3 | k=76 A=1.288e+06±5.7e+05 (+) | tau=3691±2.8e+05 | S=-2.623 P=0.4148±0.38 (n=28) | 0.006217 | arrow=Δ-1.22e+06(±1.6e+06,in-err) clock=Δ-1.04e+03(±3.09e+05,in-err) split=Δ1.09(±0.737,OUT) |

Verdict: **NO CLEAN FIXED POINT OR DIVERGENCE**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=-6.182e+07±4.3e+07 (-) | tau=852.8±1.3e+02 | S=-23.31 P=0.5528±0.47 (n=14) | 0.1352 | -- |
| 1 | k=66.8 A=-0.2613±0.17 (-) | tau=966.9±2.3e+02 | S=-21.61 P=0.06484±0.71 (n=15) | 3.877e-07 | arrow=Δ6.18e+07(±4.31e+07,OUT) clock=Δ114(±355,in-err) split=Δ-0.488(±1.19,in-err) |
| 2 | k=66.8 A=-0.2796±0.17 (-) | tau=1040±3e+02 | S=-15.49 P=-0.6893±0.9 (n=16) | 4.668e-07 | arrow=Δ-0.0184(±0.335,in-err) clock=Δ73.3(±524,in-err) split=Δ-0.754(±1.61,in-err) |
| 3 | k=66.8 A=-0.2916±0.17 (-) | tau=1250±7.9e+05 | S=-13.04 P=-0.4751±0.78 (n=17) | 5.385e-07 | arrow=Δ-0.012(±0.333,in-err) clock=Δ210(±7.88e+05,in-err) split=Δ0.214(±1.68,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=6.182e+07±4.5e+07 (+) | tau=-852.8±1.3e+02 | S=19.8 P=-0.5386±1.1 (n=13) | 0.1352 | -- |
| 1 | k=78.6 A=-7.517e+06±2.1e+06 (-) | tau=-5179±8.5e+04 | S=17.32 P=-0.2621±0.42 (n=20) | 0.03566 | arrow=Δ-6.93e+07(±4.76e+07,OUT) clock=Δ-4.33e+03(±8.48e+04,in-err) split=Δ0.277(±1.55,in-err) |
| 2 | k=62.9 A=-2.509e+06±9.4e+05 (-) | tau=-4730±4.2e+04 | S=5.94 P=0.6253±0.36 (n=25) | 0.01312 | arrow=Δ5.01e+06(±3.09e+06,OUT) clock=Δ448(±1.26e+05,in-err) split=Δ0.887(±0.783,OUT) |
| 3 | k=76 A=-1.288e+06±6e+05 (-) | tau=-3691±1.4e+05 | S=4.222 P=-0.02444±0.36 (n=28) | 0.006217 | arrow=Δ1.22e+06(±1.54e+06,in-err) clock=Δ1.04e+03(±1.8e+05,in-err) split=Δ-0.65(±0.727,in-err) |

Verdict: **NO CLEAN FIXED POINT OR DIVERGENCE**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=6.182e+07±4e+07 (+) | tau=-852.8±1.4e+02 | S=19.8 P=-0.5386±1.4 (n=13) | 0.1352 | -- |
| 1 | k=66.8 A=0.2613±0.17 (+) | tau=-966.9±2.1e+02 | S=18.91 P=-0.6241±0.74 (n=15) | 3.877e-07 | arrow=Δ-6.18e+07(±4.03e+07,OUT) clock=Δ-114(±349,in-err) split=Δ-0.0855(±2.15,in-err) |
| 2 | k=66.8 A=0.2796±0.18 (+) | tau=-1040±3.2e+02 | S=12.62 P=-0.02723±0.82 (n=16) | 4.668e-07 | arrow=Δ0.0184(±0.344,in-err) clock=Δ-73.3(±534,in-err) split=Δ0.597(±1.56,in-err) |
| 3 | k=66.8 A=0.2916±0.18 (+) | tau=-1250±2.3e+03 | S=10.46 P=-0.2049±0.81 (n=17) | 5.385e-07 | arrow=Δ0.012(±0.36,in-err) clock=Δ-210(±2.6e+03,in-err) split=Δ-0.178(±1.63,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=28.8 A=-2.146e+10±4.5e+10 (-) | tau=1937±6.2e+02 | S=-0.07049 P=0.06766±0.018 (n=14) | 0.109 | -- |
| 1 | k=102 A=-1.547e+10±1.1e+10 (-) | tau=-1.925e+04±3.7e+04 | S=0.1543 P=-0.01397±0.013 (n=25) | 0.03263 | arrow=Δ6e+09(±5.69e+10,in-err) clock=Δ-2.12e+04(±3.78e+04,in-err) split=Δ-0.0816(±0.0311,OUT) |
| 2 | k=31.4 A=-4.448e+09±6.4e+09 (-) | tau=-6451±2.9e+05 | S=0.01235 P=-0.006563±0.0066 (n=25) | 0.01432 | arrow=Δ1.1e+10(±1.78e+10,in-err) clock=Δ1.28e+04(±3.25e+05,in-err) split=Δ0.0074(±0.0192,in-err) |
| 3 | k=102 A=-5.834e+09±4.3e+09 (-) | tau=4.818e+04±4.9e+05 | S=0.03384 P=0.001154±0.0077 (n=30) | 0.007984 | arrow=Δ-1.39e+09(±1.07e+10,in-err) clock=Δ5.46e+04(±7.73e+05,in-err) split=Δ0.00772(±0.0143,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=28.8 A=-2.146e+10±4.4e+10 (-) | tau=1937±6.8e+02 | S=-0.07049 P=0.06766±0.022 (n=14) | 0.109 | -- |
| 1 | k=78.6 A=0.28±0.12 (+) | tau=3526±2.4e+04 | S=-17.95 P=-0.1468±0.33 (n=14) | 2.571e-07 | arrow=Δ2.15e+10(±4.41e+10,in-err) clock=Δ1.59e+03(±2.51e+04,in-err) split=Δ-0.214(±0.356,in-err) |
| 2 | k=78.6 A=0.2561±0.11 (+) | tau=4645±1.5e+05 | S=-19.5 P=0.2993±0.3 (n=17) | 2.961e-07 | arrow=Δ-0.0239(±0.224,in-err) clock=Δ1.12e+03(±1.78e+05,in-err) split=Δ0.446(±0.63,in-err) |
| 3 | k=77.3 A=0.2402±0.11 (+) | tau=3651±2.8e+06 | S=-18.42 P=0.2068±0.3 (n=18) | 3.313e-07 | arrow=Δ-0.0159(±0.222,in-err) clock=Δ-994(±2.98e+06,in-err) split=Δ-0.0925(±0.594,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=28.8 A=2.146e+10±4.5e+10 (+) | tau=-1937±8.1e+02 | S=-0.1375 P=-0.06333±0.034 (n=13) | 0.109 | -- |
| 1 | k=102 A=1.547e+10±1e+10 (+) | tau=1.925e+04±9.8e+04 | S=-0.1705 P=0.0117±0.014 (n=25) | 0.03263 | arrow=Δ-6e+09(±5.53e+10,in-err) clock=Δ2.12e+04(±9.92e+04,in-err) split=Δ0.075(±0.0481,OUT) |
| 2 | k=31.4 A=4.448e+09±6.2e+09 (+) | tau=6451±2.7e+05 | S=-0.01521 P=0.004135±0.0067 (n=25) | 0.01432 | arrow=Δ-1.1e+10(±1.63e+10,in-err) clock=Δ-1.28e+04(±3.68e+05,in-err) split=Δ-0.00757(±0.0209,in-err) |
| 3 | k=102 A=5.834e+09±4.2e+09 (+) | tau=-4.818e+04±2.4e+05 | S=-0.0361 P=0.001451±0.0069 (n=30) | 0.007984 | arrow=Δ1.39e+09(±1.04e+10,in-err) clock=Δ-5.46e+04(±5.14e+05,in-err) split=Δ-0.00268(±0.0136,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=28.8 A=2.146e+10±4.3e+10 (+) | tau=-1937±6.5e+02 | S=-0.1375 P=-0.06333±0.046 (n=13) | 0.109 | -- |
| 1 | k=78.6 A=-0.28±0.11 (-) | tau=-3526±1.4e+04 | S=19.53 P=-0.1509±0.29 (n=14) | 2.571e-07 | arrow=Δ-2.15e+10(±4.3e+10,in-err) clock=Δ-1.59e+03(±1.49e+04,in-err) split=Δ-0.0876(±0.333,in-err) |
| 2 | k=78.6 A=-0.2561±0.11 (-) | tau=-4645±2.4e+04 | S=20.53 P=-0.4437±0.26 (n=17) | 2.961e-07 | arrow=Δ0.0239(±0.22,in-err) clock=Δ-1.12e+03(±3.77e+04,in-err) split=Δ-0.293(±0.546,in-err) |
| 3 | k=77.3 A=-0.2402±0.12 (-) | tau=-3651±2.3e+04 | S=19.73 P=-0.4396±0.31 (n=18) | 3.313e-07 | arrow=Δ0.0159(±0.226,in-err) clock=Δ994(±4.69e+04,in-err) split=Δ0.00415(±0.57,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=5.24 A=5.72e+05±3.3e+05 (+)  |  clock: tau=5568±3.7e+04  |  split: S=-39.56 P=1.983±1 (n=29)  (raw relay ran 3 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 1.288e+06±5.7e+05 | -5.834e+09±4.3e+09 | UNSTABLE |
| clock (tau) | 3691±2.8e+05 | 4.818e+04±4.9e+05 | AGREE |
| split (P) | 0.4148±0.38 | 0.001154±0.0077 | UNSTABLE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 1.288e+06±5.7e+05 | -1.288e+06±6e+05 | UNSTABLE |
| clock (tau) | 3691±2.8e+05 | -3691±1.4e+05 | AGREE |
| split (P) | 0.4148±0.38 | -0.02444±0.36 | AGREE |

### DALET cutoff test (step sizes 0.05 / 0.10 / 0.20, BEFORE order, forward, ascent column)

**eta = 0.05**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=-6.182e+07±3.9e+07 (-) | tau=852.8±1.2e+02 | S=-23.31 P=0.5528±0.51 (n=14) | 0.1352 | -- |
| 1 | k=66.8 A=-0.249±0.14 (-) | tau=868.2±1.7e+02 | S=-23.27 P=0.008413±0.67 (n=15) | 3.503e-07 | arrow=Δ6.18e+07(±3.9e+07,OUT) clock=Δ15.4(±293,in-err) split=Δ-0.544(±1.18,in-err) |
| 2 | k=66.8 A=-0.2613±0.16 (-) | tau=960.2±1.8e+02 | S=-22.03 P=0.07339±0.75 (n=15) | 3.857e-07 | arrow=Δ-0.0123(±0.299,in-err) clock=Δ92(±353,in-err) split=Δ0.065(±1.42,in-err) |
| 3 | k=66.8 A=-0.2716±0.17 (-) | tau=1019±3.5e+02 | S=-18.43 P=-0.3283±0.66 (n=16) | 4.243e-07 | arrow=Δ-0.0102(±0.33,in-err) clock=Δ59(±530,in-err) split=Δ-0.402(±1.41,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.1**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=-6.182e+07±4.1e+07 (-) | tau=852.8±1.3e+02 | S=-23.31 P=0.5528±0.57 (n=14) | 0.1352 | -- |
| 1 | k=66.8 A=-0.2613±0.15 (-) | tau=966.9±2.1e+02 | S=-21.61 P=0.06484±0.76 (n=15) | 3.877e-07 | arrow=Δ6.18e+07(±4.09e+07,OUT) clock=Δ114(±341,in-err) split=Δ-0.488(±1.33,in-err) |
| 2 | k=66.8 A=-0.2796±0.17 (-) | tau=1040±3.8e+02 | S=-15.49 P=-0.6893±0.82 (n=16) | 4.668e-07 | arrow=Δ-0.0184(±0.319,in-err) clock=Δ73.3(±598,in-err) split=Δ-0.754(±1.59,in-err) |
| 3 | k=66.8 A=-0.2916±0.17 (-) | tau=1250±8.3e+02 | S=-13.04 P=-0.4751±0.85 (n=17) | 5.385e-07 | arrow=Δ-0.012(±0.342,in-err) clock=Δ210(±1.22e+03,in-err) split=Δ0.214(±1.67,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.2**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=66.8 A=-6.182e+07±4.2e+07 (-) | tau=852.8±1.5e+02 | S=-23.31 P=0.5528±0.46 (n=14) | 0.1352 | -- |
| 1 | k=66.8 A=-0.2784±0.17 (-) | tau=1205±4.3e+02 | S=-13.51 P=-0.6543±0.82 (n=16) | 4.637e-07 | arrow=Δ6.18e+07(±4.2e+07,OUT) clock=Δ352(±580,in-err) split=Δ-1.21(±1.27,in-err) |
| 2 | k=66.8 A=-0.2985±0.17 (-) | tau=1931±5.2e+04 | S=-10.88 P=-0.4706±0.83 (n=17) | 5.973e-07 | arrow=Δ-0.0201(±0.343,in-err) clock=Δ726(±5.24e+04,in-err) split=Δ0.184(±1.64,in-err) |
| 3 | k=32.7 A=0.3258±0.14 (+) | tau=6180±2.1e+05 | S=-12.5 P=-0.09557±0.94 (n=18) | 7.61e-07 | arrow=Δ0.624(±0.305,OUT) clock=Δ4.25e+03(±2.59e+05,in-err) split=Δ0.375(±1.77,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

---

## yeast_whole  (family: yeast, units: s, n=1531)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=34.1 A=1.974e+07±9.3e+06 (+) | tau=1730±97 | S=-153.4 P=-1.181±2 (n=29) | 0.3072 | -- |
| 1 | k=66.8 A=-5.623e+06±2.3e+06 (-) | tau=1416±65 | S=-127.3 P=-3.501±3.7 (n=34) | 0.128 | arrow=Δ-2.54e+07(±1.15e+07,OUT) clock=Δ-314(±163,OUT) split=Δ-2.32(±5.69,in-err) |
| 2 | k=66.8 A=-2.002e+06±9e+05 (-) | tau=1862±1.2e+02 | S=-66.58 P=-3.866±2.9 (n=34) | 0.06788 | arrow=Δ3.62e+06(±3.17e+06,OUT) clock=Δ445(±189,OUT) split=Δ-0.365(±6.61,in-err) |
| 3 | k=32.7 A=1.102e+06±3.8e+05 (+) | tau=2007±1.6e+02 | S=-24.41 P=-2.069±1.9 (n=34) | 0.04456 | arrow=Δ3.1e+06(±1.27e+06,OUT) clock=Δ145(±287,in-err) split=Δ1.8(±4.86,in-err) |
| 4 | k=31.4 A=6.457e+05±2.9e+05 (+) | tau=2721±3e+02 | S=-14.98 P=0.1771±2 (n=36) | 0.03293 | arrow=Δ-4.56e+05(±6.67e+05,in-err) clock=Δ714(±466,OUT) split=Δ2.25(±3.91,in-err) |
| 5 | k=31.4 A=4.612e+05±2.2e+05 (+) | tau=2596±3e+02 | S=-10.19 P=0.4658±1.4 (n=36) | 0.02629 | arrow=Δ-1.85e+05(±5.07e+05,in-err) clock=Δ-125(±603,in-err) split=Δ0.289(±3.34,in-err) |
| 6 | k=17 A=-3.591e+05±1.8e+05 (-) | tau=3238±4.8e+02 | S=-7.562 P=-0.06191±0.75 (n=36) | 0.02194 | arrow=Δ-8.2e+05(±4.02e+05,OUT) clock=Δ642(±784,in-err) split=Δ-0.528(±2.11,in-err) |
| 7 | k=17 A=-2.934e+05±1.6e+05 (-) | tau=3551±5.2e+02 | S=-6.931 P=-0.04313±0.51 (n=35) | 0.01896 | arrow=Δ6.57e+04(±3.4e+05,in-err) clock=Δ314(±1e+03,in-err) split=Δ0.0188(±1.26,in-err) |
| 8 | k=17 A=-2.519e+05±1.5e+05 (-) | tau=3305±5.5e+02 | S=-4.917 P=-0.07111±0.42 (n=35) | 0.01675 | arrow=Δ4.15e+04(±3.02e+05,in-err) clock=Δ-247(±1.07e+03,in-err) split=Δ-0.028(±0.924,in-err) |

Verdict: **FIXED POINT (from hop 4, keys: arrow,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=34.1 A=1.974e+07±9.4e+06 (+) | tau=1730±97 | S=-153.4 P=-1.181±2.1 (n=29) | 0.3072 | -- |
| 1 | k=34.1 A=0.181±0.089 (+) | tau=1867±1.3e+02 | S=-150.6 P=-1.726±1.9 (n=31) | 1.552e-06 | arrow=Δ-1.97e+07(±9.36e+06,OUT) clock=Δ136(±230,in-err) split=Δ-0.545(±4.04,in-err) |
| 2 | k=34.1 A=0.1881±0.093 (+) | tau=1888±1.4e+02 | S=-148.5 P=-1.716±2.1 (n=31) | 1.71e-06 | arrow=Δ0.00711(±0.183,in-err) clock=Δ21(±269,in-err) split=Δ0.0104(±4.07,in-err) |
| 3 | k=32.7 A=0.1973±0.12 (+) | tau=2153±2.4e+02 | S=-147.4 P=-1.644±2.3 (n=31) | 1.929e-06 | arrow=Δ0.00921(±0.21,in-err) clock=Δ266(±378,in-err) split=Δ0.0717(±4.41,in-err) |
| 4 | k=66.8 A=-0.2075±0.15 (-) | tau=2045±2e+02 | S=-148.4 P=-1.612±2.4 (n=31) | 2.037e-06 | arrow=Δ-0.405(±0.264,OUT) clock=Δ-108(±447,in-err) split=Δ0.0324(±4.71,in-err) |
| 5 | k=66.8 A=-0.2254±0.14 (-) | tau=2164±2.3e+02 | S=-149.1 P=-1.548±2.7 (n=31) | 2.142e-06 | arrow=Δ-0.0179(±0.288,in-err) clock=Δ119(±436,in-err) split=Δ0.0635(±5.1,in-err) |
| 6 | k=66.8 A=-0.2409±0.15 (-) | tau=2054±2e+02 | S=-149.6 P=-1.674±2.8 (n=31) | 2.186e-06 | arrow=Δ-0.0155(±0.289,in-err) clock=Δ-111(±433,in-err) split=Δ-0.125(±5.47,in-err) |
| 7 | k=66.8 A=-0.2572±0.15 (-) | tau=2425±3.1e+02 | S=-150.5 P=-1.043±3.9 (n=31) | 2.322e-06 | arrow=Δ-0.0163(±0.303,in-err) clock=Δ371(±513,in-err) split=Δ0.631(±6.74,in-err) |
| 8 | k=66.8 A=-0.2714±0.17 (-) | tau=2224±2.3e+02 | S=-142.7 P=-3.157±3.2 (n=32) | 2.365e-06 | arrow=Δ-0.0142(±0.322,in-err) clock=Δ-201(±538,in-err) split=Δ-2.11(±7.13,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=34.1 A=-1.974e+07±8.3e+06 (-) | tau=-1730±93 | S=146.3 P=-0.2931±1.7 (n=32) | 0.3072 | -- |
| 1 | k=66.8 A=5.623e+06±2.3e+06 (+) | tau=-1416±71 | S=125.4 P=4.845±3.6 (n=34) | 0.128 | arrow=Δ2.54e+07(±1.06e+07,OUT) clock=Δ314(±164,OUT) split=Δ5.14(±5.36,in-err) |
| 2 | k=66.8 A=2.002e+06±1e+06 (+) | tau=-1862±1.2e+02 | S=66.47 P=1.654±3.2 (n=34) | 0.06788 | arrow=Δ-3.62e+06(±3.35e+06,OUT) clock=Δ-445(±192,OUT) split=Δ-3.19(±6.82,in-err) |
| 3 | k=32.7 A=-1.102e+06±3.8e+05 (-) | tau=-2007±1.7e+02 | S=23.06 P=0.329±1.7 (n=34) | 0.04456 | arrow=Δ-3.1e+06(±1.39e+06,OUT) clock=Δ-145(±287,in-err) split=Δ-1.33(±4.89,in-err) |
| 4 | k=31.4 A=-6.457e+05±2.5e+05 (-) | tau=-2721±3e+02 | S=13.63 P=2.203±1.8 (n=36) | 0.03293 | arrow=Δ4.56e+05(±6.31e+05,in-err) clock=Δ-714(±464,OUT) split=Δ1.87(±3.49,in-err) |
| 5 | k=31.4 A=-4.612e+05±1.9e+05 (-) | tau=-2596±2.9e+02 | S=8.934 P=1.405±1.4 (n=36) | 0.02629 | arrow=Δ1.85e+05(±4.4e+05,in-err) clock=Δ125(±589,in-err) split=Δ-0.799(±3.19,in-err) |
| 6 | k=17 A=3.591e+05±2e+05 (+) | tau=-3238±4.7e+02 | S=6.835 P=0.6291±1.2 (n=36) | 0.02194 | arrow=Δ8.2e+05(±3.92e+05,OUT) clock=Δ-642(±764,in-err) split=Δ-0.776(±2.57,in-err) |
| 7 | k=17 A=2.934e+05±1.8e+05 (+) | tau=-3554±5.8e+02 | S=6.6 P=0.2433±0.8 (n=35) | 0.01896 | arrow=Δ-6.57e+04(±3.77e+05,in-err) clock=Δ-316(±1.06e+03,in-err) split=Δ-0.386(±1.98,in-err) |
| 8 | k=17 A=2.519e+05±1.6e+05 (+) | tau=-3297±5.8e+02 | S=4.79 P=0.4815±0.32 (n=35) | 0.01675 | arrow=Δ-4.15e+04(±3.34e+05,in-err) clock=Δ256(±1.16e+03,in-err) split=Δ0.238(±1.13,in-err) |

Verdict: **FIXED POINT (from hop 4, keys: arrow,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=34.1 A=-1.974e+07±8.2e+06 (-) | tau=-1730±99 | S=146.3 P=-0.2931±1.7 (n=32) | 0.3072 | -- |
| 1 | k=34.1 A=-0.181±0.09 (-) | tau=-1867±1.3e+02 | S=155.8 P=-1.64±1.9 (n=31) | 1.552e-06 | arrow=Δ1.97e+07(±8.19e+06,OUT) clock=Δ-136(±231,in-err) split=Δ-1.35(±3.63,in-err) |
| 2 | k=34.1 A=-0.1881±0.098 (-) | tau=-1888±1.6e+02 | S=154.4 P=-1.99±1.8 (n=31) | 1.71e-06 | arrow=Δ-0.00711(±0.188,in-err) clock=Δ-21(±290,in-err) split=Δ-0.35(±3.75,in-err) |
| 3 | k=32.7 A=-0.1973±0.11 (-) | tau=-2153±2.3e+02 | S=153.1 P=-2.269±1.9 (n=31) | 1.929e-06 | arrow=Δ-0.00921(±0.206,in-err) clock=Δ-266(±390,in-err) split=Δ-0.279(±3.79,in-err) |
| 4 | k=66.8 A=0.2075±0.14 (+) | tau=-2045±2.1e+02 | S=152.9 P=-2.514±2.4 (n=31) | 2.037e-06 | arrow=Δ0.405(±0.251,OUT) clock=Δ108(±441,in-err) split=Δ-0.245(±4.31,in-err) |
| 5 | k=66.8 A=0.2254±0.14 (+) | tau=-2164±2.3e+02 | S=153.3 P=-2.435±2.6 (n=31) | 2.142e-06 | arrow=Δ0.0179(±0.285,in-err) clock=Δ-119(±436,in-err) split=Δ0.079(±4.92,in-err) |
| 6 | k=66.8 A=0.2409±0.15 (+) | tau=-2054±2e+02 | S=153.8 P=-2.386±2.9 (n=31) | 2.186e-06 | arrow=Δ0.0155(±0.294,in-err) clock=Δ111(±431,in-err) split=Δ0.0498(±5.44,in-err) |
| 7 | k=66.8 A=0.2572±0.15 (+) | tau=-2425±3.2e+02 | S=149.5 P=-1.267±3 (n=31) | 2.322e-06 | arrow=Δ0.0163(±0.305,in-err) clock=Δ-371(±524,in-err) split=Δ1.12(±5.92,in-err) |
| 8 | k=66.8 A=0.2714±0.16 (+) | tau=-2224±2.3e+02 | S=143 P=-0.7349±2.6 (n=32) | 2.365e-06 | arrow=Δ0.0142(±0.309,in-err) clock=Δ201(±552,in-err) split=Δ0.532(±5.66,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=105 A=-1.516e+11±1.3e+10 (-) | tau=2155±97 | S=24.93 P=0.4449±0.25 (n=29) | 0.09945 | -- |
| 1 | k=105 A=-6.754e+10±8.6e+09 (-) | tau=1745±1.2e+02 | S=4.616 P=-0.01762±0.032 (n=31) | 0.04268 | arrow=Δ8.41e+10(±2.16e+10,OUT) clock=Δ-410(±213,OUT) split=Δ-0.463(±0.285,OUT) |
| 2 | k=105 A=-4.916e+10±7.5e+09 (-) | tau=2272±2.5e+02 | S=3.567 P=-0.01129±0.039 (n=32) | 0.0256 | arrow=Δ1.84e+10(±1.61e+10,OUT) clock=Δ527(±364,OUT) split=Δ0.00634(±0.071,in-err) |
| 3 | k=105 A=-4.009e+10±5.8e+09 (-) | tau=2523±3.1e+02 | S=2.602 P=-0.03097±0.039 (n=35) | 0.01762 | arrow=Δ9.07e+09(±1.33e+10,in-err) clock=Δ251(±556,in-err) split=Δ-0.0197(±0.0779,in-err) |
| 4 | k=105 A=-3.432e+10±4.3e+09 (-) | tau=2696±3.8e+02 | S=2.094 P=0.04251±0.03 (n=35) | 0.01337 | arrow=Δ5.77e+09(±1.02e+10,in-err) clock=Δ173(±690,in-err) split=Δ0.0735(±0.0681,OUT) |
| 5 | k=105 A=-3.026e+10±3.8e+09 (-) | tau=2730±4.3e+02 | S=1.809 P=0.03826±0.017 (n=35) | 0.01082 | arrow=Δ4.06e+09(±8.16e+09,in-err) clock=Δ33.5(±817,in-err) split=Δ-0.00425(±0.0466,in-err) |
| 6 | k=105 A=-2.732e+10±3.4e+09 (-) | tau=2439±4e+02 | S=1.598 P=0.02837±0.012 (n=34) | 0.008975 | arrow=Δ2.93e+09(±7.22e+09,in-err) clock=Δ-290(±838,in-err) split=Δ-0.00989(±0.0287,in-err) |

Verdict: **FIXED POINT (from hop 3, keys: arrow,clock)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=105 A=-1.516e+11±1.4e+10 (-) | tau=2155±1e+02 | S=24.93 P=0.4449±0.25 (n=29) | 0.09945 | -- |
| 1 | k=105 A=-0.3962±0.042 (-) | tau=2123±94 | S=-379.3 P=-1.562±1.2 (n=30) | 2.912e-08 | arrow=Δ1.52e+11(±1.37e+10,OUT) clock=Δ-32(±196,in-err) split=Δ-2.01(±1.42,OUT) |
| 2 | k=105 A=-0.4473±0.047 (-) | tau=2096±1.1e+02 | S=-384.6 P=-1.833±1.1 (n=30) | 3.598e-08 | arrow=Δ-0.0511(±0.089,in-err) clock=Δ-27.4(±202,in-err) split=Δ-0.271(±2.29,in-err) |
| 3 | k=105 A=-0.4929±0.058 (-) | tau=2071±1e+02 | S=-388.3 P=-1.828±1.4 (n=30) | 4.29e-08 | arrow=Δ-0.0456(±0.105,in-err) clock=Δ-24.6(±213,in-err) split=Δ0.00518(±2.53,in-err) |
| 4 | k=105 A=-0.532±0.067 (-) | tau=2050±1.2e+02 | S=-388.2 P=-2.556±1.2 (n=29) | 4.984e-08 | arrow=Δ-0.039(±0.125,in-err) clock=Δ-21.2(±222,in-err) split=Δ-0.728(±2.56,in-err) |
| 5 | k=105 A=-0.5634±0.074 (-) | tau=2029±1.2e+02 | S=-394.2 P=-2.062±1.5 (n=30) | 5.677e-08 | arrow=Δ-0.0314(±0.141,in-err) clock=Δ-20.7(±238,in-err) split=Δ0.494(±2.67,in-err) |
| 6 | k=105 A=-0.5866±0.081 (-) | tau=2023±1.2e+02 | S=-403.3 P=-1.085±1.7 (n=31) | 6.428e-08 | arrow=Δ-0.0232(±0.155,in-err) clock=Δ-6.71(±242,in-err) split=Δ0.977(±3.22,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=105 A=1.516e+11±1.3e+10 (+) | tau=-2155±98 | S=-25.01 P=-0.3368±0.25 (n=31) | 0.09945 | -- |
| 1 | k=105 A=6.754e+10±7.9e+09 (+) | tau=-1745±1.2e+02 | S=-4.694 P=0.01187±0.037 (n=31) | 0.04268 | arrow=Δ-8.41e+10(±2.09e+10,OUT) clock=Δ410(±222,OUT) split=Δ0.349(±0.288,OUT) |
| 2 | k=105 A=4.916e+10±7.2e+09 (+) | tau=-2273±2.5e+02 | S=-3.609 P=0.002978±0.033 (n=32) | 0.0256 | arrow=Δ-1.84e+10(±1.51e+10,OUT) clock=Δ-527(±375,OUT) split=Δ-0.00889(±0.0705,in-err) |
| 3 | k=105 A=4.009e+10±5.3e+09 (+) | tau=-2523±3.1e+02 | S=-2.658 P=0.005163±0.035 (n=35) | 0.01762 | arrow=Δ-9.07e+09(±1.24e+10,in-err) clock=Δ-251(±560,in-err) split=Δ0.00218(±0.0677,in-err) |
| 4 | k=105 A=3.432e+10±4.5e+09 (+) | tau=-2696±4e+02 | S=-2.17 P=-0.02016±0.028 (n=35) | 0.01337 | arrow=Δ-5.77e+09(±9.74e+09,in-err) clock=Δ-173(±711,in-err) split=Δ-0.0253(±0.0628,in-err) |
| 5 | k=105 A=3.026e+10±4.1e+09 (+) | tau=-2730±4.5e+02 | S=-1.903 P=-0.006321±0.021 (n=35) | 0.01082 | arrow=Δ-4.06e+09(±8.61e+09,in-err) clock=Δ-33.5(±855,in-err) split=Δ0.0138(±0.0493,in-err) |
| 6 | k=105 A=2.732e+10±3.6e+09 (+) | tau=-2439±3.6e+02 | S=-1.663 P=-0.02864±0.012 (n=34) | 0.008975 | arrow=Δ-2.93e+09(±7.78e+09,in-err) clock=Δ290(±809,in-err) split=Δ-0.0223(±0.0331,in-err) |

Verdict: **FIXED POINT (from hop 3, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=105 A=1.516e+11±1.3e+10 (+) | tau=-2155±96 | S=-25.01 P=-0.3368±0.3 (n=31) | 0.09945 | -- |
| 1 | k=105 A=0.3962±0.038 (+) | tau=-2123±1.1e+02 | S=378.4 P=-0.9231±1.9 (n=30) | 2.912e-08 | arrow=Δ-1.52e+11(±1.27e+10,OUT) clock=Δ32(±202,in-err) split=Δ-0.586(±2.17,in-err) |
| 2 | k=105 A=0.4473±0.05 (+) | tau=-2096±1e+02 | S=385.7 P=0.2035±1.6 (n=30) | 3.598e-08 | arrow=Δ0.0511(±0.088,in-err) clock=Δ27.4(±211,in-err) split=Δ1.13(±3.43,in-err) |
| 3 | k=105 A=0.4929±0.056 (+) | tau=-2071±1.1e+02 | S=392 P=0.2834±1.5 (n=30) | 4.29e-08 | arrow=Δ0.0456(±0.106,in-err) clock=Δ24.6(±218,in-err) split=Δ0.0798(±3.09,in-err) |
| 4 | k=105 A=0.532±0.066 (+) | tau=-2050±1.1e+02 | S=391.8 P=1.877±1.4 (n=29) | 4.984e-08 | arrow=Δ0.039(±0.122,in-err) clock=Δ21.2(±223,in-err) split=Δ1.59(±2.94,in-err) |
| 5 | k=105 A=0.5634±0.07 (+) | tau=-2029±1.2e+02 | S=396.5 P=2.585±1.9 (n=30) | 5.677e-08 | arrow=Δ0.0314(±0.137,in-err) clock=Δ20.7(±233,in-err) split=Δ0.708(±3.33,in-err) |
| 6 | k=105 A=0.5866±0.076 (+) | tau=-2023±1.3e+02 | S=406.1 P=0.6378±2.2 (n=31) | 6.428e-08 | arrow=Δ0.0232(±0.146,in-err) clock=Δ6.71(±249,in-err) split=Δ-1.95(±4.14,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=103 A=1.045e+04±4.3e+03 (+)  |  clock: tau=2026±1.4e+02  |  split: S=-130.7 P=3.107±2.3 (n=35)  (raw relay ran 6 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | -2.519e+05±1.5e+05 | -2.732e+10±3.4e+09 | UNSTABLE |
| clock (tau) | 3305±5.5e+02 | 2439±4e+02 | AGREE |
| split (P) | -0.07111±0.42 | 0.02837±0.012 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | -2.519e+05±1.5e+05 | 2.519e+05±1.6e+05 | UNSTABLE |
| clock (tau) | 3305±5.5e+02 | -3297±5.8e+02 | UNSTABLE |
| split (P) | -0.07111±0.42 | 0.4815±0.32 | AGREE |

---

## horn_at_horn  (family: horn, units: s, n=1423)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=0.07768±0.021 (+) | tau=1032±1.1e+02 | S=-45.1 P=10.17±7.2 (n=38) | 0.1544 | -- |
| 1 | k=18.2 A=0.01037±0.0033 (+) | tau=1.034e+04±5.1e+04 | S=-18.13 P=4.831±2.4 (n=37) | 0.04947 | arrow=Δ-0.0673(±0.0242,OUT) clock=Δ9.31e+03(±5.12e+04,in-err) split=Δ-5.34(±9.53,in-err) |
| 2 | k=23.8 A=0.002464±0.0018 (+) | tau=1701±6.8e+02 | S=-19.23 P=2.978±1.9 (n=37) | 0.02267 | arrow=Δ-0.00791(±0.00508,OUT) clock=Δ-8.64e+03(±5.18e+04,in-err) split=Δ-1.85(±4.26,in-err) |
| 3 | k=23.8 A=0.001326±0.0011 (+) | tau=1645±7.6e+02 | S=-8.31 P=0.9049±1.7 (n=37) | 0.01442 | arrow=Δ-0.00114(±0.00293,in-err) clock=Δ-56(±1.44e+03,in-err) split=Δ-2.07(±3.6,in-err) |
| 4 | k=23.8 A=0.000901±0.0009 (+) | tau=1319±4.8e+02 | S=-7.103 P=0.8456±0.83 (n=37) | 0.01119 | arrow=Δ-0.000425(±0.00204,in-err) clock=Δ-326(±1.24e+03,in-err) split=Δ-0.0594(±2.54,in-err) |
| 5 | k=23.8 A=0.0007011±0.00072 (+) | tau=852.4±1.7e+02 | S=-5.883 P=0.7393±0.7 (n=38) | 0.009407 | arrow=Δ-0.0002(±0.00162,in-err) clock=Δ-466(±649,in-err) split=Δ-0.106(±1.53,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=0.07768±0.02 (+) | tau=1032±1.1e+02 | S=-45.1 P=10.17±6.5 (n=38) | 0.1544 | -- |
| 1 | k=23.8 A=0.1885±0.049 (+) | tau=955.7±1.1e+02 | S=-8.987 P=5.728±3.3 (n=38) | 0.3002 | arrow=Δ0.111(±0.0687,OUT) clock=Δ-76.4(±214,in-err) split=Δ-4.44(±9.87,in-err) |
| 2 | k=23.8 A=0.2173±0.057 (+) | tau=906.9±1.1e+02 | S=-8.723 P=5.25±2.8 (n=37) | 0.3503 | arrow=Δ0.0288(±0.105,in-err) clock=Δ-48.8(±210,in-err) split=Δ-0.478(±6.13,in-err) |
| 3 | k=23.8 A=0.2435±0.07 (+) | tau=873.2±95 | S=-8.438 P=5.36±2.9 (n=37) | 0.3979 | arrow=Δ0.0263(±0.126,in-err) clock=Δ-33.7(±200,in-err) split=Δ0.11(±5.66,in-err) |
| 4 | k=23.8 A=0.267±0.078 (+) | tau=848.1±95 | S=-8.046 P=5.524±3.3 (n=37) | 0.447 | arrow=Δ0.0235(±0.148,in-err) clock=Δ-25.1(±190,in-err) split=Δ0.164(±6.14,in-err) |
| 5 | k=23.8 A=0.2869±0.086 (+) | tau=819.3±94 | S=-7.821 P=6.023±3.4 (n=37) | 0.4938 | arrow=Δ0.0199(±0.164,in-err) clock=Δ-28.7(±189,in-err) split=Δ0.5(±6.64,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=-0.07768±0.018 (-) | tau=-1030±1.1e+02 | S=44.34 P=-4.46±11 (n=38) | 0.1541 | -- |
| 1 | k=18.2 A=-0.01033±0.0033 (-) | tau=-1.07e+04±1.1e+05 | S=11.91 P=1.304±3 (n=37) | 0.04936 | arrow=Δ0.0673(±0.0208,OUT) clock=Δ-9.67e+03(±1.13e+05,in-err) split=Δ5.76(±14.1,in-err) |
| 2 | k=23.8 A=-0.002447±0.0017 (-) | tau=-1741±2.5e+03 | S=14.62 P=-1.877±1.5 (n=37) | 0.02263 | arrow=Δ0.00789(±0.00496,OUT) clock=Δ8.96e+03(±1.15e+05,in-err) split=Δ-3.18(±4.59,in-err) |
| 3 | k=23.8 A=-0.001327±0.0011 (-) | tau=-1587±6.6e+02 | S=4.186 P=0.07432±1.1 (n=37) | 0.01438 | arrow=Δ0.00112(±0.00275,in-err) clock=Δ154(±3.16e+03,in-err) split=Δ1.95(±2.64,in-err) |
| 4 | k=23.8 A=-0.0008933±0.00083 (-) | tau=-1496±9e+02 | S=4.503 P=0.07407±0.5 (n=37) | 0.01114 | arrow=Δ0.000433(±0.00193,in-err) clock=Δ90.9(±1.57e+03,in-err) split=Δ-0.000255(±1.6,in-err) |
| 5 | k=23.8 A=-0.0007067±0.00068 (-) | tau=-941.1±1.9e+02 | S=3.1 P=0.2673±0.57 (n=38) | 0.00937 | arrow=Δ0.000187(±0.00151,in-err) clock=Δ555(±1.1e+03,in-err) split=Δ0.193(±1.07,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=-0.07768±0.021 (-) | tau=-1030±1e+02 | S=44.34 P=-4.46±12 (n=38) | 0.1541 | -- |
| 1 | k=23.8 A=-0.1884±0.048 (-) | tau=-955.8±1e+02 | S=7.954 P=-2.992±4.4 (n=38) | 0.3 | arrow=Δ-0.111(±0.0693,OUT) clock=Δ74.7(±207,in-err) split=Δ1.47(±16.7,in-err) |
| 2 | k=23.8 A=-0.2171±0.052 (-) | tau=-907.3±1.1e+02 | S=7.295 P=-3.725±4.2 (n=37) | 0.3502 | arrow=Δ-0.0287(±0.0998,in-err) clock=Δ48.5(±208,in-err) split=Δ-0.733(±8.59,in-err) |
| 3 | k=23.8 A=-0.2433±0.063 (-) | tau=-875.4±1e+02 | S=6.501 P=-0.9076±4.9 (n=37) | 0.3978 | arrow=Δ-0.0262(±0.115,in-err) clock=Δ32(±206,in-err) split=Δ2.82(±9.04,in-err) |
| 4 | k=23.8 A=-0.2667±0.068 (-) | tau=-850.1±1e+02 | S=6.059 P=-4.442±6 (n=37) | 0.4468 | arrow=Δ-0.0234(±0.131,in-err) clock=Δ25.3(±202,in-err) split=Δ-3.53(±10.9,in-err) |
| 5 | k=23.8 A=-0.2864±0.081 (-) | tau=-826±1e+02 | S=5.462 P=-4.787±6.1 (n=37) | 0.4953 | arrow=Δ-0.0197(±0.149,in-err) clock=Δ24.2(±202,in-err) split=Δ-0.345(±12.1,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=26.4 A=-108.8±39 (-) | tau=1032±1.1e+02 | S=-1.598 P=0.2177±0.16 (n=38) | 0.1544 | -- |
| 1 | k=25.7 A=-25.33±24 (-) | tau=1.034e+04±3.7e+05 | S=-0.1844 P=0.03969±0.021 (n=37) | 0.04947 | arrow=Δ83.4(±62.9,OUT) clock=Δ9.31e+03(±3.65e+05,in-err) split=Δ-0.178(±0.177,OUT) |
| 2 | k=26.1 A=-18.14±15 (-) | tau=1701±1.8e+03 | S=-0.1277 P=0.01943±0.0095 (n=37) | 0.02267 | arrow=Δ7.19(±38.9,in-err) clock=Δ-8.64e+03(±3.67e+05,in-err) split=Δ-0.0203(±0.0306,in-err) |
| 3 | k=25.1 A=-7.693±9.6 (-) | tau=1645±6.6e+02 | S=-0.05751 P=0.00586±0.011 (n=37) | 0.01442 | arrow=Δ10.4(±24.9,in-err) clock=Δ-56(±2.49e+03,in-err) split=Δ-0.0136(±0.0201,in-err) |
| 4 | k=25.1 A=-7.542±7.9 (-) | tau=1319±3.6e+02 | S=-0.04758 P=0.0053±0.0047 (n=37) | 0.01119 | arrow=Δ0.151(±17.5,in-err) clock=Δ-326(±1.02e+03,in-err) split=Δ-0.00056(±0.0153,in-err) |
| 5 | k=26.4 A=-6.502±6.6 (-) | tau=852.4±1.5e+02 | S=-0.03982 P=0.005236±0.0037 (n=38) | 0.009407 | arrow=Δ1.04(±14.5,in-err) clock=Δ-466(±507,in-err) split=Δ-6.35e-05(±0.00831,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,clock,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=26.4 A=-108.8±42 (-) | tau=1032±1.1e+02 | S=-1.598 P=0.2177±0.19 (n=38) | 0.1544 | -- |
| 1 | k=23.8 A=0.1885±0.048 (+) | tau=955.7±1e+02 | S=-8.987 P=5.728±3.8 (n=38) | 0.3002 | arrow=Δ109(±42.2,OUT) clock=Δ-76.4(±216,in-err) split=Δ5.51(±4.02,OUT) |
| 2 | k=23.8 A=0.2173±0.059 (+) | tau=906.9±96 | S=-8.723 P=5.25±2.6 (n=37) | 0.3503 | arrow=Δ0.0288(±0.107,in-err) clock=Δ-48.8(±198,in-err) split=Δ-0.478(±6.45,in-err) |
| 3 | k=23.8 A=0.2435±0.067 (+) | tau=873.2±1.1e+02 | S=-8.438 P=5.36±2.8 (n=37) | 0.3979 | arrow=Δ0.0263(±0.126,in-err) clock=Δ-33.7(±203,in-err) split=Δ0.11(±5.41,in-err) |
| 4 | k=23.8 A=0.267±0.074 (+) | tau=848.1±95 | S=-8.046 P=5.524±3 (n=37) | 0.447 | arrow=Δ0.0235(±0.141,in-err) clock=Δ-25.1(±202,in-err) split=Δ0.164(±5.79,in-err) |
| 5 | k=23.8 A=0.2869±0.082 (+) | tau=819.3±1e+02 | S=-7.821 P=6.023±3.2 (n=37) | 0.4938 | arrow=Δ0.0199(±0.156,in-err) clock=Δ-28.7(±199,in-err) split=Δ0.5(±6.19,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=26.4 A=108.8±38 (+) | tau=-1030±1e+02 | S=1.559 P=-0.1449±0.35 (n=38) | 0.1541 | -- |
| 1 | k=25.7 A=25.63±24 (+) | tau=-1.07e+04±1e+05 | S=0.129 P=0.01039±0.025 (n=37) | 0.04936 | arrow=Δ-83.1(±62.1,OUT) clock=Δ-9.67e+03(±1.04e+05,in-err) split=Δ0.155(±0.373,in-err) |
| 2 | k=26.1 A=18.2±15 (+) | tau=-1741±5.9e+02 | S=0.09652 P=-0.01134±0.01 (n=37) | 0.02263 | arrow=Δ-7.42(±39,in-err) clock=Δ8.96e+03(±1.04e+05,in-err) split=Δ-0.0217(±0.035,in-err) |
| 3 | k=25.1 A=7.724±8.8 (+) | tau=-1587±5.8e+02 | S=0.03191 P=0.00151±0.0079 (n=37) | 0.01438 | arrow=Δ-10.5(±24.1,in-err) clock=Δ154(±1.17e+03,in-err) split=Δ0.0128(±0.0183,in-err) |
| 4 | k=25.1 A=7.745±7.5 (+) | tau=-1496±7.4e+02 | S=0.03202 P=0.000619±0.003 (n=37) | 0.01114 | arrow=Δ0.0205(±16.3,in-err) clock=Δ90.9(±1.32e+03,in-err) split=Δ-0.000891(±0.0108,in-err) |
| 5 | k=25.7 A=6.487±6.2 (+) | tau=-941.1±2.1e+02 | S=0.02337 P=0.001999±0.0036 (n=38) | 0.00937 | arrow=Δ-1.26(±13.6,in-err) clock=Δ555(±945,in-err) split=Δ0.00138(±0.00653,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=26.4 A=108.8±39 (+) | tau=-1030±1.1e+02 | S=1.559 P=-0.1449±0.3 (n=38) | 0.1541 | -- |
| 1 | k=23.8 A=-0.1884±0.046 (-) | tau=-955.8±1e+02 | S=7.954 P=-2.992±4.5 (n=38) | 0.3 | arrow=Δ-109(±39,OUT) clock=Δ74.7(±216,in-err) split=Δ-2.85(±4.79,in-err) |
| 2 | k=23.8 A=-0.2171±0.056 (-) | tau=-907.3±98 | S=7.295 P=-3.725±4.3 (n=37) | 0.3502 | arrow=Δ-0.0287(±0.102,in-err) clock=Δ48.5(±202,in-err) split=Δ-0.733(±8.81,in-err) |
| 3 | k=23.8 A=-0.2433±0.069 (-) | tau=-875.4±97 | S=6.501 P=-0.9076±5.3 (n=37) | 0.3978 | arrow=Δ-0.0262(±0.125,in-err) clock=Δ32(±195,in-err) split=Δ2.82(±9.65,in-err) |
| 4 | k=23.8 A=-0.2667±0.077 (-) | tau=-850.1±1e+02 | S=6.059 P=-4.442±5.8 (n=37) | 0.4468 | arrow=Δ-0.0234(±0.145,in-err) clock=Δ25.3(±197,in-err) split=Δ-3.53(±11.1,in-err) |
| 5 | k=23.8 A=-0.2864±0.082 (-) | tau=-826±1e+02 | S=5.462 P=-4.787±6 (n=37) | 0.4953 | arrow=Δ-0.0197(±0.159,in-err) clock=Δ24.2(±205,in-err) split=Δ-0.345(±11.8,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=16.5 A=0.0005217±0.00043 (+)  |  clock: tau=840.1±1.8e+02  |  split: S=-27.91 P=-1.465±7.3 (n=38)  (raw relay ran 5 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.0007011±0.00072 | -6.502±6.6 | AGREE |
| clock (tau) | 852.4±1.7e+02 | 852.4±1.5e+02 | AGREE |
| split (P) | 0.7393±0.7 | 0.005236±0.0037 | UNSTABLE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.0007011±0.00072 | -0.0007067±0.00068 | UNSTABLE |
| clock (tau) | 852.4±1.7e+02 | -941.1±1.9e+02 | UNSTABLE |
| split (P) | 0.7393±0.7 | 0.2673±0.57 | AGREE |

### DALET cutoff test (step sizes 0.05 / 0.10 / 0.20, BEFORE order, forward, ascent column)

**eta = 0.05**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=0.07768±0.021 (+) | tau=1032±99 | S=-45.1 P=10.17±7.5 (n=38) | 0.1544 | -- |
| 1 | k=23.8 A=0.173±0.046 (+) | tau=995.6±1e+02 | S=-9.237 P=5.575±3.2 (n=38) | 0.2773 | arrow=Δ0.0954(±0.0671,OUT) clock=Δ-36.5(±201,in-err) split=Δ-4.6(±10.7,in-err) |
| 2 | k=23.8 A=0.189±0.048 (+) | tau=952.9±1e+02 | S=-8.974 P=5.719±3.8 (n=38) | 0.3018 | arrow=Δ0.016(±0.0945,in-err) clock=Δ-42.7(±206,in-err) split=Δ0.145(±7.06,in-err) |
| 3 | k=23.8 A=0.2041±0.053 (+) | tau=925.3±1.1e+02 | S=-9.007 P=5.355±2.7 (n=37) | 0.3275 | arrow=Δ0.0151(±0.101,in-err) clock=Δ-27.6(±210,in-err) split=Δ-0.365(±6.49,in-err) |
| 4 | k=23.8 A=0.2184±0.06 (+) | tau=897.1±93 | S=-8.814 P=5.49±2.6 (n=37) | 0.3523 | arrow=Δ0.0143(±0.113,in-err) clock=Δ-28.2(±199,in-err) split=Δ0.135(±5.26,in-err) |
| 5 | k=23.8 A=0.2321±0.063 (+) | tau=878.9±1e+02 | S=-8.58 P=5.357±3.1 (n=37) | 0.3761 | arrow=Δ0.0137(±0.123,in-err) clock=Δ-18.3(±193,in-err) split=Δ-0.133(±5.73,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.1**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=0.07768±0.019 (+) | tau=1032±1.1e+02 | S=-45.1 P=10.17±6.5 (n=38) | 0.1544 | -- |
| 1 | k=23.8 A=0.1885±0.047 (+) | tau=955.7±1e+02 | S=-8.987 P=5.728±3.5 (n=38) | 0.3002 | arrow=Δ0.111(±0.0656,OUT) clock=Δ-76.4(±211,in-err) split=Δ-4.44(±9.97,in-err) |
| 2 | k=23.8 A=0.2173±0.057 (+) | tau=906.9±1e+02 | S=-8.723 P=5.25±2.9 (n=37) | 0.3503 | arrow=Δ0.0288(±0.104,in-err) clock=Δ-48.8(±205,in-err) split=Δ-0.478(±6.39,in-err) |
| 3 | k=23.8 A=0.2435±0.066 (+) | tau=873.2±99 | S=-8.438 P=5.36±2.8 (n=37) | 0.3979 | arrow=Δ0.0263(±0.123,in-err) clock=Δ-33.7(±200,in-err) split=Δ0.11(±5.69,in-err) |
| 4 | k=23.8 A=0.267±0.074 (+) | tau=848.1±1e+02 | S=-8.046 P=5.524±3.1 (n=37) | 0.447 | arrow=Δ0.0235(±0.141,in-err) clock=Δ-25.1(±201,in-err) split=Δ0.164(±5.89,in-err) |
| 5 | k=23.8 A=0.2869±0.079 (+) | tau=819.3±1e+02 | S=-7.821 P=6.023±3.2 (n=37) | 0.4938 | arrow=Δ0.0199(±0.153,in-err) clock=Δ-28.7(±201,in-err) split=Δ0.5(±6.3,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.2**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=0.07768±0.018 (+) | tau=1032±1.1e+02 | S=-45.1 P=10.17±7.1 (n=38) | 0.1544 | -- |
| 1 | k=23.8 A=0.2155±0.055 (+) | tau=914.5±98 | S=-8.858 P=5.241±2.6 (n=37) | 0.3466 | arrow=Δ0.138(±0.0732,OUT) clock=Δ-118(±206,in-err) split=Δ-4.93(±9.69,in-err) |
| 2 | k=23.8 A=0.263±0.079 (+) | tau=848.3±97 | S=-8.226 P=5.531±2.7 (n=37) | 0.4387 | arrow=Δ0.0475(±0.134,in-err) clock=Δ-66.3(±195,in-err) split=Δ0.291(±5.29,in-err) |
| 3 | k=23.8 A=0.302±0.098 (+) | tau=802.5±94 | S=-7.786 P=7.762±3.1 (n=37) | 0.5223 | arrow=Δ0.039(±0.177,in-err) clock=Δ-45.8(±191,in-err) split=Δ2.23(±5.86,in-err) |
| 4 | k=23.8 A=0.3344±0.11 (+) | tau=764.7±99 | S=-7.234 P=9.105±3.2 (n=37) | 0.6055 | arrow=Δ0.0324(±0.207,in-err) clock=Δ-37.8(±193,in-err) split=Δ1.34(±6.33,in-err) |
| 5 | k=23.8 A=0.3605±0.13 (+) | tau=739.5±97 | S=-6.754 P=7.484±3.5 (n=37) | 0.6726 | arrow=Δ0.0262(±0.241,in-err) clock=Δ-25.2(±195,in-err) split=Δ-1.62(±6.66,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

---

## horn_whole  (family: horn, units: s, n=29226)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.1 A=1.963±0.97 (+) | tau=-8.415e+04±1.1e+04 | S=-237.3 P=-51.01±48 (n=39) | 0.3159 | -- |
| 1 | k=11.9 A=0.3472±0.55 (+) | tau=1.93e+04±8e+02 | S=170.1 P=-2.296±11 (n=39) | 0.1825 | arrow=Δ-1.62(±1.51,OUT) clock=Δ1.03e+05(±1.17e+04,OUT) split=Δ48.7(±58.7,in-err) |
| 2 | k=11.2 A=0.2529±0.41 (+) | tau=7.147e+04±1.2e+04 | S=108.3 P=-0.6736±6.2 (n=39) | 0.1228 | arrow=Δ-0.0943(±0.958,in-err) clock=Δ5.22e+04(±1.3e+04,OUT) split=Δ1.62(±17.3,in-err) |
| 3 | k=16.5 A=0.1849±0.35 (+) | tau=-2.12e+05±1.8e+06 | S=80.45 P=-0.8733±4.4 (n=39) | 0.08948 | arrow=Δ-0.068(±0.758,in-err) clock=Δ-2.84e+05(±1.86e+06,in-err) split=Δ-0.2(±10.6,in-err) |
| 4 | k=16.5 A=0.1483±0.31 (+) | tau=-1.193e+05±4.5e+04 | S=77.1 P=0.8123±3 (n=39) | 0.06974 | arrow=Δ-0.0366(±0.659,in-err) clock=Δ9.27e+04(±1.89e+06,in-err) split=Δ1.69(±7.37,in-err) |
| 5 | k=16.5 A=0.1178±0.27 (+) | tau=-4.398e+04±4.2e+03 | S=59.12 P=0.07244±2.2 (n=39) | 0.0565 | arrow=Δ-0.0305(±0.58,in-err) clock=Δ7.53e+04(±4.95e+04,OUT) split=Δ-0.74(±5.19,in-err) |
| 6 | k=16.5 A=0.09629±0.26 (+) | tau=-5.766e+04±8.3e+03 | S=55.76 P=-0.4843±1.7 (n=39) | 0.04748 | arrow=Δ-0.0215(±0.524,in-err) clock=Δ-1.37e+04(±1.26e+04,OUT) split=Δ-0.557(±3.9,in-err) |
| 7 | k=16.5 A=0.07853±0.23 (+) | tau=-4.696e+04±5.3e+03 | S=46.89 P=0.1845±1.5 (n=39) | 0.04096 | arrow=Δ-0.0178(±0.484,in-err) clock=Δ1.07e+04(±1.36e+04,in-err) split=Δ0.669(±3.2,in-err) |
| 8 | k=16.5 A=0.06896±0.23 (+) | tau=-4.026e+04±4.4e+03 | S=40.61 P=0.2345±1.4 (n=39) | 0.03596 | arrow=Δ-0.00956(±0.459,in-err) clock=Δ6.7e+03(±9.72e+03,in-err) split=Δ0.0501(±2.86,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.1 A=1.963±1 (+) | tau=-8.415e+04±1e+04 | S=-237.3 P=-51.01±45 (n=39) | 0.3159 | -- |
| 1 | k=25.1 A=0.03337±0.013 (+) | tau=-7.543e+04±9.7e+03 | S=124.9 P=-13.46±14 (n=39) | 0.02181 | arrow=Δ-1.93(±1.02,OUT) clock=Δ8.72e+03(±2.01e+04,in-err) split=Δ37.6(±58.4,in-err) |
| 2 | k=25.1 A=0.03451±0.014 (+) | tau=-7.309e+04±9e+03 | S=132.2 P=-14.11±15 (n=39) | 0.02379 | arrow=Δ0.00115(±0.0268,in-err) clock=Δ2.34e+03(±1.87e+04,in-err) split=Δ-0.649(±28.5,in-err) |
| 3 | k=25.1 A=0.03577±0.016 (+) | tau=-7.76e+04±1.2e+04 | S=135.7 P=-16.31±17 (n=39) | 0.02569 | arrow=Δ0.00125(±0.0302,in-err) clock=Δ-4.51e+03(±2.11e+04,in-err) split=Δ-2.2(±31.8,in-err) |
| 4 | k=21.5 A=0.03706±0.016 (+) | tau=-8.617e+04±1.4e+04 | S=137.8 P=-16.96±18 (n=39) | 0.02747 | arrow=Δ0.00129(±0.0324,in-err) clock=Δ-8.57e+03(±2.62e+04,in-err) split=Δ-0.648(±35.4,in-err) |
| 5 | k=21.5 A=0.03827±0.017 (+) | tau=-9.559e+04±1.9e+04 | S=139.1 P=-15.76±18 (n=39) | 0.02907 | arrow=Δ0.00121(±0.0336,in-err) clock=Δ-9.41e+03(±3.32e+04,in-err) split=Δ1.2(±36.4,in-err) |
| 6 | k=21.5 A=0.0397±0.018 (+) | tau=-1.066e+05±3e+04 | S=140.2 P=-7.691±20 (n=39) | 0.0306 | arrow=Δ0.00143(±0.0352,in-err) clock=Δ-1.11e+04(±4.9e+04,in-err) split=Δ8.07(±38,in-err) |
| 7 | k=21.5 A=0.04057±0.018 (+) | tau=-1.169e+05±4.4e+04 | S=141.3 P=-7.68±22 (n=39) | 0.03205 | arrow=Δ0.000867(±0.036,in-err) clock=Δ-1.03e+04(±7.43e+04,in-err) split=Δ0.0107(±42,in-err) |
| 8 | k=21.5 A=0.04152±0.02 (+) | tau=-1.451e+05±2.1e+05 | S=141.5 P=-7.849±22 (n=39) | 0.03338 | arrow=Δ0.000957(±0.0382,in-err) clock=Δ-2.82e+04(±2.51e+05,in-err) split=Δ-0.169(±43.9,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.1 A=-1.963±0.98 (-) | tau=8.447e+04±1e+04 | S=252.9 P=43.19±48 (n=39) | 0.3159 | -- |
| 1 | k=11.9 A=-0.3473±0.54 (-) | tau=-1.925e+04±7.2e+02 | S=-159.9 P=5.406±12 (n=39) | 0.1825 | arrow=Δ1.62(±1.53,OUT) clock=Δ-1.04e+05(±1.11e+04,OUT) split=Δ-37.8(±60.1,in-err) |
| 2 | k=11.2 A=-0.2531±0.44 (-) | tau=-7.087e+04±1.1e+04 | S=-103.6 P=6.251±6.5 (n=39) | 0.1228 | arrow=Δ0.0942(±0.989,in-err) clock=Δ-5.16e+04(±1.21e+04,OUT) split=Δ0.846(±18.1,in-err) |
| 3 | k=16.5 A=-0.1851±0.34 (-) | tau=2.21e+05±4.1e+05 | S=-77.16 P=3.385±4.7 (n=39) | 0.0895 | arrow=Δ0.068(±0.787,in-err) clock=Δ2.92e+05(±4.2e+05,in-err) split=Δ-2.87(±11.1,in-err) |
| 4 | k=16.5 A=-0.1486±0.3 (-) | tau=1.212e+05±4.5e+04 | S=-74.51 P=1.485±3.3 (n=39) | 0.06976 | arrow=Δ0.0366(±0.643,in-err) clock=Δ-9.98e+04(±4.53e+05,in-err) split=Δ-1.9(±7.92,in-err) |
| 5 | k=16.5 A=-0.118±0.29 (-) | tau=4.398e+04±4.3e+03 | S=-57.44 P=2.196±2.6 (n=39) | 0.05652 | arrow=Δ0.0305(±0.592,in-err) clock=Δ-7.72e+04(±4.9e+04,OUT) split=Δ0.71(±5.84,in-err) |
| 6 | k=16.5 A=-0.09641±0.26 (-) | tau=5.78e+04±8.6e+03 | S=-54.37 P=1.17±2 (n=39) | 0.04749 | arrow=Δ0.0216(±0.553,in-err) clock=Δ1.38e+04(±1.29e+04,OUT) split=Δ-1.03(±4.57,in-err) |
| 7 | k=16.5 A=-0.07828±0.23 (-) | tau=4.686e+04±5.7e+03 | S=-45.67 P=1.027±1.6 (n=39) | 0.04097 | arrow=Δ0.0181(±0.492,in-err) clock=Δ-1.09e+04(±1.43e+04,in-err) split=Δ-0.143(±3.62,in-err) |
| 8 | k=16.5 A=-0.06906±0.22 (-) | tau=4.089e+04±4.1e+03 | S=-39.67 P=1.117±1.4 (n=39) | 0.03598 | arrow=Δ0.00922(±0.451,in-err) clock=Δ-5.97e+03(±9.81e+03,in-err) split=Δ0.0902(±3.05,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.1 A=-1.963±1.1 (-) | tau=8.447e+04±1.1e+04 | S=252.9 P=43.19±48 (n=39) | 0.3159 | -- |
| 1 | k=25.1 A=-0.03337±0.013 (-) | tau=7.567e+04±9.1e+03 | S=-121.1 P=9.188±15 (n=39) | 0.02181 | arrow=Δ1.93(±1.07,OUT) clock=Δ-8.8e+03(±1.98e+04,in-err) split=Δ-34(±63.6,in-err) |
| 2 | k=25.1 A=-0.03452±0.014 (-) | tau=7.33e+04±1e+04 | S=-129.2 P=9.505±16 (n=39) | 0.02379 | arrow=Δ-0.00115(±0.0271,in-err) clock=Δ-2.37e+03(±1.91e+04,in-err) split=Δ0.318(±31.2,in-err) |
| 3 | k=25.1 A=-0.03577±0.016 (-) | tau=7.783e+04±1.1e+04 | S=-133.7 P=16.06±18 (n=39) | 0.02569 | arrow=Δ-0.00125(±0.0297,in-err) clock=Δ4.53e+03(±2.07e+04,in-err) split=Δ6.56(±33.7,in-err) |
| 4 | k=21.5 A=-0.03706±0.017 (-) | tau=8.645e+04±1.4e+04 | S=-136.2 P=9.261±21 (n=39) | 0.02747 | arrow=Δ-0.00129(±0.0325,in-err) clock=Δ8.61e+03(±2.5e+04,in-err) split=Δ-6.8(±38.3,in-err) |
| 5 | k=21.5 A=-0.03828±0.017 (-) | tau=9.594e+04±1.8e+04 | S=-138.4 P=12.01±20 (n=39) | 0.02907 | arrow=Δ-0.00121(±0.0336,in-err) clock=Δ9.49e+03(±3.23e+04,in-err) split=Δ2.75(±40.7,in-err) |
| 6 | k=21.5 A=-0.0397±0.019 (-) | tau=1.071e+05±2.7e+04 | S=-141.1 P=17.17±23 (n=39) | 0.0306 | arrow=Δ-0.00143(±0.0357,in-err) clock=Δ1.11e+04(±4.47e+04,in-err) split=Δ5.16(±43.4,in-err) |
| 7 | k=21.5 A=-0.04057±0.02 (-) | tau=1.174e+05±3.3e+04 | S=-143 P=18.56±24 (n=39) | 0.03205 | arrow=Δ-0.000868(±0.0391,in-err) clock=Δ1.04e+04(±5.94e+04,in-err) split=Δ1.39(±47,in-err) |
| 8 | k=21.5 A=-0.04153±0.021 (-) | tau=1.461e+05±7.3e+04 | S=-144.3 P=21.54±23 (n=39) | 0.03338 | arrow=Δ-0.00096(±0.0415,in-err) clock=Δ2.86e+04(±1.06e+05,in-err) split=Δ2.98(±47,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=-15.59±37 (-) | tau=-8.415e+04±1.1e+04 | S=16.68 P=3.47±3.4 (n=39) | 0.3159 | -- |
| 1 | k=26.4 A=-9.363±25 (-) | tau=1.93e+04±8.1e+02 | S=-11.68 P=0.1465±0.75 (n=39) | 0.1825 | arrow=Δ6.23(±62.5,in-err) clock=Δ1.03e+05(±1.16e+04,OUT) split=Δ-3.32(±4.12,in-err) |
| 2 | k=26.4 A=-5.147±20 (-) | tau=7.147e+04±1.2e+04 | S=-8.121 P=0.0517±0.47 (n=39) | 0.1228 | arrow=Δ4.22(±45.8,in-err) clock=Δ5.22e+04(±1.29e+04,OUT) split=Δ-0.0948(±1.23,in-err) |
| 3 | k=26.4 A=-3.136±16 (-) | tau=-2.12e+05±7.6e+05 | S=-6.529 P=0.0709±0.39 (n=39) | 0.08948 | arrow=Δ2.01(±36,in-err) clock=Δ-2.84e+05(±7.76e+05,in-err) split=Δ0.0192(±0.868,in-err) |
| 4 | k=23.1 A=-2.003±14 (-) | tau=-1.193e+05±4.9e+04 | S=-6.667 P=-0.07025±0.25 (n=39) | 0.06974 | arrow=Δ1.13(±29.2,in-err) clock=Δ9.27e+04(±8.14e+05,in-err) split=Δ-0.141(±0.641,in-err) |
| 5 | k=23.1 A=-1.351±12 (-) | tau=-4.398e+04±4.4e+03 | S=-5.35 P=-0.006556±0.21 (n=39) | 0.0565 | arrow=Δ0.652(±25.4,in-err) clock=Δ7.53e+04(±5.38e+04,OUT) split=Δ0.0637(±0.459,in-err) |
| 6 | k=14.9 A=-1.062±10 (-) | tau=-5.766e+04±8e+03 | S=-5.244 P=0.04554±0.16 (n=39) | 0.04748 | arrow=Δ0.29(±21.9,in-err) clock=Δ-1.37e+04(±1.24e+04,OUT) split=Δ0.0521(±0.374,in-err) |
| 7 | k=14.9 A=-0.8405±10 (-) | tau=-4.696e+04±5.4e+03 | S=-4.551 P=-0.01791±0.14 (n=39) | 0.04096 | arrow=Δ0.221(±20.3,in-err) clock=Δ1.07e+04(±1.34e+04,in-err) split=Δ-0.0635(±0.307,in-err) |
| 8 | k=14.9 A=-0.6829±8.8 (-) | tau=-4.026e+04±4.4e+03 | S=-4.045 P=-0.02336±0.14 (n=39) | 0.03596 | arrow=Δ0.158(±19.1,in-err) clock=Δ6.7e+03(±9.77e+03,in-err) split=Δ-0.00545(±0.286,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=-15.59±37 (-) | tau=-8.415e+04±1e+04 | S=16.68 P=3.47±3.5 (n=39) | 0.3159 | -- |
| 1 | k=25.1 A=0.03337±0.013 (+) | tau=-7.543e+04±9.9e+03 | S=124.9 P=-13.46±13 (n=39) | 0.02181 | arrow=Δ15.6(±37.2,in-err) clock=Δ8.72e+03(±2.02e+04,in-err) split=Δ-16.9(±16.9,OUT) |
| 2 | k=25.1 A=0.03451±0.013 (+) | tau=-7.309e+04±9e+03 | S=132.2 P=-14.11±15 (n=39) | 0.02379 | arrow=Δ0.00115(±0.0267,in-err) clock=Δ2.34e+03(±1.89e+04,in-err) split=Δ-0.649(±28.7,in-err) |
| 3 | k=25.1 A=0.03577±0.015 (+) | tau=-7.76e+04±1.2e+04 | S=135.7 P=-16.31±16 (n=39) | 0.02569 | arrow=Δ0.00125(±0.0285,in-err) clock=Δ-4.51e+03(±2.12e+04,in-err) split=Δ-2.2(±31.6,in-err) |
| 4 | k=21.5 A=0.03706±0.016 (+) | tau=-8.617e+04±1.6e+04 | S=137.8 P=-16.96±17 (n=39) | 0.02747 | arrow=Δ0.00129(±0.0312,in-err) clock=Δ-8.57e+03(±2.8e+04,in-err) split=Δ-0.648(±33.5,in-err) |
| 5 | k=21.5 A=0.03827±0.017 (+) | tau=-9.559e+04±2.5e+04 | S=139.1 P=-15.76±19 (n=39) | 0.02907 | arrow=Δ0.00121(±0.0325,in-err) clock=Δ-9.41e+03(±4.06e+04,in-err) split=Δ1.2(±36.1,in-err) |
| 6 | k=21.5 A=0.0397±0.018 (+) | tau=-1.066e+05±2.6e+04 | S=140.2 P=-7.691±22 (n=39) | 0.0306 | arrow=Δ0.00143(±0.034,in-err) clock=Δ-1.11e+04(±5.08e+04,in-err) split=Δ8.07(±40.9,in-err) |
| 7 | k=21.5 A=0.04057±0.018 (+) | tau=-1.169e+05±3.2e+04 | S=141.3 P=-7.68±23 (n=39) | 0.03205 | arrow=Δ0.000867(±0.0359,in-err) clock=Δ-1.03e+04(±5.83e+04,in-err) split=Δ0.0107(±45,in-err) |
| 8 | k=21.5 A=0.04152±0.021 (+) | tau=-1.451e+05±1.1e+05 | S=141.5 P=-7.849±20 (n=39) | 0.03338 | arrow=Δ0.000957(±0.0394,in-err) clock=Δ-2.82e+04(±1.37e+05,in-err) split=Δ-0.169(±43.3,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=15.59±35 (+) | tau=8.447e+04±1e+04 | S=-18.52 P=-3.378±3.5 (n=39) | 0.3159 | -- |
| 1 | k=26.4 A=9.363±26 (+) | tau=-1.925e+04±7.9e+02 | S=11.04 P=-0.3181±0.7 (n=39) | 0.1825 | arrow=Δ-6.23(±60.7,in-err) clock=Δ-1.04e+05(±1.1e+04,OUT) split=Δ3.06(±4.21,in-err) |
| 2 | k=26.4 A=5.141±19 (+) | tau=-7.087e+04±1.1e+04 | S=7.767 P=-0.4695±0.49 (n=39) | 0.1228 | arrow=Δ-4.22(±45.1,in-err) clock=Δ-5.16e+04(±1.2e+04,OUT) split=Δ-0.151(±1.19,in-err) |
| 3 | k=26.4 A=3.129±17 (+) | tau=2.21e+05±8.3e+05 | S=6.262 P=-0.2747±0.38 (n=39) | 0.0895 | arrow=Δ-2.01(±35.7,in-err) clock=Δ2.92e+05(±8.44e+05,in-err) split=Δ0.195(±0.876,in-err) |
| 4 | k=23.1 A=1.995±12 (+) | tau=1.212e+05±4.3e+04 | S=6.443 P=-0.1285±0.3 (n=39) | 0.06976 | arrow=Δ-1.13(±29,in-err) clock=Δ-9.98e+04(±8.75e+05,in-err) split=Δ0.146(±0.68,in-err) |
| 5 | k=23.1 A=1.344±12 (+) | tau=4.398e+04±4.3e+03 | S=5.198 P=-0.1987±0.23 (n=39) | 0.05652 | arrow=Δ-0.652(±24.2,in-err) clock=Δ-7.72e+04(±4.7e+04,OUT) split=Δ-0.0703(±0.529,in-err) |
| 6 | k=14.9 A=1.058±11 (+) | tau=5.78e+04±7.9e+03 | S=5.113 P=-0.11±0.19 (n=39) | 0.04749 | arrow=Δ-0.286(±22.9,in-err) clock=Δ1.38e+04(±1.21e+04,OUT) split=Δ0.0887(±0.428,in-err) |
| 7 | k=14.9 A=0.8372±10 (+) | tau=4.686e+04±5.4e+03 | S=4.434 P=-0.09972±0.16 (n=39) | 0.04097 | arrow=Δ-0.221(±21,in-err) clock=Δ-1.09e+04(±1.32e+04,in-err) split=Δ0.0103(±0.353,in-err) |
| 8 | k=14.9 A=0.6804±9.1 (+) | tau=4.089e+04±4.2e+03 | S=3.952 P=-0.1113±0.14 (n=39) | 0.03598 | arrow=Δ-0.157(±19.2,in-err) clock=Δ-5.97e+03(±9.63e+03,in-err) split=Δ-0.0116(±0.295,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=25.7 A=15.59±37 (+) | tau=8.447e+04±1.1e+04 | S=-18.52 P=-3.378±3.6 (n=39) | 0.3159 | -- |
| 1 | k=25.1 A=-0.03337±0.013 (-) | tau=7.567e+04±8.6e+03 | S=-121.1 P=9.188±15 (n=39) | 0.02181 | arrow=Δ-15.6(±36.5,in-err) clock=Δ-8.8e+03(±1.99e+04,in-err) split=Δ12.6(±18.9,in-err) |
| 2 | k=25.1 A=-0.03452±0.015 (-) | tau=7.33e+04±9.4e+03 | S=-129.2 P=9.505±17 (n=39) | 0.02379 | arrow=Δ-0.00115(±0.0272,in-err) clock=Δ-2.37e+03(±1.8e+04,in-err) split=Δ0.318(±32.2,in-err) |
| 3 | k=25.1 A=-0.03577±0.015 (-) | tau=7.783e+04±1.1e+04 | S=-133.7 P=16.06±18 (n=39) | 0.02569 | arrow=Δ-0.00125(±0.0301,in-err) clock=Δ4.53e+03(±2.03e+04,in-err) split=Δ6.56(±34.9,in-err) |
| 4 | k=21.5 A=-0.03706±0.017 (-) | tau=8.645e+04±1.4e+04 | S=-136.2 P=9.261±20 (n=39) | 0.02747 | arrow=Δ-0.00129(±0.0323,in-err) clock=Δ8.61e+03(±2.49e+04,in-err) split=Δ-6.8(±38.4,in-err) |
| 5 | k=21.5 A=-0.03828±0.017 (-) | tau=9.594e+04±2e+04 | S=-138.4 P=12.01±20 (n=39) | 0.02907 | arrow=Δ-0.00121(±0.0343,in-err) clock=Δ9.49e+03(±3.39e+04,in-err) split=Δ2.75(±39.9,in-err) |
| 6 | k=21.5 A=-0.0397±0.021 (-) | tau=1.071e+05±3.3e+04 | S=-141.1 P=17.17±25 (n=39) | 0.0306 | arrow=Δ-0.00143(±0.038,in-err) clock=Δ1.11e+04(±5.31e+04,in-err) split=Δ5.16(±44.2,in-err) |
| 7 | k=21.5 A=-0.04057±0.02 (-) | tau=1.174e+05±4.1e+04 | S=-143 P=18.56±25 (n=39) | 0.03205 | arrow=Δ-0.000868(±0.0404,in-err) clock=Δ1.04e+04(±7.47e+04,in-err) split=Δ1.39(±49.4,in-err) |
| 8 | k=21.5 A=-0.04153±0.02 (-) | tau=1.461e+05±6.1e+04 | S=-144.3 P=21.54±24 (n=39) | 0.03338 | arrow=Δ-0.00096(±0.04,in-err) clock=Δ2.86e+04(±1.03e+05,in-err) split=Δ2.98(±49.2,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=17.8 A=0.06325±0.032 (+)  |  clock: tau=-4.333e+04±5e+03  |  split: S=778.3 P=6.714±48 (n=39)  (raw relay ran 8 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.06896±0.23 | -0.6829±8.8 | AGREE |
| clock (tau) | -4.026e+04±4.4e+03 | -4.026e+04±4.4e+03 | AGREE |
| split (P) | 0.2345±1.4 | -0.02336±0.14 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.06896±0.23 | -0.06906±0.22 | AGREE |
| clock (tau) | -4.026e+04±4.4e+03 | 4.089e+04±4.1e+03 | UNSTABLE |
| split (P) | 0.2345±1.4 | 1.117±1.4 | AGREE |

---

## buzz_seat80  (family: buzz, units: shots, n=4000)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=-131.7±60 (-) | tau=1.016e+05±2.1e+06 | S=-24.35 P=-0.7363±3.5 (n=38) | 0.1945 | -- |
| 1 | k=40 A=21±9.3 (+) | tau=4.916e+04±2.5e+05 | S=-44.93 P=-3.436±5.1 (n=38) | 0.06402 | arrow=Δ153(±69.5,OUT) clock=Δ-5.24e+04(±2.4e+06,in-err) split=Δ-2.7(±8.65,in-err) |
| 2 | k=8 A=4.3±3 (+) | tau=1.687e+04±2.7e+03 | S=-108.3 P=0.1429±6.5 (n=38) | 0.0301 | arrow=Δ-16.7(±12.3,OUT) clock=Δ-3.23e+04(±2.55e+05,in-err) split=Δ3.58(±11.6,in-err) |
| 3 | k=20 A=2.856±1.4 (+) | tau=1.033e+04±1.3e+03 | S=-139 P=19.18±13 (n=38) | 0.0185 | arrow=Δ-1.44(±4.37,in-err) clock=Δ-6.55e+03(±4.02e+03,OUT) split=Δ19(±19.3,in-err) |
| 4 | k=53 A=2.474±0.87 (+) | tau=1.105e+04±1.5e+03 | S=-142.4 P=-6.578±17 (n=39) | 0.01319 | arrow=Δ-0.382(±2.26,in-err) clock=Δ719(±2.81e+03,in-err) split=Δ-25.8(±30,in-err) |
| 5 | k=53 A=2.013±0.62 (+) | tau=1.006e+04±1.4e+03 | S=-144.9 P=9.975±11 (n=38) | 0.01016 | arrow=Δ-0.46(±1.49,in-err) clock=Δ-986(±2.91e+03,in-err) split=Δ16.6(±27.8,in-err) |
| 6 | k=53 A=1.714±0.5 (+) | tau=7903±6.9e+02 | S=-143.9 P=8.003±22 (n=38) | 0.008141 | arrow=Δ-0.299(±1.12,in-err) clock=Δ-2.16e+03(±2.12e+03,OUT) split=Δ-1.97(±32.3,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=-131.7±56 (-) | tau=1.016e+05±9.2e+05 | S=-24.35 P=-0.7363±3.4 (n=38) | 0.1945 | -- |
| 1 | k=76 A=-0.03181±0.016 (-) | tau=3.713e+05±6.9e+06 | S=-26.5 P=-3.388±3.3 (n=38) | 0.0009121 | arrow=Δ132(±56.1,OUT) clock=Δ2.7e+05(±7.77e+06,in-err) split=Δ-2.65(±6.65,in-err) |
| 2 | k=76 A=-0.03546±0.02 (-) | tau=3.091e+05±2e+06 | S=-31.17 P=-0.909±4.2 (n=38) | 0.001062 | arrow=Δ-0.00366(±0.036,in-err) clock=Δ-6.21e+04(±8.84e+06,in-err) split=Δ2.48(±7.51,in-err) |
| 3 | k=80 A=-0.04083±0.019 (-) | tau=1.677e+05±3.2e+06 | S=-37.76 P=-2.755±7.8 (n=38) | 0.001192 | arrow=Δ-0.00537(±0.039,in-err) clock=Δ-1.41e+05(±5.18e+06,in-err) split=Δ-1.85(±12.1,in-err) |
| 4 | k=80 A=-0.04795±0.02 (-) | tau=2.446e+05±2.3e+06 | S=-38.33 P=-3.473±5.2 (n=38) | 0.001329 | arrow=Δ-0.00712(±0.0397,in-err) clock=Δ7.69e+04(±5.52e+06,in-err) split=Δ-0.718(±13.1,in-err) |
| 5 | k=80 A=-0.05536±0.025 (-) | tau=-7.055e+05±1.4e+07 | S=-41.88 P=-2.437±5.8 (n=38) | 0.001461 | arrow=Δ-0.00742(±0.0452,in-err) clock=Δ-9.5e+05(±1.68e+07,in-err) split=Δ1.04(±11,in-err) |
| 6 | k=80 A=-0.06221±0.025 (-) | tau=-1.073e+05±3e+06 | S=-47.08 P=2.528±7.3 (n=38) | 0.00159 | arrow=Δ-0.00684(±0.0495,in-err) clock=Δ5.98e+05(±1.75e+07,in-err) split=Δ4.96(±13.1,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=131.7±54 (+) | tau=-1.016e+05±1.3e+06 | S=26.73 P=-8.978±4.3 (n=38) | 0.1945 | -- |
| 1 | k=40 A=-21±9.1 (-) | tau=-4.916e+04±1.3e+05 | S=45.41 P=0.9831±8.3 (n=38) | 0.06402 | arrow=Δ-153(±62.8,OUT) clock=Δ5.24e+04(±1.42e+06,in-err) split=Δ9.96(±12.6,in-err) |
| 2 | k=8 A=-4.3±3 (-) | tau=-1.687e+04±2.9e+03 | S=104.7 P=6.685±5.8 (n=38) | 0.0301 | arrow=Δ16.7(±12.1,OUT) clock=Δ3.23e+04(±1.36e+05,in-err) split=Δ5.7(±14.1,in-err) |
| 3 | k=20 A=-2.856±1.4 (-) | tau=-1.033e+04±1.2e+03 | S=137.7 P=30.59±15 (n=38) | 0.0185 | arrow=Δ1.44(±4.39,in-err) clock=Δ6.55e+03(±4.14e+03,OUT) split=Δ23.9(±20.9,OUT) |
| 4 | k=53 A=-2.474±0.92 (-) | tau=-1.105e+04±1.5e+03 | S=142.4 P=-12.53±17 (n=39) | 0.01319 | arrow=Δ0.382(±2.34,in-err) clock=Δ-719(±2.7e+03,in-err) split=Δ-43.1(±32.2,OUT) |
| 5 | k=53 A=-2.013±0.65 (-) | tau=-1.006e+04±1.2e+03 | S=143.2 P=1.274±22 (n=38) | 0.01016 | arrow=Δ0.46(±1.58,in-err) clock=Δ986(±2.63e+03,in-err) split=Δ13.8(±39,in-err) |
| 6 | k=53 A=-1.714±0.51 (-) | tau=-7903±7.4e+02 | S=137.4 P=1.852±30 (n=38) | 0.008141 | arrow=Δ0.299(±1.16,in-err) clock=Δ2.16e+03(±1.92e+03,OUT) split=Δ0.578(±52.1,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=131.7±58 (+) | tau=-1.016e+05±9.4e+05 | S=26.73 P=-8.978±4.1 (n=38) | 0.1945 | -- |
| 1 | k=76 A=0.03181±0.015 (+) | tau=-3.713e+05±1.3e+07 | S=28.74 P=-3.606±7.2 (n=38) | 0.0009121 | arrow=Δ-132(±57.8,OUT) clock=Δ-2.7e+05(±1.37e+07,in-err) split=Δ5.37(±11.4,in-err) |
| 2 | k=76 A=0.03546±0.019 (+) | tau=-3.091e+05±1e+06 | S=32.31 P=-1.629±6.8 (n=38) | 0.001062 | arrow=Δ0.00366(±0.0341,in-err) clock=Δ6.21e+04(±1.38e+07,in-err) split=Δ1.98(±14,in-err) |
| 3 | k=80 A=0.04083±0.019 (+) | tau=-1.677e+05±4.9e+06 | S=36.91 P=-0.8677±7.5 (n=38) | 0.001192 | arrow=Δ0.00537(±0.0379,in-err) clock=Δ1.41e+05(±5.9e+06,in-err) split=Δ0.761(±14.3,in-err) |
| 4 | k=80 A=0.04795±0.022 (+) | tau=-2.446e+05±1e+06 | S=40.46 P=-0.03411±8.4 (n=38) | 0.001329 | arrow=Δ0.00712(±0.041,in-err) clock=Δ-7.69e+04(±5.91e+06,in-err) split=Δ0.834(±15.9,in-err) |
| 5 | k=80 A=0.05536±0.023 (+) | tau=7.055e+05±8.6e+06 | S=43.8 P=0.6485±8.8 (n=38) | 0.001461 | arrow=Δ0.00742(±0.045,in-err) clock=Δ9.5e+05(±9.68e+06,in-err) split=Δ0.683(±17.2,in-err) |
| 6 | k=80 A=0.06221±0.026 (+) | tau=1.073e+05±1.5e+06 | S=46.74 P=3.214±11 (n=38) | 0.00159 | arrow=Δ0.00684(±0.049,in-err) clock=Δ-5.98e+05(±1.01e+07,in-err) split=Δ2.57(±19.8,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=2.919e+04±2.8e+03 (+) | tau=-1.138e+04±1.3e+03 | S=606.1 P=5.613±10 (n=38) | 0.2278 | -- |
| 1 | k=80 A=1.767e+04±1.6e+03 (+) | tau=1.259e+04±2.9e+03 | S=173.5 P=3.705±2.2 (n=38) | 0.1158 | arrow=Δ-1.15e+04(±4.31e+03,OUT) clock=Δ2.4e+04(±4.26e+03,OUT) split=Δ-1.91(±12.3,in-err) |
| 2 | k=80 A=1.508e+04±1.1e+03 (+) | tau=2.108e+05±9.7e+05 | S=133.7 P=2.249±1.5 (n=38) | 0.07216 | arrow=Δ-2.58e+03(±2.67e+03,in-err) clock=Δ1.98e+05(±9.72e+05,in-err) split=Δ-1.46(±3.68,in-err) |
| 3 | k=80 A=1.31e+04±8.7e+02 (+) | tau=-2.324e+04±7.6e+04 | S=106 P=1.314±0.94 (n=38) | 0.05323 | arrow=Δ-1.99e+03(±1.98e+03,OUT) clock=Δ-2.34e+05(±1.04e+06,in-err) split=Δ-0.935(±2.43,in-err) |
| 4 | k=80 A=1.179e+04±7.3e+02 (+) | tau=-4.08e+04±1.9e+05 | S=87.43 P=-0.5088±1.1 (n=38) | 0.0433 | arrow=Δ-1.31e+03(±1.59e+03,in-err) clock=Δ-1.76e+04(±2.7e+05,in-err) split=Δ-1.82(±2.03,in-err) |
| 5 | k=80 A=1.093e+04±6.6e+02 (+) | tau=-3.793e+04±2.7e+05 | S=74.9 P=-1.263±0.88 (n=38) | 0.03778 | arrow=Δ-855(±1.39e+03,in-err) clock=Δ2.88e+03(±4.61e+05,in-err) split=Δ-0.754(±1.96,in-err) |
| 6 | k=80 A=1.036e+04±6.3e+02 (+) | tau=-4.923e+04±2.2e+06 | S=67.35 P=-0.599±0.73 (n=38) | 0.03412 | arrow=Δ-570(±1.29e+03,in-err) clock=Δ-1.13e+04(±2.46e+06,in-err) split=Δ0.664(±1.62,in-err) |
| 7 | k=80 A=9938±6e+02 (+) | tau=-2.101e+05±3.4e+05 | S=61.2 P=-0.635±0.55 (n=38) | 0.03151 | arrow=Δ-423(±1.23e+03,in-err) clock=Δ-1.61e+05(±2.53e+06,in-err) split=Δ-0.036(±1.29,in-err) |
| 8 | k=80 A=9615±6e+02 (+) | tau=-1.041e+05±8.6e+05 | S=56.26 P=0.08895±0.23 (n=38) | 0.02949 | arrow=Δ-323(±1.21e+03,in-err) clock=Δ1.06e+05(±1.2e+06,in-err) split=Δ0.724(±0.78,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: clock,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=2.919e+04±2.8e+03 (+) | tau=-1.138e+04±1.4e+03 | S=606.1 P=5.613±10 (n=38) | 0.2278 | -- |
| 1 | k=80 A=0.09401±0.008 (+) | tau=-1.115e+04±1.4e+03 | S=101.5 P=-30.28±14 (n=38) | 0.0001251 | arrow=Δ-2.92e+04(±2.76e+03,OUT) clock=Δ231(±2.72e+03,in-err) split=Δ-35.9(±23.9,OUT) |
| 2 | k=80 A=0.1136±0.0096 (+) | tau=-1.118e+04±1.5e+03 | S=90.46 P=-15.32±17 (n=38) | 0.0001436 | arrow=Δ0.0196(±0.0175,OUT) clock=Δ-21.7(±2.86e+03,in-err) split=Δ15(±30.4,in-err) |
| 3 | k=80 A=0.1333±0.01 (+) | tau=-1.139e+04±1.9e+03 | S=82.33 P=-15.31±19 (n=38) | 0.0001619 | arrow=Δ0.0196(±0.02,in-err) clock=Δ-216(±3.39e+03,in-err) split=Δ0.011(±36,in-err) |
| 4 | k=80 A=0.1527±0.012 (+) | tau=-1.201e+04±2.1e+03 | S=74.29 P=-17.81±19 (n=38) | 0.0001801 | arrow=Δ0.0194(±0.022,in-err) clock=Δ-622(±3.97e+03,in-err) split=Δ-2.5(±38.7,in-err) |
| 5 | k=80 A=0.1715±0.013 (+) | tau=-1.214e+04±2.4e+03 | S=67.29 P=-25.22±20 (n=38) | 0.0001978 | arrow=Δ0.0188(±0.0248,in-err) clock=Δ-123(±4.45e+03,in-err) split=Δ-7.4(±38.8,in-err) |
| 6 | k=80 A=0.1895±0.013 (+) | tau=-1.308e+04±3.1e+03 | S=59.66 P=-36.58±22 (n=38) | 0.0002127 | arrow=Δ0.018(±0.0264,in-err) clock=Δ-943(±5.48e+03,in-err) split=Δ-11.4(±42,in-err) |
| 7 | k=80 A=0.2068±0.015 (+) | tau=-1.394e+04±3.3e+03 | S=52.14 P=-38.74±22 (n=38) | 0.0002275 | arrow=Δ0.0173(±0.028,in-err) clock=Δ-864(±6.42e+03,in-err) split=Δ-2.16(±44.8,in-err) |
| 8 | k=80 A=0.2232±0.015 (+) | tau=-1.581e+04±4.7e+03 | S=44.48 P=-23.85±25 (n=38) | 0.0002404 | arrow=Δ0.0164(±0.0296,in-err) clock=Δ-1.86e+03(±8.09e+03,in-err) split=Δ14.9(±47,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-2.919e+04±2.8e+03 (-) | tau=1.138e+04±1.3e+03 | S=-620.9 P=43.52±13 (n=38) | 0.2278 | -- |
| 1 | k=80 A=-1.767e+04±1.6e+03 (-) | tau=-1.259e+04±2.7e+03 | S=-173.5 P=-2.738±2.3 (n=38) | 0.1158 | arrow=Δ1.15e+04(±4.33e+03,OUT) clock=Δ-2.4e+04(±4.01e+03,OUT) split=Δ-46.3(±15.3,OUT) |
| 2 | k=80 A=-1.508e+04±1.2e+03 (-) | tau=-2.108e+05±1e+06 | S=-134.6 P=1.686±2 (n=38) | 0.07216 | arrow=Δ2.58e+03(±2.77e+03,in-err) clock=Δ-1.98e+05(±9.98e+05,in-err) split=Δ4.42(±4.35,OUT) |
| 3 | k=80 A=-1.31e+04±8.2e+02 (-) | tau=2.324e+04±3.1e+06 | S=-106.8 P=1.527±1.4 (n=38) | 0.05323 | arrow=Δ1.99e+03(±2.02e+03,in-err) clock=Δ2.34e+05(±4.14e+06,in-err) split=Δ-0.159(±3.38,in-err) |
| 4 | k=80 A=-1.179e+04±7.3e+02 (-) | tau=4.08e+04±2.4e+05 | S=-87.35 P=1.194±0.98 (n=38) | 0.0433 | arrow=Δ1.31e+03(±1.55e+03,in-err) clock=Δ1.76e+04(±3.38e+06,in-err) split=Δ-0.333(±2.33,in-err) |
| 5 | k=80 A=-1.093e+04±7e+02 (-) | tau=3.793e+04±6.1e+05 | S=-75.22 P=1.57±0.8 (n=38) | 0.03778 | arrow=Δ855(±1.43e+03,in-err) clock=Δ-2.88e+03(±8.49e+05,in-err) split=Δ0.377(±1.78,in-err) |
| 6 | k=80 A=-1.036e+04±6.2e+02 (-) | tau=4.923e+04±2.1e+06 | S=-66.07 P=-0.02782±0.68 (n=38) | 0.03412 | arrow=Δ570(±1.32e+03,in-err) clock=Δ1.13e+04(±2.74e+06,in-err) split=Δ-1.6(±1.48,OUT) |
| 7 | k=80 A=-9938±6.1e+02 (-) | tau=2.101e+05±3.3e+05 | S=-60.29 P=-0.01637±0.5 (n=38) | 0.03151 | arrow=Δ423(±1.23e+03,in-err) clock=Δ1.61e+05(±2.45e+06,in-err) split=Δ0.0115(±1.18,in-err) |
| 8 | k=80 A=-9615±5.9e+02 (-) | tau=1.041e+05±4.1e+05 | S=-57.08 P=-0.07012±0.28 (n=38) | 0.02949 | arrow=Δ323(±1.2e+03,in-err) clock=Δ-1.06e+05(±7.34e+05,in-err) split=Δ-0.0538(±0.783,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,clock)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-2.919e+04±2.7e+03 (-) | tau=1.138e+04±1.5e+03 | S=-620.9 P=43.52±15 (n=38) | 0.2278 | -- |
| 1 | k=80 A=-0.09401±0.0073 (-) | tau=1.115e+04±1.5e+03 | S=-98.41 P=52.48±21 (n=38) | 0.0001251 | arrow=Δ2.92e+04(±2.7e+03,OUT) clock=Δ-231(±3.02e+03,in-err) split=Δ8.95(±36.1,in-err) |
| 2 | k=80 A=-0.1136±0.0087 (-) | tau=1.118e+04±1.6e+03 | S=-90.17 P=54.6±23 (n=38) | 0.0001436 | arrow=Δ-0.0196(±0.016,OUT) clock=Δ21.7(±3.16e+03,in-err) split=Δ2.13(±44,in-err) |
| 3 | k=80 A=-0.1333±0.01 (-) | tau=1.139e+04±1.8e+03 | S=-81.71 P=56.96±27 (n=38) | 0.0001619 | arrow=Δ-0.0196(±0.0188,OUT) clock=Δ216(±3.49e+03,in-err) split=Δ2.36(±49.8,in-err) |
| 4 | k=80 A=-0.1527±0.011 (-) | tau=1.201e+04±2.1e+03 | S=-72.94 P=53.63±27 (n=38) | 0.0001801 | arrow=Δ-0.0194(±0.0215,in-err) clock=Δ622(±3.91e+03,in-err) split=Δ-3.33(±54.3,in-err) |
| 5 | k=80 A=-0.1715±0.013 (-) | tau=1.214e+04±2.4e+03 | S=-63.87 P=43.76±30 (n=38) | 0.0001978 | arrow=Δ-0.0188(±0.0242,in-err) clock=Δ123(±4.46e+03,in-err) split=Δ-9.87(±57.6,in-err) |
| 6 | k=80 A=-0.1895±0.014 (-) | tau=1.308e+04±3.4e+03 | S=-56.01 P=24.02±24 (n=38) | 0.0002127 | arrow=Δ-0.018(±0.0267,in-err) clock=Δ943(±5.77e+03,in-err) split=Δ-19.7(±53.9,in-err) |
| 7 | k=80 A=-0.2068±0.015 (-) | tau=1.394e+04±3.7e+03 | S=-48.3 P=25.8±27 (n=38) | 0.0002275 | arrow=Δ-0.0173(±0.0286,in-err) clock=Δ864(±7.08e+03,in-err) split=Δ1.78(±50.5,in-err) |
| 8 | k=80 A=-0.2232±0.017 (-) | tau=1.581e+04±4.8e+03 | S=-41.39 P=27.81±26 (n=38) | 0.0002404 | arrow=Δ-0.0164(±0.0314,in-err) clock=Δ1.86e+03(±8.54e+03,in-err) split=Δ2.02(±52.6,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=42 A=263.6±33 (+)  |  clock: tau=-4.347e+04±2.9e+05  |  split: S=1.565 P=1.672±20 (n=35)  (raw relay ran 8 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 1.714±0.5 | 9615±6e+02 | UNSTABLE |
| clock (tau) | 7903±6.9e+02 | -1.041e+05±8.6e+05 | AGREE |
| split (P) | 8.003±22 | 0.08895±0.23 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 1.714±0.5 | -1.714±0.51 | UNSTABLE |
| clock (tau) | 7903±6.9e+02 | -7903±7.4e+02 | UNSTABLE |
| split (P) | 8.003±22 | 1.852±30 | AGREE |

### DALET cutoff test (step sizes 0.05 / 0.10 / 0.20, BEFORE order, forward, ascent column)

**eta = 0.05**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=-131.7±57 (-) | tau=1.016e+05±1.8e+06 | S=-24.35 P=-0.7363±3.5 (n=38) | 0.1945 | -- |
| 1 | k=76 A=-0.03195±0.016 (-) | tau=1.789e+05±6.9e+05 | S=-25.49 P=-2.623±2.9 (n=38) | 0.0008398 | arrow=Δ132(±56.6,OUT) clock=Δ7.73e+04(±2.51e+06,in-err) split=Δ-1.89(±6.4,in-err) |
| 2 | k=76 A=-0.03266±0.017 (-) | tau=1.769e+05±2.5e+06 | S=-27.05 P=-3.519±4 (n=38) | 0.0009167 | arrow=Δ-0.000708(±0.0323,in-err) clock=Δ-2.09e+03(±3.21e+06,in-err) split=Δ-0.896(±6.89,in-err) |
| 3 | k=76 A=-0.03411±0.018 (-) | tau=4.778e+05±1.6e+07 | S=-29.34 P=-1.066±3.7 (n=38) | 0.0009869 | arrow=Δ-0.00145(±0.0346,in-err) clock=Δ3.01e+05(±1.83e+07,in-err) split=Δ2.45(±7.62,in-err) |
| 4 | k=77 A=-0.03636±0.019 (-) | tau=1.929e+05±1.4e+06 | S=-31.87 P=-0.7306±4.5 (n=38) | 0.001066 | arrow=Δ-0.00224(±0.0372,in-err) clock=Δ-2.85e+05(±1.71e+07,in-err) split=Δ0.336(±8.17,in-err) |
| 5 | k=77 A=-0.03897±0.019 (-) | tau=1.702e+05±3.6e+06 | S=-35.85 P=-2.959±7.2 (n=38) | 0.001129 | arrow=Δ-0.00261(±0.038,in-err) clock=Δ-2.27e+04(±4.93e+06,in-err) split=Δ-2.23(±11.7,in-err) |
| 6 | k=80 A=-0.04221±0.019 (-) | tau=1.689e+05±3.5e+06 | S=-35.43 P=-2.789±4.9 (n=38) | 0.001196 | arrow=Δ-0.00324(±0.0379,in-err) clock=Δ-1.28e+03(±7.08e+06,in-err) split=Δ0.17(±12.1,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.1**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=-131.7±62 (-) | tau=1.016e+05±7.6e+05 | S=-24.35 P=-0.7363±3.2 (n=38) | 0.1945 | -- |
| 1 | k=76 A=-0.03181±0.015 (-) | tau=3.713e+05±1.6e+06 | S=-26.5 P=-3.388±3.2 (n=38) | 0.0009121 | arrow=Δ132(±61.8,OUT) clock=Δ2.7e+05(±2.35e+06,in-err) split=Δ-2.65(±6.36,in-err) |
| 2 | k=76 A=-0.03546±0.018 (-) | tau=3.091e+05±2.4e+06 | S=-31.17 P=-0.909±4.5 (n=38) | 0.001062 | arrow=Δ-0.00366(±0.0331,in-err) clock=Δ-6.21e+04(±3.99e+06,in-err) split=Δ2.48(±7.7,in-err) |
| 3 | k=80 A=-0.04083±0.021 (-) | tau=1.677e+05±6.3e+06 | S=-37.76 P=-2.755±7.5 (n=38) | 0.001192 | arrow=Δ-0.00537(±0.0389,in-err) clock=Δ-1.41e+05(±8.66e+06,in-err) split=Δ-1.85(±12,in-err) |
| 4 | k=80 A=-0.04795±0.022 (-) | tau=2.446e+05±1.5e+06 | S=-38.33 P=-3.473±5.5 (n=38) | 0.001329 | arrow=Δ-0.00712(±0.0427,in-err) clock=Δ7.69e+04(±7.75e+06,in-err) split=Δ-0.718(±12.9,in-err) |
| 5 | k=80 A=-0.05536±0.024 (-) | tau=-7.055e+05±9e+05 | S=-41.88 P=-2.437±6.2 (n=38) | 0.001461 | arrow=Δ-0.00742(±0.0465,in-err) clock=Δ-9.5e+05(±2.4e+06,in-err) split=Δ1.04(±11.6,in-err) |
| 6 | k=80 A=-0.06221±0.026 (-) | tau=-1.073e+05±9e+05 | S=-47.08 P=2.528±7.2 (n=38) | 0.00159 | arrow=Δ-0.00684(±0.0507,in-err) clock=Δ5.98e+05(±1.8e+06,in-err) split=Δ4.96(±13.3,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.2**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=75 A=-131.7±63 (-) | tau=1.016e+05±1.8e+06 | S=-24.35 P=-0.7363±3.1 (n=38) | 0.1945 | -- |
| 1 | k=77 A=-0.03256±0.018 (-) | tau=-3.392e+05±2e+06 | S=-31.98 P=-0.4887±5.3 (n=38) | 0.001051 | arrow=Δ132(±62.6,OUT) clock=Δ-4.41e+05(±3.76e+06,in-err) split=Δ0.248(±8.42,in-err) |
| 2 | k=80 A=-0.04448±0.021 (-) | tau=1.451e+06±3.7e+06 | S=-42.96 P=2.992±7 (n=38) | 0.001313 | arrow=Δ-0.0119(±0.0395,in-err) clock=Δ1.79e+06(±5.75e+06,in-err) split=Δ3.48(±12.3,in-err) |
| 3 | k=80 A=-0.0586±0.023 (-) | tau=-1.371e+05±5.2e+06 | S=-48.46 P=-3.328±7.8 (n=38) | 0.001528 | arrow=Δ-0.0141(±0.0439,in-err) clock=Δ-1.59e+06(±8.95e+06,in-err) split=Δ-6.32(±14.8,in-err) |
| 4 | k=80 A=-0.07182±0.026 (-) | tau=6.292e+04±1.5e+06 | S=-54.65 P=-6.636±9.1 (n=38) | 0.001719 | arrow=Δ-0.0132(±0.0493,in-err) clock=Δ2e+05(±6.66e+06,in-err) split=Δ-3.31(±16.8,in-err) |
| 5 | k=80 A=-0.08341±0.028 (-) | tau=3.891e+04±4.7e+05 | S=-54.3 P=-4.929±8.4 (n=38) | 0.001842 | arrow=Δ-0.0116(±0.0548,in-err) clock=Δ-2.4e+04(±1.93e+06,in-err) split=Δ1.71(±17.5,in-err) |
| 6 | k=80 A=-0.09438±0.033 (-) | tau=4.595e+04±3.2e+05 | S=-51.33 P=-0.1012±10 (n=38) | 0.001924 | arrow=Δ-0.011(±0.0615,in-err) clock=Δ7.04e+03(±7.92e+05,in-err) split=Δ4.83(±18.7,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

---

## buzz_seat100  (family: buzz, units: shots, n=4000)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=525.8±1.1e+02 (+) | tau=5061±2e+02 | S=-303 P=-3.654±8.3 (n=38) | 0.2031 | -- |
| 1 | k=80 A=123.3±25 (+) | tau=1.476e+04±2e+03 | S=-185.4 P=1.669±10 (n=38) | 0.06341 | arrow=Δ-402(±138,OUT) clock=Δ9.7e+03(±2.2e+03,OUT) split=Δ5.32(±18.8,in-err) |
| 2 | k=78 A=-13.02±9 (-) | tau=7643±6.2e+02 | S=-1.221 P=-12.16±7.9 (n=38) | 0.02862 | arrow=Δ-136(±33.9,OUT) clock=Δ-7.12e+03(±2.61e+03,OUT) split=Δ-13.8(±18.3,in-err) |
| 3 | k=80 A=-10.76±5.1 (-) | tau=-2.145e+05±4.4e+06 | S=62.23 P=-15.32±10 (n=38) | 0.01762 | arrow=Δ2.27(±14.1,in-err) clock=Δ-2.22e+05(±4.45e+06,in-err) split=Δ-3.16(±18,in-err) |
| 4 | k=80 A=-6.61±3.9 (-) | tau=-3.056e+04±3.2e+04 | S=65.97 P=5.588±5.7 (n=38) | 0.01244 | arrow=Δ4.15(±9.02,in-err) clock=Δ1.84e+05(±4.48e+06,in-err) split=Δ20.9(±15.9,OUT) |
| 5 | k=80 A=-4.608±3 (-) | tau=-4.569e+04±2.7e+05 | S=74.12 P=-5.739±6.3 (n=38) | 0.009509 | arrow=Δ2(±6.93,in-err) clock=Δ-1.51e+04(±3.04e+05,in-err) split=Δ-11.3(±12,in-err) |

Verdict: **FIXED POINT (from hop 3, keys: arrow,clock)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=525.8±1.1e+02 (+) | tau=5061±2e+02 | S=-303 P=-3.654±8.6 (n=38) | 0.2031 | -- |
| 1 | k=80 A=0.07336±0.015 (+) | tau=5065±2.5e+02 | S=-305.3 P=0.3701±7.5 (n=38) | 0.0005929 | arrow=Δ-526(±111,OUT) clock=Δ4.33(±448,in-err) split=Δ4.02(±16.2,in-err) |
| 2 | k=66 A=0.07875±0.017 (+) | tau=5115±2.7e+02 | S=-301.9 P=-0.9086±8.7 (n=38) | 0.0006593 | arrow=Δ0.00539(±0.0327,in-err) clock=Δ49.2(±520,in-err) split=Δ-1.28(±16.2,in-err) |
| 3 | k=66 A=0.08407±0.02 (+) | tau=5307±2.8e+02 | S=-295.6 P=-0.008453±8.4 (n=38) | 0.0007314 | arrow=Δ0.00532(±0.037,in-err) clock=Δ192(±552,in-err) split=Δ0.9(±17.1,in-err) |
| 4 | k=66 A=0.08827±0.021 (+) | tau=5456±3.2e+02 | S=-287.3 P=-1.189±8.8 (n=38) | 0.0007869 | arrow=Δ0.0042(±0.0405,in-err) clock=Δ149(±597,in-err) split=Δ-1.18(±17.2,in-err) |
| 5 | k=66 A=0.0911±0.023 (+) | tau=5735±3.5e+02 | S=-277.3 P=-2.026±9.2 (n=38) | 0.00084 | arrow=Δ0.00284(±0.0442,in-err) clock=Δ279(±670,in-err) split=Δ-0.836(±17.9,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-525.8±1.1e+02 (-) | tau=-5061±2e+02 | S=307.6 P=0.3067±10 (n=38) | 0.2031 | -- |
| 1 | k=80 A=-123.3±25 (-) | tau=-1.476e+04±2e+03 | S=186.9 P=-7.134±5.5 (n=38) | 0.06341 | arrow=Δ402(±136,OUT) clock=Δ-9.7e+03(±2.16e+03,OUT) split=Δ-7.44(±15.8,in-err) |
| 2 | k=78 A=13.02±8.7 (+) | tau=-7643±6.1e+02 | S=12.65 P=2.667±10 (n=38) | 0.02862 | arrow=Δ136(±33.6,OUT) clock=Δ7.12e+03(±2.57e+03,OUT) split=Δ9.8(±15.5,in-err) |
| 3 | k=80 A=10.76±5.3 (+) | tau=2.145e+05±6.6e+05 | S=-54.45 P=4.415±8.2 (n=38) | 0.01762 | arrow=Δ-2.27(±14,in-err) clock=Δ2.22e+05(±6.63e+05,in-err) split=Δ1.75(±18.3,in-err) |
| 4 | k=80 A=6.61±3.8 (+) | tau=3.056e+04±7.9e+04 | S=-62.29 P=4.209±8.7 (n=38) | 0.01244 | arrow=Δ-4.15(±9.09,in-err) clock=Δ-1.84e+05(±7.41e+05,in-err) split=Δ-0.206(±17,in-err) |
| 5 | k=80 A=4.608±3.1 (+) | tau=4.569e+04±6.8e+07 | S=-69.41 P=3.261±4.2 (n=38) | 0.009509 | arrow=Δ-2(±6.87,in-err) clock=Δ1.51e+04(±6.76e+07,in-err) split=Δ-0.947(±12.9,in-err) |

Verdict: **FIXED POINT (from hop 3, keys: arrow,clock,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-525.8±1.1e+02 (-) | tau=-5061±2e+02 | S=307.6 P=0.3067±10 (n=38) | 0.2031 | -- |
| 1 | k=80 A=-0.07336±0.015 (-) | tau=-5065±2.3e+02 | S=308.1 P=-2.263±8.6 (n=38) | 0.0005929 | arrow=Δ526(±106,OUT) clock=Δ-4.33(±423,in-err) split=Δ-2.57(±19,in-err) |
| 2 | k=66 A=-0.07875±0.017 (-) | tau=-5115±2.4e+02 | S=302.2 P=12.58±7.8 (n=38) | 0.0006593 | arrow=Δ-0.00539(±0.0319,in-err) clock=Δ-49.2(±462,in-err) split=Δ14.8(±16.4,in-err) |
| 3 | k=66 A=-0.08407±0.02 (-) | tau=-5307±3e+02 | S=297.8 P=14.79±7.7 (n=38) | 0.0007314 | arrow=Δ-0.00532(±0.037,in-err) clock=Δ-192(±533,in-err) split=Δ2.21(±15.5,in-err) |
| 4 | k=66 A=-0.08827±0.02 (-) | tau=-5456±3.2e+02 | S=289.6 P=10.68±9.7 (n=38) | 0.0007869 | arrow=Δ-0.0042(±0.0397,in-err) clock=Δ-149(±612,in-err) split=Δ-4.1(±17.4,in-err) |
| 5 | k=66 A=-0.0911±0.023 (-) | tau=-5735±3.9e+02 | S=281.4 P=6.337±8.9 (n=38) | 0.00084 | arrow=Δ-0.00284(±0.0434,in-err) clock=Δ-279(±705,in-err) split=Δ-4.35(±18.6,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=98.84±3.7e+02 (+) | tau=1.29e+04±9.3e+02 | S=-391.7 P=12.83±14 (n=38) | 0.1555 | -- |
| 1 | k=63 A=108.3±82 (+) | tau=-9160±6.9e+02 | S=-182.8 P=2.582±3.8 (n=38) | 0.05343 | arrow=Δ9.47(±450,in-err) clock=Δ-2.21e+04(±1.62e+03,OUT) split=Δ-10.3(±17.6,in-err) |
| 2 | k=3 A=29.95±20 (+) | tau=-2.205e+04±6.6e+03 | S=-115.1 P=3.637±6 (n=38) | 0.0249 | arrow=Δ-78.4(±102,in-err) clock=Δ-1.29e+04(±7.29e+03,OUT) split=Δ1.06(±9.85,in-err) |
| 3 | k=3 A=15.11±13 (+) | tau=2.367e+04±5.3e+04 | S=-67.46 P=0.3375±4 (n=38) | 0.01477 | arrow=Δ-14.8(±33.1,in-err) clock=Δ4.57e+04(±5.99e+04,in-err) split=Δ-3.3(±10,in-err) |
| 4 | k=2 A=9.266±9.3 (+) | tau=2.441e+04±8.9e+03 | S=-54.89 P=1.672±2.8 (n=38) | 0.01004 | arrow=Δ-5.85(±22.8,in-err) clock=Δ741(±6.21e+04,in-err) split=Δ1.33(±6.77,in-err) |
| 5 | k=2 A=6.662±7.9 (+) | tau=1.183e+04±1.6e+03 | S=-43.52 P=1.181±1.4 (n=38) | 0.007325 | arrow=Δ-2.6(±17.2,in-err) clock=Δ-1.26e+04(±1.05e+04,OUT) split=Δ-0.49(±4.16,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=98.84±3.6e+02 (+) | tau=1.29e+04±1e+03 | S=-391.7 P=12.83±14 (n=38) | 0.1555 | -- |
| 1 | k=57 A=0.004063±0.014 (+) | tau=1.221e+04±1e+03 | S=67.69 P=-2.493±11 (n=38) | 0.0002645 | arrow=Δ-98.8(±365,in-err) clock=Δ-691(±2.03e+03,in-err) split=Δ-15.3(±25.4,in-err) |
| 2 | k=57 A=0.005223±0.017 (+) | tau=1.244e+04±1.1e+03 | S=69.27 P=-7.779±10 (n=38) | 0.0003024 | arrow=Δ0.00116(±0.0319,in-err) clock=Δ235(±2.11e+03,in-err) split=Δ-5.29(±21.6,in-err) |
| 3 | k=57 A=0.007007±0.018 (+) | tau=1.246e+04±1.3e+03 | S=70.97 P=-7.029±13 (n=38) | 0.0003405 | arrow=Δ0.00178(±0.0358,in-err) clock=Δ14.1(±2.42e+03,in-err) split=Δ0.75(±23.6,in-err) |
| 4 | k=57 A=0.009063±0.022 (+) | tau=1.282e+04±1.4e+03 | S=72.23 P=3.601±10 (n=38) | 0.0003777 | arrow=Δ0.00206(±0.0403,in-err) clock=Δ360(±2.69e+03,in-err) split=Δ10.6(±23.4,in-err) |
| 5 | k=60 A=0.01099±0.022 (+) | tau=1.341e+04±1.6e+03 | S=74.86 P=-0.8775±11 (n=38) | 0.000416 | arrow=Δ0.00193(±0.0435,in-err) clock=Δ593(±2.95e+03,in-err) split=Δ-4.48(±21.4,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-98.84±4e+02 (-) | tau=-1.29e+04±9.8e+02 | S=390.9 P=-2.149±16 (n=38) | 0.1555 | -- |
| 1 | k=63 A=-108.3±88 (-) | tau=9160±7.1e+02 | S=183.7 P=-7.978±4.8 (n=38) | 0.05343 | arrow=Δ-9.47(±485,in-err) clock=Δ2.21e+04(±1.7e+03,OUT) split=Δ-5.83(±21.1,in-err) |
| 2 | k=3 A=-29.95±19 (-) | tau=2.205e+04±6.1e+03 | S=115 P=-4.363±5.8 (n=38) | 0.0249 | arrow=Δ78.4(±107,in-err) clock=Δ1.29e+04(±6.79e+03,OUT) split=Δ3.61(±10.6,in-err) |
| 3 | k=3 A=-15.11±14 (-) | tau=-2.367e+04±7.3e+03 | S=68.09 P=-5.741±1.6 (n=38) | 0.01477 | arrow=Δ14.8(±32.6,in-err) clock=Δ-4.57e+04(±1.34e+04,OUT) split=Δ-1.38(±7.41,in-err) |
| 4 | k=2 A=-9.266±8.7 (-) | tau=-2.441e+04±9.8e+03 | S=54.45 P=-1.638±2.5 (n=38) | 0.01004 | arrow=Δ5.85(±22.4,in-err) clock=Δ-741(±1.7e+04,in-err) split=Δ4.1(±4.13,in-err) |
| 5 | k=2 A=-6.662±7.4 (-) | tau=-1.183e+04±1.8e+03 | S=43.22 P=-0.9981±1.6 (n=38) | 0.007325 | arrow=Δ2.6(±16.1,in-err) clock=Δ1.26e+04(±1.15e+04,OUT) split=Δ0.64(±4.18,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-98.84±3.8e+02 (-) | tau=-1.29e+04±1e+03 | S=390.9 P=-2.149±14 (n=38) | 0.1555 | -- |
| 1 | k=57 A=-0.004063±0.016 (-) | tau=-1.221e+04±9.8e+02 | S=-67.63 P=4.827±10 (n=38) | 0.0002645 | arrow=Δ98.8(±383,in-err) clock=Δ691(±1.99e+03,in-err) split=Δ6.98(±24.8,in-err) |
| 2 | k=57 A=-0.005223±0.017 (-) | tau=-1.244e+04±1.1e+03 | S=-68.76 P=4.205±10 (n=38) | 0.0003024 | arrow=Δ-0.00116(±0.033,in-err) clock=Δ-235(±2.13e+03,in-err) split=Δ-0.622(±20.7,in-err) |
| 3 | k=57 A=-0.007007±0.019 (-) | tau=-1.246e+04±1.3e+03 | S=-70.62 P=-0.5446±13 (n=38) | 0.0003405 | arrow=Δ-0.00178(±0.0361,in-err) clock=Δ-14.1(±2.48e+03,in-err) split=Δ-4.75(±23,in-err) |
| 4 | k=57 A=-0.009063±0.023 (-) | tau=-1.282e+04±1.4e+03 | S=-74.99 P=12.05±9.9 (n=38) | 0.0003777 | arrow=Δ-0.00206(±0.0416,in-err) clock=Δ-360(±2.72e+03,in-err) split=Δ12.6(±22.5,in-err) |
| 5 | k=60 A=-0.01099±0.025 (-) | tau=-1.341e+04±1.6e+03 | S=-77.29 P=10.23±8.2 (n=38) | 0.000416 | arrow=Δ-0.00193(±0.0475,in-err) clock=Δ-593(±2.98e+03,in-err) split=Δ-1.82(±18.2,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=2 A=5.019±2.6 (+)  |  clock: tau=4.228e+04±1e+05  |  split: S=-49.38 P=3.562±13 (n=38)  (raw relay ran 5 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | -4.608±3 | 6.662±7.9 | UNSTABLE |
| clock (tau) | -4.569e+04±2.7e+05 | 1.183e+04±1.6e+03 | AGREE |
| split (P) | -5.739±6.3 | 1.181±1.4 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | -4.608±3 | 4.608±3.1 | UNSTABLE |
| clock (tau) | -4.569e+04±2.7e+05 | 4.569e+04±6.8e+07 | AGREE |
| split (P) | -5.739±6.3 | 3.261±4.2 | AGREE |

---

## buzz_seat116  (family: buzz, units: shots, n=4000)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-210.9±2.1e+02 (-) | tau=1.1e+04±9.5e+02 | S=-145.2 P=8.647±10 (n=38) | 0.1766 | -- |
| 1 | k=48 A=78.3±32 (+) | tau=-7.967e+04±9.3e+05 | S=-15.02 P=14.89±14 (n=38) | 0.0383 | arrow=Δ289(±247,OUT) clock=Δ-9.07e+04(±9.32e+05,in-err) split=Δ6.24(±24.2,in-err) |
| 2 | k=28 A=-12.61±8 (-) | tau=1.472e+04±2.3e+03 | S=-113.1 P=12.26±9.9 (n=38) | 0.01281 | arrow=Δ-90.9(±39.9,OUT) clock=Δ9.44e+04(±9.33e+05,in-err) split=Δ-2.63(±23.8,in-err) |
| 3 | k=60 A=-5.662±4.1 (-) | tau=-4.81e+05±2.4e+06 | S=-43.88 P=5.968±4.7 (n=38) | 0.005703 | arrow=Δ6.94(±12.1,in-err) clock=Δ-4.96e+05(±2.43e+06,in-err) split=Δ-6.29(±14.6,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-210.9±2.3e+02 (-) | tau=1.1e+04±1e+03 | S=-145.2 P=8.647±10 (n=38) | 0.1766 | -- |
| 1 | k=80 A=-0.008537±0.012 (-) | tau=1.03e+04±9.5e+02 | S=-148 P=11.1±12 (n=38) | 0.0002746 | arrow=Δ211(±229,in-err) clock=Δ-693(±1.96e+03,in-err) split=Δ2.45(±22.1,in-err) |
| 2 | k=55 A=0.007437±0.012 (+) | tau=9781±9.9e+02 | S=-147.1 P=12.06±13 (n=38) | 0.0003254 | arrow=Δ0.016(±0.0238,in-err) clock=Δ-522(±1.93e+03,in-err) split=Δ0.956(±25,in-err) |
| 3 | k=52 A=0.01042±0.013 (+) | tau=9011±9.4e+02 | S=-146.6 P=21.94±12 (n=38) | 0.0003757 | arrow=Δ0.00299(±0.0249,in-err) clock=Δ-770(±1.92e+03,in-err) split=Δ9.88(±25,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=210.9±2.2e+02 (+) | tau=-1.1e+04±9.5e+02 | S=142.3 P=3.097±14 (n=38) | 0.1766 | -- |
| 1 | k=48 A=-78.3±35 (-) | tau=7.967e+04±2.3e+06 | S=12.62 P=-6.329±10 (n=38) | 0.0383 | arrow=Δ-289(±258,OUT) clock=Δ9.07e+04(±2.33e+06,in-err) split=Δ-9.43(±23.6,in-err) |
| 2 | k=28 A=12.61±8.2 (+) | tau=-1.472e+04±2.5e+03 | S=109.5 P=-0.7324±8.1 (n=38) | 0.01281 | arrow=Δ90.9(±43,OUT) clock=Δ-9.44e+04(±2.33e+06,in-err) split=Δ5.6(±18.3,in-err) |
| 3 | k=60 A=5.662±4.1 (+) | tau=4.81e+05±6.6e+06 | S=43.64 P=3.004±7.5 (n=38) | 0.005703 | arrow=Δ-6.94(±12.3,in-err) clock=Δ4.96e+05(±6.63e+06,in-err) split=Δ3.74(±15.7,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=210.9±2.4e+02 (+) | tau=-1.1e+04±9.9e+02 | S=142.3 P=3.097±14 (n=38) | 0.1766 | -- |
| 1 | k=80 A=0.008537±0.012 (+) | tau=-1.03e+04±9.6e+02 | S=147 P=-3.829±10 (n=38) | 0.0002746 | arrow=Δ-211(±236,in-err) clock=Δ693(±1.95e+03,in-err) split=Δ-6.93(±23.9,in-err) |
| 2 | k=55 A=-0.007437±0.011 (-) | tau=-9781±9.9e+02 | S=144.9 P=-1.279±14 (n=38) | 0.0003254 | arrow=Δ-0.016(±0.0233,in-err) clock=Δ522(±1.96e+03,in-err) split=Δ2.55(±24.7,in-err) |
| 3 | k=52 A=-0.01042±0.013 (-) | tau=-9011±9.3e+02 | S=142.3 P=-6.487±13 (n=38) | 0.0003757 | arrow=Δ-0.00299(±0.0241,in-err) clock=Δ770(±1.92e+03,in-err) split=Δ-5.21(±27,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=3.9e+04±5.2e+03 (+) | tau=-3.79e+04±3.8e+05 | S=482.2 P=-0.8529±9.4 (n=38) | 0.2532 | -- |
| 1 | k=80 A=2.576e+04±3.4e+03 (+) | tau=6722±7e+02 | S=231.9 P=-4.233±4.5 (n=38) | 0.1203 | arrow=Δ-1.32e+04(±8.62e+03,OUT) clock=Δ4.46e+04(±3.81e+05,in-err) split=Δ-3.38(±13.8,in-err) |
| 2 | k=80 A=2.305e+04±2.2e+03 (+) | tau=1.163e+04±2.1e+03 | S=172.3 P=1.757±2.3 (n=38) | 0.0601 | arrow=Δ-2.72e+03(±5.62e+03,in-err) clock=Δ4.91e+03(±2.84e+03,OUT) split=Δ5.99(±6.82,in-err) |
| 3 | k=80 A=1.943e+04±1.8e+03 (+) | tau=4584±3e+02 | S=111.3 P=-1.237±2.3 (n=38) | 0.03146 | arrow=Δ-3.61e+03(±4.01e+03,in-err) clock=Δ-7.05e+03(±2.45e+03,OUT) split=Δ-2.99(±4.59,in-err) |
| 4 | k=80 A=1.712e+04±1.4e+03 (+) | tau=5214±3.9e+02 | S=78.66 P=-1.226±1 (n=38) | 0.01995 | arrow=Δ-2.31e+03(±3.16e+03,in-err) clock=Δ629(±695,in-err) split=Δ0.0109(±3.29,in-err) |
| 5 | k=80 A=1.538e+04±1.2e+03 (+) | tau=5147±4.2e+02 | S=56.07 P=0.5365±0.66 (n=38) | 0.01477 | arrow=Δ-1.74e+03(±2.54e+03,in-err) clock=Δ-66.2(±813,in-err) split=Δ1.76(±1.7,OUT) |
| 6 | k=80 A=1.417e+04±1.1e+03 (+) | tau=5897±6.5e+02 | S=44.57 P=-0.672±0.52 (n=38) | 0.01236 | arrow=Δ-1.21e+03(±2.3e+03,in-err) clock=Δ750(±1.07e+03,in-err) split=Δ-1.21(±1.18,OUT) |
| 7 | k=80 A=1.337e+04±1.1e+03 (+) | tau=6344±9.2e+02 | S=38.05 P=0.2846±0.2 (n=38) | 0.01097 | arrow=Δ-795(±2.23e+03,in-err) clock=Δ447(±1.57e+03,in-err) split=Δ0.957(±0.713,OUT) |
| 8 | k=80 A=1.28e+04±9.8e+02 (+) | tau=8960±2.5e+03 | S=33.89 P=-0.07299±0.24 (n=38) | 0.01005 | arrow=Δ-573(±2.08e+03,in-err) clock=Δ2.62e+03(±3.41e+03,in-err) split=Δ-0.358(±0.438,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=3.9e+04±5e+03 (+) | tau=-3.79e+04±3.8e+04 | S=482.2 P=-0.8529±9.2 (n=38) | 0.2532 | -- |
| 1 | k=80 A=0.06812±0.008 (+) | tau=-4.531e+04±1.4e+05 | S=-192.9 P=20±20 (n=38) | 6.876e-05 | arrow=Δ-3.9e+04(±5.01e+03,OUT) clock=Δ-7.41e+03(±1.76e+05,in-err) split=Δ20.9(±28.8,in-err) |
| 2 | k=80 A=0.07822±0.0079 (+) | tau=-6.029e+04±5.5e+05 | S=-205.4 P=25.12±16 (n=38) | 7.45e-05 | arrow=Δ0.0101(±0.0159,in-err) clock=Δ-1.5e+04(±6.86e+05,in-err) split=Δ5.12(±36.1,in-err) |
| 3 | k=80 A=0.08824±0.0085 (+) | tau=-9.273e+04±4.6e+05 | S=-217.9 P=43.87±16 (n=38) | 8.045e-05 | arrow=Δ0.01(±0.0164,in-err) clock=Δ-3.24e+04(±1.01e+06,in-err) split=Δ18.8(±32.5,in-err) |
| 4 | k=80 A=0.098±0.0091 (+) | tau=-2.03e+05±7.6e+05 | S=-225.1 P=35.91±18 (n=38) | 8.61e-05 | arrow=Δ0.00977(±0.0176,in-err) clock=Δ-1.1e+05(±1.22e+06,in-err) split=Δ-7.97(±33.7,in-err) |
| 5 | k=80 A=0.1075±0.0098 (+) | tau=1.274e+06±1.7e+08 | S=-232.3 P=37.73±23 (n=38) | 9.14e-05 | arrow=Δ0.00948(±0.0189,in-err) clock=Δ1.48e+06(±1.72e+08,in-err) split=Δ1.83(±40.6,in-err) |
| 6 | k=80 A=0.1167±0.01 (+) | tau=1.613e+05±4.2e+06 | S=-238 P=38.02±26 (n=38) | 9.63e-05 | arrow=Δ0.00921(±0.0203,in-err) clock=Δ-1.11e+06(±1.76e+08,in-err) split=Δ0.29(±48.5,in-err) |
| 7 | k=80 A=0.1257±0.011 (+) | tau=9.144e+04±5.2e+05 | S=-242.5 P=38.99±26 (n=38) | 0.0001008 | arrow=Δ0.00899(±0.0212,in-err) clock=Δ-6.98e+04(±4.7e+06,in-err) split=Δ0.963(±51.8,in-err) |
| 8 | k=80 A=0.1345±0.011 (+) | tau=6.454e+04±5e+05 | S=-246.5 P=32.1±22 (n=38) | 0.0001051 | arrow=Δ0.00883(±0.0215,in-err) clock=Δ-2.69e+04(±1.02e+06,in-err) split=Δ-6.89(±48.4,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-3.9e+04±5.7e+03 (-) | tau=3.79e+04±4.1e+04 | S=-481.9 P=-20.86±8.5 (n=38) | 0.2532 | -- |
| 1 | k=80 A=-2.576e+04±3.3e+03 (-) | tau=-6722±7e+02 | S=-228.2 P=-4.32±3.2 (n=38) | 0.1203 | arrow=Δ1.32e+04(±9.01e+03,OUT) clock=Δ-4.46e+04(±4.15e+04,OUT) split=Δ16.5(±11.7,OUT) |
| 2 | k=80 A=-2.305e+04±2.4e+03 (-) | tau=-1.163e+04±2.3e+03 | S=-172 P=1.777±2.4 (n=38) | 0.0601 | arrow=Δ2.72e+03(±5.65e+03,in-err) clock=Δ-4.91e+03(±2.96e+03,OUT) split=Δ6.1(±5.61,OUT) |
| 3 | k=80 A=-1.943e+04±1.6e+03 (-) | tau=-4584±3.4e+02 | S=-112.7 P=6.725±1.7 (n=38) | 0.03146 | arrow=Δ3.61e+03(±3.98e+03,in-err) clock=Δ7.05e+03(±2.6e+03,OUT) split=Δ4.95(±4.09,OUT) |
| 4 | k=80 A=-1.712e+04±1.3e+03 (-) | tau=-5214±4.3e+02 | S=-78.06 P=-1.15±1.2 (n=38) | 0.01995 | arrow=Δ2.31e+03(±2.93e+03,in-err) clock=Δ-629(±769,in-err) split=Δ-7.87(±2.84,OUT) |
| 5 | k=80 A=-1.538e+04±1.3e+03 (-) | tau=-5147±4.4e+02 | S=-55.81 P=-0.03516±0.65 (n=38) | 0.01477 | arrow=Δ1.74e+03(±2.62e+03,in-err) clock=Δ66.2(±873,in-err) split=Δ1.11(±1.82,in-err) |
| 6 | k=80 A=-1.417e+04±1.1e+03 (-) | tau=-5897±6.6e+02 | S=-44.87 P=-0.0967±0.42 (n=38) | 0.01236 | arrow=Δ1.21e+03(±2.42e+03,in-err) clock=Δ-750(±1.1e+03,in-err) split=Δ-0.0615(±1.07,in-err) |
| 7 | k=80 A=-1.337e+04±1.1e+03 (-) | tau=-6344±8.8e+02 | S=-37.7 P=-0.01224±0.15 (n=38) | 0.01097 | arrow=Δ795(±2.2e+03,in-err) clock=Δ-447(±1.54e+03,in-err) split=Δ0.0845(±0.57,in-err) |
| 8 | k=80 A=-1.28e+04±1e+03 (-) | tau=-8960±2.7e+03 | S=-34.14 P=0.1412±0.15 (n=38) | 0.01005 | arrow=Δ573(±2.12e+03,in-err) clock=Δ-2.62e+03(±3.58e+03,in-err) split=Δ0.153(±0.294,in-err) |

Verdict: **FIXED POINT (from hop 4, keys: arrow,clock)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=80 A=-3.9e+04±5.3e+03 (-) | tau=3.79e+04±5.5e+04 | S=-481.9 P=-20.86±9 (n=38) | 0.2532 | -- |
| 1 | k=80 A=-0.06812±0.0077 (-) | tau=4.531e+04±9.1e+04 | S=197 P=-22.16±15 (n=38) | 6.876e-05 | arrow=Δ3.9e+04(±5.32e+03,OUT) clock=Δ7.41e+03(±1.47e+05,in-err) split=Δ-1.3(±23.6,in-err) |
| 2 | k=80 A=-0.07822±0.0082 (-) | tau=6.029e+04±5.3e+05 | S=204.9 P=-15.28±20 (n=38) | 7.45e-05 | arrow=Δ-0.0101(±0.0159,in-err) clock=Δ1.5e+04(±6.17e+05,in-err) split=Δ6.87(±34.6,in-err) |
| 3 | k=80 A=-0.08824±0.0086 (-) | tau=9.273e+04±1.2e+06 | S=214.2 P=-4.44±25 (n=38) | 8.045e-05 | arrow=Δ-0.01(±0.0168,in-err) clock=Δ3.24e+04(±1.71e+06,in-err) split=Δ10.8(±44.6,in-err) |
| 4 | k=80 A=-0.098±0.0099 (-) | tau=2.03e+05±8.5e+06 | S=223.4 P=-4.562±30 (n=38) | 8.61e-05 | arrow=Δ-0.00977(±0.0185,in-err) clock=Δ1.1e+05(±9.74e+06,in-err) split=Δ-0.122(±54.9,in-err) |
| 5 | k=80 A=-0.1075±0.0095 (-) | tau=-1.274e+06±1.7e+06 | S=229.7 P=7.899±30 (n=38) | 9.14e-05 | arrow=Δ-0.00948(±0.0193,in-err) clock=Δ-1.48e+06(±1.02e+07,in-err) split=Δ12.5(±60.3,in-err) |
| 6 | k=80 A=-0.1167±0.01 (-) | tau=-1.613e+05±2e+06 | S=235.6 P=9.446±30 (n=38) | 9.63e-05 | arrow=Δ-0.00921(±0.0195,in-err) clock=Δ1.11e+06(±3.64e+06,in-err) split=Δ1.55(±60,in-err) |
| 7 | k=80 A=-0.1257±0.01 (-) | tau=-9.144e+04±2.1e+06 | S=240.3 P=10.16±31 (n=38) | 0.0001008 | arrow=Δ-0.00899(±0.0203,in-err) clock=Δ6.98e+04(±4.02e+06,in-err) split=Δ0.711(±60.5,in-err) |
| 8 | k=80 A=-0.1345±0.011 (-) | tau=-6.454e+04±7.2e+05 | S=235.5 P=39.17±24 (n=38) | 0.0001051 | arrow=Δ-0.00883(±0.0212,in-err) clock=Δ2.69e+04(±2.77e+06,in-err) split=Δ29(±54.2,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=32 A=207±31 (+)  |  clock: tau=-3.475e+04±1.1e+05  |  split: S=93.66 P=-2.415±12 (n=36)  (raw relay ran 8 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | -5.662±4.1 | 1.28e+04±9.8e+02 | UNSTABLE |
| clock (tau) | -4.81e+05±2.4e+06 | 8960±2.5e+03 | AGREE |
| split (P) | 5.968±4.7 | -0.07299±0.24 | UNSTABLE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | -5.662±4.1 | 5.662±4.1 | UNSTABLE |
| clock (tau) | -4.81e+05±2.4e+06 | 4.81e+05±6.6e+06 | AGREE |
| split (P) | 5.968±4.7 | 3.004±7.5 | AGREE |

---

## mice_size1  (family: mice, units: h, n=8192)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=-0.171±0.05 (-) | tau=-5672±3.5e+02 | S=68.98 P=-9.474±9 (n=39) | 0.2687 | -- |
| 1 | k=7 A=0.09347±0.025 (+) | tau=-4965±4.1e+02 | S=77.35 P=-7.143±25 (n=39) | 0.1686 | arrow=Δ0.264(±0.0754,OUT) clock=Δ706(±756,in-err) split=Δ2.33(±34.5,in-err) |
| 2 | k=7 A=0.08027±0.023 (+) | tau=-3244±1.9e+02 | S=125.2 P=-1.491±35 (n=39) | 0.1352 | arrow=Δ-0.0132(±0.0489,in-err) clock=Δ1.72e+03(±593,OUT) split=Δ5.65(±60.3,in-err) |
| 3 | k=7 A=0.07283±0.021 (+) | tau=-2375±1.2e+02 | S=183.9 P=36.44±65 (n=39) | 0.1199 | arrow=Δ-0.00743(±0.0441,in-err) clock=Δ870(±303,OUT) split=Δ37.9(±100,in-err) |
| 4 | k=7 A=0.06788±0.02 (+) | tau=-2110±97 | S=248.4 P=87.35±83 (n=39) | 0.1105 | arrow=Δ-0.00495(±0.0407,in-err) clock=Δ265(±213,OUT) split=Δ50.9(±148,in-err) |
| 5 | k=7 A=0.06418±0.019 (+) | tau=-1920±88 | S=276.4 P=-17.78±82 (n=39) | 0.1036 | arrow=Δ-0.0037(±0.039,in-err) clock=Δ189(±184,OUT) split=Δ-105(±165,in-err) |
| 6 | k=7 A=0.06111±0.017 (+) | tau=-1806±80 | S=253 P=4.928±79 (n=39) | 0.09791 | arrow=Δ-0.00307(±0.0361,in-err) clock=Δ114(±168,in-err) split=Δ22.7(±161,in-err) |
| 7 | k=7 A=0.05842±0.016 (+) | tau=-1789±83 | S=225.5 P=-27.45±58 (n=39) | 0.09305 | arrow=Δ-0.00269(±0.0334,in-err) clock=Δ17.5(±163,in-err) split=Δ-32.4(±137,in-err) |
| 8 | k=7 A=0.05602±0.016 (+) | tau=-1821±84 | S=202 P=-38.05±45 (n=39) | 0.08877 | arrow=Δ-0.00241(±0.0321,in-err) clock=Δ-31.7(±167,in-err) split=Δ-10.6(±103,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=-0.171±0.051 (-) | tau=-5672±3.6e+02 | S=68.98 P=-9.474±9 (n=39) | 0.2687 | -- |
| 1 | k=5.5 A=0.2739±0.071 (+) | tau=-5629±4.1e+02 | S=70.24 P=-10.05±15 (n=39) | 0.3907 | arrow=Δ0.445(±0.121,OUT) clock=Δ42.4(±772,in-err) split=Δ-0.576(±24.1,in-err) |
| 2 | k=7 A=0.3263±0.097 (+) | tau=-5866±4.8e+02 | S=71.79 P=-15.26±20 (n=39) | 0.4536 | arrow=Δ0.0524(±0.167,in-err) clock=Δ-237(±895,in-err) split=Δ-5.21(±34.8,in-err) |
| 3 | k=7 A=0.3865±0.11 (+) | tau=-5810±4.7e+02 | S=74.11 P=-16.81±24 (n=39) | 0.513 | arrow=Δ0.0602(±0.208,in-err) clock=Δ56(±959,in-err) split=Δ-1.55(±43.2,in-err) |
| 4 | k=7 A=0.4465±0.13 (+) | tau=-5585±5.4e+02 | S=76.55 P=-18.47±24 (n=39) | 0.5664 | arrow=Δ0.06(±0.245,in-err) clock=Δ225(±1.01e+03,in-err) split=Δ-1.66(±47.1,in-err) |
| 5 | k=7 A=0.5052±0.15 (+) | tau=-5350±5.2e+02 | S=78.9 P=-27.43±20 (n=39) | 0.617 | arrow=Δ0.0587(±0.284,in-err) clock=Δ235(±1.05e+03,in-err) split=Δ-8.96(±43.2,in-err) |
| 6 | k=7 A=0.5621±0.17 (+) | tau=-5134±5e+02 | S=80.95 P=-29.43±22 (n=39) | 0.6627 | arrow=Δ0.0569(±0.317,in-err) clock=Δ216(±1.01e+03,in-err) split=Δ-1.99(±41.2,in-err) |
| 7 | k=7 A=0.6165±0.18 (+) | tau=-5015±5.6e+02 | S=82.5 P=-31.4±22 (n=39) | 0.7042 | arrow=Δ0.0544(±0.349,in-err) clock=Δ119(±1.05e+03,in-err) split=Δ-1.98(±43.9,in-err) |
| 8 | k=7 A=0.6683±0.19 (+) | tau=-5003±5.6e+02 | S=83.92 P=-35.68±21 (n=39) | 0.7406 | arrow=Δ0.0518(±0.371,in-err) clock=Δ11.2(±1.12e+03,in-err) split=Δ-4.27(±43.7,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=0.171±0.053 (+) | tau=5672±3.7e+02 | S=-68.54 P=-15.13±8.7 (n=39) | 0.2687 | -- |
| 1 | k=7 A=-0.09347±0.029 (-) | tau=4965±3.8e+02 | S=-80.4 P=37.13±27 (n=39) | 0.1686 | arrow=Δ-0.264(±0.0812,OUT) clock=Δ-706(±745,in-err) split=Δ52.3(±35.2,OUT) |
| 2 | k=7 A=-0.08027±0.023 (-) | tau=3244±1.9e+02 | S=-129.9 P=9.336±61 (n=39) | 0.1352 | arrow=Δ0.0132(±0.0511,in-err) clock=Δ-1.72e+03(±574,OUT) split=Δ-27.8(±87.2,in-err) |
| 3 | k=7 A=-0.07283±0.019 (-) | tau=2375±1.2e+02 | S=-191.6 P=52.12±44 (n=39) | 0.1199 | arrow=Δ0.00743(±0.0419,in-err) clock=Δ-870(±311,OUT) split=Δ42.8(±104,in-err) |
| 4 | k=7 A=-0.06788±0.019 (-) | tau=2110±1e+02 | S=-259.2 P=116.6±55 (n=39) | 0.1105 | arrow=Δ0.00495(±0.0381,in-err) clock=Δ-265(±219,OUT) split=Δ64.4(±98.4,in-err) |
| 5 | k=7 A=-0.06418±0.017 (-) | tau=1920±93 | S=-287.5 P=117.9±65 (n=39) | 0.1036 | arrow=Δ0.0037(±0.0355,in-err) clock=Δ-189(±195,in-err) split=Δ1.39(±120,in-err) |
| 6 | k=7 A=-0.06111±0.017 (-) | tau=1806±86 | S=-262 P=31.47±64 (n=39) | 0.09791 | arrow=Δ0.00307(±0.0338,in-err) clock=Δ-114(±180,in-err) split=Δ-86.5(±130,in-err) |
| 7 | k=7 A=-0.05842±0.017 (-) | tau=1789±76 | S=-233.2 P=35.24±50 (n=39) | 0.09305 | arrow=Δ0.00269(±0.0336,in-err) clock=Δ-17.5(±162,in-err) split=Δ3.77(±114,in-err) |
| 8 | k=7 A=-0.05602±0.015 (-) | tau=1821±90 | S=-208.5 P=40.88±27 (n=39) | 0.08877 | arrow=Δ0.00241(±0.0317,in-err) clock=Δ31.7(±166,in-err) split=Δ5.64(±76.6,in-err) |

Verdict: **FIXED POINT (from hop 2, keys: arrow,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=0.171±0.055 (+) | tau=5672±3.6e+02 | S=-68.54 P=-15.13±9.5 (n=39) | 0.2687 | -- |
| 1 | k=5.5 A=-0.2739±0.075 (-) | tau=5629±4.2e+02 | S=-70.72 P=-14.48±11 (n=39) | 0.3907 | arrow=Δ-0.445(±0.13,OUT) clock=Δ-42.4(±775,in-err) split=Δ0.653(±20.2,in-err) |
| 2 | k=7 A=-0.3263±0.091 (-) | tau=5866±4.7e+02 | S=-72.64 P=-9.013±16 (n=39) | 0.4536 | arrow=Δ-0.0524(±0.166,in-err) clock=Δ237(±887,in-err) split=Δ5.47(±26.9,in-err) |
| 3 | k=7 A=-0.3865±0.11 (-) | tau=5810±5.7e+02 | S=-75.12 P=-12.34±18 (n=39) | 0.513 | arrow=Δ-0.0602(±0.205,in-err) clock=Δ-56(±1.03e+03,in-err) split=Δ-3.33(±34.5,in-err) |
| 4 | k=7 A=-0.4465±0.14 (-) | tau=5585±5e+02 | S=-77.57 P=-24.67±20 (n=39) | 0.5664 | arrow=Δ-0.06(±0.252,in-err) clock=Δ-225(±1.06e+03,in-err) split=Δ-12.3(±38.7,in-err) |
| 5 | k=7 A=-0.5052±0.14 (-) | tau=5350±4.9e+02 | S=-79.9 P=-29.36±23 (n=39) | 0.617 | arrow=Δ-0.0587(±0.278,in-err) clock=Δ-235(±983,in-err) split=Δ-4.68(±42.9,in-err) |
| 6 | k=7 A=-0.5621±0.17 (-) | tau=5134±5.2e+02 | S=-82 P=-32.29±24 (n=39) | 0.6627 | arrow=Δ-0.0569(±0.312,in-err) clock=Δ-216(±1.01e+03,in-err) split=Δ-2.93(±46.9,in-err) |
| 7 | k=7 A=-0.6165±0.17 (-) | tau=5015±5.2e+02 | S=-83.64 P=-33.15±27 (n=39) | 0.7042 | arrow=Δ-0.0544(±0.346,in-err) clock=Δ-119(±1.04e+03,in-err) split=Δ-0.868(±51.3,in-err) |
| 8 | k=7 A=-0.6683±0.2 (-) | tau=5003±5.6e+02 | S=-85.14 P=-35.88±28 (n=39) | 0.7406 | arrow=Δ-0.0518(±0.377,in-err) clock=Δ-11.2(±1.08e+03,in-err) split=Δ-2.72(±54.9,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=10 A=8.552±20 (+) | tau=-5145±2.9e+02 | S=-3.27 P=0.2928±0.24 (n=39) | 0.2416 | -- |
| 1 | k=4.5 A=2.061±6.5 (+) | tau=-3665±2.2e+02 | S=-1.62 P=0.3959±0.24 (n=39) | 0.1568 | arrow=Δ-6.49(±26.6,in-err) clock=Δ1.48e+03(±503,OUT) split=Δ0.103(±0.482,in-err) |
| 2 | k=4.25 A=0.9861±4.6 (+) | tau=-2670±1.3e+02 | S=-0.9619 P=0.05571±0.19 (n=39) | 0.1269 | arrow=Δ-1.08(±11.1,in-err) clock=Δ994(±350,OUT) split=Δ-0.34(±0.429,in-err) |
| 3 | k=4.25 A=0.9017±3.8 (+) | tau=-2374±1.2e+02 | S=-0.9479 P=0.2166±0.17 (n=39) | 0.1136 | arrow=Δ-0.0844(±8.42,in-err) clock=Δ296(±249,OUT) split=Δ0.161(±0.362,in-err) |
| 4 | k=4.5 A=0.7625±3.7 (+) | tau=-2101±95 | S=-0.855 P=0.08637±0.17 (n=39) | 0.1049 | arrow=Δ-0.139(±7.5,in-err) clock=Δ273(±212,OUT) split=Δ-0.13(±0.342,in-err) |
| 5 | k=4.5 A=0.7066±3.3 (+) | tau=-1922±90 | S=-0.7992 P=0.0868±0.13 (n=39) | 0.09844 | arrow=Δ-0.0559(±7.04,in-err) clock=Δ179(±186,in-err) split=Δ0.000425(±0.303,in-err) |
| 6 | k=14 A=0.6715±5.3 (+) | tau=-1874±88 | S=-0.7593 P=-0.06906±0.078 (n=39) | 0.09305 | arrow=Δ-0.035(±8.64,in-err) clock=Δ48.1(±178,in-err) split=Δ-0.156(±0.211,in-err) |
| 7 | k=14.8 A=0.6768±4.9 (+) | tau=-1811±84 | S=-0.7226 P=0.04556±0.12 (n=39) | 0.08833 | arrow=Δ0.00525(±10.2,in-err) clock=Δ62.9(±171,in-err) split=Δ0.115(±0.198,in-err) |
| 8 | k=20 A=0.7008±5.8 (+) | tau=-1824±81 | S=-0.6955 P=-0.0001111±0.05 (n=39) | 0.08423 | arrow=Δ0.024(±10.7,in-err) clock=Δ-13.7(±164,in-err) split=Δ-0.0457(±0.17,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,split)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=10 A=8.552±20 (+) | tau=-5145±3e+02 | S=-3.27 P=0.2928±0.25 (n=39) | 0.2416 | -- |
| 1 | k=5.5 A=0.2877±0.078 (+) | tau=-5374±3.8e+02 | S=73.56 P=-3.813±14 (n=39) | 0.352 | arrow=Δ-8.26(±20.4,in-err) clock=Δ-229(±686,in-err) split=Δ-4.11(±13.8,in-err) |
| 2 | k=7 A=0.3519±0.099 (+) | tau=-5547±4.3e+02 | S=74.22 P=-8.994±16 (n=39) | 0.4182 | arrow=Δ0.0642(±0.177,in-err) clock=Δ-173(±813,in-err) split=Δ-5.18(±29.9,in-err) |
| 3 | k=7 A=0.4196±0.13 (+) | tau=-5556±4.7e+02 | S=75.67 P=-8.399±16 (n=39) | 0.4805 | arrow=Δ0.0677(±0.224,in-err) clock=Δ-8.77(±903,in-err) split=Δ0.595(±32.5,in-err) |
| 4 | k=7 A=0.487±0.15 (+) | tau=-5398±4.8e+02 | S=78.1 P=-12.93±11 (n=39) | 0.5369 | arrow=Δ0.0675(±0.28,in-err) clock=Δ158(±956,in-err) split=Δ-4.53(±27.2,in-err) |
| 5 | k=7 A=0.5528±0.16 (+) | tau=-5010±4.2e+02 | S=80.6 P=-12.12±20 (n=39) | 0.5858 | arrow=Δ0.0658(±0.313,in-err) clock=Δ388(±907,in-err) split=Δ0.812(±31.3,in-err) |
| 6 | k=7 A=0.6164±0.19 (+) | tau=-4523±3.4e+02 | S=83.25 P=-11.63±19 (n=39) | 0.63 | arrow=Δ0.0636(±0.344,in-err) clock=Δ487(±769,in-err) split=Δ0.488(±39.1,in-err) |
| 7 | k=7 A=0.6779±0.21 (+) | tau=-4172±3.3e+02 | S=85.4 P=-9.122±20 (n=39) | 0.6689 | arrow=Δ0.0615(±0.397,in-err) clock=Δ351(±677,in-err) split=Δ2.51(±39.3,in-err) |
| 8 | k=7 A=0.7371±0.2 (+) | tau=-3946±3.2e+02 | S=86.94 P=-15.26±17 (n=39) | 0.7037 | arrow=Δ0.0592(±0.41,in-err) clock=Δ226(±651,in-err) split=Δ-6.14(±37.4,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=10 A=-8.552±18 (-) | tau=5145±2.9e+02 | S=3.297 P=-0.4954±0.22 (n=39) | 0.2416 | -- |
| 1 | k=4.5 A=-2.061±6.9 (-) | tau=3665±2.2e+02 | S=1.636 P=0.1247±0.22 (n=39) | 0.1568 | arrow=Δ6.49(±25.1,in-err) clock=Δ-1.48e+03(±512,OUT) split=Δ0.62(±0.446,OUT) |
| 2 | k=4.25 A=-0.9861±4.8 (-) | tau=2670±1.3e+02 | S=0.9815 P=0.2247±0.14 (n=39) | 0.1269 | arrow=Δ1.08(±11.7,in-err) clock=Δ-994(±354,OUT) split=Δ0.1(±0.359,in-err) |
| 3 | k=4.25 A=-0.9017±3.9 (-) | tau=2374±1.1e+02 | S=0.9701 P=-0.2616±0.15 (n=39) | 0.1136 | arrow=Δ0.0844(±8.62,in-err) clock=Δ-296(±249,OUT) split=Δ-0.486(±0.284,OUT) |
| 4 | k=4.5 A=-0.7625±3.7 (-) | tau=2101±1.1e+02 | S=0.8711 P=0.09806±0.086 (n=39) | 0.1049 | arrow=Δ0.139(±7.56,in-err) clock=Δ-273(±220,OUT) split=Δ0.36(±0.233,OUT) |
| 5 | k=4.5 A=-0.7066±3.4 (-) | tau=1922±88 | S=0.817 P=0.2063±0.1 (n=39) | 0.09844 | arrow=Δ0.0559(±7.05,in-err) clock=Δ-179(±193,in-err) split=Δ0.108(±0.191,in-err) |
| 6 | k=14 A=-0.6715±5.3 (-) | tau=1874±86 | S=0.776 P=0.08919±0.092 (n=39) | 0.09305 | arrow=Δ0.035(±8.66,in-err) clock=Δ-48.1(±174,in-err) split=Δ-0.117(±0.197,in-err) |
| 7 | k=14.8 A=-0.6768±5.1 (-) | tau=1811±89 | S=0.7397 P=0.1024±0.078 (n=39) | 0.08833 | arrow=Δ-0.00525(±10.4,in-err) clock=Δ-62.9(±175,in-err) split=Δ0.0132(±0.17,in-err) |
| 8 | k=20 A=-0.7008±5.5 (-) | tau=1824±87 | S=0.7108 P=0.1301±0.072 (n=39) | 0.08423 | arrow=Δ-0.024(±10.6,in-err) clock=Δ13.7(±176,in-err) split=Δ0.0276(±0.15,in-err) |

Verdict: **FIXED POINT (from hop 5, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=10 A=-8.552±19 (-) | tau=5145±2.9e+02 | S=3.297 P=-0.4954±0.25 (n=39) | 0.2416 | -- |
| 1 | k=5.5 A=-0.2877±0.077 (-) | tau=5374±3.7e+02 | S=-74.6 P=-2.941±14 (n=39) | 0.352 | arrow=Δ8.26(±18.7,in-err) clock=Δ229(±656,in-err) split=Δ-2.45(±14.7,in-err) |
| 2 | k=7 A=-0.3519±0.1 (-) | tau=5547±4.2e+02 | S=-75.37 P=-4.776±15 (n=39) | 0.4182 | arrow=Δ-0.0642(±0.178,in-err) clock=Δ173(±784,in-err) split=Δ-1.83(±29.4,in-err) |
| 3 | k=7 A=-0.4196±0.12 (-) | tau=5556±4.5e+02 | S=-77.09 P=11.68±13 (n=39) | 0.4805 | arrow=Δ-0.0677(±0.223,in-err) clock=Δ8.77(±866,in-err) split=Δ16.5(±28.3,in-err) |
| 4 | k=7 A=-0.487±0.14 (-) | tau=5398±4.7e+02 | S=-79.18 P=-14.09±19 (n=39) | 0.5369 | arrow=Δ-0.0675(±0.261,in-err) clock=Δ-158(±922,in-err) split=Δ-25.8(±32.2,in-err) |
| 5 | k=7 A=-0.5528±0.17 (-) | tau=5010±4.1e+02 | S=-81.95 P=-4.32±16 (n=39) | 0.5858 | arrow=Δ-0.0658(±0.306,in-err) clock=Δ-388(±882,in-err) split=Δ9.77(±35,in-err) |
| 6 | k=7 A=-0.6164±0.19 (-) | tau=4523±3.6e+02 | S=-84.71 P=-4.071±18 (n=39) | 0.63 | arrow=Δ-0.0636(±0.359,in-err) clock=Δ-487(±772,in-err) split=Δ0.249(±34.3,in-err) |
| 7 | k=7 A=-0.6779±0.22 (-) | tau=4172±3.1e+02 | S=-86.91 P=-2.662±19 (n=39) | 0.6689 | arrow=Δ-0.0615(±0.409,in-err) clock=Δ-351(±678,in-err) split=Δ1.41(±37.4,in-err) |
| 8 | k=7 A=-0.7371±0.21 (-) | tau=3946±3.1e+02 | S=-88.27 P=-3.063±21 (n=39) | 0.7037 | arrow=Δ-0.0592(±0.426,in-err) clock=Δ-226(±623,in-err) split=Δ-0.401(±40.2,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=7 A=0.05358±0.015 (+)  |  clock: tau=-1888±95  |  split: S=279.1 P=26.15±20 (n=38)  (raw relay ran 8 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.05602±0.016 | 0.7008±5.8 | AGREE |
| clock (tau) | -1821±84 | -1824±81 | AGREE |
| split (P) | -38.05±45 | -0.0001111±0.05 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 0.05602±0.016 | -0.05602±0.015 | UNSTABLE |
| clock (tau) | -1821±84 | 1821±90 | UNSTABLE |
| split (P) | -38.05±45 | 40.88±27 | UNSTABLE |

### DALET cutoff test (step sizes 0.05 / 0.10 / 0.20, BEFORE order, forward, ascent column)

**eta = 0.05**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=-0.171±0.054 (-) | tau=-5672±3.8e+02 | S=68.98 P=-9.474±9.2 (n=39) | 0.2687 | -- |
| 1 | k=20 A=-0.2507±0.073 (-) | tau=-5599±3.8e+02 | S=69.53 P=-10.4±14 (n=39) | 0.3577 | arrow=Δ-0.0797(±0.127,in-err) clock=Δ72.9(±758,in-err) split=Δ-0.929(±23.5,in-err) |
| 2 | k=5.5 A=0.2748±0.075 (+) | tau=-5605±4e+02 | S=70.32 P=-10.08±14 (n=39) | 0.3906 | arrow=Δ0.525(±0.148,OUT) clock=Δ-6.64(±777,in-err) split=Δ0.319(±28,in-err) |
| 3 | k=5.5 A=0.3005±0.088 (+) | tau=-5720±4.7e+02 | S=71.1 P=-11.31±16 (n=39) | 0.4234 | arrow=Δ0.0257(±0.163,in-err) clock=Δ-115(±869,in-err) split=Δ-1.22(±29.4,in-err) |
| 4 | k=7 A=0.3285±0.1 (+) | tau=-5794±4.9e+02 | S=72.09 P=-15.12±20 (n=39) | 0.4548 | arrow=Δ0.028(±0.188,in-err) clock=Δ-74(±965,in-err) split=Δ-3.81(±35.3,in-err) |
| 5 | k=7 A=0.3593±0.11 (+) | tau=-5829±5.2e+02 | S=73.18 P=-16.02±21 (n=39) | 0.4854 | arrow=Δ0.0308(±0.211,in-err) clock=Δ-35.3(±1.01e+03,in-err) split=Δ-0.899(±40.6,in-err) |
| 6 | k=7 A=0.3902±0.11 (+) | tau=-5777±5.6e+02 | S=74.37 P=-16.9±23 (n=39) | 0.5151 | arrow=Δ0.0309(±0.225,in-err) clock=Δ52.1(±1.08e+03,in-err) split=Δ-0.881(±43.6,in-err) |
| 7 | k=7 A=0.4209±0.12 (+) | tau=-5674±5e+02 | S=75.6 P=-17.75±23 (n=39) | 0.5432 | arrow=Δ0.0307(±0.233,in-err) clock=Δ104(±1.06e+03,in-err) split=Δ-0.853(±45.2,in-err) |
| 8 | k=7 A=0.4515±0.13 (+) | tau=-5563±5.3e+02 | S=76.76 P=-18.52±25 (n=39) | 0.5702 | arrow=Δ0.0306(±0.248,in-err) clock=Δ110(±1.03e+03,in-err) split=Δ-0.766(±47.7,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.1**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=-0.171±0.052 (-) | tau=-5672±3.7e+02 | S=68.98 P=-9.474±9.5 (n=39) | 0.2687 | -- |
| 1 | k=5.5 A=0.2739±0.075 (+) | tau=-5629±4.1e+02 | S=70.24 P=-10.05±14 (n=39) | 0.3907 | arrow=Δ0.445(±0.126,OUT) clock=Δ42.4(±782,in-err) split=Δ-0.576(±23.8,in-err) |
| 2 | k=7 A=0.3263±0.099 (+) | tau=-5866±5.1e+02 | S=71.79 P=-15.26±20 (n=39) | 0.4536 | arrow=Δ0.0524(±0.174,in-err) clock=Δ-237(±918,in-err) split=Δ-5.21(±34.4,in-err) |
| 3 | k=7 A=0.3865±0.11 (+) | tau=-5810±5.5e+02 | S=74.11 P=-16.81±24 (n=39) | 0.513 | arrow=Δ0.0602(±0.21,in-err) clock=Δ56(±1.05e+03,in-err) split=Δ-1.55(±43.9,in-err) |
| 4 | k=7 A=0.4465±0.13 (+) | tau=-5585±5.7e+02 | S=76.55 P=-18.47±24 (n=39) | 0.5664 | arrow=Δ0.06(±0.241,in-err) clock=Δ225(±1.12e+03,in-err) split=Δ-1.66(±48.1,in-err) |
| 5 | k=7 A=0.5052±0.14 (+) | tau=-5350±5.8e+02 | S=78.9 P=-27.43±19 (n=39) | 0.617 | arrow=Δ0.0587(±0.271,in-err) clock=Δ235(±1.15e+03,in-err) split=Δ-8.96(±43.8,in-err) |
| 6 | k=7 A=0.5621±0.18 (+) | tau=-5134±5e+02 | S=80.95 P=-29.43±19 (n=39) | 0.6627 | arrow=Δ0.0569(±0.324,in-err) clock=Δ216(±1.08e+03,in-err) split=Δ-1.99(±38.9,in-err) |
| 7 | k=7 A=0.6165±0.17 (+) | tau=-5015±5.1e+02 | S=82.5 P=-31.4±22 (n=39) | 0.7042 | arrow=Δ0.0544(±0.351,in-err) clock=Δ119(±1.01e+03,in-err) split=Δ-1.98(±41.3,in-err) |
| 8 | k=7 A=0.6683±0.18 (+) | tau=-5003±5.5e+02 | S=83.92 P=-35.68±22 (n=39) | 0.7406 | arrow=Δ0.0518(±0.346,in-err) clock=Δ11.2(±1.06e+03,in-err) split=Δ-4.27(±44.2,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**eta = 0.2**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=20 A=-0.171±0.054 (-) | tau=-5672±3.6e+02 | S=68.98 P=-9.474±9 (n=39) | 0.2687 | -- |
| 1 | k=7 A=0.3218±0.093 (+) | tau=-5981±5.2e+02 | S=70.99 P=-14.89±21 (n=39) | 0.4498 | arrow=Δ0.493(±0.147,OUT) clock=Δ-309(±874,in-err) split=Δ-5.41(±30,in-err) |
| 2 | k=7 A=0.4381±0.14 (+) | tau=-5672±5.3e+02 | S=76.38 P=-21.23±14 (n=39) | 0.5601 | arrow=Δ0.116(±0.229,in-err) clock=Δ309(±1.05e+03,in-err) split=Δ-6.34(±34.6,in-err) |
| 3 | k=7 A=0.5503±0.16 (+) | tau=-5257±5e+02 | S=80.48 P=-18.6±25 (n=39) | 0.6524 | arrow=Δ0.112(±0.293,in-err) clock=Δ415(±1.03e+03,in-err) split=Δ2.63(±38.1,in-err) |
| 4 | k=7 A=0.6534±0.19 (+) | tau=-4976±5.1e+02 | S=83.74 P=-33.22±36 (n=39) | 0.7283 | arrow=Δ0.103(±0.344,in-err) clock=Δ281(±1.01e+03,in-err) split=Δ-14.6(±60.8,in-err) |
| 5 | k=7 A=0.7481±0.23 (+) | tau=-4979±5.4e+02 | S=86.1 P=-51.89±30 (n=39) | 0.7916 | arrow=Δ0.0947(±0.413,in-err) clock=Δ-3.37(±1.06e+03,in-err) split=Δ-18.7(±66.2,in-err) |
| 6 | k=7 A=0.8332±0.23 (+) | tau=-5178±5.9e+02 | S=88.87 P=-19.9±37 (n=39) | 0.8407 | arrow=Δ0.0852(±0.457,in-err) clock=Δ-199(±1.13e+03,in-err) split=Δ32(±67.5,in-err) |
| 7 | k=7 A=0.9115±0.25 (+) | tau=-4974±6.2e+02 | S=92.68 P=-65.49±36 (n=39) | 0.8818 | arrow=Δ0.0783(±0.48,in-err) clock=Δ204(±1.21e+03,in-err) split=Δ-45.6(±73.1,in-err) |
| 8 | k=7 A=0.9825±0.33 (+) | tau=-4804±5.3e+02 | S=95.83 P=-0.3743±43 (n=39) | 0.9136 | arrow=Δ0.071(±0.582,in-err) clock=Δ170(±1.15e+03,in-err) split=Δ65.1(±78.9,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

---

## mice_size45_pooled  (family: mice, units: h, n=8192)

**BEFORE order, forward -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=0.5 A=0.01783±0.0028 (+) | tau=-3.145e+04±1.8e+04 | S=13.08 P=-2.281±4.5 (n=39) | 0.1821 | -- |
| 1 | k=0.75 A=0.001413±0.00044 (+) | tau=-3.034e+04±5.1e+04 | S=12.99 P=-0.1524±5 (n=39) | 0.05255 | arrow=Δ-0.0164(±0.00327,OUT) clock=Δ1.11e+03(±6.89e+04,in-err) split=Δ2.13(±9.49,in-err) |
| 2 | k=15.8 A=-0.000321±0.00011 (-) | tau=-1.72e+04±7.2e+03 | S=13.81 P=-2.598±6.9 (n=39) | 0.02176 | arrow=Δ-0.00173(±0.000553,OUT) clock=Δ1.31e+04(±5.8e+04,in-err) split=Δ-2.45(±11.9,in-err) |
| 3 | k=0.25 A=0.0001411±5e-05 (+) | tau=-4.435e+05±1.3e+06 | S=7.187 P=7.455±5.9 (n=39) | 0.01255 | arrow=Δ0.000462(±0.000165,OUT) clock=Δ-4.26e+05(±1.34e+06,in-err) split=Δ10.1(±12.8,in-err) |
| 4 | k=0.25 A=9.427e-05±3.4e-05 (+) | tau=-7.02e+04±1e+06 | S=10.3 P=-9.584±11 (n=39) | 0.008889 | arrow=Δ-4.68e-05(±8.38e-05,in-err) clock=Δ3.73e+05(±2.37e+06,in-err) split=Δ-17(±17.1,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, forward -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=0.5 A=0.01783±0.0026 (+) | tau=-3.145e+04±1.8e+04 | S=13.08 P=-2.281±4.6 (n=39) | 0.1821 | -- |
| 1 | k=0.5 A=0.09252±0.013 (+) | tau=-3.705e+04±2.3e+06 | S=12.97 P=-1.864±9 (n=39) | 0.638 | arrow=Δ0.0747(±0.0159,OUT) clock=Δ-5.6e+03(±2.35e+06,in-err) split=Δ0.417(±13.5,in-err) |
| 2 | k=0.5 A=0.09721±0.015 (+) | tau=-3.886e+04±1.6e+06 | S=13.54 P=-1.18±9.6 (n=39) | 0.7378 | arrow=Δ0.00469(±0.0279,in-err) clock=Δ-1.81e+03(±3.97e+06,in-err) split=Δ0.684(±18.5,in-err) |
| 3 | k=0.75 A=0.102±0.02 (+) | tau=-3.763e+04±3.7e+05 | S=14.17 P=4.394±9.4 (n=39) | 0.8354 | arrow=Δ0.00484(±0.0346,in-err) clock=Δ1.23e+03(±2e+06,in-err) split=Δ5.57(±19,in-err) |
| 4 | k=0.75 A=0.1066±0.022 (+) | tau=-3.07e+04±1.2e+06 | S=15.05 P=-3.486±11 (n=39) | 0.9294 | arrow=Δ0.00452(±0.0418,in-err) clock=Δ6.93e+03(±1.54e+06,in-err) split=Δ-7.88(±20,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**BEFORE order, reversed -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=0.5 A=-0.01783±0.0027 (-) | tau=3.145e+04±8.8e+04 | S=-13.17 P=0.2561±5.1 (n=39) | 0.1821 | -- |
| 1 | k=0.75 A=-0.001413±0.00041 (-) | tau=3.034e+04±8.4e+04 | S=-12.85 P=-5.972±4.2 (n=39) | 0.05255 | arrow=Δ0.0164(±0.00311,OUT) clock=Δ-1.11e+03(±1.72e+05,in-err) split=Δ-6.23(±9.29,in-err) |
| 2 | k=15.8 A=0.000321±0.00012 (+) | tau=1.72e+04±5.5e+03 | S=-13.82 P=3.922±4.8 (n=39) | 0.02176 | arrow=Δ0.00173(±0.000531,OUT) clock=Δ-1.31e+04(±9e+04,in-err) split=Δ9.89(±8.98,OUT) |
| 3 | k=0.25 A=-0.0001411±4.9e-05 (-) | tau=4.435e+05±1.8e+06 | S=-6.43 P=3.908±10 (n=39) | 0.01255 | arrow=Δ-0.000462(±0.000166,OUT) clock=Δ4.26e+05(±1.84e+06,in-err) split=Δ-0.0136(±15.2,in-err) |
| 4 | k=0.25 A=-9.427e-05±3.3e-05 (-) | tau=7.02e+04±4.7e+05 | S=-9.787 P=-1.49±11 (n=39) | 0.008889 | arrow=Δ4.68e-05(±8.2e-05,in-err) clock=Δ-3.73e+05(±2.31e+06,in-err) split=Δ-5.4(±21.4,in-err) |

Verdict: **FIXED POINT (from hop 3, keys: clock,split)**

**BEFORE order, reversed -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=0.5 A=-0.01783±0.0026 (-) | tau=3.145e+04±2.9e+04 | S=-13.17 P=0.2561±5.5 (n=39) | 0.1821 | -- |
| 1 | k=0.5 A=-0.09252±0.013 (-) | tau=3.705e+04±4.3e+05 | S=-12.95 P=-8.693±6.7 (n=39) | 0.638 | arrow=Δ-0.0747(±0.0157,OUT) clock=Δ5.6e+03(±4.58e+05,in-err) split=Δ-8.95(±12.3,in-err) |
| 2 | k=0.5 A=-0.09721±0.015 (-) | tau=3.886e+04±1.2e+05 | S=-13.36 P=-17.2±5.9 (n=39) | 0.7378 | arrow=Δ-0.00469(±0.0283,in-err) clock=Δ1.81e+03(±5.52e+05,in-err) split=Δ-8.51(±12.7,in-err) |
| 3 | k=0.75 A=-0.102±0.02 (-) | tau=3.763e+04±4e+06 | S=-13.88 P=-12.51±9.7 (n=39) | 0.8354 | arrow=Δ-0.00484(±0.0352,in-err) clock=Δ-1.23e+03(±4.08e+06,in-err) split=Δ4.69(±15.6,in-err) |
| 4 | k=0.75 A=-0.1066±0.021 (-) | tau=3.07e+04±1.6e+05 | S=-14.7 P=-12.88±8.3 (n=39) | 0.9294 | arrow=Δ-0.00452(±0.0412,in-err) clock=Δ-6.93e+03(±4.12e+06,in-err) split=Δ-0.367(±17.9,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: clock,split)**

**AFTER order, forward (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=12.2 A=4.928±13 (+) | tau=-1.702e+04±3.6e+03 | S=-0.9306 P=0.07802±0.099 (n=39) | 0.1858 | -- |
| 1 | k=18.2 A=1.515±5.5 (+) | tau=-1.387e+04±3.3e+03 | S=-0.3088 P=-0.1567±0.044 (n=39) | 0.0532 | arrow=Δ-3.41(±18.6,in-err) clock=Δ3.15e+03(±6.87e+03,in-err) split=Δ-0.235(±0.143,OUT) |
| 2 | k=11.5 A=0.5584±2.9 (+) | tau=-1.581e+04±5.2e+03 | S=-0.05622 P=-0.008033±0.026 (n=39) | 0.0228 | arrow=Δ-0.956(±8.49,in-err) clock=Δ-1.94e+03(±8.52e+03,in-err) split=Δ0.149(±0.0697,OUT) |
| 3 | k=17.8 A=0.593±1.7 (+) | tau=-2.25e+04±5.7e+04 | S=-0.1079 P=0.0235±0.024 (n=39) | 0.01281 | arrow=Δ0.0346(±4.67,in-err) clock=Δ-6.69e+03(±6.18e+04,in-err) split=Δ0.0315(±0.0505,in-err) |
| 4 | k=17 A=0.4737±1.6 (+) | tau=-7.491e+04±6.3e+05 | S=-0.08158 P=-0.007804±0.017 (n=39) | 0.008872 | arrow=Δ-0.119(±3.29,in-err) clock=Δ-5.24e+04(±6.87e+05,in-err) split=Δ-0.0313(±0.0413,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order, forward (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=12.2 A=4.928±13 (+) | tau=-1.702e+04±3.6e+03 | S=-0.9306 P=0.07802±0.096 (n=39) | 0.1858 | -- |
| 1 | k=0.5 A=0.08899±0.012 (+) | tau=-1.709e+04±5.4e+03 | S=24.4 P=18.33±7.6 (n=39) | 0.6287 | arrow=Δ-4.84(±12.6,in-err) clock=Δ-69.2(±9.01e+03,in-err) split=Δ18.3(±7.7,OUT) |
| 2 | k=0.5 A=0.09233±0.015 (+) | tau=-1.729e+04±4.9e+03 | S=25.1 P=18.94±7.9 (n=39) | 0.7212 | arrow=Δ0.00333(±0.0269,in-err) clock=Δ-204(±1.03e+04,in-err) split=Δ0.606(±15.5,in-err) |
| 3 | k=0.5 A=0.09503±0.016 (+) | tau=-1.67e+04±4.7e+03 | S=26.4 P=21.68±7.6 (n=39) | 0.83 | arrow=Δ0.00271(±0.0306,in-err) clock=Δ598(±9.56e+03,in-err) split=Δ2.74(±15.5,in-err) |
| 4 | k=0.75 A=0.09802±0.021 (+) | tau=-1.726e+04±9.1e+03 | S=27.42 P=21.79±9.9 (n=39) | 0.9289 | arrow=Δ0.00299(±0.0374,in-err) clock=Δ-561(±1.38e+04,in-err) split=Δ0.106(±17.5,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order, reversed (raw relay) -- plain-subtraction**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=12.2 A=-4.928±13 (-) | tau=1.702e+04±3.2e+03 | S=0.941 P=0.2066±0.19 (n=39) | 0.1858 | -- |
| 1 | k=18.2 A=-1.515±5.6 (-) | tau=1.387e+04±2.9e+03 | S=0.3131 P=-0.02846±0.043 (n=39) | 0.0532 | arrow=Δ3.41(±18.2,in-err) clock=Δ-3.15e+03(±6.07e+03,in-err) split=Δ-0.235(±0.237,in-err) |
| 2 | k=11.5 A=-0.5584±3.1 (-) | tau=1.581e+04±5.2e+03 | S=0.0582 P=-0.04043±0.025 (n=39) | 0.0228 | arrow=Δ0.956(±8.76,in-err) clock=Δ1.94e+03(±8.11e+03,in-err) split=Δ-0.012(±0.068,in-err) |
| 3 | k=17.8 A=-0.593±1.9 (-) | tau=2.25e+04±1e+05 | S=0.1091 P=-0.0001816±0.021 (n=39) | 0.01281 | arrow=Δ-0.0346(±5.04,in-err) clock=Δ6.69e+03(±1.08e+05,in-err) split=Δ0.0402(±0.0461,in-err) |
| 4 | k=17 A=-0.4737±1.4 (-) | tau=7.491e+04±8.3e+05 | S=0.0829 P=-0.01624±0.012 (n=39) | 0.008872 | arrow=Δ0.119(±3.35,in-err) clock=Δ5.24e+04(±9.29e+05,in-err) split=Δ-0.0161(±0.0329,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock,split)**

**AFTER order, reversed (raw relay) -- DALET (ascent, eta=0.10)**

| hop | arrow | clock | split(c) | resid var frac (of x0) | delta vs prev hop |
|---|---|---|---|---|---|
| 0 | k=12.2 A=-4.928±15 (-) | tau=1.702e+04±2.9e+03 | S=0.941 P=0.2066±0.19 (n=39) | 0.1858 | -- |
| 1 | k=0.5 A=-0.08899±0.013 (-) | tau=1.709e+04±6.4e+03 | S=-24.34 P=-14.82±5.8 (n=39) | 0.6287 | arrow=Δ4.84(±14.6,in-err) clock=Δ69.2(±9.38e+03,in-err) split=Δ-15(±5.97,OUT) |
| 2 | k=0.5 A=-0.09233±0.014 (-) | tau=1.729e+04±6.5e+03 | S=-25.01 P=-12.88±6.6 (n=39) | 0.7212 | arrow=Δ-0.00333(±0.0272,in-err) clock=Δ204(±1.29e+04,in-err) split=Δ1.94(±12.4,in-err) |
| 3 | k=0.5 A=-0.09503±0.015 (-) | tau=1.67e+04±6.6e+03 | S=-26.28 P=-2.835±8.2 (n=39) | 0.83 | arrow=Δ-0.00271(±0.0293,in-err) clock=Δ-598(±1.31e+04,in-err) split=Δ10(±14.7,in-err) |
| 4 | k=0.75 A=-0.09802±0.022 (-) | tau=1.726e+04±2.4e+04 | S=-27.19 P=0.3318±11 (n=39) | 0.9289 | arrow=Δ-0.00299(±0.0367,in-err) clock=Δ561(±3.08e+04,in-err) split=Δ3.17(±18.7,in-err) |

Verdict: **FIXED POINT (from hop 1, keys: arrow,clock)**

**AFTER order: final sub-chain residual, textbook-residualized once more**

arrow: k=4.25 A=7.573e-05±3.5e-05 (+)  |  clock: tau=-1.379e+05±1.1e+06  |  split: S=18.28 P=-15.36±10 (n=39)  (raw relay ran 4 hop(s) before stopping)

**BEFORE vs AFTER, forward, plain-subtraction column, each number's last finite hop:**

| number | BEFORE (last hop) | AFTER (last hop) | call |
|---|---|---|---|
| arrow (A) | 9.427e-05±3.4e-05 | 0.4737±1.6 | AGREE |
| clock (tau) | -7.02e+04±1e+06 | -7.491e+04±6.3e+05 | AGREE |
| split (P) | -9.584±11 | -0.007804±0.017 | AGREE |

**Forward vs reversed, BEFORE order, plain-subtraction column, each number's last finite hop:**

| number | forward (last hop) | reversed (last hop) | call |
|---|---|---|---|
| arrow (A) | 9.427e-05±3.4e-05 | -9.427e-05±3.3e-05 | UNSTABLE |
| clock (tau) | -7.02e+04±1e+06 | 7.02e+04±4.7e+05 | AGREE |
| split (P) | -9.584±11 | -1.49±11 | AGREE |

---

## Errors and uncomputable cells -- count

Total hop-level formula-error/uncomputable cells found across all 9 records x 4 order/direction combos x 2 columns x up to 9 hops, including the 4-record DALET cutoff test: **0**. Checked by walking the raw results JSON for every `"error"` key, not just by eyeballing the tables. Read plainly: every hop's arrow k-sweep found a finite best k and >0 valid bootstrap draws, every clock Hilbert-envelope fit found a finite nonzero tau, and every split(c) window had >=5 naive peaks and >=4 cycles, on every record, every order, every direction, every column, every hop up to the stopping point -- a real finding (these are short, noisy, non-yeast-like series that could plausibly have starved the peak detector or the envelope fit), not a hidden zero from a bug: the JSON was walked programmatically (`scan()` over every dict for an `"error"` string key), and the count is reproduced by rerunning that same walk over `reverse_gradient_results.json`.

## Tries

Per hop, per column, per combo: arrow = one k-sweep (<=80 k, direct argmax|A|, no shuffle) + 300 case-resample bootstrap draws at the best k. Clock = one Hilbert-envelope exp-decay fit + 300 case-resample bootstrap draws. Split(c) = one peak-detect + candidate_c fit + 300 case-resample bootstrap draws. 9 records x 4 order/direction combos x 2 columns x up to 9 measurement rows (hop 0..8) = up to 648 hop-measurements, each with 3x300=900 draws when all three formulas compute successfully (~580,000 draws before uncomputable cells are subtracted out); plus the DALET cutoff test (4 records x 2 extra step sizes x up to 9 hops x 900 draws, ascent column only, sub column reused conceptually but NOT actually recomputed-shared in this pass -- each eta's relay() call reruns both columns independently, so cutoff draws are counted in the same total via the hop-measurement count above, not double-counted separately) plus the AFTER-order final-textbook single-pass re-derivation (9 records x 1 extra measurement row x 900 draws = 8,100 draws). No shuffle-floor draws in this pass (departure from `three_formulas.py`, documented above).
