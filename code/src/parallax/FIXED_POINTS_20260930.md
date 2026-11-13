Method notes (read before the numbers): "terminal hop" = the last hop actually computed for that chain in `reverse_gradient_results.json` (the relay's own stopping point: plain-subtraction stops itself at resid-var-frac < 1% or hop 8; DALET always runs to hop 8, since it's ascent and never self-stops). "hop where fixed-point criterion met" is the source script's own rule (`fixed_point_verdict`: two consecutive hops with ≥2 of {arrow, clock, split} deltas within combined bootstrap error) -- re-derived here directly from the JSON deltas, matching the markdown report's verdicts. Where that rule never fired, terminal hop is just wherever the relay stopped, not a real fixed point -- flagged "none" in the table.

"Record's own dominant period" = the hop-0 (unrelayed) arrow-lag `k_native` from the BEFORE-order, forward, plain-subtraction chain -- the arrow statistic's own best-lag on the raw residualized signal, already computed once per record in the source run, used here (not recomputed) as the one native yardstick per record so k and tau can be read as multiples of "the record's own beat." Arrow's lag k carries no bootstrap error in this run (only the arrow amplitude A was bootstrapped) -- k and k/period are reported as bare numbers, no error bar, and are excluded from the AGREE/DISAGREE calls below for that reason.

Call rule (no shuffle, ever): a number counts as "well-resolved" only if its bootstrap error is smaller than its own magnitude. Two well-resolved numbers get compared -- AGREE if |delta| ≤ combined error, STABLE DISAGREEMENT if not. If either side isn't well-resolved (error ≥ |value|, or a value is missing/non-finite), the call is UNSTABLE regardless of nominal overlap -- a comparison built on a number that isn't pinned down isn't a real agreement or a real disagreement, just noise touching noise.

## The fixed points, side by side

| sub-record | period (native, hop-0 arrow lag) | column | arrow k (native) | k / period | sign | clock tau (native) | tau / period | split S | split P | resid var frac (terminal) | terminal hop | hop where fixed-point criterion met |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| yeast during | 66.81 s | plain | 75.98 s | 1.14 | + | 3691±2.844e+05 s | 55.25±4258 | -2.623 | 0.4148±0.3756 (n=28) | 0.006217 | 3 | none (ran to cap/stop, 4 hops only -- plain stopped itself early on rvf<1%) |
| yeast during | 66.81 s | DALET | 66.81 s | 1 | - | 1250±7.877e+05 s | 18.71±1.179e+04 | -13.04 | -0.4751±0.7808 (n=17) | 5.385e-07 | 3 | 1 |
| yeast whole | 34.06 s | plain | 17.03 s | 0.5 | - | 3305±551.1 s | 97.03±16.18 | -4.917 | -0.07111±0.4163 (n=35) | 0.01675 | 8 | 4 |
| yeast whole | 34.06 s | DALET | 66.81 s | 1.96 | - | 2224±226.6 s | 65.29±6.652 | -142.7 | -3.157±3.184 (n=32) | 2.365e-06 | 8 | 1 |
| horn at-horn | 25.74 s | plain | 23.76 s | 0.923 | + | 852.4±172.3 s | 33.12±6.696 | -5.883 | 0.7393±0.7006 (n=38) | 0.009407 | 5 | 1 |
| horn at-horn | 25.74 s | DALET | 23.76 s | 0.923 | + | 819.3±94.28 s | 31.83±3.663 | -7.821 | 6.023±3.359 (n=37) | 0.4938 | 5 | 1 |
| horn whole | 25.08 s | plain | 16.5 s | 0.658 | + | -4.026e+04±4399 s | -1605±175.4 | 40.61 | 0.2345±1.363 (n=39) | 0.03596 | 8 | 2 |
| horn whole | 25.08 s | DALET | 21.45 s | 0.855 | + | -1.451e+05±2.063e+05 s | -5785±8226 | 141.5 | -7.849±22.03 (n=39) | 0.03338 | 8 | 1 |
| buzz 80 | 75 shots | plain | 53 shots | 0.707 | + | 7903±694.7 shots | 105.4±9.262 | -143.9 | 8.003±21.62 (n=38) | 0.008141 | 6 | 1 |
| buzz 80 | 75 shots | DALET | 80 shots | 1.07 | - | -1.073e+05±3.001e+06 shots | -1430±4.002e+04 | -47.08 | 2.528±7.26 (n=38) | 0.00159 | 6 | 1 |
| buzz 100 | 80 shots | plain | 80 shots | 1 | - | -4.569e+04±2.719e+05 shots | -571.1±3399 | 74.12 | -5.739±6.266 (n=38) | 0.009509 | 5 | 3 |
| buzz 100 | 80 shots | DALET | 66 shots | 0.825 | + | 5735±351.2 shots | 71.68±4.39 | -277.3 | -2.026±9.178 (n=38) | 0.00084 | 5 | 1 |
| buzz 116 | 80 shots | plain | 60 shots | 0.75 | - | -4.81e+05±2.43e+06 shots | -6012±3.037e+04 | -43.88 | 5.968±4.699 (n=38) | 0.005703 | 3 | 1 |
| buzz 116 | 80 shots | DALET | 52 shots | 0.65 | + | 9011±937.2 shots | 112.6±11.72 | -146.6 | 21.94±12.11 (n=38) | 0.0003757 | 3 | 1 |
| mice size-1 | 20 h | plain | 7 h | 0.35 | + | -1821±83.93 h | -91.03±4.196 | 202.0 | -38.05±44.89 (n=39) | 0.08877 | 8 | 2 |
| mice size-1 | 20 h | DALET | 7 h | 0.35 | + | -5003±562 h | -250.2±28.1 | 83.92 | -35.68±21.38 (n=39) | 0.7406 | 8 | 1 |
| mice 4-5 | 0.5 h | plain | 0.25 h | 0.5 | + | -7.02e+04±1.034e+06 h | -1.404e+05±2.069e+06 | 10.30 | -9.584±11.2 (n=39) | 0.008889 | 4 | 1 |
| mice 4-5 | 0.5 h | DALET | 0.75 h | 1.5 | + | -3.07e+04±1.174e+06 h | -6.141e+04±2.349e+06 | 15.05 | -3.486±10.6 (n=39) | 0.9294 | 4 | 1 |

