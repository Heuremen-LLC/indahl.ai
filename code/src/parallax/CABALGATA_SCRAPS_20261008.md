# THE SCRAPS -- what was already paid for, and never read

Bones, 8 October 2026. Wayfinder: *"we dropped like ten big beans on qubits, go through the scraps and see
if you can use those first."* Reading only. **No chip time spent; the 59 seconds remaining in the rolling
window were not touched.**

## The inventory

Nine fired runs on disk carry the closure arms, in three read-sets:

```
ibm_kingston     97 circuits   k = 1, 2, 3, 4, 6, 9    reads 1191-1193   (statedark)
ibm_kingston     72 circuits   k = 1, 2, 4             reads 1201-1203   (spaced)
ibm_pittsburgh   46 circuits   k = 1, 2, 4             reads 1281-1283   (meilong)
```

## The scrap that mattered

**The statedark runs carry the full closure at k = 1, 2, 3, 4, 6, 9. The first pass read only k <= 4.**
The window reading, and every honest-ruler count built on Kingston, was drawn on a quarter of the range we
had already bought. Extended to the whole range, at zero cost:

```
                    was (k<=4)              now (k<=9)
T=2  wired decided  27/168   product 26/27  37/216   product 35/37    p 4.2e-07 -> 1.0e-08
T=3  wired decided  21/168   product 21/21  30/216   product 30/30    p 9.5e-07 -> 1.9e-09
T=3  sight decided  10/182   product  5/10  16/234   product  8/16    exactly the coin, p 1.000

decidability  T=2  wired 37/216 = 17.1%  sight 14/234 = 6.0%  odds 3.25  Fisher p 0.00028
              T=3  wired 30/216 = 13.9%  sight 16/234 = 6.8%  odds 2.20  Fisher p 0.019

POOLED with Pittsburgh, T=3, decided wired cells:  product 36/37 = 97.3%   p 5.5e-10
```

**Ten more decided cells, nine more to the product, and the control landed on exactly 50 percent with
sixteen cells.** A control sitting dead on the coin with more data is the best evidence available that the
rebuilt ruler does not lean.

## And the window reading survives the wider range

The reason the extension was run at all was that "flat across the window" had been declared on k <= 4.
Over the full range it is still flat: slope -0.0133 and -0.0182 per look across k = 1 to 9, spread 0.167 and
0.250. **The earlier conclusion holds on 2.25 times the range.** Reported because the correction could as
easily have gone the other way.

### One thing the wider range showed that the win-rate ruler could not

```
statedark wired |1>   k=1   SUM 0.0806  PROD 0.0716   |y-1| 0.1359
                      k=9   SUM 0.2130  PROD 0.1021   |y-1| 0.6506
```

The sum's error nearly triples across the window while the product's barely moves. **This is not a finding.**
By the identity `SUM err = PROD err + (b-1)(z-1)`, a growing deviation inflates the sum error by
construction, and `|y-1|` grows from 0.136 to 0.651 across the same range. It is the lean, seen again, and it
is logged here so nobody later reads it as a result.

## The second scrap, parked and named

Runs 1291-1293, ibm_kingston, fired 7 Oct after the maker published a **new calibration**: arms
`D0 K KR T0 T10 T20 T30 F0 F1` at k = 1, 2, 4. **No `D1`/`S1`/`DH`/`SH`, so no closure** -- but `K` beside
`KR` is the same looks in **index order against reversed measure order**. That is a per-qubit send-order
control on the same clocks, across a calibration boundary, and it bears directly on a standing order of this
house (read every anomaly with a per-qubit send-order trace). **Unread. Named here so it is not lost twice.**

## What was not bought, and is still open

A call was written and hashed for a fourth statedark read to decide whether the per-cell scatter is read
noise or drift between sessions -- the question that decides whether "more reads" is the right next step at
all. **It was not fired.** The call is kept, marked VOID with the reason, at
`darkwave_disco/calls/FOURTH_READ_CALL_20261008.txt`. **The drift question is unbought and unanswered.**
