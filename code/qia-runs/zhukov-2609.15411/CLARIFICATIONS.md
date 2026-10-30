# Clarifications, for Andrey Zhukov (30 October 2026)

## 1. The exact circuit on 24 October: [-8.18, -0.17] against [-8.89, +0.54]

Both files come from the same code. `29oct/date_reading.py` imports `24oct/zhukov.py` unchanged. The two numbers differ because the between-job spread is treated differently.

**results_24oct.text** follows reading (c) of the plan committed before the 24 October jobs (`24oct/PLAN_ZHUKOV.md.text`, function `combine` in `zhukov.py`). The half-width is the larger of two terms, not their sum in quadrature:

| Term | Formula | Value (deg) |
|---|---|---|
| Counting, both sides | 2.576 x sqrt(0.728^2 + 1.375^2) | 4.006 |
| Between jobs | t(0.975, 3 dof) x sd / sqrt(4) = 3.182 x 1.956 / 2 | 3.113 |

The counting term is larger, so the half-width is 4.006 and the reading is -4.178 +- 4.006 = [-8.18, -0.17]. Per-job values: -2.47, +0.18, +0.68, -3.31. Your September value is +2.947 with standard error 1.375.

**readings_date.json** stores our side alone. Its `oct24_half` of 3.113 is the same rule without your error: max(2.576 x 0.728 = 1.875, 3.113) = 3.113, which is the between-job term. Treating 3.113 as a 99% normal half-width and adding your 1.375 in quadrature gives your [-8.89, +0.54].

Your question finds two weak points in our rule. Taking the larger term drops the between-job spread whenever counting dominates. And the between-job term is a 95% t interval, not 99%. With all three terms in quadrature at 99% (ours 0.728, between jobs 1.956 / 2 = 0.978, yours 1.375), the half-width is 4.733 and the interval is [-8.91, +0.55]. A t factor for 3 degrees of freedom on the between-job term widens it further. Either way the interval includes zero.

So the 24 October BELOW for the exact circuit depends on the combination rule and does not survive a stricter one. Our email line that "the exact circuits stay put" was stronger than the readings support. Every rule we tried gives the following:

| Exact circuit minus September (deg) | Committed rule | All terms in quadrature, 99% |
|---|---|---|
| 24 October | -4.18 [-8.18, -0.17] | -4.18 [-8.91, +0.55] |
| 29 October | -2.47 [-6.40, +1.47] | -2.47 [-6.51, +1.58] |

| Strang r = 8 minus September (deg) | Committed rule | All terms in quadrature, 99% |
|---|---|---|
| 24 October | -93.09 [-100.78, -85.41] | -93.09 [-100.79, -85.40] |
| 29 October | -55.67 [-63.22, -48.12] | -55.67 [-63.71, -47.63] |

The Strang intervals barely change between rules, because counting dominates there and the four jobs agree closely (sd 0.34 on 24 October).

## 2. S0 MM prep0: intervals exclude zero, labelled CONSISTENT

S0 is not scored against zero. The rule (`outcome_band` in `zhukov.py`, fixed in the plan before the jobs) compares the 99% interval with a tolerance band of +-0.041 around zero. The value 0.041 is one minus the worst control minimum you publish (0.959). CONSISTENT means the whole interval lies inside the band. ABOVE or BELOW needs the interval entirely beyond +0.041 or -0.041. Anything else is CANNOT_TELL.

| | 24 October | 29 October |
|---|---|---|
| S0, qubit 16, prep 0 | -0.0165 [-0.0282, -0.0047] | -0.0121 [-0.0197, -0.0046] |
| S1, qubit 16, prep 1 | -0.0008 [-0.0130, +0.0113] | -0.0030 [-0.0142, +0.0081] |
| SC, qubit 3, prep 0 (control) | +0.0001 [-0.0010, +0.0013] | -0.0002 [-0.0010, +0.0005] |

Both S0 intervals exclude zero and both sit inside +-0.041. So on both nights the double-read statistic on qubit 16 after a preparation in 0 is small and negative, about -0.012 to -0.017. Against zero alone both would read BELOW. The qubit-3 control reads zero on both nights, so the effect belongs to qubit 16, not to back-to-back reads in general. A negative value is the sign a state already wrong before the first read would give. There is a component of that kind on qubit 16, below the threshold we set for a call.

Our files should have printed the band and the fact that the interval excludes zero beside the label. The plan says CONSISTENT "rules out a persisting state". With the band, it rules out one larger than 0.041, not any. The line in our write-up that the double-read and delay arms "found nothing to separate" should have said this.

Heuremen LLC
