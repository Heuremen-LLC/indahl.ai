#!/usr/bin/env python3
"""scoreboard.py (8 Nov, Flight Mode v2): inside confidence (p, what the seat said) against outside evaluation, per seat.
y = 1 when the claim is grounded (exact quote in the shown chunk) AND the triangle's external judge gives q >= 0.5; else 0.
Per seat: n, mean p, mean q, grounded rate, accuracy (mean y), Brier (p vs y), ECE (5 bins), confident-wrong rate (p >= 0.8, y = 0),
no-p rate (seat gave no number). Also locks the held-out plant set (holdout_plants.json) the first time it runs.
Writes scoreboard.json (the map and the demo read it) and prints the table."""
import json, os, sqlite3, hashlib, collections as C
H = os.path.dirname(os.path.abspath(__file__))
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=15)
HO = os.path.join(H, 'holdout_plants.json')
if not os.path.exists(HO):   # gap 9: a fixed held-out set, locked once, never trained on
    ids = [r[0] for r in c.execute("select id from calib where truth is not null")]
    pick = sorted(ids, key=lambda i: hashlib.sha256(f'holdout-{i}'.encode()).hexdigest())[:200]
    json.dump({'locked': True, 'n': len(pick), 'rule': 'first 200 calib ids by sha256("holdout-<id>")', 'ids': sorted(pick)}, open(HO, 'w'))
try: rows = c.execute("select model, seat, triangle, tag, grounded, p, q_judge, demo, lp from pq").fetchall()
except sqlite3.OperationalError:
    try: rows = [r + (None,) for r in c.execute("select model, seat, triangle, tag, grounded, p, q_judge, demo from pq").fetchall()]
    except sqlite3.OperationalError: rows = []
S = C.defaultdict(list)
def wilson(k, n, z=1.96):
    if not n: return None
    ph = k / n; d = 1 + z * z / n; m = (ph + z * z / (2 * n)) / d; h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0, m - h), 3), round(min(1, m + h), 3)]
LPS = C.defaultdict(list)
for m, seat, tri, tag, g, p, q, demo, lp in rows:
    S[m].append((g, p, q))
    if lp is not None: LPS[m].append((lp, 1 if (g and q is not None and q >= 0.5) else 0))
out = {}
for m, xs in S.items():
    ys = [(1 if (g and q is not None and q >= 0.5) else 0) for g, p, q in xs]
    ps = [(p, y) for (g, p, q), y in zip(xs, ys) if p is not None]
    brier = sum((p - y) ** 2 for p, y in ps) / len(ps) if ps else None
    bins = C.defaultdict(list); [bins[min(4, int(p * 5))].append((p, y)) for p, y in ps]
    ece = sum(len(b) / len(ps) * abs(sum(p for p, _ in b) / len(b) - sum(y for _, y in b) / len(b)) for b in bins.values()) if ps else None
    qs = [q for _, _, q in xs if q is not None]
    out[m] = {'n': len(xs), 'mean_p': round(sum(p for p, _ in ps) / len(ps), 3) if ps else None, 'mean_q': round(sum(qs) / len(qs), 3) if qs else None,
              'grounded': round(sum(g for g, _, _ in xs) / len(xs), 3), 'accuracy': round(sum(ys) / len(ys), 3),
              'brier': round(brier, 3) if brier is not None else None, 'ece': round(ece, 3) if ece is not None else None,
              'confident_wrong': round(sum(1 for p, y in ps if p >= 0.8 and y == 0) / len(ps), 3) if ps else None,
              'acc_ci95': wilson(sum(ys), len(ys)),   # Sage: n=18 is a wide interval; every number carries it
              'no_p': round(sum(1 for _, p, _ in xs if p is None) / len(xs), 3),
              'mean_lp': round(sum(a for a, _ in LPS[m]) / len(LPS[m]), 3) if LPS[m] else None,
              'brier_lp': round(sum((a - y) ** 2 for a, y in LPS[m]) / len(LPS[m]), 3) if LPS[m] else None}   # gap 8: token confidence vs outcome
# gap 6: council diversity. Per (cycle, triangle): share of voice pairs whose R1 outcomes differ. A promotion that drives this to ~0 is a collapse.
try: oc = c.execute("select cycle, triangle, seat, max(outcome) from pq where outcome is not null and outcome != '' group by cycle, triangle, seat").fetchall()
except sqlite3.OperationalError: oc = []
by = C.defaultdict(list); [by[(cy, t)].append(o) for cy, t, _, o in oc]
dis = [sum(a != b for i, a in enumerate(v) for b in v[i + 1:]) / (len(v) * (len(v) - 1) / 2) for v in by.values() if len(v) >= 2]
diversity = round(sum(dis) / len(dis), 3) if dis else None
json.dump({'seats': out, 'rows': len(rows), 'holdout': json.load(open(HO))['n'], 'disagreement': diversity, 'disagreement_n': len(dis)}, open(os.path.join(H, 'scoreboard.json'), 'w'), indent=1)
print(f"{'model':18s} {'n':>4s} {'p':>5s} {'q':>5s} {'grnd':>5s} {'acc':>5s} {'brier':>6s} {'ece':>5s} {'cf-wrong':>8s} {'no-p':>5s} {'lp':>5s} {'br-lp':>6s}")
for m, r in sorted(out.items(), key=lambda kv: -kv[1]['n']):
    f = lambda v: '-' if v is None else f'{v:.2f}'
    print(f"{m:18s} {r['n']:4d} {f(r['mean_p']):>5s} {f(r['mean_q']):>5s} {f(r['grounded']):>5s} {f(r['accuracy']):>5s} {f(r['brier']):>6s} {f(r['ece']):>5s} {f(r['confident_wrong']):>8s} {f(r['no_p']):>5s} {f(r['mean_lp']):>5s} {f(r['brier_lp']):>6s}  acc95 {r['acc_ci95']}")
print(f'rows {len(rows)} · holdout plants locked: {json.load(open(HO))["n"]} · council disagreement {diversity} over {len(dis)} triangle-cycles')
