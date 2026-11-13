"""analyze_ufsm_pairs.py -- addendum 2 reading: per pair, DD-off deficit (b) with the committed ufsm.analyze; outcome per pair vs THEIR
published 4.673 pp (b) deficit and vs our [81,82] DD-off 51.8 pp: a pair is LIKE-THEIRS if its (b) deficit 99% band includes <= ~10 pp,
LIKE-81-82 if its band includes >= ~40 pp, else BETWEEN; CANNOT_TELL if the band spans both. Rule fixed before the job."""
import json, os, sys; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import ufsm
E = json.load(open(f'{HERE}/raw_ufsm_pairs.json'))
for p, ents in E.items():
    r = ufsm.analyze([tuple(e) for e in ents], nboot=400); b, s = 100*r['def_b'], 100*r['sD']; lo, hi = b - ufsm.Z99*s, b + ufsm.Z99*s
    o = 'CANNOT_TELL' if (lo <= 10 and hi >= 40) else 'LIKE-THEIRS' if lo <= 10 else 'LIKE-81-82' if hi >= 40 else 'BETWEEN'
    print(f'pair {p}: deficit(b) {b:.2f} pp [{lo:.2f}, {hi:.2f}] (a) {100*r["def_a"]:.2f} pp -> {o}')
