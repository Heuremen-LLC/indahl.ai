"""Referee second pass: share rows (second reading B) under Addendum 6.1/6.3/6.5, and the with/without-6.5 flip count over every view."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from second_pass import *

def share(view, per, use65=True):
    vals = view_vals(view, per)
    names = ['Facebook', 'Instagram'] if view[0] == 'combined' else [NAMES[view[1]]]
    scope = 'ads' if view[0] == 'ads' else ('nonads' if view[0] == 'main' and view[1] in ADS else 'all')
    so, no = vals['solely'], vals['not_']
    if so is None or no is None or so + no == 0: return None
    T = so + no; s = so / T
    s5, s6 = vals.get('s5'), vals['s6']
    O = vals.get('orders') or 0; E = O + ((s5 or {}).get('spam', 0) if s5 else 0) + (s6['spam'] if s6 else 0)
    inh = inherit(vals) if use65 else None
    if inh: E = max(E, T - max(0, min(T - E, inh['lo_total'] - E)))
    cand = [s] + ([(so - min(E, so)) / (T - E), (so - max(0, E - no)) / (T - E)] if 0 < E < T else [])
    slo, shi = min(cand), max(cand)
    a0, b0 = PER[per]; d = sub_db(names, scope)
    app = d[(d.app >= a0) & (d.app <= b0)]; cre = d[(d.cre >= a0) & (d.cre <= b0)]
    ta, tc = app.n.sum(), cre.n.sum()
    if not ta or not tc: return None
    fa, fc = app.n[app.ad == FU].sum() / ta, cre.n[cre.ad == FU].sum() / tc
    ha, hc = app.n[app.ad.isin([FU, PA])].sum() / ta, cre.n[cre.ad.isin([FU, PA])].sum() / tc
    lo, hi = min(fa, fc) - shi, max(ha, hc) - slo
    oc = 'ABOVE' if lo > 0.05 else ('BELOW' if hi < -0.05 else ('CONSISTENT' if lo >= -0.05 and hi <= 0.05 else 'CANNOT_TELL'))
    return dict(s=round(s, 4), slo=round(slo, 4), shi=round(shi, 4), d=round(fa, 4), lo=round(lo * 100, 1), hi=round(hi * 100, 1), oc=oc, inh=bool(inh))

if __name__ == '__main__':
    rows = json.load(open(os.path.join(DSA, 'data', 'dsa.json')))
    pub = {(r['platform'], r['period'], r['measure']): r for r in rows if r.get('measure') != 'label_split'}
    views = [(('main', s), s) for s in NAMES if s != 'Stripchat'] + [(('ads', s), s + ' (ads)') for s in ADS] + [(('combined', None), 'Facebook and Instagram')]
    diffs = 0; n = 0
    for view, name in views:
        for per in PER:
            if view[0] != 'combined' and '%s|%s' % (view[1], per) not in ST: continue
            r = share(view, per); p = pub.get((name, per, 'share'))
            if r is None or p is None or p.get('stated_share') is None: continue
            n += 1
            mine = (r['s'], r['slo'], r['shi'], r['d'], r['lo'], r['hi'])
            theirs = (p['stated_share'], p['stated_share_lo'], p['stated_share_hi'], p['delivered_share'], p['diff_lo_points'], p['diff_hi_points'])
            if mine != theirs or (r['oc'] != p['outcome'] and not p.get('note_rule')):
                diffs += 1; print('DIFF', name, per, mine, theirs, r['oc'], p['outcome'], p.get('note_rule'))
    print('share rows compared', n, 'differences', diffs)
    # with and without 6.5, every view, total/solely/not/share, outcome before notes and 6.7
    moved = []
    for view, name in views:
        for per in PER:
            if view[0] != 'combined' and '%s|%s' % (view[1], per) not in ST: continue
            for m in ('total', 'solely', 'not'):
                a = row(view, per, m, use65=True); b = row(view, per, m, use65=False)
                if a['S'] is not None and a['oc'] != b['oc']: moved.append((name, per, m, b['oc'], '->', a['oc'], a['inh']['identity'] if a['inh'] else None))
            a, b = share(view, per, True), share(view, per, False)
            if a and b and a['oc'] != b['oc']: moved.append((name, per, 'share', b['oc'], '->', a['oc']))
    print('rows Addendum 6.5 moves (before notes and 6.7):', len(moved))
    for x in moved: print('   ', x)
