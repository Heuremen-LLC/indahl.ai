# LA CABALGATA ON A SECOND CHIP -- the call scored, and the ruler on the rack

Bones, 8 October 2026. Reading only. Runs 1281-1283 were fired 7 October, before any of this code existed.
Scripts: `parallax/out/qubit_fifth_run/cabalgata_pitt.py`, `cabalgata_potro.py`.

## The call, as it was written

`darkwave_disco/calls/MEILONG_PITT_CALL_20261007.txt`, written 7 Oct **before any shot**, having first
checked no run 1281-1283 existed. Three readings printed in advance:

- **P1 IT TRAVELS** -- wired product share above the coin beyond its binomial width, sight control at the coin.
- **P2 IT DOESN'T** -- wired at the coin. Kingston's composition was that chip's.
- **P3 BOTH / MOVING** -- above the coin on one state and not the other, or by read; **or the sight control
  leaves the coin too, in which case the closure ruler itself leans.**

Kingston's standing number (section 450): product beat sum on 573/864 wired cells (66%, p 5e-22), sight
control 341/702 (49%).

## Scored, by the call's own arithmetic, goalposts unmoved

```
wired |1>    product   68/117 = 58.1%   p 9.57e-02     by window  k1:46%  k2:62%  k4:67%
wired half   product   62/117 = 53.0%   p 5.79e-01     by window  k1:41%  k2:46%  k4:72%
sight |1>    product   72/126 = 57.1%   p 1.30e-01     by window  k1:52%  k2:71%  k4:48%
sight half   product   74/126 = 58.7%   p 6.09e-02     by window  k1:55%  k2:62%  k4:60%

ALL wired    130/234 = 55.6%   p 1.02e-01      Kingston said 66%
ALL sight    146/252 = 57.9%   p 1.39e-02      Kingston said 49%

by clock     wired 17/26  p 0.1686        sight 20/28  p 0.0357
```

**P3. And in the worst of its three forms: the sight control left the coin, and left it ABOVE the wired.**
The wired number is at the coin on both states and by clock. By the call's own words the closure ruler leans,
and the wired number cannot be read as a composition until that is accounted for.

## El Potro: the ruler as an object

Algebra before data:

```
SUM error     = |(y-1) - (b-1) - (z-1)| = |y - b - z + 1| = |(y - b z) + (b-1)(z-1)|
PRODUCT error = |y - b z| = |r|
PRODUCT wins  iff  |r| < |r + c|     with   c = (b-1)(z-1)
```

**The test never compared two models.** It asks whether the cross term is large next to the residual -- and
the cross term grows whenever both corners sit far from 1, for any reason, physics or noise. Measured:

```
                          KINGSTON                PITTSBURGH
cross/residual lowest     51.9%                   49.0%
                          48.6%                   56.1%
                          54.3%                   51.0%
                          46.2%                   61.2%
cross/residual highest    83.3%                   67.3%
```

**The ruler leans, on both chips, exactly as the algebra says it must.** That was never flagged before today
and it sits under every products-versus-sums count the house has made, Kingston's 66% and the 78.3% of
8 October included.

## Does the wire survive the lean?

Wired against sight **inside** bands of cross/residual, so the ruler's own bias is held fixed:

```
KINGSTON    q1 -1.1   q2 +12.3   q3 +17.7   q4 +14.3   q5 +14.2 pts
            POOLED  wired 334/504 = 66.3%   sight 263/546 = 48.2%   diff +18.1 pts

PITTSBURGH  q1 -21.0  q2 -18.4   q3  -1.6   q4  -0.3   q5  +5.8 pts
            POOLED  wired 132/236 = 55.9%   sight 147/254 = 57.9%   diff  -1.9 pts
```

**Kingston survives the control. Pittsburgh is nothing.** +18.1 points against -1.9.

## And the rescue is dead

The obvious rescue is that Pittsburgh's Galleta is weaker, so there was less to compose. It is not:

```
wired |z-1| / sight |z-1|     Kingston 0.1645 / 0.0723 = 2.3x     Pittsburgh 0.1472 / 0.0700 = 2.1x
```

**The Galleta is present on Pittsburgh at the same wired-against-sight contrast, and the product advantage
still is not.** The rescue is unavailable. Not taken.

## Where this leaves the morning's reading

El Barrido de Ventanas (8 Oct) read the base leg as **moving with the coupling** -- wired 78.3%, sight 51.2%,
p 0.0002, on Kingston. That reading is:

- **not withdrawn.** It survived a control it was never built to pass: matched on the ruler's own bias, the
  Kingston wired/sight gap is still +18.1 points.
- **one chip, with a failed replication on the chip its own call named.** By the house's own rule -- a thing
  earns its weight by holding on a chip it was not read on -- **it did not earn its weight.**

Both of those are true at once and neither cancels the other. The composition does not travel.

## What lands it next

A third chip, Fez, in the same layout; and separately, a closure ruler that is not the cross term in disguise
-- compare the product against the sum **at matched cross/residual by construction**, or score the residual
itself rather than which of two errors is smaller. The present ruler cannot answer the question it was
built for.
