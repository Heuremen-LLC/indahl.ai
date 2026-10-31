#!/usr/bin/env python3
"""T1 and P4b of PLAN.md Addendum 2 (2836e40, committed before this ran; defined after the data). Our code; his files read as data."""
import os, json, csv, math, collections
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); REL = G + '/theirs/release_data'; RUNS = G + '/runs'
import hashlib
_sha = lambda s: None if s is None else hashlib.sha256(s.encode('utf-8')).hexdigest()   # the package keeps reply hashes, not reply text
FILES = [('bielik-11b-v3', 'Q4_K_M', 'v3_11b_2026-06-18__q4_no_repair'), ('bielik-11b-v3', 'Q3_K_M', 'v3_11b_2026-06-18__q3_no_repair'),
         ('bielik-11b-v3', 'Q2_K', 'v3_11b_2026-06-18__q2_no_repair'), ('llama-pllum-8b', 'Q3_K_M', 'v3_pllum_2026-07-29__q3_main_no_repair'),
         ('llama-pllum-8b', 'Q2_K', 'v3_pllum_2026-07-29__q2_main_no_repair')]
TWINS = ['v3_chain_001', 'v3_chain_004', 'v3_chain_005', 'v3_chain_006', 'v3_chain_007', 'v3_chain_010', 'v3_chain_en_001', 'v3_chain_en_003', 'v3_chain_en_004', 'v3_chain_en_005']
HIS = collections.defaultdict(dict)
for r in csv.DictReader(open(REL + '/matrices/per_task_main67.csv')):
    if r['suite'] == 'main67' and r['repair'] == 'off': HIS[(r['model_id'], r['quant'])][r['task_id']] = int(r['passed'])
def jl(p): return {d['task_id']: d for d in map(json.loads, open(p, encoding='utf-8'))}
texts = lambda d: [s['raw_sha256'] if 'raw_sha256' in s else _sha(s.get('raw_model_output')) for s in d['steps']]
def mcnemar(b, c): n = b + c; return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n)
print('T1 twin pairs whose every raw reply is identical between the two members (of 10)')
tot_o = tot_h = 0
for m, q, slug in FILES:
    o = jl('%s/%s_%s_r1.jsonl' % (RUNS, m, q)); h = jl('%s/trajectories/%s.jsonl' % (REL, slug))
    assert all(t in o and t + '_arith' in o for t in TWINS)
    so = sum(texts(o[t]) == texts(o[t + '_arith']) for t in TWINS); sh = sum(texts(h[t]) == texts(h[t + '_arith']) for t in TWINS); tot_o += so; tot_h += sh
    print('  %-15s %-6s ours %2d | his %2d' % (m, q, so, sh))
print('  all five files: ours %d of 50 | his %d of 50' % (tot_o, tot_h))
print('\nP4b Bielik-11B Q4_K_M against Q3_K_M with both members of every twin pair removed')
drop = set(TWINS) | {t + '_arith' for t in TWINS}
o4, o3 = jl(RUNS + '/bielik-11b-v3_Q4_K_M_r1.jsonl'), jl(RUNS + '/bielik-11b-v3_Q3_K_M_r1.jsonl')
ids = sorted(set(o4) - drop)
for nm, a, b in (('ours', {i: o4[i]['passed'] for i in ids}, {i: o3[i]['passed'] for i in ids}), ('his', {i: HIS[('bielik-11b-v3', 'Q4_K_M')][i] for i in ids}, {i: HIS[('bielik-11b-v3', 'Q3_K_M')][i] for i in ids})):
    n10 = sum(a[i] and not b[i] for i in ids); n01 = sum(b[i] and not a[i] for i in ids)
    print('  %-4s %d tasks: Q4_K_M %d, Q3_K_M %d | Q4 only %d, Q3 only %d, exact p %.3g' % (nm, len(ids), sum(map(bool, a.values())), sum(map(bool, b.values())), n10, n01, mcnemar(n10, n01)))
