"""analyze_ufsm.py -- both copies through ufsm.analyze(); also each copy alone (copy gap reported, not scored)."""
import json, sys, os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import ufsm
E = {c: [(k, l, x) for k, l, x in json.load(open(f'{HERE}/raw_ufsm_copy{c}.json'))] for c in (1, 2)}
r = ufsm.analyze(E[1] + E[2], nboot=400)
pp = lambda v: f'{100*v:+.3f} pp'
print(f"pair {json.load(open(f'{HERE}/job_ufsm.json'))['pair']}")
print(f"deficit (a) {100*r['def_a']:.3f} pp, (b) {100*r['def_b']:.3f} pp; readout-only from our bracket (a) {100*r['ro_a']:.3f}, (b) {100*r['ro_b']:.3f} pp")
print(f"R1 raw extra deficit D = {pp(r['D'])} +- {100*r['sD']:.3f} vs theirs {pp(r['R1_theirs'])} -> {r['R1']}")
print(f"R2 extra deficit beyond the readout it adds, Dc = {pp(r['Dc'])} +- {100*r['sDc']:.3f} (99 % band) -> {r['R2']}")
print(f"R3 instance spread: chi-square min p {r['spread_p']:.4f} (gate {ufsm.SPREAD_P}); sd ratio {r['spread_ratio']:.2f}")
print(f"descriptive: (a) 01 minus 10 asymmetry {pp(r['asym_a'])} (theirs +1.86 pp); bracket flips {r['flips']}")
for c in (1, 2):
    rc = ufsm.readings(E[c]); print(f"copy {c} alone: D {pp(rc['D'])}, Dc {pp(rc['Dc'])}")