## Record vs record, cross-substrate, on the dimensionless cells (DALET terminal, the column that actually reaches a real fixed point in all 9 records)

**split P**

| pair | P (record A) | P (record B) | call |
|---|---|---|---|
| horn at-horn vs buzz 116 | 6.023±3.359 | 21.94±12.11 | STABLE DISAGREEMENT |
| horn at-horn vs mice size-1 | 6.023±3.359 | -35.68±21.38 | STABLE DISAGREEMENT |
| buzz 116 vs mice size-1 | 21.94±12.11 | -35.68±21.38 | STABLE DISAGREEMENT |
| all other 25 cross-substrate pairs (yeast during/whole, horn whole, buzz 80/100, mice 4-5, in every other combination) | -- | -- | UNSTABLE -- at least one side's P isn't well-resolved (bootstrap error ≥ \|P\|) |

**tau / period**

| pair | tau/period (A) | tau/period (B) | call |
|---|---|---|---|
| yeast whole vs buzz 100 | 65.29±6.652 | 71.68±4.39 | **AGREE** |
| yeast whole vs horn at-horn | 65.29±6.652 | 31.83±3.663 | STABLE DISAGREEMENT |
| yeast whole vs buzz 116 | 65.29±6.652 | 112.6±11.72 | STABLE DISAGREEMENT |
| yeast whole vs mice size-1 | 65.29±6.652 | -250.2±28.1 | STABLE DISAGREEMENT |
| horn at-horn vs buzz 100 | 31.83±3.663 | 71.68±4.39 | STABLE DISAGREEMENT |
| horn at-horn vs buzz 116 | 31.83±3.663 | 112.6±11.72 | STABLE DISAGREEMENT |
| horn at-horn vs mice size-1 | 31.83±3.663 | -250.2±28.1 | STABLE DISAGREEMENT |
| buzz 100 vs mice size-1 | 71.68±4.39 | -250.2±28.1 | STABLE DISAGREEMENT |
| buzz 116 vs mice size-1 | 112.6±11.72 | -250.2±28.1 | STABLE DISAGREEMENT |
| all remaining cross-substrate pairs (any pairing touching yeast during, horn whole, buzz 80, or mice 4-5) | -- | -- | UNSTABLE -- tau/period isn't well-resolved on at least one side (yeast during, horn whole, buzz 80, mice 4-5 all carry tau errors bigger than tau itself at the fixed point) |

