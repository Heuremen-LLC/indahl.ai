# EL PICNIC -- the closure ruler that can say it cannot tell

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_picnic.py`, run on both chips. Reading only.

## Why

Wayfinder, 8 Oct: *"envision a ruler chasing a smaller ruler chasing one smaller than that with each one
thinking it has the best way to measure, at some point we all have to stop and reflect, maybe picnic."*

The regress is real and this house walked three steps of it in one morning: the closure ruler, the ruler
that tested it, the matched control that tested that. **It has a stopping condition, and the condition is
not fatigue.**

> A ruler that can only say A or B must be chased by another ruler.
> A ruler that can say **I cannot tell** terminates the regress, because it can report its own insufficiency.

That is **EL PICNIC**. It is the same fix as the witness corner of this morning, and it is why La Cabalgata
carries GUARDADO / CAIDO / ABIERTO instead of two outcomes. Here it is applied to La Cabalgata's own ruler.

## The old ruler, as an equation

    y - b - z + 1  =  (y - b z) + (b-1)(z-1)
    SUM error      =  PRODUCT error  +  the cross term

The old verdict was `|r| < |r + c|` with `c = (b-1)(z-1)`. **It never compared two models.** It asked whether
the cross term was large next to the residual, and the cross term grows whenever both corners sit far from 1
for any reason at all. Win rate climbs with `c/r` on both chips (Kingston to 83 percent).

## The new ruler -- each model against the noise, never against the other

    per read i    rp_i = y_i - b_i z_i              rs_i = y_i - b_i - z_i + 1
    per cell      zp = |mean(rp)| / sem(rp)         zs = |mean(rs)| / sem(rs)

    GUARDADO   zp < T and zs >= T      the product is the closure
    CAIDO      zs < T and zp >= T      the sum is the closure
    ABIERTO    both, or neither        LA NADA. Carried whole, never scored.

## What it says

```
                 cells   GUARDADO      CAIDO      ABIERTO        decided    product of decided
KINGSTON T=2
  wired            168   26 (15.5%)   1 (0.6%)   141 (83.9%)     16%        26/27 =  96%  p 4.2e-07
  sight            182    5 ( 2.7%)   4 (2.2%)   173 (95.1%)      5%         5/9  =  56%  p 1.0
KINGSTON T=3
  wired            168   21 (12.5%)   0 (0.0%)   147 (87.5%)     12%        21/21 = 100%  p 9.5e-07
  sight            182    5 ( 2.7%)   5 (2.7%)   172 (94.5%)      5%         5/10 =  50%  p 1.0
PITTSBURGH T=2
  wired             78    5 ( 6.4%)   3 (3.8%)    70 (89.7%)     10%         5/8  =  62%  p 0.73
  sight             84    1 ( 1.2%)   0 (0.0%)    83 (98.8%)      1%         1/1
PITTSBURGH T=3
  wired             78    6 ( 7.7%)   1 (1.3%)    71 (91.0%)      9%         6/7  =  86%  p 0.125
  sight             84    0 ( 0.0%)   1 (1.2%)    83 (98.8%)      1%         0/1

BOTH CHIPS, wired, T=3, decided cells only:   product 27/28 = 96.4%   p 2.2e-07
```

## Five readings, and the first one is the biggest

**1. Most of the record cannot tell. 84 to 99 percent of every cell is ABIERTO.** The old ruler hid that by
forcing a verdict on every cell. This is the honest state of the data and it is the first finding.

**2. A ruler that forces a verdict manufactures sample size.** Pittsburgh's 234 wired cells looked like 234
data points at p 0.102 -- a clean-looking null. Only 7 or 8 of them carry information. **The "failed
replication" of this morning was substantially a power failure that the old ruler dressed as a null.**

**3. Where the record can tell, the product wins on wired clocks, and it is not close.** 27 of 28 decided
wired cells across both chips, 96.4 percent, p 2.2e-07. Kingston alone at T=3 is 21 of 21.

**4. The sight control sits at the coin on the honest ruler.** 5/10 and 0/1. The old ruler had the sight
control *off* the coin on Pittsburgh at p 0.0139, which is what told us it leaned. **The new ruler fixed its
own control.** That is the strongest evidence that the lean is gone.

**5. Decidability is itself a wire effect, and it TRAVELS.** The first thing all morning that has.

```
decidable   Kingston T=2   wired 27/168 = 16.1%   sight  9/182 = 4.9%   odds 3.68   Fisher p 0.00069
            Kingston T=3   wired 21/168 = 12.5%   sight 10/182 = 5.5%   odds 2.46   Fisher p 0.024
            Pittsburgh T=2 wired  8/ 78 = 10.3%   sight  1/ 84 = 1.2%   odds 9.49   Fisher p 0.015
            Pittsburgh T=3 wired  7/ 78 =  9.0%   sight  1/ 84 = 1.2%   odds 8.18   Fisher p 0.029
```

A wired clock is two to nine times more likely to produce a decidable closure, **on both chips**, in the same
direction, at p < 0.03 each. A sight clock has no Galleta, so there is nothing to decide, so it does not
decide. The mechanism and the measurement agree.

## Honest cuts

- **Three reads per cell is two degrees of freedom.** The sem is wide, which is why ABIERTO is most of the
  record. The thinness is reported, not worked around.
- **The complex sem's null distribution is not exactly normal**, so T = 2 and T = 3 are stated side by side
  rather than converted to a p-value per cell. The verdicts are stable between them, which is the point of
  printing both.
- **28 decided wired cells is a small number**, and they are not fully independent -- a clock contributes
  cells at several windows and states.
- **Decidability depends on the threshold**, and the wired/sight odds ratio moves with it (3.68 to 2.46 on
  Kingston). The direction does not move.

## What lands it

More reads per cell, not more cells -- the limit is `sem`, and `sem` falls as `1/sqrt(reads)`. Six reads
instead of three would roughly halve it and move cells out of ABIERTO. **That is the one thing worth chip
time here**, and it is the opposite of what the old ruler would have asked for.
