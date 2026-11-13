#!/usr/bin/env python3
"""system_eval.py (8 Nov: a system-wide eval beside the per-seat weight training).
The whole council, not one seat: every judged claim the live council made (demo=0), in fixed windows, from the record.
  per window: deep cycles, claims, grounded rate, accuracy (grounded AND judge q >= 0.5), Brier (p vs that), confident-wrong rate
              (p >= 0.8 and not right), each with a Wilson / normal 95% interval; council disagreement from scoreboard.json.
  per seat:   the same, split into BASE (Ollama copy) and LIVE (its trained MLX adapter, model 'mlx:<seat>@<port>'), so a seat's
              training shows up as a delta with a width, and so does the council around it.
Windows: the last 6 h against the 6 h before it (6 h = about one seat turn plus its need_n live claims at the 8 Nov pace).
Writes system_eval.json (latest) and appends one row to system_eval.jsonl. Read-only on sage_v.db."""
import json, math, os, sqlite3, time, datetime as dt
H = os.path.dirname(os.path.abspath(__file__))
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=30)
now = dt.datetime.utcnow(); W = dt.timedelta(hours=6)
def iso(t): return t.strftime('%Y-%m-%dT%H:%M:%S')
def wilson(k, n):
    if not n: return None
    p = k / n; z = 1.96; d = 1 + z * z / n; m = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 3), round(m - h, 3), round(m + h, 3)]
def block(rows):
    n = len(rows); g = sum(r[0] for r in rows); judged = [r for r in rows if r[2] is not None]
    right = [int(bool(r[0]) and r[2] >= 0.5) for r in judged]
    ps = [(r[1], y) for r, y in zip(judged, right) if r[1] is not None]
    br = [(p - y) ** 2 for p, y in ps]
    bm = sum(br) / len(br) if br else None; bs = (math.sqrt(sum((b - bm) ** 2 for b in br) / (len(br) - 1)) / math.sqrt(len(br))) if len(br) > 1 else None
    cw = sum(1 for p, y in ps if p >= 0.8 and not y)
    return {'claims': n, 'grounded': wilson(g, n), 'accuracy': wilson(sum(right), len(right)), 'judged': len(right),
            'brier': [round(bm, 3), round(bm - 1.96 * bs, 3), round(bm + 1.96 * bs, 3)] if bs is not None else None,
            'confident_wrong': wilson(cw, len(ps))}
def window(a, b):
    rows = c.execute("select grounded, p, q_judge, model, cycle from pq where demo=0 and ts > ? and ts <= ?", (iso(a), iso(b))).fetchall()
    out = {'from': iso(a), 'to': iso(b), 'cycles': len({r[4] for r in rows}), 'council': block(rows), 'seats': {}}
    for m in sorted({r[3] for r in rows}):
        live = m.startswith('mlx:'); seat = m[4:].split('@')[0] if live else m
        out['seats'].setdefault(seat, {})['LIVE' if live else 'BASE'] = block([r for r in rows if r[3] == m])
    return out
cur, prev = window(now - W, now), window(now - W - dt.timedelta(hours=24), now - W)   # Sage 8 Nov: a 3-cycle 'before' is no baseline; before = the 24 h preceding the window
rec = {'ts': iso(now) + 'Z', 'window_h': 6, 'now': cur, 'before': prev}
try: sb = json.load(open(H + '/scoreboard.json')); rec['disagreement'] = {'value': sb.get('disagreement'), 'n': sb.get('disagreement_n')}
except Exception: pass
try: rec['promoted'] = json.load(open(H + '/scheduler_state.json')).get('promoted', {})
except Exception: pass
json.dump(rec, open(H + '/system_eval.json', 'w'), indent=1)
open(H + '/system_eval.jsonl', 'a').write(json.dumps(rec) + '\n')
k = cur['council']; p_ = prev['council']
print(f"council 6h: {cur['cycles']} cycles, {k['claims']} claims, grounded {k['grounded']}, accuracy {k['accuracy']}, brier {k['brier']}, confident-wrong {k['confident_wrong']}"
      f" | 24h before: {prev['cycles']} cycles, grounded {p_['grounded']}, accuracy {p_['accuracy']}")
