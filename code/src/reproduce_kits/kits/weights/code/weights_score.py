"""weights_score.py: the summary step of weights_index/weights_tick.py (lines 70 to 76 and the headline and ever blocks of out, lines 84 to 86), as
written. Reads data/repos.json (the file hashes Hugging Face reported on each pass and every change between passes), writes out.json."""
import json
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
store = json.load(open('data/repos.json'))
evs = sorted([(i, c) for i, r in store.items() for c in r['changes'] if c['kind'] == 'CHANGED'], key=lambda x: x[1]['t'], reverse=True)
cmp = [r for r in store.values() if r.get('last_pair') in ('SAME', 'CHANGED')]; ch = [r for r in cmp if r['last_pair'] == 'CHANGED']
lo, hi = K.wilson(len(ch), len(cmp)) if cmp else (0, 1)
oc = 'NOTHING_RETURNED' if not cmp else (K.ABOVE if lo > 0.01 else (K.CONSISTENT if hi < 0.01 else K.CANNOT_TELL))
ever_n = len({i for i, c in evs}); ever_of = len({i for i, r in store.items() if r.get('last_pair') in ('SAME', 'CHANGED')} | {i for i, c in evs}); elo, ehi = K.wilson(ever_n, ever_of) if ever_of else (0, 1)
json.dump(dict(headline=dict(of=len(cmp), n=len(ch), share=round(len(ch) / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc),
               ever=dict(of=ever_of, n=ever_n, events=len(evs), share=round(ever_n / ever_of, 4) if ever_of else None, share_lo=round(elo, 4), share_hi=round(ehi, 4))), open('out.json', 'w'), indent=1)
