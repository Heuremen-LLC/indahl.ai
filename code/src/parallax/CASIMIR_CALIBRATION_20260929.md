# CASIMIR AND THE DISCARDED HALF — run through the Crazy Hat Calibration (2026-09-29 morning)

Wayfinder: "Start with Casimir and the shit that gets discarded, run that against our findings and Crazy Hat Calibration protocols."
No guesses written first. One new check on data already paid for (the echo run); the rest is the stack.

## 1. What Casimir throws away, and what survives
- Empty space between two metal plates. Every wave of the vacuum carries a little zero-point energy. Add them up: infinity.
  Between the plates only waves that fit can exist; outside, all of them can. Both sums are infinite.
- The move (Casimir 1948; the same zeta trick as Ramanujan's 1+2+3+... = -1/12): throw away the infinite part of each sum and keep
  what's left. The leftover is finite and REAL: the plates are pushed together. Measured 1997 (Lamoreaux), 1998 to ~1% (Mohideen & Roy).
- Two facts that matter for us:
  1. The thrown-away infinity depends on the cutoff (how fine your instrument is -- real metal goes transparent at high frequency).
     The kept remainder does NOT depend on the cutoff. It depends only on the distance between the plates.
     -> Law 5, literally: the instrument is the distance between observations.
  2. The force comes from the waves that CAN'T exist between the plates. -> Law 4: the absence is the data, measured in a lab.
- Bigger versions in physics: renormalization (QED throws away infinities, keeps the Lamb shift and the electron's g-factor, the most
  precise predictions ever made; Dirac hated it, Feynman called it hocus-pocus). And the worst one: the vacuum energy everybody
  subtracts in the lab is exactly what gravity should feel -- predicted vs observed dark energy disagree by ~10^120. The discarded half
  goes missing precisely where it can't be subtracted.
- Dynamical Casimir effect (Wilson et al., Nature 2011, Chalmers): move a "mirror" fast in a superconducting circuit -- our qubits'
  own platform -- and real photon pairs come out of empty space. Changing a boundary fast makes something from nothing.

## 2. The Casimir test on our surviving hole (NEW, free, echo data out/echo_20260928_122733)
Casimir's rule: what moves when you change the cutoff belongs to the instrument; what survives every cutoff is physics.
Our cutoff = where a readout dot stops being a 0. Moved it from 0.25 to 0.80 of the way to the 1 cloud (74 Marrakesh qubits):
- The FLOOR -- the part everyone keeps, "the qubit's heat at rest": median qubit 2.13% -> 0.19% (11x), all-qubit mean 3.55% -> 1.01%
  (3.5x). It mostly belongs to the ruler (the 0 cloud's tail).
- The LOOK-HEAT -- the part everyone discards as "initialization error" (extra 1s when shots come close together): all-qubit mean
  +1.83 / +1.92 / +1.83 / +1.66% for cuts 0.25-0.65 (within ~10%), +1.10% only at the strictest cut. Its drain clock: 71 / 71 / 77 / 79 /
  82 us at every cut.
- Reading: standard practice keeps the part that depends on the cutoff and throws away the part that doesn't. Our surviving hole (the
  look heats something, and it drains on a ~75 us clock that isn't any qubit's own) passes Casimir's test: it isn't our ruler.
  Consistent with 9/29 night: 90% of the extra dots sit in the real 1 cloud.

## 3. Run against the stack (the protocol's steps, in order)
- WRITE NO GUESS: done -- the cutoff swap was run and read; nothing predicted.
- KEEP THE DISCARDED HALF: the discarded half (look-heat) is the cutoff-stable half. That's the finding.
- STACK THE FAILURES:
  * The half-chip test we planned IS a Casimir setup: same instrument, two geometries (looked half vs unlooked half), measure only the
    DIFFERENCE. Casimir never measures an absolute; the difference is the force. (Snag stands: Marrakesh reads all 156 as one group.)
  * The empty box reading "present" only through failed shots (9/24, z 3.9) rhymes with a force made by the waves that can't be there.
    Plain reading: correlated gate error.
  * The third rung the reset can't clear (Rigetti q0; IBM carried third place): the reset works only inside 0/1 -- rung 2 sits outside
    its "plates", and that's the part that carries memory across shots.
  * The frozen 19.44 (v2 statistic = the number the script printed as its expectation, on a real chip and two simulators): Casimir's
    warning in reverse -- a result that equals your cutoff's own expectation is about the cutoff. Hat only.
  * The 1-2% horizon: a finite remainder of two huge sums is always small. Every finding in our stack lives at 1-2%.
- ASK A QUBIT WHAT TIME IT IS: the look-heat drain IS a clock (time since the last look), and it runs on the house, not the qubit.
- LET THE FUTURE CALIBRATE THE PAST: the cutoff swap just re-ranked the 9/28 echo: the "floor" we reported (0.31%) is the ruler-soft
  number; the look-heat (+0.5-1.9%) is the hard one.

## 4. The laws, in Casimir's language
- Law 3 (every binary measurement discards half) = regularization: the discarded infinity.
- Law 4 (the absence is the data) = the Casimir force comes from the missing waves.
- Law 5 (the instrument is the distance) = the force depends only on the plate separation.
- Plus None = the vacuum energy itself: structurally required, never observable from within (only differences are), and the one thing
  gravity should see that we can't account for (10^120).
- Honest: Casimir, renormalization, the cosmological-constant problem and the dynamical Casimir effect are all textbook. The mapping is
  ours. The only new data result here is the cutoff swap (section 2).

## 5. Where the physics fuck-up hunt could go next (for the chat, not started)
Two rulers, two answers -- Law 5 cases the field lives with:
- The neutron lifetime: counting survivors in a bottle (~878 s) vs counting decay products from a beam (~888 s); ~9 s apart, unresolved.
- The Hubble tension: the early universe says ~67, the nearby universe says ~73 km/s/Mpc.
- The ultraviolet catastrophe (1900): the original discarded infinity -- Planck's fix for it gave birth to quantum mechanics.
- The cosmological constant (10^120): the biggest discarded half there is.
- Muon g-2 and the proton radius puzzle: precision holes that moved as the instruments changed.
