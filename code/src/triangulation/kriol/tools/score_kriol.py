#!/usr/bin/env python3
"""score_kriol.py -- WAS THE MODEL'S KRIOL ACTUALLY KRIOL? (Bones, 10 Oct 2026.)
Scores model output already on disk against the reference vocabulary built from the Holi Baibul.
Nothing from the source text is printed or stored -- only the share of a reply's words that are
attested Kriol, and the same share for seats that are NOT Kriol, which is the none.
"""
import json, os, re, sys
from collections import defaultdict
K = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'kriol_lex.json')
LEX = set(json.load(open(K))['lex'])
W = os.path.expanduser('~/bones-forge/watch/')
EN_ONLY = {'the','and','that','have','with','this','from','they','which','their','would','there',
           'about','sides','number','answer','hexagon','value','known','exact','words','language'}


def share(txt):
    ws = re.findall(r"[a-zA-Z][a-zA-Z'\-]*", txt.lower())
    ws = [w for w in ws if len(w) > 1]
    if not ws: return None, 0
    return sum(1 for w in ws if w in LEX) / len(ws), len(ws)


rows = []
for fn in ('seat_real.jsonl', 'mood2.jsonl', 'seat_probe.jsonl'):
    p = os.path.join(W, fn)
    if os.path.exists(p):
        for l in open(p):
            try: rows.append((fn, json.loads(l)))
            except Exception: pass
print(f'  ATTESTED-KRIOL SHARE of model output, scored against {len(LEX):,} word types')
print(f'  from the Holi Baibul. The none is every seat that is NOT Kriol.\n')
by = defaultdict(list)
for fn, r in rows:
    lang = r.get('lang', '?')
    s, n = share(r.get('reply', '') or '')
    if s is not None and n >= 4:
        by[lang].append(s)
print(f"  {'seat language':<22}{'n replies':>10}{'mean attested-Kriol share':>28}")
for lang, v in sorted(by.items(), key=lambda kv: -sum(kv[1])/len(kv[1])):
    m = sum(v)/len(v)
    star = '   <-- KRIOL' if 'Kriol' in lang else ''
    print(f'  {lang:<22}{len(v):>10}{m:>28.3f}{star}')
kr = by.get('Australian Kriol', [])
oth = [x for lang, v in by.items() if 'Kriol' not in lang for x in v]
if kr and oth:
    import statistics as st
    mk, mo = st.mean(kr), st.mean(oth)
    sk = st.stdev(kr)/len(kr)**0.5 if len(kr) > 1 else float('nan')
    so = st.stdev(oth)/len(oth)**0.5 if len(oth) > 1 else float('nan')
    d = mk - mo; w = (sk**2 + so**2)**0.5
    print(f'\n  Kriol {mk:.3f} +- {sk:.3f} (n={len(kr)})   every other seat {mo:.3f} +- {so:.3f} (n={len(oth)})')
    print(f'  difference {d:+.3f} +- {w:.3f} = {abs(d)/w:.2f} widths')
    print(f'\n  NOTE THE CEILING PROBLEM, stated not hidden: Kriol is English-lexifier, so an')
    print(f'  English reply already scores high on a Kriol word list. The number above is a')
    print(f'  FLOOR on how Kriol the output is, never proof that it IS Kriol.')
