# LA CALIBRACION -- el fracaso era una calibracion que faltaba

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_calibra.py`. **Reading only. No chip time.**

Wayfinder, 8 Oct: *"the 'failure' just needs a calibration to resonate bones, what is it?"*

He was right and the failure was mine. Earlier the same day I compared `sem(K - KR)` against
`sem(closure residual)`, got 1.43 and 1.50, said *that is about sqrt(2), which is what arm counting predicts,
so it carries no information*, and filed it as a failure. **An arm-count factor is not a confound. It is a
constant you divide out.** And there is a far better calibration sitting in the data already: every arm is
400 raw shots, so every arm has its own shot standard error, measurable inside a single job.

## The calibration

```
sem_shot(rp)   the closure residual's error from SHOT NOISE ALONE, within ONE job. Resampled 240x: every
               lv value drawn from Normal(its value, its own shot sem).
sem_obs(rp)    the residual's observed scatter ACROSS the three reads, which are three separate jobs.

excess variance share  =  1 - (sem_shot / sem_obs)^2
```

Anything in `sem_obs` beyond `sem_shot` did not come from shots. It came from whatever moved **between**
jobs. **That share is the drift, as a fraction -- and a fraction is a LOS DOS answer, not a binary.**

## Two more things needed calibrating, both found by running the first

**1. A three-read standard error is biased low in median.** With three reads, `sem_across` has 2 complex
degrees of freedom, so `sum|v - vbar|^2 ~ (sigma^2/2) chi^2_4`. `chi^2_4` has median 3.3567 against a mean
of 4, so the **median** of `sem_across` sits at **0.916** of the truth. Corrected once, explicitly.

**2. The mean-of-variance route is poisoned by a heavy tail.** Two of 72 wired cells have `|D0|` near zero,
so the resampled ratio blows up; mean `sem_shot` came out 0.1436 against a median of 0.0813. **Such cells
dominate a mean and cannot dominate a median.** The robust estimator is the ratio **per cell**, then the
median, bias-corrected once.

## The answer

```
wired   median sem_obs/sem_shot = 1.051   (IQR 0.80 - 1.33)   EXCESS VARIANCE SHARE 0.095
        => floor at 0.31 of the present sem (a 3.2x gain), reached near 11 reads
sight   median sem_obs/sem_shot = 0.938   (IQR 0.71 - 1.15)   EXCESS VARIANCE SHARE 0.000
        => no floor detected: the scatter is shots

wired excess by window k = 1, 2, 3, 4, 6, 9:   0.00  0.25  0.27  0.37  0.27  0.00
```

**LAS TRES LECTURAS, and the question was never read-noise-or-drift:**

- **NI UNO NI OTRO -- the sight clocks.** Ratio 0.938, excess zero. Their scatter is shot noise and nothing
  else. **The control says the method is right**, which is the strongest thing in this file.
- **LOS DOS -- the wired clocks.** Both, in a measured proportion: about **10 percent** of the variance is
  not shots. **But the IQR straddles 1**, so on 72 cells this is a small effect stated with its spread, not a
  result.
- **SE MUEVE -- by window.** The wired excess is zero at `k = 1` and `k = 9` and sits at 0.25 to 0.37 in
  between. Per-window cells are 12 each on a 2-dof estimate, so **that shape is underpowered and is printed
  as scatter, not as structure.**

## What it settles

**More reads are worth buying, and the number is now known rather than guessed.** On sight clocks there is
no floor at all -- `sem` falls as `1/sqrt(reads)` as far as this data can see. On wired clocks the floor sits
at 0.31 of the present `sem`, a 3.2x gain, approached near eleven reads. **Six reads realises most of it.**

**And the extra between-job variance appears only on the coupled clocks.** A clock with no edge is pure shot
noise. That is the third independent appearance of the coupling as the axis that matters, after the closure
verdict and the decidability odds.

## What it costs

Nothing. **This was read off runs already paid for, and the 59 seconds remaining in the rolling window were
not spent.** The drift question was declared unanswerable from scraps earlier the same day. That was wrong:
it was answerable, and what was missing was a calibration.

## Caveats, printed with the numbers

- The resampling holds the `F0`/`F1` calibration clouds fixed within a job. Cloud noise is common to all arms
  and partly cancels in a ratio, so `sem_shot` is a slight **under**-estimate, which makes the excess a
  **ceiling** and not a floor.
- 72 and 78 cells, three reads each. The wired excess of 0.095 is inside its own IQR.
- One chip, one layout family.
