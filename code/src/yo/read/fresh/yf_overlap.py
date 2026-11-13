"""yf_overlap.py -- overlap receipt for PLAN_YO_FRESH Addendum 1: fresh papers vs YO Read's 671 (ids, arXiv without version, normalised titles, ratio > 0.9)."""
import json, re, os, importlib.util, unicodedata, difflib
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); Q = os.path.expanduser('~/bones-forge/qia_leads/')
spec = importlib.util.spec_from_file_location('yd', R + '/yr_data.py'); yd = importlib.util.module_from_spec(spec); spec.loader.exec_module(yd)
old = {k: r for k, r, _ in yd.papers()}
fresh = sorted({json.loads(l)['paper'] for l in open(H + '/data/test_items_fresh.jsonl')})
L = json.load(open(Q + 'matrix_page/list.json')); rows = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
by = {}
for r in rows: by.setdefault(yd.norm(r['link']), r)
ax = lambda k: re.sub(r'v\d+$', '', k[3:]) if k.startswith('ax:') else None
tn = lambda t: re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', t or '').lower()).strip()
oax = {ax(k) for k in old if ax(k)}; ot = [tn(r.get('study')) for r in old.values() if tn(r.get('study'))]
ids = sum(k in old for k in fresh); axs = sum(bool(ax(k)) and ax(k) in oax for k in fresh); ex = ne = 0
for k in fresh:
    t = tn(by[k].get('study'))
    if not t: continue
    if t in ot: ex += 1; continue
    if any(abs(len(t) - len(o)) < 15 and difflib.SequenceMatcher(None, t, o).ratio() > 0.9 for o in ot): ne += 1
print(f'fresh {len(fresh)} vs old {len(old)}: id {ids}, arXiv (version stripped) {axs}, exact title {ex}, title ratio > 0.9 {ne}')
