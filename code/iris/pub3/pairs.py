"""pairs.py (31 Oct 2026): every pairwise reading of the serving study with one rule (faultsbench2_mac_builds/PLAN.md addendum 1):
I = items byte-identical between bare and bare_copy in both runs; CONSISTENT if none of I changes across, ABOVE if any does, CANNOT_TELL
if I holds fewer than 100. Beside it: each run's own repeat, byte-identical counts across (bare, guard), scored-class changes on gated
families item by item, and the per-family paired bootstrap of seats_compare/compare.py. Writes pairs_results.txt and pairs.json."""
import json, os, sys, random
from math import comb
IB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(IB, 'faultsbench2')); import score as S
MODELS = ['phi4-mini', 'llama3.2_3b', 'qwen2.5_1.5b', 'granite4.1_3b', 'ministral-3_3b']
RUNS = {  # name: (folder holding out/, how a model's subfolder is named, what it is)
 'mac-brew-0.34.2-30oct': None, 'mac-brew-0.34.2-31oct': ('faultsbench2_mac_builds', 'brew-0.34.2-today/{m}'),
 'mac-official-0.34.2': ('faultsbench2_mac_builds', 'official-0.34.2/{m}'), 'mac-official-0.34.3': ('faultsbench2_mac_builds', 'official-0.34.3/{m}'),
 '3080-0.34.3-4slots': ('faultsbench2_armature', '{a}'), '3080-0.34.3-4slots-31oct': ('faultsbench2_armature_1slot', '../out_4slot_today/{a}'),
 '3080-0.34.3-1slot': ('faultsbench2_armature_1slot', '{a}')}
def loc(run, m):
    if run == 'mac-brew-0.34.2-30oct': return ('faultsbench2', 'phi4-mini') if m == 'phi4-mini' else ('faultsbench2_mac_cross', m)
    h, pat = RUNS[run]; return h, pat.format(m=m, a='phi4-mini_latest' if m == 'phi4-mini' else m)
def rows(run, m, arm):
    h, mm = loc(run, m); p = os.path.join(IB, h, 'out', mm, arm + '.jsonl')
    return {r['id']: r for r in map(json.loads, open(p))} if os.path.exists(p) else {}
def gate(run, m):
    h, mm = loc(run, m); S.HERE = os.path.join(IB, h); r = S.score(mm)
    fam = {f: not str(v['outcome']).startswith('CANNOT_TELL (repeat') and not str(v['outcome']).startswith('CANNOT_TELL (family') for f, v in r['fam'].items()}
    return dict(passed=r['model_gate'] == 'pass', families=fam)
def cp_upper(n, a=0.05):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2; (lo, hi) = (mid, hi) if (1 - mid) ** n > a / 2 else (lo, mid)
    return hi
PAIRS = [('mac-brew-0.34.2-30oct', 'mac-official-0.34.2', 'B1 build and day (Mac, same version)'),
         ('mac-brew-0.34.2-30oct', 'mac-brew-0.34.2-31oct', 'B1b day only (Mac, same build), defined after the data'),
         ('mac-brew-0.34.2-31oct', 'mac-official-0.34.2', 'B1c build only (Mac, same day), defined after the data'),
         ('mac-official-0.34.2', 'mac-official-0.34.3', 'B2 version (Mac, same build family)'),
         ('3080-0.34.3-4slots', '3080-0.34.3-1slot', 'C1 slots and day (3080, same build)'),
         ('3080-0.34.3-4slots', '3080-0.34.3-4slots-31oct', 'C1b day only (3080, same configuration), defined after the data'),
         ('3080-0.34.3-4slots-31oct', '3080-0.34.3-1slot', 'C1c slots only (3080, same day), defined after the data'),
         ('mac-official-0.34.3', '3080-0.34.3-1slot', 'C2 machine (version and slots matched)'),
         ('mac-brew-0.34.2-30oct', '3080-0.34.3-4slots', 'Pub #2 pair (reference)')]
