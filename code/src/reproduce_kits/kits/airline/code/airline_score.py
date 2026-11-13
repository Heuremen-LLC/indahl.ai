"""airline_score.py: the headline step of bts_index/airline_summary.py (NAME, line 7, table() lines 12 to 20 and the headline block, lines 21 to 25), as written.
Reads data/results.json, the per-airline comparisons bts_index/airline_tick.py wrote from the BTS month files, and writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json
import heuremen_kit as K
NAME = dict(AA='American', AS='Alaska', B6='JetBlue', DL='Delta', F9='Frontier', G4='Allegiant', HA='Hawaiian', MQ='Envoy', NK='Spirit', OH='PSA', OO='SkyWest', UA='United', WN='Southwest', YX='Republic')
r = json.load(open('data/results.json'))
a = {NAME.get(c, c) + ' (' + c + ')': dict(routes=v['routes'], outcome=v['outcome']) for c, v in r['c26_25'].items()}
nb = [k for k, v in a.items() if v['outcome'] == 'ABOVE']; n = len([v for v in a.values() if v['outcome'] != 'NOTHING_RETURNED'])
lo, hi = K.wilson(len(nb), n)
json.dump(dict(read=r['t'], months=r['months'], headline_n=len(nb), headline_of=n, headline=dict(of=n, n=len(nb), share=round(len(nb) / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome='CANNOT_TELL', above=nb)), open('out.json', 'w'), indent=1)
