"""change_score.py: the lifespan step of change_index/change_tick.py (days(), lrows and life_of(), lines 128 to 143), as written. Reads data/rows.json
(the dated rows the desk keeps from each vendor page), writes out.json."""
import json, statistics as S, datetime as D
store = json.load(open('data/rows.json')); rows = list(store['rows'].values())
def days(a, b): return (D.date.fromisoformat(b) - D.date.fromisoformat(a)).days
lrows = [r for r in rows if r.get('present') and r.get('released') and r['shutdown'] and not r['tentative']]
def life_of(rs):
    x = [days(r['released'], r['shutdown']) for r in rs]; m = S.median(x)
    return dict(n=len(x), median=int(m) if m == int(m) else m, shortest=min(x), under180=len([y for y in x if y < 180]), share=round(len([y for y in x if y < 180]) / len(x), 3))
lifespan = {}
if lrows:
    lifespan['Google'] = life_of(lrows)
    pv = [r for r in lrows if 'preview' in r['name'].lower()]; ot = [r for r in lrows if 'preview' not in r['name'].lower()]
    if pv: lifespan['Google, names with preview'] = life_of(pv)
    if ot: lifespan['Google, other names'] = life_of(ot)
json.dump(dict(lifespan=lifespan), open('out.json', 'w'), indent=1)
