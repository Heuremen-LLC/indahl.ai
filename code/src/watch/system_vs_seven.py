#!/usr/bin/env python3
"""system_vs_seven.py -- the system we built against the framework it was built for (Bones, 8 Oct 2026).

Wayfinder: "use our entire current system, evaluate the system with the seven, and build any differences
into Nueva." So: every rule the system now ENFORCES, set against what the Sevens SAY. Three outcomes --
the rule is in the framework, the rule EXTENDS it, or the rule CONTRADICTS it. The contradictions are the
ones that matter and they go into Nueva.
"""
R = [
 # (what the system enforces, where it lives, the Seven's position, verdict)
 ('a reading is a magnitude AND a sign; check both roots',
  'triangle.py, council_cases.py, nova_seven.py, loops_closure.py',
  'IN THE FRAMEWORK -- the clock is x^2 = x + 1 with two roots, phi for magnitude and psi for sign',
  'IN'),
 ('a ruler must be able to say it cannot tell',
  'EL PICNIC everywhere, loops_closure, physics_cases',
  'IN THE FRAMEWORK -- SIETE-SEIS, word for word',
  'IN'),
 ('three readings compose as a product, never a sum',
  'physics_cases, the Meilong exam, La Cabalgata',
  'IN THE FRAMEWORK -- SIETE-CUATRO',
  'IN'),
 ('a number counts only when its own error is smaller than itself',
  'the WIDTH GATE; physics_cases; nova_seven throw_widthed',
  'EXTENDS -- the Sevens state widths for some claims and nowhere require one',
  'EXTENDS'),
 ('a match counts only when the next candidate is separable at that width',
  'the RIVAL GATE; physics_cases; throw_widthed',
  'EXTENDS -- and it is what makes phi x 11/12 untestable against 3/2, which the Sevens never noticed',
  'EXTENDS'),
 ('a match is a ROW, never a reason: state its cheap-match rate',
  'LA SIETE law; bonefish_coin; nova_seven rows',
  'IN THE FRAMEWORK -- the Bonefish demands it; the Sevens printed it inconsistently',
  'IN'),
 ('every ABIERTO carries an AGE, and resolving one RETIRES it',
  'nova_seven abierto_age.json; loops_closure closure_none_age.json',
  'EXTENDS -- SIETE-SEIS says a ruler may decline. It does NOT say a decline expires',
  'EXTENDS'),
 ('every finding is priced by a NONE: the same apparatus with the structure removed',
  'Shep; chance() and shep(); the offset injection',
  'EXTENDS -- SIETE-TRES says the none is a corner with a size. It does not say the none PRICES',
  'EXTENDS'),
 ('a control handed no evidence is not a control, and its reliability is a gradient',
  'seats.py standing: PRICES IT / THINLY / TONE ONLY',
  'EXTENDS -- nothing in either Seven says what a none must be handed',
  'EXTENDS'),
 ('the none has its own measured bias against the third verdict, divided out',
  'shep_offset.json: 16.7 / 16.7 / 50.0 / 100.0% by how far the text declines',
  'EXTENDS -- and it is a maker look on our own instrument, which the Sevens apply only outward',
  'EXTENDS'),
 ('a claim and the instrument that tests it must not share an assumption',
  'the mirror in her reader; the conversion in the Bonefish bookkeeping',
  'CONTRADICTS -- SEVEN-THREE is asserted BY an instrument that assumes it, and SEVEN-ONE is a derived '
  'identity reported as agreeing with measurement',
  'CONTRADICTS'),
 ('a zero width is UNDEFINED, not resolved',
  'the ninth law; loops_closure abierto on a nan',
  'EXTENDS -- SIETE-SEIS covers declining, not undefined. They are different states',
  'EXTENDS'),
 ('naming a frame is not using it; a check must score USES',
  'the CRITIQUE exemption; the width gate exemption',
  'EXTENDS -- no Seven distinguishes naming from using',
  'EXTENDS'),
 ('a rate carries its denominator inside it; score with every ruler',
  'THE DENOMINATOR law; per reply vs per thousand words',
  'IN THE FRAMEWORK -- SIETE-DOS, a clock is a ruler laid on a volume',
  'IN'),
 ('a live quantity carries the moment it was read',
  'THE CLOCK law; the five stale-copy instances',
  'EXTENDS -- the Sevens treat time as a dimension, never as a property of a QUOTED number',
  'EXTENDS'),
 ('a check is priced like a finding: run it on text not written for it',
  'calibrate_physics.py; the 419-reply measurement; the chance baselines',
  'EXTENDS -- nothing in either Seven turns the method on the method',
  'EXTENDS'),
 ('the Exor is wrong as an ANSWER and right as a QUESTION; pairs are EDGES',
  'the dyad triangle in Wen, the seats, the closure',
  'EXTENDS -- SIETE-SEIS forbids forcing a choice. It does not say the exclusive form is an INSTRUMENT',
  'EXTENDS'),
 ('FOUR seats, not three: a triangle plus its none is a tetrahedron',
  'Wen, the seats, Nueva, now the miner',
  'CONTRADICTS -- SIETE-UNO says THREE POSITIONS ON ONE EVENT. The system measured that three is not '
  'enough: without a none nothing is priced, and the none is a fourth vertex',
  'CONTRADICTS'),
 ('a vertex may OPEN into a solid; its edges run to the whole inner solid',
  'Wen\'s rounds as a vertex of the clock tetrahedron',
  'CONTRADICTS -- neither Seven has a nesting rule, and SIETE-UNO\'s flat "three positions" cannot '
  'express a position that is itself a structure',
  'CONTRADICTS'),
]
import collections
print('=' * 100)
print('  THE SYSTEM AGAINST THE SEVEN')
print('=' * 100)
t=collections.Counter(v for *_x, v in R)
print(f"  {len(R)} rules the system enforces:  " + '  '.join(f'{k} {v}' for k,v in t.most_common()) + '\n')
for what, where, pos, v in R:
    if v != 'CONTRADICTS': continue
    print(f"  [CONTRADICTS] {what}")
    print(f"      lives in: {where}")
    for ln in [pos[i:i+88] for i in range(0,len(pos),88)]: print(f"      {ln}")
    print()
print('=' * 100)
print('  THE THREE CONTRADICTIONS, and they are one family')
print('=' * 100)
print("""
  All three are about STRUCTURE, not about measurement:

  1. SIETE-UNO says THREE POSITIONS. The system needs FOUR -- three readers and a none -- because
     without a none nothing is priced, and a finding that is never priced is the two-lane failure with
     more machinery. Measured tonight: her reading has two controls, Wen has shep, the seats have the
     untuned twin, and the miner had NOTHING until the Mac's clock was named as its fourth vertex.

  2. A POSITION CAN BE A STRUCTURE. "Wen's rounds" is one vertex of the clock tetrahedron AND a whole
     tetrahedron of its own. SIETE-UNO's flat three cannot say that, and the edge rule matters: an edge
     to an opened vertex runs to the WHOLE inner solid, never to one inner point.

  3. A CLAIM AND ITS INSTRUMENT MUST NOT SHARE AN ASSUMPTION. SEVEN-THREE (the mirror) was asserted by a
     reader that throws every value reversed, and SEVEN-ONE is a derived identity reported as agreeing
     with measurement. Neither Seven forbids this, and both do it.

  THE FOURTEEN CLAIMS WERE ABOUT THE WORLD. THE SYSTEM'S RULES ARE ABOUT THE READING OF IT, and sixteen
  of nineteen extend the framework rather than conflicting with it -- which is what a method is.""")
