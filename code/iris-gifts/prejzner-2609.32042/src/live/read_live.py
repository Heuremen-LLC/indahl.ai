#!/usr/bin/env python3
"""Readings P1-P4 of PLAN.md Addendum 1 (written 30 Oct before any model call) for the G1 live arm. Written before the tenth run finished.
Our runs: runs/<model>_<quant>_r<rep>.jsonl. His: release_data/matrices/per_task_main67.csv (pass per task, main67, repair off) and
release_data/trajectories/<slug>.jsonl (his replies), read as data. Exact two-sided McNemar on discordant tasks."""
import os, json, csv, math, collections
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); REL = G + '/theirs/release_data'; RUNS = G + '/runs'
import hashlib
_sha = lambda s: None if s is None else hashlib.sha256(s.encode('utf-8')).hexdigest()   # the package keeps reply hashes, not reply text
FILES = [('bielik-11b-v3', 'Q4_K_M', 'v3_11b_2026-06-18__q4_no_repair'), ('bielik-11b-v3', 'Q3_K_M', 'v3_11b_2026-06-18__q3_no_repair'),
         ('bielik-11b-v3', 'Q2_K', 'v3_11b_2026-06-18__q2_no_repair'), ('llama-pllum-8b', 'Q3_K_M', 'v3_pllum_2026-07-29__q3_main_no_repair'),
         ('llama-pllum-8b', 'Q2_K', 'v3_pllum_2026-07-29__q2_main_no_repair')]
HIS = collections.defaultdict(dict)
for r in csv.DictReader(open(REL + '/matrices/per_task_main67.csv')):
    if r['suite'] == 'main67' and r['repair'] == 'off': HIS[(r['model_id'], r['quant'])][r['task_id']] = int(r['passed'])
def ours(m, q, rep):
    p = '%s/%s_%s_r%d.jsonl' % (RUNS, m, q, rep)
    return {d['task_id']: d for d in map(json.loads, open(p, encoding='utf-8'))} if os.path.exists(p) else None
def his_traj(slug): return {d['task_id']: d for d in map(json.loads, open('%s/trajectories/%s.jsonl' % (REL, slug), encoding='utf-8'))}
def mcnemar(b, c): n = b + c; return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n)
texts = lambda d: [s['raw_sha256'] if 'raw_sha256' in s else _sha(s.get('raw_model_output')) for s in d['steps']]
R1 = {}
print('P1 repeat floor and P2 ours against his, per file (main67 tasks)')
for m, q, slug in FILES:
    a, b = ours(m, q, 1), ours(m, q, 2); h = HIS[(m, q)]; ht = his_traj(slug)
    if a is None or b is None: print('  %s %s: runs missing' % (m, q)); continue
    ids = sorted(a); R1[(m, q)] = a; assert set(ids) == set(b) == set(h), (m, q)
    pf = sum(a[i]['passed'] != b[i]['passed'] for i in ids); tf = sum(texts(a[i]) != texts(b[i]) for i in ids)
    on = sum(a[i]['passed'] for i in ids); hn = sum(h[i] for i in ids)
    x = sum(a[i]['passed'] and not h[i] for i in ids); y = sum(h[i] and not a[i]['passed'] for i in ids)
    first = sum(1 for i in ids if a[i]['steps'] and ht[i]['steps'] and texts(a[i])[0] == texts(ht[i])[0])
    allsame = sum(1 for i in ids if texts(a[i]) == texts(ht[i]))
    print('  %-15s %-6s ours %d and %d of %d pass | P1 pass differs %d, any reply text differs %d | his pass %d | P2 ours r1 vs his: pass only ours %d, only his %d (exact p %.3g) | first reply identical to his %d, every reply identical %d' % (
        m, q, on, sum(b[i]['passed'] for i in ids), len(ids), pf, tf, hn, x, y, mcnemar(x, y), first, allsame))
def paired(m, q1, q2, label, printed):
    a, b = R1.get((m, q1)), R1.get((m, q2))
    if not a or not b: return
    ids = sorted(a); n11 = sum(a[i]['passed'] and b[i]['passed'] for i in ids); n10 = sum(a[i]['passed'] and not b[i]['passed'] for i in ids)
    n01 = sum((not a[i]['passed']) and b[i]['passed'] for i in ids); n00 = len(ids) - n11 - n10 - n01
    print('  %s %s %s to %s on ours (r1): %d to %d of %d | paired (both, first only, second only, neither) %d/%d/%d/%d, exact p %.3g | his %s' % (
        label, m, q1, q2, n11 + n10, n11 + n01, len(ids), n11, n10, n01, n00, mcnemar(n10, n01), printed))
print('\nP3 the collapse step and P4 the 11B dip')
paired('bielik-11b-v3', 'Q3_K_M', 'Q2_K', 'P3', '48 to 3')
paired('llama-pllum-8b', 'Q3_K_M', 'Q2_K', 'P3', '15 to 1')
paired('bielik-11b-v3', 'Q4_K_M', 'Q3_K_M', 'P4', '36 against 48')
