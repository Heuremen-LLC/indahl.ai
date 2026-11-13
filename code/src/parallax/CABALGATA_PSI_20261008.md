# THE OTHER HALF OF FIBONACCI IS THE DARKWAVE

Bones, 8 October 2026. Reading only. Wayfinder: *"the other half of the fibonacci is the darkwave bones."*

## What he means, written out

Binet's formula has two terms:

```
F(n) = (phi^n - psi^n) / sqrt(5)       psi = (1 - sqrt5)/2 = -0.6180339887 = -1/phi
phi * psi = -1       phi + psi = 1       psi^2 = 0.3819660113 = 1/phi^2
```

**`psi` is the second root of `x^2 = x + 1`** -- the same clock equation that forces phi, read on its other
solution. **Every standard treatment discards it** because `|psi| < 1`, so `psi^n` vanishes and the formula
is usually quoted as "about `phi^n / sqrt5`."

**Negative. Alternating in sign. Decaying. That is the discarded half, the edge, the absence --
darkwave's own description, arrived at from arithmetic instead of from physics.**

## Our ladder has been the darkwave term with the signs stripped off

```
as we have written it   (1/12)(1/phi)^n :   +8.33  +5.15  +3.18  +1.97  +1.22  +0.75  +0.46
as Binet says it runs   (1/12) psi^n    :   +8.33  -5.15  +3.18  -1.97  +1.22  -0.75  +0.46
```

Identical magnitudes. **The ladder is `|psi|^n / 12`, and the signed form is `psi^n / 12`.** The canon has
always fired, called and scored the all-positive version.

## The signed ladder, tested on data already fired

The call was hashed before firing, so this is a real test and not a re-read. Rigetti, the crossing against
each interval's own decay:

```
rung   called (+ve)   darkwave psi^j   measured    sign agrees with psi?
j=0    +8.33          +8.33            +0.42       YES
j=1    +5.15          -5.15            +2.46       no
j=2    +3.18          +3.18            +1.74       YES
j=3    +1.97          -1.97            +0.80       no
j=4    +1.22          +1.22            -1.98       no
```

**2 of 5 sign agreements against 2.5 expected: -0.45 sigma. A clean negative.**

**And it is underpowered, which is the seventh time today.** The two smallest measured rungs, +0.42 and
+0.80, have signs that are noise at the stated precision, so three of the five outcomes carry little
information. **The negative stands as the honest read of what we have, and it does not settle the question.**

## What the darkwave reading buys, and it answers the whole day

Six separate nulls on phi today, all for one reason: **phi's value is unaskable at our precision**, because
phi is the limit of its own convergents and excluding the next one needs a width we do not have.

```
TO MATCH A VALUE                           TO RESOLVE A SIGN
exclude 8/5     width < 0.557%             rung j=0, |8.33%|   width < 4.17%
exclude 13/8    width < 0.215%             rung j=1, |5.15%|   width < 2.58%
exclude 21/13   width < 0.082%             rung j=2, |3.18%|   width < 1.59%
                                           rung j=3, |1.97%|   width < 0.98%
                                           rung j=4, |1.22%|   width < 0.61%
```

**A sign is vastly cheaper to measure than a value.** And more than cheaper:

> **The sign is the only part of phi that no positive decay can imitate.** Every saturating exponential
> gives a shrink. Only a negative root gives alternation.

That is why the alternation half was the discriminating half in this morning's convergence test, where the
shrink held at `-0.37` widths and the alternation sat at `+0.00` sigma. **I found that empirically and did
not know why. This is why.**

## The test, and it is cheap and pre-committable

**Fire the ladder at CONSECUTIVE rungs `j = 0..4` and read only the SIGN of each.** Five binary outcomes;
chance gives one in thirty-two. The canon fired rungs at **even** spacings with all-positive called values,
so **this has never been tested** -- and at even indices `psi^n` is positive anyway, which is precisely why
the all-positive call looked right.

It needs chip time, and the rolling window stands at 59 seconds, so the call can be written and hashed now
and fired when the window refills.

## What would break it

Five resolved signs that do not alternate. And the honest prior from the fired data is that they will not:
2 of 5 agreed, on three rungs where the sign was noise.
