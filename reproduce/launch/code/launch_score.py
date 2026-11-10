"""launch_score.py: the scoring step of launch_index/launch_tick.py (lines 28 to 58: flown_watched and the cells), as written, without the count of
launches still waiting, which depends on the time of the run. Reads data/snapshots.jsonl (every stated time as read, with its read time), writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, datetime as D, collections as C
import heuremen_kit as _K
iso = lambda s: D.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
snaps = [json.loads(l) for l in open('data/snapshots.jsonl')]; hist = C.defaultdict(list)
for s in snaps: hist[s['id']].append(s)
FLOWN = {'Success', 'Failure', 'Partial Failure'}; USABLE = {'Second', 'Minute', 'Hour', 'Day'}
LEADS = [(1, '1 day'), (7, '7 days'), (30, '30 days')]
def wil(k, n): return _K.wilson(k, n)
scored = {L: [] for L, _ in LEADS}; flown = 0; coarse = 0; flown_watched = 0
for i, hs in hist.items():
    fin = hs[-1]
    if fin['status'] in FLOWN:
        flown += 1; act = iso(fin['net']); flown_watched += 1 if any(h['status'] not in FLOWN for h in hs) else 0
        for L, _ in LEADS:
            before = [h for h in hs if h['read'] <= act - L * 86400]
            if not before: continue
            b = before[-1]
            if b['prec'] not in USABLE: coarse += 1; continue
            scored[L].append((fin['provider'], (act - iso(b['net'])) / 3600))
cells = []
def cell(lbl, ll, rows):
    n = len(rows)
    if not n: return None
    sl = sorted(abs(x) for _, x in rows); med = sl[n // 2] if n % 2 else (sl[n // 2 - 1] + sl[n // 2]) / 2; k = sum(1 for _, x in rows if abs(x) > 24); a, b = wil(k, n)
    oc = 'CANNOT_TELL' if (n < 30 or ll != '7 days') else ('ABOVE' if a > 0.25 else ('CONSISTENT' if b < 0.10 else 'CANNOT_TELL'))
    sg = sorted(x for _, x in rows); msg = sg[n // 2] if n % 2 else (sg[n // 2 - 1] + sg[n // 2]) / 2
    return dict(who=lbl, lead=ll, n=n, median_abs_slip_h=round(med, 1), median_signed_slip_h=round(msg, 1), later_than_24h=sum(1 for _, x in rows if x > 24), earlier_than_24h=sum(1 for _, x in rows if x < -24), over_24h=k, share=round(k / n, 3), lo=round(a, 3), hi=round(b, 3), outcome=oc)
for L, ll in LEADS:
    c = cell('All providers', ll, scored[L]); cells.append(c) if c else None
    byp = C.defaultdict(list)
    for p, x in scored[L]: byp[p or 'Unknown'].append((p, x))
    for p, rs in sorted(byp.items(), key=lambda kv: -len(kv[1])):
        if len(rs) >= 10:
            c = cell(p, ll, rs); cells.append(c) if c else None
json.dump(dict(flown=flown, flown_watched=flown_watched, coarse=coarse, cells=cells), open('out.json', 'w'), indent=1)
