# THE SECOND SCRAP -- send order, across a calibration boundary

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_orden.py`. Reading only, no chip time,
**no guess written before the run.** Runs 1291-1293, ibm_kingston, fired 7 Oct after the maker published a
new calibration, never read until now.

`K` is the looks taken in index order. `KR` is **the same looks in reversed measure order**, on the same
clocks, in the same job. That is a per-qubit send-order control, which is a standing order of this house.

## 1. The send order does not move the clocks

```
pooled, median z(K - KR) across the three reads     wired 0.92     sight 0.73
null reference (the closure residual, same chip)             ~1.01
share of cells with z > 2                           wired 0.11     sight 0.08
per cell at T = 3                     IMPORTA  wired 1/36     sight 0/39
```

**At or below the null on both.** The send-order difference is what pure scatter produces and nothing more.
The standing worry is addressed, negatively, at the pooled level.

**But it is not bounded tightly per cell.** The equivalence verdict NO IMPORTA came back on 0 to 2 cells of
75 at every threshold and every bound. We can say the order effect is not visible; we cannot say it is small.

## 2. The number that explains the whole morning

```
within-job differential standard error    wired 0.0549     sight 0.0462
the look's own effect, median |K - 1|     wired 0.1409     sight 0.1319
                                   ratio        0.36            0.26
```

**The per-cell noise on this chip is a quarter to a third of the look's own effect.** That is measured here
on a quantity that should be null, independently of any closure, and **it is the direct reason 84 to 99
percent of cells came back ABIERTO this morning.** Not an excuse for the ABIERTO rate -- the cause of it,
with a number.

**Correction to our own first framing:** the median `|K - KR|` of 0.0505 was initially read as "the order
effect is a third of the look." It is not an effect. `median |mean(d)| / median sem(d) = 0.92`, so that
0.0505 **is the noise floor expressed in units of the look.** The quantity and the scatter are the same size
because the quantity is the scatter.

## 3. The carriers held across the calibration

```
clocks passing the quality gates BEFORE the new calibration (statedark 1191-1193)   25
clocks passing the quality gates AFTER  the new calibration (carriers  1291-1293)   25
in both 25   |   only before 0   |   only after 0   |   overlap 1.00
```

**What is construction and what is measurement.** Both scripts use the same role seed and the same chip
configuration, so `far`, `emitters`, `n` and `witness_of` are **byte-identical by construction** -- verified,
not assumed. What is measured is which of those 61 candidates **pass the data-dependent gates**
(`|T0| > 0.15`, separation `> 3`) in each session. All 25 that passed before passed after. Perfect overlap.

## 4. The drift question: an attempt that failed, printed as a failure

`K - KR` is a within-job difference, so common-mode motion between jobs cancels in it. The closure residual's
standard error across three reads carries whatever moved between those jobs. Comparing the two looked like it
would separate drift from read noise for nothing:

```
median sem(closure residual), statedark+spaced    wired 0.0784    sight 0.0691
median sem(K - KR),           carriers            wired 0.0549    sight 0.0462
                                           ratio        1.43            1.50
```

**It does not work, and the reason is arm counting.** `rp = S1/D0 - (K/D0)(D1/D0)` is built from four arms;
`d = K/D0 - KR/D0` from two, with the shared normaliser partly cancelling. Roughly twice the independent
arms predicts a ratio near `sqrt(2) = 1.41`. **The observed 1.43 and 1.50 are what arm counting alone gives,
so the comparison carries no information about drift.**

**The drift question remains unbought and unanswered**, and no dataset on disk can answer it: it needs two
sessions of the *same* closure arms, and we hold one session of each. Until it is answered, the 36-of-37
closure verdict rests on a scatter whose composition we have not characterised.

## What lands it

One more read of the statedark arms, in a later session. 45 seconds. It was written, hashed and **not fired**
on 8 October; the call is kept and marked VOID with the reason at
`darkwave_disco/calls/FOURTH_READ_CALL_20261008.txt`.
