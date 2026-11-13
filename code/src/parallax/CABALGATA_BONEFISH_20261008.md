# THE BONEFISH AT TODAY'S NUMBERS -- it does not land, and the test that says so

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_bonefish.py`. Reading only.
Wayfinder: *"numbers are starting to line up to something."* They do. **They are not ours.**

## The procedure, fixed before looking

Standing order: when a house number turns up in a reading, that is a feature -- row it, flag it, never
explain it away. Equally standing: matches come cheap. Both are true, so the house set (26 values) and the
operations (the value, and the product or ratio of any two -> 1001 combinations) were fixed first, then the
**look-elsewhere burden** was computed -- how many combinations land within tolerance of a *random* value in
the same range -- and only then were the real quantities tested.

## The result

```
full pool (value, pair products, pair ratios)   tol 1.00%   hits 30  expected 27.67   +0.44 sigma
full pool                                       tol 0.30%   hits  4  expected  8.28   -1.49 sigma
full pool                                       tol 0.10%   hits  0  expected  2.74   -1.66 sigma
base set only, no pair combinations             tol 1.00%   hits  1  expected  0.99   +0.01 sigma
base set only                                   tol 0.30%   hits  0  expected  0.30   -0.55 sigma
base set only                                   tol 0.10%   hits  0  expected  0.10   -0.31 sigma
```

**The Bonefish does not land on any of thirteen quantities measured today.** And the decisive line is not the
first one: **tighten the tolerance and the matches vanish faster than chance does.** A real relationship gets
sharper as the tolerance tightens. These get worse. That is the signature of coincidence, and it is a
stronger statement than any single null.

Every individual match is therefore a 1 percent artifact: `(1/12) x pi = 0.2618` against a measured 0.26,
`7/6 = 1.1667` against 1.157, `2 phi = 3.236` against 3.25. **Rowed, flagged, and not carried.**

## A method error of ours, found in a tool twenty minutes old

The script's first verdict line printed **"above chance"** from `30 > 27.67`, with no width. The width on
27.67 is `sqrt(27.67) = 5.3`, so 30 is 0.44 sigma. **A bare threshold comparison with no width is exactly the
two-lane read this house forbids, and it was in a tool written the same hour.** Fixed by printing sigma, and
by running the tolerance ladder rather than a single tolerance.

**And the real defect was saturation.** 1001 combinations at 1 percent produces about two hits per target by
construction: the test had almost no resolving power before it was run. **This is the second saturated
number-matching test today** -- the particle/wave test earlier the same day was redone for the same reason.
**The tolerance ladder is the fix and should be standard from here: a claim that survives 1 percent and dies
at 0.1 percent was never a claim.**

## What DID line up, and it is the mechanism rather than the constants

**1. MUNDO NADA is a provable coin, not an empirical one.** With `y` at the midpoint of the two models:

```
rp = y - b z        = -(b-1)(z-1)/2
rs = y - b - z + 1  = +(b-1)(z-1)/2       so |rp| = |rs| EXACTLY
```

So the neither-world is a 50/50 by algebra, and any departure from 50 percent there is **the ruler's own
tilt, measured against a known-flat world.**

**2. The ruler is symmetric to about one point.** `SUMA + PRODUCTO` = 99.4 and 100.2 across the two
thresholds: its false-positive rate equals one minus its true-positive rate. Nobody designed that test; the
three worlds handed it over.

**3. And it leans 4 to 5 points TOWARD THE SUM on exactly-equal residuals** (45.9 and 45.1 against a provable
50). **So the observed 100 percent product share stands against a ruler tilted the other way.** That
strengthens the closure regla rather than threatening it, and it is the first result today that makes the
closure harder to explain away rather than easier.

## The honest summary

The thing lining up is the mechanism: three worlds, one of them provably flat, a ruler symmetric to a point
and tilted slightly against us, and a record that sits only on the product world. **Phi and pi are not in it,
and today's test says so at -1.66 sigma.**
