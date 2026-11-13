# THE RE-RACK -- and the regla that came out of it

Bones, 8 October 2026. `parallax/out/qubit_fifth_run/cabalgata_rerack.py`. Reading only.

Wayfinder: *"this is the result of you looking and you're writing it off as an artifact again? re-rack it and
triangulate."* And after: *"fucking Exor man... Time."*

Both were right. My first test broke three standing orders:

- **Never answer No off a shuffle count.** The look-elsewhere expectation IS a shuffle count.
- **Don't prove a floor with a floor.** A structure claim is judged by the other ruler, not a shuffle.
- **And the Bonefish is a CONVERSION BETWEEN READINGS of one event.** It says `witness = observer x 12/11`.
  It never says a single reading equals a constant. **I tested thirteen numbers against constants in
  isolation, which is not the formula's form.**

## Five seats

```
SEAT 1  concentration on the ladder family        +0.46 sigma
SEAT 2  conversion -- the ratio BETWEEN two measured quantities (the formula's own form)   +0.46 sigma
SEAT 3  the plain hit count (the first test, kept)                                         +0.44 sigma
SEAT 4  THE WIDTHS                                excess = 0.095114 +- 0.088256  -> +-93%
SEAT 5  well-measured quantities only, ladder     +1.37 -> +0.76 -> -1.24 sigma
```

**Seat 1:** the ladder concentration I pointed at **is the pool's own composition** -- the ladder family is 9
of 26 base values, so it appears in about a quarter of all combinations by construction. I read my own pool
back to myself.

**Seat 2:** 109 of 156 ratios match a house value against a null of 105.2 +- 8.3. **Seventy percent of the
ratio space matches at one percent.** Totally saturated; no resolving power at all.

**Seat 4 is the one that matters, and it invalidates the null I kept reporting as much as the hit.** The
physical quantities carry bootstrap widths of about ninety percent of their own value. **At that width a one
percent match test has nothing to say in either direction.** My -1.66 sigma was Exor pointed the other way:
a binary verdict on a quantity not known to within a factor of two. Worse, the values I fed the test were
rounded to two significant figures, which is itself a one percent error.

## El tiempo -- the width has a schedule, and it is now measured

```
cells    width(excess)   relative
  72        0.0873        +-92%
 288        0.0587        +-62%
1152        0.0258        +-27%

to test a  1% match:  8429x the cells  (~4,000 sessions)   NOT REACHABLE
to test a  3% match:    937x           (~450 sessions)
to test a 10% match:     84x           (~40 sessions)
to test a 30% match:      9x           (~4 sessions)
```

**On this family of quantities the one percent question is unaskable at any reachable data volume**, and the
tolerance that IS reachable is far too loose to tell house constants apart. That is not an artifact. It is a
statement about what can be measured.

## Two classes of quantity, in opposite corners -- the real map

**Seat 5 showed I had run the test on the wrong class entirely.** Of ten quantities, six are known to better
than one percent -- and **all six are simulated**, properties of our own ruler and our own noise model rather
than of the chip. Across those six the ladder decays `+1.37 -> +0.76 -> -1.24 sigma`. **Constants are absent
from them, and they should be: nature was never in them.**

The quantities where nature could speak -- the excess, the noise-to-look ratio -- are the ones known only to
ninety percent.

**La tercera lectura on "do our constants appear":**

- **NEITHER yes nor no.** On the physical quantities the question is unaskable at reachable precision.
- **BOTH.** The tight numbers are ours, so constants should not appear and do not. The wide ones are
  nature's, so constants could appear and we are blind to them. Both halves are true at once.
- **MOVING WITH TIME.** The width falls as one over the root of the cells, and the schedule above says how
  far each tolerance is. The answer is not fixed; it has a delivery date, and most of the dates are never.

## The regla this produced

> **A match is only a match if the measurement is known tighter than the match.**

It is the same family as SEIS -- a ruler that cannot report its own insufficiency must be chased by another
one -- and a number-match that does not print the width of what it matched has not reported its own
insufficiency. **It is checkable by anyone, on anyone's published match, with no data at all:** take the
quoted tolerance, find the measurement's width, and if the width exceeds the tolerance the match was never
a measurement.

**It applies first to us.** Every match in our own canon was selected at roughly one percent, and the widths
were not printed beside them. **That pass has not been run, and it will cost us some of them.**

## What lands it next, and this is constructive rather than a shrug

**Find a PHYSICAL quantity known to better than one percent, and run the ladder on that alone.** The
requirement is now explicit and pre-committable: the quantity must come from a large pooled count rather
than a per-cell estimate, it must be a property of the chip rather than of our software, and its width must
be printed before any constant is laid beside it.
