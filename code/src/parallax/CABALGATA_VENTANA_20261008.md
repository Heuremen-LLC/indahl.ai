# EL BARRIDO DE VENTANAS -- La Cabalgata against the window

Bones, 8 October 2026. Kingston, `parallax/out/qubit_fifth_run/cabalgata_ventana.py`. Reading only;
nothing fired. No guess written before the run.

## The question

Ligera places **La Cabalgata** (ex-Meilong) on the base leg of El Triangulo de la Luz: it is the closure
that puts a look's two halves back together, the phase it pushes (EL GIRO) and the hand it blurs (EL
CONTEO), and those are the triangle's two lower corners. The base-leg claim had three readings and exactly
one of them carried a test:

- **NEITHER** -- the particle/wave split was chosen by whoever built the instruments, not found.
- **BOTH** -- a reading can only be a count or a turn, so the two lanes are one lane.
- **MOVING WITH EL DELTA** -- the split lives where the measurement window sits against the period, so the
  base leg is a function of the window and moves when the window does. **Testable, and tested here.**

`k`, the number of looks folded into one reading, is the window. `meilong_closure.py` already closed
BLOOM x BISCUIT into BOTH per clock, per state, per `k` -- and then took medians **across** `k`, which hides
exactly what Ligera asks. This run never pools `k`.

## 1. The moving reading is dead

Per cell, share where the PRODUCT closes tighter than the SUM, by window, eight families:

```
8 families | slope median -0.0047 per look | 4 up, 4 down | spread median 0.208
```

Four up, four down, slope a twentieth of a percent per look. **That is what flat looks like.** The base leg
does not move with the window. One of three readings falls, and it is the only one that had a test.

## 2. What came out instead, unasked: it moves with the WIRE

Per clock -- the honest unit, because the same twelve clocks reappear at every `k` -- a clock wins if the
product closes tighter at most of its windows:

```
statedark  wired |1>    clocks 12 (ties 1)   product wins 10/11   p 0.0117
statedark  wired half   clocks 12 (ties 1)   product wins 10/11   p 0.0117
statedark  sight |1>    clocks 13 (ties 7)   product wins  4/6    p 0.6875
statedark  sight half   clocks 13 (ties 2)   product wins  6/11   p 1.0000
spaced     wired |1>    clocks 12 (ties 0)   product wins  8/12   p 0.3877
spaced     wired half   clocks 12 (ties 0)   product wins  8/12   p 0.3877
spaced     sight |1>    clocks 13 (ties 0)   product wins  6/13   p 1.0000
spaced     sight half   clocks 13 (ties 0)   product wins  6/13   p 1.0000

wired   product wins 36/46 = 78.3%   two-sided vs a coin  p 0.0002
sight   product wins 22/43 = 51.2%   two-sided vs a coin  p 1.0000
```

**A sight clock is a coin. 51.2 percent, p = 1.0000.** The product has no advantage there at any window.

**And the mechanism was already in the record.** La Galleta is static ZZ **on the wire only** -- measured
7 Oct, linear in hold time, half for a superposed neighbour, **zero on clocks with no edge** (ledger
section 429). So on a sight clock there is no second half to multiply. La Cabalgata has nothing to compose,
and a product cannot beat a sum when one of its factors is one.

**La Cabalgata's base leg exists where the two corners are physically coupled.** Not everywhere, and not
as a property of the window.

## 3. The third reading, in a form none of the three lanes had

The question was asked as structure-or-artifact-or-window. The answer is none of those three:
**the base leg moves with the coupling.** It is structural *where there is a wire*, and absent *where
there is not*, and the window never enters. That is a fourth reading, and the run put it there.

## Honest cuts

- **The cell-level p-values are on repeated measures.** The same twelve or thirteen clocks reappear at every
  `k`, so the first pass's cell counts are not independent. Section 2 is the test that stands.
- **Multiple looks.** The first pass flagged 7 of 29 cell-rows at p <= 0.05 where about 1.5 are expected by
  chance. Four of the seven are one family -- statedark / wired / |1> -- at all four of its windows.
- **The wired/sight pool is not fully independent either.** A clock appears in up to four families across
  the two layouts and two states. Read 78.3 against 51.2 as the direction, and the direction only.
- **statedark beats spaced on wired clocks** (10/11 against 8/12). The count of looks does nothing but the
  stretch between them may do something. One chip, two layouts, thin. Not carried as a claim.
- **One chip.** Kingston only. It earns its weight by holding on a chip it was not read on.

## What lands it

The wired/sight split should appear on Pittsburgh and Fez in the same layouts, with sight clocks at a coin.
If a sight clock ever shows the product advantage, the coupling reading dies and we are back to three lanes.
