"""compare.py: the SEAT CHECK of faultsbench_armature/PLAN.md and faultsbench2_armature/PLAN.md, for bench v2 (scorer b87a2b08), as committed:
per model present on both seats with the same weights digest, (1) the share of byte-identical replies per arm (bare, bare_copy, guard), and
(2) per family the paired bare fault-rate difference (Armature minus Mac, items readable on both seats), bootstrap over items 2,000, 95%:
CONSISTENT if the interval holds 0, else ABOVE/BELOW, and that family is labelled seat-dependent. A model whose known-good gate fails on either seat
reads CANNOT_TELL. Seats are never pooled. Writes seats_compare/results.json and results.txt."""
import json, os, sys, random
IB = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(IB, 'faultsbench2')); import score as S
PAIRS = [('phi4-mini', 'faultsbench2/out/phi4-mini', 'faultsbench2_armature/out/phi4-mini_latest')] + \
        [(m, f'faultsbench2_mac_cross/out/{m}', f'faultsbench2_armature/out/{m}') for m in ('llama3.2_3b', 'qwen2.5_1.5b', 'granite4.1_3b', 'ministral-3_3b')]
def rows(d, arm):
    p = os.path.join(IB, d, arm + '.jsonl'); return {r['id']: r for r in map(json.loads, open(p))} if os.path.exists(p) else {}
def gate(d):
    """30 Oct correction (before any family reading was printed): the gate is the committed v2 scorer's own (score.score on that folder):
    model gate = exact repeats agree on the scored class >= 95%; family gate = P1/P3 controls right >= 80% of >= 10 read, P2/P4 readable >= 80%."""
    folder, m = os.path.split(d.rstrip('/')); S.HERE = os.path.join(IB, os.path.dirname(folder)) if False else os.path.join(IB, d.split('/out/')[0])
    r = S.score(d.split('/out/')[1])
    fam = {f: not str(v['outcome']).startswith('CANNOT_TELL (repeat') and not str(v['outcome']).startswith('CANNOT_TELL (family') for f, v in r['fam'].items()}
    return dict(model_gate=r['model_gate'], class_repeat_agree=r['class_repeat_agree'], families=fam, passed=r['model_gate'] == 'pass')
rng = random.Random(20261030); out = {}
for m, dm, da in PAIRS:
    gm, ga = gate(dm), gate(da); res = dict(gate_mac=gm, gate_armature=ga, identical={}, families={})
    for arm in ('bare', 'bare_copy', 'guard'):
        A, M = rows(da, arm), rows(dm, arm); ks = [k for k in A if k in M]
        res['identical'][arm] = [sum(A[k]['raw'] == M[k]['raw'] for k in ks), len(ks)]
    A, M = rows(da, 'bare'), rows(dm, 'bare')
    for f in ('P1', 'P2', 'P3', 'P4'):
        ks = [k for k in S.IT if S.IT[k]['fam'] == f and S.IT[k].get('kind') not in ('control', 'gw') and k in A and k in M]
        pr = []
        for k in ks:
            ca, cm = S.cls(S.IT[k], A[k]['raw'], 'bare', A[k].get('done_reason')), S.cls(S.IT[k], M[k]['raw'], 'bare', M[k].get('done_reason'))
            if ca in ('FAULT', 'OK') and cm in ('FAULT', 'OK'): pr.append((ca == 'FAULT', cm == 'FAULT'))
        okf = gm['passed'] and ga['passed'] and gm['families'][f] and ga['families'][f]
        if not okf or len(pr) < 10: res['families'][f] = dict(outcome='CANNOT_TELL', why='gate failed (%s/%s)' % ('Mac ok' if gm['passed'] and gm['families'][f] else 'Mac fails', 'Armature ok' if ga['passed'] and ga['families'][f] else 'Armature fails') if not okf else 'too few read on both seats', n=len(pr)); continue
        d = sum(a - b for a, b in pr) / len(pr); bs = sorted(sum(a - b for a, b in (rng.choice(pr) for _ in pr)) / len(pr) for _ in range(2000))
        lo, hi = bs[49], bs[1949]; o = 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'
        res['families'][f] = dict(outcome=o, diff=round(d, 3), ci=[round(lo, 3), round(hi, 3)], n=len(pr), armature_rate=round(sum(a for a, b in pr) / len(pr), 3), mac_rate=round(sum(b for a, b in pr) / len(pr), 3))
    out[m] = res
json.dump(out, open(os.path.join(IB, 'seats_compare', 'results.json'), 'w'), indent=1)
L = []
for m, r in out.items():
    L.append(f"{m}: model gate Mac {r['gate_mac']['model_gate']} ({r['gate_mac']['class_repeat_agree']}) Armature {r['gate_armature']['model_gate']} ({r['gate_armature']['class_repeat_agree']}); identical replies " + ', '.join(f"{a} {v[0]}/{v[1]}" for a, v in r['identical'].items()))
    for f, v in r['families'].items(): L.append(f"   {f}: " + (f"{v['outcome']} diff {v['diff']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}] n {v['n']} (Armature {v['armature_rate']:.3f}, Mac {v['mac_rate']:.3f})" if 'diff' in v else f"{v['outcome']} ({v['why']}, n {v['n']})"))
open(os.path.join(IB, 'seats_compare', 'results.txt'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
