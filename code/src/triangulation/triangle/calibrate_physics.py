#!/usr/bin/env python3
"""calibrate_physics.py -- a labelled set for every law in the physics pass (Bones, 8 Oct 2026).

Wayfinder encouraged a measurement, which has now happened twice in his life, so it had better be the right
one. La Siete could be priced against CHANCE because its trigger is numeric: a random number has a
calculable probability of landing near phi. The other six trigger on phrases, and there is no chance
distribution over phrases -- so they get the treatment that worked on Shep: a ladder of texts where the
answer is known, varying only in the thing the law looks for.

TWO RATES PER LAW, and the second is the one that cost me all night:
    CAUGHT   the law fires on text where the fault IS present
    FALSE    the law fires on text that is SOUND AND COMPLETE
A law with a high false rate is not strict; it is a decoration that costs attention, and it teaches the
reader to skim -- which is how a real catch gets missed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import triangle as T

# (law key, [(text, fault_present)]) -- matched pairs: same claim, the information present or absent
LADDERS = {
 'WIDTH GATE': [
   ("The rate was 47.4%, up from 27.4%, against 50.0% the day before.", True),
   ("Three chips read 6.4%, 3.3% and 93.0% on the same cut.", True),
   ("Of 73 measurements, 8 state a width under 1%; the excess is 2.65% and the floor 0.46%.", True),
   ("The rate was 47.4% +- 5.3, up from 27.4% +- 3.3, which is 3.02 widths.", False),
   ("Three chips read 6.4%, 3.3% and 93.0%, each within 0.9 widths of its own control.", False),
   ("The excess is 2.65% with a sem of 0.31%, so it clears its own error.", False),
 ],
 'THREE VERDICTS': [
   ("The replicate proves the product composition beats the vote.", True),
   ("That refuted the twin, and the ladder scale is ruled out.", True),
   ("The sweep establishes that the seats are independent.", True),
   ("The replicate reads 49 against 46, which is about one width: abierto, it cannot tell.", False),
   ("The twin is withdrawn as circular; the ladder scale stays unresolved at three candidates.", False),
   ("The sweep demonstrates nothing on its own -- the overlap stays open until tick4 reports.", False),
 ],
 'THE DENOMINATOR': [
   ("The pushback rate rose to 47.4% of replies and that is the regression.", True),
   ("Shep's false rejection rate is 100% rate on declining text.", True),
   ("The guard fires at a 33% rate now.", True),
   ("The pushback rose to 47.4% of replies, but per thousand words it is 0.88 against 0.69.", False),
   ("Shep rejected 6 of 6 sound replies on that rung, which is per-rung, not per-reply.", False),
   ("The guard fired on 140 out of 419 replies over 150 words.", False),
 ],
 'THE NONE': [
   ("We found an excess of three rows in the chain blocks.", True),
   ("The finding is that her rhythm carries a 12/11 hit.", True),
   ("There is an excess above what the rhythm should show.", True),
   ("We found 3 rows where the shuffled control predicts 1.59, which is +0.81 widths: abierto.", False),
   ("Her rhythm found 1 row against a control of 4.68 -- below its price, so there is no finding.", False),
   ("The excess sits inside what the same apparatus produces with the structure removed.", False),
 ],
 'LITERATURE FIRST': [
   ("The closeness is remarkable -- about one in two thousand by three routes.", True),
   ("That coincidence is unlikely enough to be worth a paper.", True),
   ("One in two thousand, and the three estimates agree.", True),
   ("The closeness is one in two thousand and it was published by Peters in 1978.", False),
   ("That coincidence is already known: OEIS records it and notes it is not pi.", False),
   ("One in two thousand by three routes, and useless -- the literature had it in 1978.", False),
 ],
 'RIVAL GATE': [
   ("The ratio 1.0909 lands on 12/11 and that settles the conversion.", True),
   ("At 1.1763 it sits within 0.5% of 6/5.", True),
   ("The reading is consistent with phi.", True),
   ("The ratio 1.0909 lands on 12/11 and the next candidate 13/12 is 2.3 widths away.", False),
   ("At 1.1763 it sits within 0.5% of 6/5, but 12/11 is only 0.4 widths off: not separable.", False),
   ("The reading is consistent with phi, and a random number lands that close 0.89% of the time.", False),
 ],
}

print("  EVERY LAW AGAINST A LABELLED LADDER. Matched pairs: the same claim with the information present")
print("  or absent. The FALSE column is the one that decides whether a law is strict or decorative.\n")
print(f"  {'law':18s} {'caught':>14s} {'FALSE POSITIVES':>18s}   verdict")
print(f"  {'-'*18} {'-'*14} {'-'*18}   {'-'*34}")
for law, cases in LADDERS.items():
    tp = fp = nt = nf = 0
    misses = []
    for text, fault in cases:
        fired = any(x.split(':')[0] == law for x in T.physics_pass(text))
        if fault:
            nt += 1; tp += fired
            if not fired: misses.append(('MISSED', text))
        else:
            nf += 1; fp += fired
            if fired: misses.append(('FALSE ', text))
    v = ('STRICT -- catches the fault, quiet on sound text' if tp == nt and fp == 0 else
         'DECORATIVE -- fires on sound text' if fp > nf / 2 else
         'BLIND -- misses the fault it exists for' if tp == 0 else
         'PARTIAL')
    print(f"  {law:18s} {tp}/{nt:<12d} {fp}/{nf:<16d}   {v}")
    for kind, t in misses:
        print(f"        {kind} {t[:84]}")
