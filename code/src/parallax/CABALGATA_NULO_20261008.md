# EL MODELO NULO -- the pipeline run on worlds where the truth is known

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_nulo.py`. **Reading only, no chip time.**
Wayfinder: shore up the data points, end the arguments before they begin.

## The objection this answers

> *"The product wins 36 of 37 DECIDED cells. You chose those cells by decidability, and decidability is
> computed from the same residuals as the verdict. That is selection bias, and your 97 percent is an
> artifact of the cut."*

**It cannot be answered by argument.** It is answered by running the pipeline on records where the truth is
known, with this record's own noise, and reading what the pipeline says.

## The design, written before the run

Three worlds, each built from the **real measured arms of every real cell**:

| world | construction |
|---|---|
| **MUNDO SUMA** | `y` forced to `b + z - 1` exactly, so the SUM is true |
| **MUNDO PRODUCTO** | `y` forced to `b * z` exactly, so the PRODUCT is true |
| **MUNDO NADA** | `y` forced to the midpoint, so NEITHER is true |

Each cell then gets **this record's own noise**: every arm's `lv` resampled inside its own measured shot
error, three reads per cell to match the real structure, plus the measured between-read excess (0.095 of
variance on coupled clocks, 0.000 on uncoupled -- la calibracion, same day) as a term common to the three
reads. Then EL PICNIC runs unchanged. 400 simulations per cell, 150 cells, 60,000 simulated cells per world.

**What each outcome would mean, stated in the script before it ran:**

- MUNDO SUMA near 50 percent product on decided -> the cut is innocent, the real figure is a measurement.
- **MUNDO SUMA high product -> the ruler manufactures the result and CUATRO falls today.**
- MUNDO PRODUCTO high and SUMA not -> the pipeline has the resolving power we claim.
- MUNDO NADA mostly ABIERTO -> the none is the pipeline reporting its own insufficiency.

## What it says

```
                                 ABIERTO   decided   product of decided
T = 2.0
  OBSERVED            wired       79.2%     20.8%     100.0%  (15/15)
  MUNDO SUMA          wired       66.9%     33.1%       6.4%
  MUNDO PRODUCTO      wired       67.0%     33.0%      93.0%
  MUNDO NADA          wired       87.9%     12.1%      45.9%

  OBSERVED            sight       96.2%      3.8%      33.3%  (1/3)
  MUNDO SUMA          sight       86.2%     13.8%      16.0%
  MUNDO PRODUCTO      sight       86.5%     13.5%      84.4%
  MUNDO NADA          sight       89.5%     10.5%      49.5%

T = 3.0
  OBSERVED            wired       81.9%     18.1%     100.0%  (13/13)
  MUNDO SUMA          wired       69.3%     30.7%       3.3%
  MUNDO PRODUCTO      wired       70.8%     29.2%      96.9%
  MUNDO NADA          wired       91.3%      8.7%      45.1%

  OBSERVED            sight       92.3%      7.7%      50.0%  (3/6)
  MUNDO SUMA          sight       92.9%      7.1%      14.7%
  MUNDO PRODUCTO      sight       93.0%      7.0%      87.8%
  MUNDO NADA          sight       95.5%      4.5%      48.2%
```

(These observed figures are the statedark-only subset -- 150 cells with all four arms present in all three
reads -- so 13 of 13 here rather than the 30 of 30 of the wider statedark-plus-spaced set. Within the subset
the observed product share is 100 percent at both thresholds.)

## Four readings

**1. The ruler does not manufacture the product. The selection-bias objection is dead.** In a world where
the sum is true by construction, the pipeline reports the sum on **94 to 97 percent** of the cells it decides.
Product share falls to 6.4 and 3.3 percent. **The cut is innocent, and the real figure is a measurement.**

**2. The real record behaves like MUNDO PRODUCTO and like nothing else.** Observed 100 percent against a
product-world 93 to 97, a sum-world 3 to 6, and a neither-world 45. There is no reading of the table in which
the real record resembles the sum-world.

**3. The uncoupled control lands on the neither-world, quantitatively.** Observed 33.3 and 50.0 percent
against MUNDO NADA's 49.5 and 48.2 -- and **not** against MUNDO PRODUCTO's 84.4 and 87.8. The control is not
merely "at a coin": it sits where a world with no mechanism in it predicts it should sit. **Nobody designed
that comparison; it fell out of the same run.**

**4. The ABIERTO rate is substantially predicted, and the residual is named.** The product-world predicts
67.0 and 70.8 percent against an observed 79.2 and 81.9 on coupled clocks. **So most of the cannot-tell rate
is the arithmetic of the record** -- but the simulation under-predicts it by about eleven points.

## Honest cuts

- **The eleven-point gap is ours, and here is where it comes from.** The simulation uses the **median**
  excess (0.095) for every cell, while the measured per-cell ratio has an interquartile range of 0.80 to
  1.33. A single median cannot carry that spread, so the simulation is quieter than the record and decides
  more often than the record does (33 percent against 21). **The excess share is therefore a floor, not a
  ceiling -- which reverses the direction of the caveat printed with la calibracion the same day.**
- The headline result is untouched by that gap: readings 1 and 2 are about the ruler's **bias**, not about
  the rate, and a quieter simulation makes a sum-world *easier* to detect, not harder.
- One chip, one layout family, 150 cells.
- The truth is imposed exactly in each world, so each is noiseless at its centre. A real record carries a
  real residual on top, which makes real cells slightly **easier** to decide than simulated ones -- and the
  record still decides less often, which is the gap above.

## What would break it

A world construction we have not tried in which the ruler reports a high product share without the product
being true. **The three built here do not do it**, and the one designed to try hardest -- MUNDO SUMA -- comes
back at 3 percent.
