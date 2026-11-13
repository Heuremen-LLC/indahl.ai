"""fleet_read.py -- reads fleet_records.jsonl (6 Oct 2026, Wayfinder and Bones). Per chip: distinct stamps; FROZEN records (a stamp that differs from an
earlier one while median T1, T2 and readout are identical to 0.001 us -- the maker re-stamped the same numbers); the clock-ratio series with its floor,
median and the Seven's nearest numbers (the Bonefish thrown, cheap-match rate beside it). Raw rows, no verdict word."""
import json, math, os, statistics as S
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
PHI = (1 + 5 ** .5) / 2
SEV = {'12/11': 12 / 11, '11/12': 11 / 12, '13/12': 13 / 12, 'phi': PHI, '1/phi': 1 / PHI, 'pi': math.pi, '1/pi': 1 / math.pi, '6/5': 1.2, '5/6': 5 / 6,
       '9/12': .75, '10/12': 10 / 12, '4/3': 4 / 3, '3/2': 1.5, '2/3': 2 / 3, '1/ln(phi^2)': 1 / math.log(PHI ** 2), '1/phi^2': 1 / PHI ** 2, '1/2': .5}
near = lambda v: ' | '.join(f'{k} {100 * (v / x - 1):+.2f} %' for k, x in sorted(SEV.items(), key=lambda kv: abs(math.log(v / kv[1])))[:2])
rows = [json.loads(l) for l in open(os.path.join(HERE, 'fleet_records.jsonl')) if '"error"' not in l]
by = defaultdict(dict)
for r in rows:
    by[r['chip']].setdefault(r['stamp'], r)
for chip, stamps in sorted(by.items()):
    R = sorted(stamps.values(), key=lambda r: r['stamp'])
    frozen = []
    for i in range(1, len(R)):
        a, b = R[i - 1], R[i]
        if a['t1'] == b['t1'] and a['t2'] == b['t2'] and a['readout'] == b['readout']:
            frozen.append((a['stamp'][:16], b['stamp'][:16]))
    rat = [r['ratio'] for r in R if r['ratio']]
    print(f"\n{chip}: {len(R)} distinct stamps {R[0]['stamp'][:10]} .. {R[-1]['stamp'][:10]}; qubits {R[-1]['n']}; readout {R[-1]['readout']} us")
    print(f"  FROZEN (new stamp, identical medians): {len(frozen)}" + ''.join(f"\n     {x} -> {y}" for x, y in frozen))
    if rat:
        s = sorted(rat)
        print(f"  T2:T1 floor {s[0]:.4f} ({near(s[0])}) | 2nd {s[1] if len(s) > 1 else float('nan'):.4f} | median {S.median(rat):.4f} ({near(S.median(rat))}) | top {s[-1]:.4f} | sd {S.pstdev(rat):.4f}")
        print('  series: ' + ' '.join(f'{x:.3f}' for x in rat))