**k / period** -- listed, not called: arrow's lag k has no bootstrap error in this run, so no AGREE/DISAGREE/UNSTABLE call is honest here. Values (DALET terminal): yeast during 1.0, yeast whole 1.96, horn at-horn 0.923, horn whole 0.855, buzz 80 1.07, buzz 100 0.825, buzz 116 0.65, mice size-1 0.35, mice 4-5 1.5. Six of nine sit within 20% of 1.0 (the record's own hop-0 beat); mice (both) and yeast whole are the outliers.

Within-family (same substrate) pairs, for reference: only buzz 100 vs buzz 116 resolves on tau/period, and it's a STABLE DISAGREEMENT (71.68±4.39 vs 112.6±11.72); yeast during vs yeast whole, horn at-horn vs horn whole, buzz 80 vs either other seat, and mice size-1 vs mice 4-5 are all UNSTABLE on both P and tau/period.

## DALET vs plain fixed points, per record (native units, terminal hop each)

| record | P: plain vs DALET | call | tau: plain vs DALET | call |
|---|---|---|---|---|
| yeast during | 0.4148±0.3756 vs -0.4751±0.7808 | UNSTABLE | 3691±2.844e+05 vs 1250±7.877e+05 | UNSTABLE |
| yeast whole | -0.07111±0.4163 vs -3.157±3.184 | UNSTABLE | 3305±551.1 vs 2224±226.6 | STABLE DISAGREEMENT |
| horn at-horn | 0.7393±0.7006 vs 6.023±3.359 | STABLE DISAGREEMENT | 852.4±172.3 vs 819.3±94.28 | **AGREE** |
| horn whole | 0.2345±1.363 vs -7.849±22.03 | UNSTABLE | -4.026e+04±4399 vs -1.451e+05±2.063e+05 | UNSTABLE |
| buzz 80 | 8.003±21.62 vs 2.528±7.26 | UNSTABLE | 7903±694.7 vs -1.073e+05±3.001e+06 | UNSTABLE |
| buzz 100 | -5.739±6.266 vs -2.026±9.178 | UNSTABLE | -4.569e+04±2.719e+05 vs 5735±351.2 | UNSTABLE |
| buzz 116 | 5.968±4.699 vs 21.94±12.11 | **AGREE** | -4.81e+05±2.43e+06 vs 9011±937.2 | UNSTABLE |
| mice size-1 | -38.05±44.89 vs -35.68±21.38 | UNSTABLE | -1821±83.93 vs -5003±562 | STABLE DISAGREEMENT |
| mice 4-5 | -9.584±11.2 vs -3.486±10.6 | UNSTABLE | -7.02e+04±1.034e+06 vs -3.07e+04±1.174e+06 | UNSTABLE |

## BEFORE vs AFTER, per record (plain-subtraction column, terminal hop each)

| record | P: BEFORE vs AFTER | call | tau: BEFORE vs AFTER | call |
|---|---|---|---|---|
| yeast during | 0.4148±0.3756 vs 0.001154±0.0077 | UNSTABLE | 3691±2.844e+05 vs 4.818e+04±4.85e+05 | UNSTABLE |
| yeast whole | -0.07111±0.4163 vs 0.02837±0.0117 | UNSTABLE | 3305±551.1 vs 2439±403 | **AGREE** |
| horn at-horn | 0.7393±0.7006 vs 0.005236±0.00366 | STABLE DISAGREEMENT | 852.4±172.3 vs 852.4±147 | **AGREE** |
| horn whole | 0.2345±1.363 vs -0.02336±0.142 | UNSTABLE | -4.026e+04±4399 vs -4.026e+04±4383 | **AGREE** |
| buzz 80 | 8.003±21.62 vs 0.08895±0.228 | UNSTABLE | 7903±694.7 vs -1.041e+05±8.55e+05 | UNSTABLE |
| buzz 100 | -5.739±6.266 vs 1.181±1.41 | UNSTABLE | -4.569e+04±2.719e+05 vs 1.183e+04±1620 | UNSTABLE |
| buzz 116 | 5.968±4.699 vs -0.07299±0.242 | UNSTABLE | -4.81e+05±2.43e+06 vs 8960±2480 | UNSTABLE |
| mice size-1 | -38.05±44.89 vs -0.0001111±0.0498 | UNSTABLE | -1821±83.93 vs -1824±80.6 | **AGREE** |
| mice 4-5 | -9.584±11.2 vs -0.007804±0.017 | UNSTABLE | -7.02e+04±1.034e+06 vs -7.491e+04±6.31e+05 | UNSTABLE |

