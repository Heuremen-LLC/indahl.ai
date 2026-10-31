"""builds_compare.py (PLAN.md and its addendum 1): known-good repeats per build, then B1 (brew-0.34.2 against official-0.34.2) and B2
(official-0.34.2 against official-0.34.3) on the Mac, five models. Writes builds_results.txt."""
import json, os, sys, random, collections
from math import comb
IB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(IB, 'faultsbench2')); import score as S
MODELS = ['phi4-mini', 'llama3.2_3b', 'qwen2.5_1.5b', 'granite4.1_3b', 'ministral-3_3b']
def where(build, m):
    if build == 'brew-0.34.2': return ('faultsbench2', 'phi4-mini') if m == 'phi4-mini' else ('faultsbench2_mac_cross', m)
    return ('faultsbench2_mac_builds', f'{build}/{m}')
def rows(build, m, arm):
    h, mm = where(build, m); p = os.path.join(IB, h, 'out', mm, arm + '.jsonl')
    return {r['id']: r for r in map(json.loads, open(p))}
def gate(build, m):
    h, mm = where(build, m); S.HERE = os.path.join(IB, h); r = S.score(mm)
    fam = {f: not str(v['outcome']).startswith('CANNOT_TELL (repeat') and not str(v['outcome']).startswith('CANNOT_TELL (family') for f, v in r['fam'].items()}
    return dict(model_gate=r['model_gate'], class_repeat_agree=r['class_repeat_agree'], families=fam, passed=r['model_gate'] == 'pass')
def cp_upper(k, n, a=0.05):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2; tail = sum(comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
        (lo, hi) = (mid, hi) if tail > a / 2 else (lo, mid)
    return hi
L = []; rng = random.Random(20261031)
for b in ('brew-0.34.2', 'official-0.34.2', 'official-0.34.3'):
    for m in MODELS:
        B, C = rows(b, m, 'bare'), rows(b, m, 'bare_copy'); ks = [k for k in B if k in C]
        L.append(f'repeat {b:16s} {m:15s} byte-identical {sum(B[k]["raw"] == C[k]["raw"] for k in ks)}/{len(ks)}')
for (a, b, tag) in (('brew-0.34.2', 'official-0.34.2', 'B1 build, same version'), ('official-0.34.2', 'official-0.34.3', 'B2 version, same build')):
    L.append(''); L.append(f'== {tag}: {a} against {b}')
    up = dn = 0
    for m in MODELS:
        Ab, Ac, Bb, Bc = rows(a, m, 'bare'), rows(a, m, 'bare_copy'), rows(b, m, 'bare'), rows(b, m, 'bare_copy')
        Ag, Bg = rows(a, m, 'guard'), rows(b, m, 'guard')
        I = [k for k in Ab if k in Ac and k in Bb and k in Bc and Ab[k]['raw'] == Ac[k]['raw'] and Bb[k]['raw'] == Bc[k]['raw']]
        ch = sum(Ab[k]['raw'] != Bb[k]['raw'] for k in I)
        across = sum(Ab[k]['raw'] == Bb[k]['raw'] for k in Ab if k in Bb); guard = sum(Ag[k]['raw'] == Bg[k]['raw'] for k in Ag if k in Bg)
        o = 'CANNOT_TELL' if len(I) < 100 else ('CONSISTENT' if ch == 0 else 'ABOVE')
        L.append(f'{m:15s} I={len(I)} changed across builds {ch} ({o}' + (f', 95% upper bound {cp_upper(0, len(I)):.3f})' if o == 'CONSISTENT' else ')')
                 + f' | byte-identical across: bare {across}/170, guard {guard}/170')
        ga, gb = gate(a, m), gate(b, m)
        for f in ('P1', 'P2', 'P3', 'P4'):
            ks = [k for k in S.IT if S.IT[k]['fam'] == f and S.IT[k].get('kind') not in ('control', 'gw') and k in Ab and k in Bb]
            pr = []
            for k in ks:
                ca, cb = S.cls(S.IT[k], Ab[k]['raw'], 'bare', Ab[k].get('done_reason')), S.cls(S.IT[k], Bb[k]['raw'], 'bare', Bb[k].get('done_reason'))
                if ca in ('FAULT', 'OK') and cb in ('FAULT', 'OK'): pr.append((cb == 'FAULT', ca == 'FAULT'))
            ok = ga['passed'] and gb['passed'] and ga['families'][f] and gb['families'][f]
            flips = sum(x != y for x, y in pr); up += sum(x and not y for x, y in pr) if ok else 0; dn += sum(y and not x for x, y in pr) if ok else 0
            if not ok or len(pr) < 10: L.append(f'   {f}: CANNOT_TELL ({"gate failed" if not ok else "too few read"}, n {len(pr)}, class flips {flips})'); continue
            d = sum(x - y for x, y in pr) / len(pr); bs = sorted(sum(x - y for x, y in (rng.choice(pr) for _ in pr)) / len(pr) for _ in range(2000))
            lo, hi = bs[49], bs[1949]; oo = 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'
            L.append(f'   {f}: {oo} diff {d:+.3f} [{lo:+.3f}, {hi:+.3f}] n {len(pr)}, class flips {flips} ({b} minus {a})')
    n = up + dn; p = min(1.0, 2 * sum(comb(n, i) for i in range(max(up, dn), n + 1)) / 2 ** n) if n else 1.0
    L.append(f'direction of class flips in gated families: to fault on {b} {up}, to OK {dn}, exact two-sided p {p:.3f}')
open(os.path.join(IB, 'faultsbench2_mac_builds', 'builds_results.txt'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
