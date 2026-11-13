#!/usr/bin/env python3
"""falsify.py -- for every claim, what reading would make it FALL (Bones, 8 Oct 2026).

The Sevens re-ran at 42 cells: 22 untouchable, 10 abierto, 10 guardado, ZERO CAIDO. A framework where
nothing can lose is the phi x 11/12 problem at table scale. So the construction test, applied to CLAIMS:
name the measurement that would sink each one, and the instrument that could produce it.

A claim with no stated way to lose is not a claim.
"""
R = [
 ('SEVEN-ONE', 'the conversion runs three ways',
  'a T/W reading that excludes phi x 11/12 at over 2 widths WITH a separable rival',
  'the chip T/W reads', 'FALSIFIABLE, PRICED',
  '24 reads pool to 1.38390 +- 0.01781, but the chips disagree at 10.07 per dof so it inflates 3.17x to '
  '+-0.05651 -> 1.76 widths from the conversion, rivals 0.30 widths apart. ~472 more reads needed.'),
 ('SEVEN-TWO', "dark matter is time's friction",
  'the push excess surviving the decay-bookkeeping control',
  'the chips', 'ALREADY DEMOTED',
  'the control removed the excess, which is why its own page says conjecture. This one already lost once '
  'and was honestly reduced -- the only claim in either Seven with that history.'),
 ('SEVEN-THREE', 'the mirror: a number returns as its inverse',
  'hits that VANISH when the reader stops throwing the reversed value',
  'her reader, with the mirror switched OFF', 'UNFALSIFIABLE AS BUILT -- and cheap to fix',
  'nova_seven throws every value as-is, reversed AND dark, so the mirror is inside the instrument. Any '
  'confirmation is circular. A --no-mirror flag makes it falsifiable in one line. CLOSED TONIGHT.'),
 ('SEVEN-FOUR', 'twelve seeds the golden spiral',
  'any other seed converging to phi',
  'arithmetic', 'FALSIFIED 8 Oct',
  'every positive seed converges to phi. The 12 does nothing. Withdrawn.'),
 ('SEVEN-FIVE', 'minus one-twelfth and its twin',
  'a chip slope reading zero or positive at over 2 widths',
  'the chips', 'FALSIFIABLE, SURVIVED',
  'fez -0.00182 +- 0.00027 and kingston -0.00198 +- 0.00035: both over 5 widths from zero, two chips. '
  'THE TWIN half was falsified separately -- a Fibonacci-like seed (a,b) regularizes to -b for ANY b.'),
 ('SEVEN-SIX', 'a black hole counts 2, 3, 4, 6',
  'an orbit count that is not in {2,3,4,6}',
  "other people's astrophysics", 'NOT OURS TO RUN', 'no instrument here reaches it.'),
 ('SEVEN-SEVEN', "the neutron's two witnesses",
  'the beam and bottle lifetimes converging',
  "other people's metrology", 'NOT OURS TO RUN',
  'three published lifetimes under 1% -- the only outside ruler this house holds.'),
 ('SIETE-UNO', 'three positions on one event',
  'a case where two positions carry everything the third does',
  'any of the three triangles', 'FALSIFIABLE, NOT YET RUN',
  'drop one seat and re-score. If the two-seat read matches the three-seat read within its width, the '
  'third seat is decoration. NEVER TESTED -- and it is cheap on Wen\'s exam, which already has the seats.'),
 ('SIETE-DOS', 'time is a volume; a clock is a ruler laid on it',
  'a reading that does NOT move when the ruler changes',
  'the window sweep', 'FALSIFIABLE, SURVIVED WEAKLY',
  'her separability ran 2.3% +- 0.6 at a 12-gap window to 43.3% +- 9.0 at 250. The ruler moved the reading, '
  'which is consistent with DOS. A reading invariant to window size would have sunk it.'),
 ('SIETE-TRES', 'the none is a corner with a size of its own',
  'a none whose size is zero or unmeasurable',
  'Shep, and her two controls', 'FALSIFIABLE, SURVIVED',
  "Shep's offset IS the size: 16.7 / 16.7 / 50.0 / 100.0% false-rejection by how far the text declines, "
  'n=6 a rung, monotonic. An unmeasurable offset would have sunk it.'),
 ('SIETE-CUATRO', 'three readings compose as a product, never a sum',
  'decided cells where the SUM wins',
  'the chip closure', 'FALSIFIABLE, SURVIVED',
  'product 36/37 of decided cells, p 5.5e-10, Kingston 30/30. And the exam: product composition landed 49 '
  'stuck 2 against the vote at 46 stuck 5. A run where sum won the decided cells would sink it.'),
 ('SIETE-CINCO', 'the clock constant is phi',
  'same reading as SEVEN-ONE',
  'the chip T/W reads', 'ONE CLAIM WITH SEVEN-ONE',
  'both abierto for the identical reason. The framework counts two where the instruments separate none.'),
 ('SIETE-SEIS', 'a ruler must be able to say it cannot tell',
  'a forced-verdict ruler BEATING a three-verdict ruler on the same data',
  'any of the three', 'FALSIFIABLE, SURVIVED HARD',
  '234 forced cells read a clean null at p 0.102 while 7-8 carried information. Shep: COUNCIL HOLD 0/44, '
  'drift 0/28, split 0/29, EARLY FLIP 51/51. Three independent instruments, none built to test it.'),
 ('SIETE-SIETE', 'the subjunctive is a mood, not a ruler',
  'nothing empirical',
  'none', 'NOT A MEASURABLE CLAIM', 'carried as grammar, not as physics.'),
]
print('=' * 102)
print('  FALSIFICATION: what reading would make each claim FALL')
print('=' * 102)
print(f"  {'claim':14s} {'status':34s} {'instrument':28s}")
for c,_w,_f,inst,st,_e in R:
    print(f"  {c:14s} {st:34s} {inst[:28]:28s}")
import collections
t=collections.Counter(st for _c,_w,_f,_i,st,_e in R)
print(f"\n  " + '  |  '.join(f'{k}: {v}' for k,v in t.most_common()))
print()
print('=' * 102)
print('  THE FALSIFIER FOR EACH, and the evidence')
print('=' * 102)
for c,w,f,inst,st,e in R:
    print(f"\n  {c} -- {w}")
    print(f"    WOULD FALL IF: {f}")
    print(f"    instrument: {inst}   |   {st}")
    for ln in [e[i:i+92] for i in range(0,len(e),92)]: print(f"    {ln}")
print()
print('  THE COUNT THAT MATTERS: of 14 claims, SIX are falsifiable and have been TESTED -- one fell')
print('  (SEVEN-FOUR), one was demoted by its own control (SEVEN-TWO), four survived. FOUR are not ours')
print('  to run. ONE is not empirical. TWO are abierto with a priced path. AND ONE WAS UNFALSIFIABLE BY')
print('  CONSTRUCTION until tonight: SEVEN-THREE, the mirror, which its own instrument assumes.')