## In plain words

**(1) Cross-substrate agreements within errors, at the fixed point.** Exactly one: **yeast whole and buzz seat 100 agree on tau/period** -- 65.29±6.65 vs 71.68±4.39 (DALET terminal), both well inside each other's combined bootstrap error (delta 6.39, combined error 11.0). That's a yeast glycolytic-oscillation record and a superconducting-chip echo record landing on almost the same multiple of their own beat at the point where the reverse-gradient relay quits moving. No other cross-substrate cell (P, or any other tau/period pair) resolves to AGREE -- everything else is either a real (STABLE) disagreement or too noisy to call (UNSTABLE). BEFORE-vs-AFTER tau agrees for 4 of 9 records (yeast whole, horn at-horn, horn whole, mice size-1) -- but that's the same record's own two processing orders, not a cross-substrate claim.

**(2) Stable disagreements** (both sides well-resolved, real gap): on split P -- horn at-horn vs buzz 116, horn at-horn vs mice size-1, buzz 116 vs mice size-1 (radio, chip, and mouse all pull apart from each other, pairwise, once they're resolved enough to compare). On tau/period -- yeast whole disagrees with horn at-horn, buzz 116, and mice size-1; horn at-horn disagrees with buzz 100, buzz 116, and mice size-1; buzz 100 and buzz 116 each disagree with mice size-1. Within one record, DALET vs plain gives a stable disagreement on P at horn at-horn, on tau at yeast whole and at mice size-1 -- the two columns are not measuring the same fixed point there, they're measuring two different converged states.

**(3) Deepest vs shallowest residual variance at the fixed point** (plain-subtraction terminal hop, the column that's actually built to shrink): **mice size-1 gave up the most** -- 0.0888 of its variance still unexplained at hop 8, never got under the 1% stop rule in 8 hops. **Buzz seat 116 gave up the least** -- 0.0057, cleanest fixed point of the nine, reached by hop 3.

Tries: one pass, all numbers pulled straight from `reverse_gradient_results.json` (no re-fit, no re-bootstrap) plus one light derived computation (period from hop-0 arrow lag, unit conversions, the AGREE/DISAGREE/UNSTABLE calls). No fitting code was rerun.

## NORMALIZATION CHECK

The claim under test: yeast-whole and buzz seat 100 "agree" at their DALET fixed points on tau/period (65.29±6.65 vs 71.68±4.39). That period was one specific choice -- each record's own hop-0 arrow lag. Re-normalized three ways, same fixed-point tau (DALET/ascent, BEFORE-order-forward, terminal hop -- read straight from `reverse_gradient_results.json`, never recomputed) divided by three different, independently-derived periods. Neighbors run alongside: buzz seats 80 and 116, and the yeast-during window.

**Raw taus at the fixed point, native units (do not compare seconds to shots directly)**

| record | units | terminal hop | tau (native) |
|---|---|---|---|
| yeast whole | s | 8 | 2224±227 |
| yeast during | s | 3 | 1250±7.88e+05 |
| buzz 80 | shots | 6 | -1.073e+05±3.00e+06 |
| buzz 100 | shots | 5 | 5735±351 |
| buzz 116 | shots | 3 | 9011±937 |

**(a) Spectral peak period** -- FFT of the detrended (textbook, hop-0) record, peak bin's period, bootstrap error from 300 moving-block resamples (block length ≈ n/20).

| record | period (native) | tau/period | call vs its partner |
|---|---|---|---|
| yeast whole | 48.92±95.0 | 45.46±88.4 | -- |
| buzz 100 | 4000±1167 | 1.434±0.427 | **main pair: UNSTABLE** (yeast-whole period error > its own value) |
| yeast during | 50.22±83.2 | 24.90±1.57e+04 | UNSTABLE vs both |
| buzz 80 | 1000±1175 | -107.3±3004 | UNSTABLE vs both |
| buzz 116 | 2000±1184 | 4.506±2.708 | UNSTABLE vs yeast-whole; **AGREE vs buzz 100** (4.51±2.71 vs 1.43±0.43, delta 3.07 ≤ combined 3.14 -- but this is a within-buzz pair, not the cross-substrate claim) |

FFT peak periods for the buzz seats land on suspicious round numbers (1000/2000/4000 shots -- exact fractions of the 4000-shot record length), a sign the "peak" is the lowest resolvable frequency bin, not a real periodicity. Every period here carries a bootstrap error bigger than itself. Nothing cross-substrate is well-resolved enough to call.

**(b) Median peak-to-peak interval** -- from the hop-0 (pre-relay) series, same peak-finder the split instrument uses (`naive_peaks_idx`), bootstrap error from 300 resamples-with-replacement of the interval list.

| record | period (native) | tau/period | call vs its partner |
|---|---|---|---|
| yeast whole | 58.74±3.33 | 37.86±4.41 | -- |
| buzz 100 | 103.5±0.72 | 55.41±3.41 | **main pair: STABLE DISAGREEMENT** (delta 17.55, combined error 7.83) |
| yeast during | 46.99±4.16 | 26.61±1.68e+04 | UNSTABLE (tau error dominates) |
| buzz 80 | 103.5±0.66 | -1036±2.90e+04 | UNSTABLE |
| buzz 116 | 103.5±1.09 | 87.07±9.10 | STABLE DISAGREEMENT vs yeast-whole and vs buzz 100 |

Both main-pair numbers are well-resolved here (errors well under the values) -- and they do NOT agree. The claimed agreement was an artifact of the specific period choice, not something that survives the clock's own beat.

**(c) Independent-window period, fixed point on the rest** -- period = hop-0 arrow-lag k_native computed ONLY on the first third of the record (own textbook detrend, restricted to that slice); tau = fresh DALET relay run to its terminal hop on the LAST TWO-THIRDS only (never seen by the period estimate).

| record | n(1st third) | n(rest) | indep. period (native) | tau on rest | tau/period | call vs its partner |
|---|---|---|---|---|---|---|
| yeast whole | 510 | 1021 | 103.5 | 635.8±32.1 | 6.143±0.311 | -- |
| buzz 100 | 1333 | 2667 | 57 | -3314±308 | -58.14±5.40 | **main pair: STABLE DISAGREEMENT** (delta 64.3, combined error 5.71) |
| yeast during | 153 | 307 | 73.4 | 439.9±37.4 | 5.996±0.509 | **AGREE vs yeast-whole** (delta 0.147, combined 0.82); STABLE DISAGREEMENT vs buzz 100 |
| buzz 80 | 1333 | 2667 | 71 | -1.312e+04±2.42e+04 | -184.8±341 | UNSTABLE (tau on the rest never resolves) |
| buzz 116 | 1333 | 2667 | 18 | -3696±347 | -205.4±19.3 | STABLE DISAGREEMENT vs both |

Note the sign flip: on the independent split, buzz 100's and buzz 116's rest-window tau comes out negative (the DALET relay on a shorter, later-starting sub-series converges to a different-signed decay than the full-series run) -- a hint that the "fixed point" itself is sensitive to which stretch of the record it's measured on, on top of the period question.

### The three calls, plain

- **(a) spectral peak:** UNSTABLE -- can't call it either way, every period here is noise-dominated.
- **(b) clock's own beat (peak-to-peak):** STABLE DISAGREEMENT -- both sides resolve, and they disagree.
- **(c) independent window:** STABLE DISAGREEMENT -- both sides resolve, and they disagree.

**The claimed agreement does not survive any of the three re-normalizations.** It was specific to the one period definition used in the original pass (hop-0 arrow lag). Seat 100 does not agree with yeast under (b) or (c); no cross-substrate pair does under (a) either. The one AGREE that shows up anywhere in this check is same-substrate: yeast-during vs yeast-whole under normalization (c) (5.996±0.509 vs 6.143±0.311) -- the two yeast windows agree with each other, not with the buzz record. Neighbors buzz 80 and buzz 116 never land near yeast or near buzz 100 under any of the three normalizations; where they resolve at all, they're STABLE DISAGREEMENTs.

Tries: one pass. Fixed-point taus read straight from `reverse_gradient_results.json` (no re-fit). Three new period estimators written fresh (FFT+block-bootstrap, peak-to-peak+resample-bootstrap, independent-window arrow-lag + a fresh DALET relay call on the held-out two-thirds, reusing `reverse_gradient.py`'s own `relay()`, `measure_arrow()`, and `split_v2.naive_peaks_idx` verbatim -- no re-fit of the frozen instruments themselves, only new slicing/resampling around them). No shuffle used as judge.