L, J, rng = [], {}, random.Random(20261031)
avail = lambda run: all(rows(run, m, 'bare') for m in MODELS)
L.append('Repeats (bare against bare_copy, byte-identical of 170):')
for run in RUNS:
    if avail(run): L.append(f'  {run:24s} ' + '  '.join(f'{m} {sum(rows(run,m,"bare")[k]["raw"] == rows(run,m,"bare_copy")[k]["raw"] for k in rows(run,m,"bare") if k in rows(run,m,"bare_copy"))}' for m in MODELS))
for a, b, tag in PAIRS:
    if not (avail(a) and avail(b)): L.append(f'\n== {tag}: {a} against {b}: NOT RUN YET'); continue
    L.append(f'\n== {tag}: {a} against {b}'); up = dn = 0; J[tag] = {}
    for m in MODELS:
        Ab, Ac, Bb, Bc, Ag, Bg = rows(a, m, 'bare'), rows(a, m, 'bare_copy'), rows(b, m, 'bare'), rows(b, m, 'bare_copy'), rows(a, m, 'guard'), rows(b, m, 'guard')
        I = [k for k in Ab if k in Ac and k in Bb and k in Bc and Ab[k]['raw'] == Ac[k]['raw'] and Bb[k]['raw'] == Bc[k]['raw']]
        ch = sum(Ab[k]['raw'] != Bb[k]['raw'] for k in I); o = 'CANNOT_TELL' if len(I) < 100 else ('CONSISTENT' if ch == 0 else 'ABOVE')
        across = sum(Ab[k]['raw'] == Bb[k]['raw'] for k in Ab if k in Bb); gacross = sum(Ag[k]['raw'] == Bg[k]['raw'] for k in Ag if k in Bg)
        ga, gb = gate(a, m), gate(b, m); flips = 0; fams = {}
        for f in ('P1', 'P2', 'P3', 'P4'):
            ks = [k for k in S.IT if S.IT[k]['fam'] == f and S.IT[k].get('kind') not in ('control', 'gw') and k in Ab and k in Bb]
            pr = []
            for k in ks:
                ca, cb = S.cls(S.IT[k], Ab[k]['raw'], 'bare', Ab[k].get('done_reason')), S.cls(S.IT[k], Bb[k]['raw'], 'bare', Bb[k].get('done_reason'))
                if ca in ('FAULT', 'OK') and cb in ('FAULT', 'OK'): pr.append((cb == 'FAULT', ca == 'FAULT'))
            ok = ga['passed'] and gb['passed'] and ga['families'][f] and gb['families'][f]
            fl = sum(x != y for x, y in pr)
            if ok: flips += fl; up += sum(x and not y for x, y in pr); dn += sum(y and not x for x, y in pr)
            if not ok or len(pr) < 10: fams[f] = f'CANNOT_TELL ({"gate" if not ok else "few"}, n {len(pr)}, flips {fl})'; continue
            d = sum(x - y for x, y in pr) / len(pr); bs = sorted(sum(x - y for x, y in (rng.choice(pr) for _ in pr)) / len(pr) for _ in range(2000))
            lo, hi = bs[49], bs[1949]; fams[f] = f'{"ABOVE" if lo > 0 else "BELOW" if hi < 0 else "CONSISTENT"} {d:+.3f} [{lo:+.3f}, {hi:+.3f}] n {len(pr)} flips {fl}'
        J[tag][m] = dict(I=len(I), changed=ch, outcome=o, bare_identical=across, guard_identical=gacross, gated_class_flips=flips, families=fams)
        L.append(f'  {m:15s} I={len(I):3d} changed {ch:3d} {o}' + (f' (95% upper {cp_upper(len(I)):.3f})' if o == 'CONSISTENT' else '') + f' | identical across bare {across}/170 guard {gacross}/170 | gated class flips {flips}')
        L.append('      ' + ' | '.join(f'{f} {v}' for f, v in fams.items()))
    n = up + dn; p = min(1.0, 2 * sum(comb(n, i) for i in range(max(up, dn), n + 1)) / 2 ** n) if n else 1.0
    L.append(f'  class flips in gated families: to fault on {b} {up}, to OK {dn}, exact two-sided p {p:.3f}')
H = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(H, 'pairs_results.txt'), 'w').write('\n'.join(L) + '\n'); json.dump(J, open(os.path.join(H, 'pairs.json'), 'w'), indent=1); print('\n'.join(L))
