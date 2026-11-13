"""analyze_ufsm_dd.py -- addendum readings. R2' = Dc with DD ON (same rule as R2). R4 = deficit(b) DD ON minus DD OFF (J1 vs J2, back to
back; drift scale from run 1's two DD-off copies 26 s apart: D 49.95 vs 49.45 pp). Four outcomes, 99 % band, bootstrap."""
import json, sys, os, numpy as np; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import ufsm
L = lambda t: [(k, l, x) for k, l, x in json.load(open(f'{HERE}/raw_ufsm_{t}.json'))]
on, off = L('ddon'), L('ddoff'); ron = ufsm.analyze(on, nboot=400); roff = ufsm.analyze(off, nboot=400, seed=12)
print(f"DD ON : deficit (a) {100*ron['def_a']:.3f} pp, (b) {100*ron['def_b']:.3f} pp; D {100*ron['D']:+.3f} +- {100*ron['sD']:.3f}; Dc {100*ron['Dc']:+.3f} +- {100*ron['sDc']:.3f}  R1 {ron['R1']}  R2' {ron['R2']}")
print(f"DD OFF: deficit (a) {100*roff['def_a']:.3f} pp, (b) {100*roff['def_b']:.3f} pp; D {100*roff['D']:+.3f} +- {100*roff['sD']:.3f}; Dc {100*roff['Dc']:+.3f}  R1 {roff['R1']}  R2 {roff['R2']}")
d = ron['def_b'] - roff['def_b']; sd = np.hypot(ron['sD'], roff['sD'])
R4 = 'ABOVE' if d - ufsm.Z99 * sd > 0 else 'BELOW' if d + ufsm.Z99 * sd < 0 else 'CONSISTENT'
print(f"R4 deficit(b) DD ON minus DD OFF = {100*d:+.3f} pp +- {100*sd:.3f} -> {R4}")
for name, ents in (('ON', on), ('OFF', off)):
    for k, l, x in ents:
        if k == 'b': n = sum(x.values()); print(f"  {name} b{l}", {s: round(v / n, 3) for s, v in sorted(x.items())})
