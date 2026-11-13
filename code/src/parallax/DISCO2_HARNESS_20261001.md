# DISCO 2 HARNESS -- built, proven on synthetic only, NOT run on real pairs (Bones, 2026-10-01)

Code: `out/disco2/disco2.py`. Results: `out/disco2/synthetic_results.json`. Reuses
`out/darkwave_v1/darkwave_v1.py` (arrow, clock, split, the cutoff ladder, Aitken leftover, call_verdict,
run_record, safe_std3) **by import, unedited**. numpy/scipy, single process, no multiprocessing. `--real`
is wired but refuses to run without `out/disco2/REVIEWED.txt` (it does not exist; not run).

---

## WHERE IT BROKE AND WHY

173 break-rows logged over the 6 synthetic cases. None were tuned away; the harness that produced them
is the harness delivered. Full machine-readable list: `synthetic_results.json["breaks"]` (one case's
`"breaks"` key holds the whole run's log, not per-case). Grouped:

| # | WHERE | WHY (exact mechanism) | WHAT IT MEANS FOR THE REAL PAIRS |
|---|---|---|---|
| A (139 rows) | Every control that shortens or coarsens a series -- `same_instrument_shift` (64 rows: split 36, clock 25, arrow 3), `alignment_ruler` (32: split 26, clock 6), `length_variants` (26: split 16, clock 8, arrow 2), the main pair itself at full length (10: split 8, clock 2), `unrelated_record_control` (7: split 6, clock 1) | The split part needs >=4-5 real peaks (`split_v2.candidate_c`, frozen); at cutoff 13 a 300-point sine series block-averages down to ~23 points, often under 5 cycles. The clock needs >=3 usable lags past a `lag_max` that shrinks with series length; short truncations (length/4, same-instrument 1/3 segment) run out of lags before cutoff 13. | **This is not a synthetic-only quirk -- darkwave_v1 already found it on real records** (Old Faithful, lynx-hare, the buzz: "UNCOMPUTABLE by construction"). On the real DISCO 2 table, the short pairs (Bell NIST ~hundreds of rows, Marrakesh placed-vs-arisen 7 points) will run out of ladder before cutoff 13, same as here. The harness reports the missing rungs as reasons, not blanks -- that behavior is confirmed working here on cases of a *known* length where the failure point can be checked by hand. |
| B (6 rows, one per case) | `order_swap_algebraic_check`, part=arrow: sign_error(A,B) = arrow(A)+arrow(rev(B)) and sign_error(B,A) = arrow(B)+arrow(rev(A)) are **exact negatives of each other on all 6 cases** (residual ~1e-17, machine precision) | Because `core.arrow_stat` is forced to flip sign exactly under reversal (darkwave_v1's own finding, re-confirmed here), the arrow's "sign error" algebraically collapses to arrow(A) - arrow(B), a **plain difference with a sign fixed by witness order alone**. Order swap cannot add information for this part. This is **FOR_SHUTTLE section 6, weak spot 3, now proven on 6/6 synthetic cases, not just suspected.** |
| C (6 rows, one per case) | Same check, part=clock: sign_error(A,B) and sign_error(B,A) are **exactly equal** on all 6 cases (residual ~1e-13, floating point) | Because the clock is reversal-invariant by construction (darkwave_v1's own finding), the clock's "sign error" collapses to clock(A) + clock(B), a sum that **cannot distinguish which witness is A and which is B**. Combined with B: of the three parts, **only the split carries order-dependent information that isn't forced by algebra alone** -- confirmed, not assumed, on every synthetic case run. |
| D (6 rows, one per case) | `ruler_row`'s first-pass verdict (`verdict_naive_same_sign`) compares a witness's forward value to its reversed value **directly**, as if every part were reversal-even. That is correct for the clock but wrong for arrow and split, which are reversal-**odd** (darkwave_v1: arrow flips exactly; split closes to ~0, i.e. reversed ~= -forward). On arrow, the naive check called `UNSTABLE` on a relationship that is forced and exact. | **Fixed in this delivery** (parity-corrected comparison added; the naive number is kept in the JSON as `verdict_naive_same_sign`, not deleted -- the "before" row). This is the same disease as [THE THIRD STATE / shape-checks-break-silently]: a verdict function built to say AGREE/DISAGREE silently assumed a shape ("forward equals reversed") that only one of the three parts actually has. Any real-pair ruler row that uses a same-sign comparison on arrow or split would mislabel a working circle as a disagreement. |
| F (15 rows) | `control-vs-main magnitude` check: for every case, at least one of `same_instrument_shift` (same instrument, non-overlapping segment, not a real second witness) or `unrelated_record_control` (white noise, not a real second witness) gives a sign-error magnitude **at or above** the real A-vs-B pair's, for at least one part. This happened on **every one of the 6 cases**, for clock on all 6, for split on 5/6, for arrow on 4/6. | **This is the central finding.** The DISCO 2 sign error's raw *size* at cutoff 1, by itself, does not distinguish "two real witnesses of one event" from "one instrument cut into two pieces" or "an unrelated noise record of matched length" -- on any of the six known-construction cases. The controls are doing their job (catching this); what they're catching is that the correction/ladder step (rho, Aitken leftover across cutoffs), not the raw cutoff-1 number, has to carry the actual discriminating weight, if anything does. A real-pair table that reports only the cutoff-1 sign error without these controls beside it would be reporting a number that a known-null input can match or beat. |
| G (1 row) | `alignment_ruler`: on case (a) -- the one synthetic case built with genuinely different sampling for A and B -- the **native/unaligned** split sign error is `-1.61`, while **all three** aligned methods (block-average, nearest, linear) agree with each other at `+1.27` to `+1.58`. Sign flips between "run each witness on its own timebase/length" (the harness's default) and any common-grid alignment. On the five same-sampling-rate cases, native and aligned agree in sign. | **Confirmed, isolated exactly where predicted**: FOR_SHUTTLE section 6, weak spot 2 ("aligning them is a ruler we haven't built yet"). The real pairs (sunspots vs F10.7, LOD vs tide, etc.) all have mismatched sampling like case (a) -- this is the ruler row the spec asked for, and it fires on the one synthetic input designed to test it, not on the controls that shouldn't trigger it. |

No crashes, no exceptions, no NaN-producing part on any of the 6 cases or their sub-runs (checked: zero
`run failed` / `exception` entries in the break log). The 0/1 flag (control 7) never fired on any
synthetic witness (by design -- none were constructed near-binary); the flag code path itself was
exercised and returns `{"flagged": false, ...}` with its reasoning, not a silent pass.

---

## 1. The design

Every row is **one event, two witnesses**, never one record read alone (darkwave V1 proved a single
record reversed is a circle: arrow and clock close exactly by their own algebra; the split closes to its
length's resolution). THE DISCO 2:

1. **Step 1 (outside):** witness A, forward, all parts (arrow, clock, split -- `darkwave_v1.part_arrow`,
   `part_clock`, `part_split`, called verbatim via `run_formula_on_series`).
2. **Step 2 (observer):** witness B, reversed, all parts.
3. **SIGN ERROR** = A_forward + B_reversed, part by part, at every rung of the cutoff ladder
   `{1,2,3,5,8,13}` (`darkwave_v1.ratios_from_ladder`).
4. **CORRECTION** = the sign-error-vs-cutoff sequence itself run through `darkwave_v1.leftover_from_ladder`
   (rho ladder + Aitken leftover) -- the 1/phi hunter applied to the sign error, not to the raw series.
5. **Error bars** = thirds of each witness, crossed (A's third i with B's third i) -- implemented via
   `darkwave_v1.run_record`'s thirds machinery and `safe_std3`, reused in `ruler_row`.
6. **Ruler rows** = each witness against its own reverse (`ruler_row`, reusing `run_record` +
   `call_verdict`), beside every pair.

No shuffles or surrogate nulls anywhere. No guess written before running. Every unreadable part is a
row with its reason (see table above).

## 2. The control list, mapped to rows

| Spec control | Where it lives in the code / JSON |
|---|---|
| 1. Alignment ruler (3 methods x raw/z-score, common overlap window) | `alignment_ruler()` -> `row["alignment_ruler"]` |
| 2. "It's just A-B" (plain diff + cross-correlation) | `plain_diff_control()` -> `row["order_AB"]["plain_diff"]`, `row["order_BA"]["plain_diff"]` |
| 3. Same instrument, different event (non-overlapping segments, no wraparound) | `same_instrument_shift()` -> `row["same_instrument_shift_A"]`, `row["same_instrument_shift_B"]` |
| 4. Different instrument, different event (unrelated matched-length record; control pair reserved for real run) | `unrelated_record_control()` -> `row["unrelated_record_control"]` |
| 5. Length (shortest common / half / quarter) | `length_variants()` -> `row["length_variants"]` |
| 6. Order (A,B) and (B,A) | `row["order_AB"]`, `row["order_BA"]`, plus the algebraic check `row["order_swap_algebraic_check"]` |
| 7. 0/1 flag | `is_near_binary()` -> `row["binary_flag"]` |
| Ruler rows (witness vs own reverse) | `ruler_row()` -> `row["order_AB"]["ruler_A"]`, `["ruler_B"]` |

## 3. Synthetic results table (cutoff = 1, the raw sign error; full ladders in the JSON)

| Case | A-B sign error: arrow / clock / split | Plain A-B diff (mean, xcorr@lag0) | Order swap forced? | Alignment ruler fires? | Control matches/exceeds main? |
|---|---|---|---|---|---|
| (a) one source, two noisy instruments, different sampling | 0.0183 / 296.8 / **-1.614** | mean -0.146 (truncated), xcorr0 0.100, peak 0.384@lag22 | arrow & clock yes (algebra) | **YES** -- native -1.61 vs aligned +1.3 to +1.6 | split & arrow: yes |
| (b) two independent sources (different events) | -0.118 / 578.2 / -1.909 | mean -0.010, xcorr0 0.117, peak -0.192@lag-72 | arrow & clock yes | no | clock, split, arrow: yes |
| (c) one source, time-lagged second instrument | 0.00038 / 424.2 / -2.159 | mean -0.008, xcorr0 -0.078, peak **0.945@lag-15** (recovers the true 15-sample lag) | arrow & clock yes | no | clock: yes |
| (d) one source, sign-flipped second instrument | 0.00057 / 460.3 / -0.662 | mean 0.014, xcorr0 **-0.983@lag0** (recovers the flip) | arrow & clock yes | no | clock, split: yes |
| (e) time-irreversible source (sawtooth), two instruments | -0.00146 / 494.0 / 2.544 | mean -0.008, xcorr0 **0.979@lag0** | arrow & clock yes | no | clock, split: yes |
| (f) time-reversible source (sine+noise), two instruments | -0.00050 / 461.3 / -2.678 | mean -0.004, xcorr0 **0.981@lag0** | arrow & clock yes | no | clock: yes |

## 4. Plain-words reading of what the harness does to each known input

- **(a) same event, two noisy instruments, different sampling -- the case the design is for.** The plain
  cross-correlation finds a weak peak (0.38) off at lag 22, not at 0 -- a real artifact of resampling two
  different-rate instruments without alignment, not of the underlying shared signal. The DISCO 2 sign
  error's split value **changes sign** depending on whether the two witnesses are put on a common grid
  first. This is the harness correctly exposing that its own default (unaligned) run is not safe to read
  on mismatched-sampling pairs -- which is every real pair on the table. **This case is the clearest
  single result: build the alignment step before reading any real split number.**
- **(b) two independent sources (different events, the spirit of the control pair).** The sign error is
  no smaller than case (a)'s, and the unrelated-record control sits at or above it on arrow, clock, and
  split. The plain cross-correlation is weak (0.12-0.19) and off-centered, correctly showing no real
  relationship -- but the DISCO 2 sign error numbers alone do not visibly distinguish this "nothing
  there" case from the "something there" case (a). The harness cannot yet tell these apart by eye without
  the controls sitting beside the number.
- **(c) time lag.** The plain cross-correlation is the standout tool here -- it recovers the planted
  15-sample lag almost exactly (peak 0.945 at lag -15). The DISCO 2 sign error itself (arrow near zero,
  clock tracking length, split -2.16) gives no direct readout of the lag; a reader would need the
  cross-correlation control to learn what actually happened to this pair.
- **(d) sign-flipped response.** Same story: the plain cross-correlation nails it (-0.983 at lag 0, the
  textbook signature of B = -A). The DISCO 2 split value (-0.66) is smaller in magnitude than most other
  cases but gives no obvious "sign flip" signature on its own.
- **(e) time-irreversible source (sawtooth).** The plain cross-correlation is strong and centered (0.98
  at lag 0, as expected for two noisy readings of the same signal). The arrow's sign error is tiny
  (-0.0015); it does not visibly register the source's time-asymmetry -- it is dominated by the forced
  cancellation described in break-row B, not by any property of the sawtooth.
- **(f) time-reversible source (sine+noise).** Cross-correlation strong and centered (0.98 at lag 0), as
  for (e). Side by side, (e) and (f) do not look different in the DISCO 2 numbers the harness currently
  reports (arrow and clock are both forced; the split magnitudes, -2.68 vs 2.54 in (e), are comparable in
  size with opposite signs that are not obviously tied to reversibility). **The harness as built does not
  yet show a signature that separates an irreversible source from a reversible one** -- that would need
  to show up in the full ladder/Aitken correction (reported in the JSON) rather than the raw cutoff-1
  number, and nothing here claims it does.
- **Across all six:** the arrow part of the sign error is algebraically a plain difference with a forced
  order-dependent sign (break B); the clock part is algebraically an order-independent sum (break C);
  only the **split** carries information that order swap, by itself, doesn't force into a fixed relation
  -- but its raw size is matched or beaten by at least one null control on 5 of 6 cases (break F). The
  ladder/Aitken correction step is computed and stored for every case but this delivery does not claim it
  resolves what the raw number can't; that is exactly the "measured as an object" deliverable, not a
  finding about real data, since nothing here is run on real data.

## 5. Exact command to run on the real pairs (gated, not run)

```
python3 out/disco2/disco2.py --real
```

This currently exits with code 2 and refuses, because `out/disco2/REVIEWED.txt` does not exist. Once an
outside reviewer has signed off (per FOR_SHUTTLE_DISCO_2_20261001.md) and that file is created, `--real`
still needs the real-pair loaders (THE_DISCO_2's table rows 1-10: LIGO H1/L1, NIST Bell Alice/Bob,
sunspots/F10.7, Kp-Ap/Oulu, Mauna Loa/EPICA+CH4, LOD/NYC tide, Nino3.4/GISTEMP, Marrakesh/Kingston,
Jacques/Grangier, mice/neurons) and the LIGO L1 fetch wired in -- `run_real()` is a stub that prints what
is still missing and exits 3. That wiring is out of scope for this delivery on purpose (task instruction:
write the fetch, don't run the analysis; do not run on real pairs at all without review).

## 6. Files

- `out/disco2/disco2.py` -- the harness (imports `out/darkwave_v1/darkwave_v1.py` unedited)
- `out/disco2/synthetic_results.json` -- full synthetic output, including the 173-row break log
  (`["breaks"]`)
- `out/disco2/REVIEWED.txt` -- does not exist (by design; `--real` refuses without it)

---

# THE TRIANGLE -- three witnesses, three firings (Wayfinder's extension, 2026-10-01)

New mode `--triangle` in `out/disco2/disco2.py`. The two-witness mode above is **unchanged** (`--synthetic`
still writes the same `synthetic_results.json`, re-run and confirmed identical: 173 breaks). Triangle
results: `out/disco2/triangle_synthetic_results.json`. Same import discipline (darkwave_v1 unedited, plus
one new function, `cross_arrow_stat`, the cross-witness generalization of `core.arrow_stat`, added in
disco2.py itself, not in core.py). Single process, no multiprocessing. `--real` unchanged (still refuses
without `REVIEWED.txt`); the triangle real pairs (GW170814 H1/L1/Virgo, sun = sunspots/F10.7/Oulu,
carbon = Mauna Loa/EPICA+CH4, Bell = Alice/Bob/sync) are **not fetched or wired in this delivery** --
flagged as still-open below, since the task asked for synthetic proof first.

## WHERE IT BROKE AND WHY -- the triangle

421 break-rows over 7 synthetic cases. Grouped:

| # | WHERE | WHY | WHAT IT MEANS |
|---|---|---|---|
| A (336 rows) | Same disease as the two-witness harness, now hitting three witnesses at once: `same_instrument_three_thirds` (A cut into thirds runs out of cycles/lags fast), `length_variants` (quarter length almost always starves the split), cross terms at native length | Split needs >=4-5 peaks; clock needs >=3 usable lags past a length-dependent `lag_max`. Three-way segmentation (thirds of an already-finite record) hits this ceiling constantly. | Confirms again: short real triangles (Bell NIST, any sub-minute chip run) will run out of ladder fast. Not tuned away. |
| B (10 rows) | `three_cornered_hat` returned a **negative** solved variance, raw, on: g's quarter-length truncation, h's same-instrument-thirds control and quarter truncation, j's same-instrument-thirds and half-length, **k (sign-flipped) at full length AND at all three length truncations**, l's unrelated-record control. | The case **deliberately built** to be the textbook negative (h, hidden common noise between A and B) did **NOT** go negative at full length. Worked out algebraically after the fact: a noise term shared equally between A and B cancels out of `var(A-B)` (it never appears there) and cancels again in the *difference* `var(C-A) - var(B-C)` used to solve `var_A` (it appears in both with the same sign and the same magnitude) -- so it never pushes `var_A` negative in expectation. It DOES inflate `var_C` (the *uncorrelated* third witness gets erroneously assigned ~5x its true noise variance: true 0.01, solved 0.048), because the shared term appears in both `var(B-C)` and `var(C-A)`, which both feed `var_C`'s formula with a plus sign. The most RELIABLE negative in this run came from **k, the sign-flipped witness** -- consistently negative across every length -- because sign-flipping breaks the hat's core assumption (that every witness reads the same signed source) badly enough that the decomposition goes unstable regardless of sample size. | **The three-cornered hat's negative-variance "textbook signature" is not where the textbook case puts it.** A real pair with correlated noise between two witnesses may show up as *inflated variance on the clean third witness*, not as a negative on the correlated pair. A sign convention error (easy to make wiring up a real third witness, e.g. Virgo's or a detector's polarity) is a much more reliable negative-producer than hidden shared noise. Report BOTH signatures when reading real triangles; don't assume "negative = correlated noise" without checking the sign conventions first. |
| C (41 rows) | `split_closure` loop totals (forward vs reverse direction around the loop) are **equal to float precision on every readable case/sub-run** (41/42 readable). | **FORCED, confirmed**: the split closure loop's TOTAL telescopes algebraically to `sum(split_forward over A,B,C) + sum(split_reversed over A,B,C)`, independent of which pairing order or direction you sum in. Same disease as the two-witness clock (break C in that section): a quantity that looks like it encodes loop structure, but collapses to an order-independent sum. | The per-pair terms (`AB`, `BC`, `CA` individually) are NOT forced equal to each other and are the only place in the split closure where real loop-order information could live -- confirmed by checking the totals cancel while the individual terms (reported in the table below) do not. |
| D (0 rows, checked) | `closure_identity_ruler`: with A=B=C exactly (tripled witness), forward loop == reverse loop == `3 * arrow_stat(A)` to float precision, every case. Zero violations. | This is the one algebraic identity for the cross-witness arrow loop that **is** forced -- but only in the degenerate case of three identical witnesses. For genuinely distinct A, B, C there is **no known forced-zero identity** for the arrow closure loop; it is free to carry real information (see F below for how much). | The closure arithmetic itself is verified bug-free before reading anything into the real numbers. |
| E (21 rows, 7 cases x 3 parts, 0 failures) | `rotation_latin_square`: seat 1 (forward) and seat 3 (reference) effects come out **exactly equal** on every case/part. | **FORCED, confirmed, and explained**: seats 1 and 3 apply the *identical* function (forward, cutoff-1 part value) to the full witness set across the three firings, so their column means are the same set of three numbers in a different order -- the Latin-square decomposition cannot tell them apart. **A second identity found, NOT separately forced**: `seat_effect[1] (reversed) = -2 * seat_effect[0]` held on every case/part we checked, including **split**, where seat 1 and seat 2 are NOT related by any known algebra. This is **not** a physics finding -- it is pure arithmetic: once two of three column effects are equal, the three effects (deviations from a shared grand mean, equal group sizes) are forced to sum to zero, so the third is forced to `-2x` the other two automatically, regardless of what function produced it. **Flagged here explicitly so this identity is never mistaken for evidence that the split obeys a forced reversal relation -- it does not; the arithmetic of "effects sum to zero" would produce this ratio even from three unrelated random numbers with two of them equal.** | Only `firing_effect` and `witness_effect` (and the *residual*) in the Latin square decomposition carry information not forced by the design itself. |
| F (12 rows) | `control-vs-main magnitude`: on **6 of 7 cases**, `same_instrument_three_thirds` or `unrelated_record_in_place_of_C` gave an arrow-closure-loop or split-closure `AB`-term magnitude **at or above** the real triangle's own, for at least one metric. The **one case where neither control beat the main value**, on the arrow-closure-loop metric specifically, was **case i, three unrelated sources** (main 0.631 vs controls 0.183 and 0.312 -- both well below). | Same disease as the two-witness harness's central finding, now on closure quantities: controls built to NOT be a real three-witness-of-one-event signal routinely match or exceed the real triangle's magnitude. The one case that *didn't* collapse this way is notable precisely because it's the case that should look different from a real triangle (three genuinely unrelated sources) -- see the synthetic table below, this is the clearest candidate for separation the design has produced so far. | The raw size of either the arrow-closure or split-closure term is still not, by itself, a reliable discriminator case-by-case; it is only suggestive on the one case built to be obviously null. |
| G (1 row) | `alignment ruler`, triangle version: on case (g) -- the one built with mismatched sampling (C on a coarser grid) -- the three-cornered-hat's `any_negative` flag flips depending on alignment method: **native=False, block_average=True (barely: var_A=-3.2e-5), nearest=False, linear=False.** | Even among the three ALIGNED methods, the headline "did it go negative" flag is not stable -- one method's numerical noise floor crossed zero, the other two didn't, on the same aligned data. | The three-cornered hat's negative/non-negative call near zero is sensitive enough to alignment-method numerical noise that "any_negative" should never be read as a clean boolean without the actual variance magnitude and its sign stability across methods sitting beside it. |

No crashes, no exceptions, no unhandled NaN propagation on any of the 7 cases or their sub-runs.

## 1. The design

Reused verbatim from `darkwave_v1.py`: `run_formula_on_series`, `ratios_from_ladder`, `leftover_from_ladder`,
`core.arrow_stat`, `core.call_verdict`. New in `disco2.py` (not in `core.py` or `darkwave_v1.py`):
`cross_arrow_stat(X,Y,k)` -- the cross-witness generalization `<X_t^2 Y_{t+k}> - <X_t Y_{t+k}^2>`, which
reduces to `core.arrow_stat` when X is Y.

1. **CLOSURE** (one firing, three witnesses A,B,C of one event):
   - (a) **three-cornered hat**: `var(A-B)`, `var(B-C)`, `var(C-A)` solved algebraically for `var_A`,
     `var_B`, `var_C`. Negative solutions reported raw, never clipped.
   - (b) **arrow closure loop**: `cross_arrow_stat` summed `A->B->C->A` (forward) and `A->C->B->A`
     (reverse), at k=1, cutoff=1 only (no established cutoff-ladder identity exists yet for the cross
     term, so none was invented).
   - (c) **split closure loop**: the two-witness split sign error (`split_fwd(X) + split_rev(Y)`), summed
     the same way around the loop, both directions.
   - **Algebra done first** (see break rows D, C above): the only forced-to-a-fixed-value identity found
     is the degenerate A=B=C case for the arrow loop; the split loop's TOTAL (not its individual terms)
     is forced order/direction-independent. No cross-witness closure term is forced to exactly zero for
     three genuinely distinct witnesses.
2. **ROTATION** (three firings, a 3x3 Latin square): firing 1 seats (A,B,C), firing 2 seats (B,C,A),
   firing 3 seats (C,A,B). Seat 1 = forward, seat 2 = reversed, seat 3 = reference (same operation as
   seat 1, by design, as a label-artifact check). Decomposed `cell = mu + firing_effect + seat_effect +
   witness_effect + residual`, the standard Latin-square ANOVA solve (9 cells, 7 parameters, 2 residual
   d.o.f.). **Algebra done first** (see break row E): seat 1 and seat 3 are forced equal (identical
   operation on the same witness set); seat 2's effect is then forced to `-2x` seat 1's by the "effects
   sum to zero" arithmetic alone, for EVERY part, including split -- this is NOT evidence of a forced
   reversal relation for the split, it is forced by the shape of a 3-column effect decomposition with two
   equal columns, and would appear even on random unrelated numbers. What survives, and isn't forced:
   `firing_effect`, `witness_effect`, and the `residual`.
3. **Controls**, extended to three witnesses: alignment (block-average/nearest/linear, now chained
   pairwise A-B then (A,B)-C), same-instrument-different-event (A cut into three non-overlapping thirds,
   treated as a faux A/B/C), unrelated-record (C replaced by white noise of matched length), length
   (shortest-common/half/quarter), binary flag (all three witnesses checked).

## 2. Synthetic cases and headline numbers

| Case | 3-cornered hat: var_A / var_B / var_C (any negative?) | Arrow closure loop: fwd / rev | Split closure: AB / BC / CA (loop totals forced-equal, confirmed) |
|---|---|---|---|
| (g) 3 instruments, independent noise (C on coarser grid) | 4.7e-5 / 0.0288 / **0.876** (No) | -0.000104 / -0.00907 | -4.12 / -2.84 / 5.19 |
| (h) hidden common noise between A,B; C independent | 0.00205 / 0.00293 / 0.0481 (No) | -0.00530 / -0.00484 | -0.206 / 1.712 / -1.215 |
| (i) three unrelated sources | 1.799 / 1.487 / 1.145 (No) | **-0.631 / +0.474** | -12.30 / 10.46 / 0.193 |
| (j) one instrument (C) lagged 15 samples | 0.0137 / 0.00371 / 1.131 (No) | 0.0142 / -0.00576 | -0.660 / -1.895 / 0.995 |
| (k) one instrument (C) sign-flipped | 0.0194 / **-0.00082** / 2.155 (**Yes**) | 0.0376 / -0.0329 | -1.134 / -0.248 / -0.794 |
| (l) time-irreversible source (sawtooth) | 0.00687 / 0.00573 / 0.00639 (No) | **-0.192 / -0.193** | 0.497 / -1.898 / 0.009 |
| (m) time-reversible source (sine+noise) | 0.00853 / 0.0110 / 0.0104 (No) | **0.000295 / 0.0000231** | -1.738 / -2.464 / 1.048 |

(Full per-case tables, including the `same_instrument_three_thirds`, `unrelated_record_in_place_of_C`,
`length_variants`, and `alignment_ruler` sub-rows, and every split-closure AB/BC/CA value, are in
`triangle_synthetic_results.json`.)

## 3. Does closure + rotation separate real-source from unrelated/null cases, where two-witness could not?

**Partially, and only on one specific signature -- the arrow closure loop's absolute size -- not on the
three-cornered hat or the split closure, and not reliably once the controls are checked.**

- **The clearest positive result**: the arrow closure loop's magnitude for the **three genuinely
  unrelated sources (case i)** is 0.47-0.63, roughly **5-50x larger** than every case built around a
  single real shared source (g, h, j, k, m: 0.0001-0.04). Even better, this is the **one case (of
  seven) where neither null control (same-instrument-thirds, unrelated-record) matched or exceeded the
  real triangle's own value** -- everywhere else, at least one control did (break F). This did not exist
  in the two-witness version: there, the arrow's sign error was proven to collapse to a forced,
  order-fixed plain difference carrying no real information (break B/C in the two-witness section). Here,
  the CROSS-witness arrow loop is not forced by any known identity (break D confirms this only holds in
  the A=B=C degenerate case), and it is the one quantity in this whole exercise that cleanly separated a
  "real" case from the deliberately-null one.
- **It also shows something the two-witness arrow never could**: the **time-irreversible source (sawtooth,
  case l)** gives an arrow closure loop of magnitude **~0.19**, about **650x larger** than the
  **time-reversible source (sine, case m)** at **~0.0003**. The two-witness arrow part could not
  distinguish these at all (both were dominated by the forced-antisymmetric collapse). This is the single
  most interesting number in this delivery and the strongest argument for the triangle design: cross-
  witness arrow closure may be sensitive to the source's own time-reversal symmetry in a way no
  two-witness quantity here was.
- **But it does not hold up everywhere**: on 6 of the 7 cases (all except i), at least one null control
  (same-instrument segmentation or unrelated white noise standing in for a witness) produced an
  arrow-closure-loop or split-closure magnitude as large as or larger than the real triangle's own (break
  F) -- including, notably, **case l itself**: its `same_instrument_three_thirds` control gave **0.432**,
  *larger* than the real triangle's 0.192. So the irreversible-vs-reversible separation (l vs m) is real
  and large, but "is this number itself large" is not a safe standalone test without a same-instrument
  control run beside it every time, because splitting ONE irreversible-source record into three chunks
  can itself produce an even bigger number than three real noisy instruments reading it.
- **The three-cornered hat did NOT separate anything cleanly.** `var_C` was inflated in g, j (both ~0.9-1.1,
  driven by the coarser/lagged third witness, not by relatedness) and in i (the genuinely unrelated case,
  ~1.1-1.8 across all three) -- the unrelated case's variances are larger in an absolute sense but the
  *shape* (which witness gets the inflated variance) does not cleanly flag "these are unrelated" versus
  "one witness has worse instrument noise," which is exactly what the hat is suppose to distinguish and,
  per break B, is exactly where it got confused on the case built to test it.
- **The split closure's individual pairwise terms (AB, BC, CA) are large and noisy on every case**,
  real and null alike (magnitudes 0.2 to 12), with no visible pattern separating cases -- same disease as
  the two-witness split's raw cutoff-1 value.
- **Rotation's witness_effect (the one truly new, non-forced quantity on the split part) did not separate
  case i from the rest either** -- magnitudes across all 7 cases are the same rough order (0.01-2.3), no
  case stands out.

**Bottom line**: closure + rotation gives ONE real, non-forced signal that the two-witness design could
not produce at all -- the cross-witness arrow closure loop, which (a) is far larger for three unrelated
sources than for any single-source case, and (b) is far larger for an irreversible source than a
reversible one. That signal does not yet survive every control on every case, and every other triangle
quantity (the hat, the split closure, the rotation's witness effect) failed to separate anything cleanly
in this synthetic run. This is reported as what it is: a lead, not a result, and not run on anything real.

## 4. Real triangles to wire up (fetch only, do NOT run; `--real` still locked)

| Triangle | Witnesses | Status |
|---|---|---|
| GW170814 | LIGO H1, LIGO L1, Virgo | fetch from GWOSC, not yet wired |
| The sun | sunspot number, F10.7, Oulu neutron monitor | sunspots and F10.7 already loaded by darkwave_v1's world folders; Oulu already loaded too -- three-way loader not yet wired |
| Earth's carbon | Mauna Loa CO2, EPICA ice core (overlap), CH4 | all three already loaded individually by darkwave_v1; three-way loader not yet wired |
| Bell | Alice's clicks, Bob's clicks, sync channel (if the NIST files carry one) | Alice/Bob loaded (as `bell_nist_neighbors_diffpp`, two-witness only so far); whether a sync channel exists in the NIST files is unchecked -- open item |

`python3 out/disco2/disco2.py --real` still refuses (exit 2) without `out/disco2/REVIEWED.txt`, which does
not exist. The real-triangle loaders above are not implemented in this delivery, per instruction (fetch
only where needed, do not run the analysis).

## 5. Files

- `out/disco2/disco2.py` -- two-witness mode (`--synthetic`, unchanged) + new triangle mode (`--triangle`)
- `out/disco2/synthetic_results.json` -- two-witness results (unchanged, 173 breaks)
- `out/disco2/triangle_synthetic_results.json` -- triangle results, 421 breaks in `["breaks"]`
