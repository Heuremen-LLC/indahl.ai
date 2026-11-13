import sys, os, site, json
sys.path.append(site.getusersitepackages())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_side import *
df = load()
rows = json.load(open(os.path.join(DSA, 'data', 'dsa.json')))
st = json.load(open(os.path.join(DSA, 'data', 'db_status.json')))
SF = {k: v.get('shortfall', 0) for k, v in st['shortfall_addendum3'].items()}
ADD = {'solely': 'PA', 'not': 'PA', 'own': 'OTH', 'own_illegal': 'OTH_ILL', 'own_tc': 'OTH_INC', 'notice': 'OTH'}
bad = []
for r in rows:
    if r['measure'] == 'share' or 'delivered' not in r or r['db_name'] is None: continue
    svc, per, m, dv = r['platform'], r['period'], r['measure'], r['delivered']
    dbn = NAMES[svc]; a, b = PER[per]
    d = df[df.platform == dbn]
    app = d[(d.app >= a) & (d.app <= b)]; cre = d[(d.cre >= a) & (d.cre <= b)]
    ma, mc = masks(app), masks(cre)
    if m == 'own_auto':
        v = dict(af=app.n[ma['own_auto']].sum(), ad=app.n[ma['VOL_DET']].sum(), cf=cre.n[mc['own_auto']].sum(), cd=cre.n[mc['VOL_DET']].sum())
        lo_key = 'own_auto' if v['af'] <= v['ad'] else 'VOL_DET'
        noneu = app.n[ma[lo_key] & (app.sc == 'NONEU_ONLY')].sum()
        lo = min(v.values()) - noneu
        hi = max(app.n[ma['VOL_FUPA']].sum(), v['ad'], cre.n[mc['VOL_FUPA']].sum(), v['cd'])
        late = max(max(app[(app.cre == dd)].n[masks(app[(app.cre == dd)])['VOL_FUPA']].sum(), app[(app.cre == dd)].n[masks(app[(app.cre == dd)])['VOL_DET']].sum()) for dd in ('2026-10-31', '2026-11-03'))
    else:
        base = ma[m]; add = ADD.get(m)
        lo = min(app.n[base].sum(), cre.n[mc[m]].sum()) - app.n[base & (app.sc == 'NONEU_ONLY')].sum()
        hi = max(app.n[base].sum() + (app.n[ma[add]].sum() if add else 0), cre.n[mc[m]].sum() + (cre.n[mc[add]].sum() if add else 0))
        late = 0
        for dd in ('2026-10-31', '2026-11-03'):
            s = app[app.cre == dd]; ms = masks(s)
            late = max(late, s.n[ms[m]].sum() + (s.n[ms[add]].sum() if add else 0))
    D_lo = max(0, int(lo)); D_hi = int(hi) + 2 * int(late) + SF.get(dbn, 0)
    if D_lo != dv['D_lo'] or D_hi != dv['D_hi']:
        bad.append((svc, per, m, dv['D_lo'], D_lo, dv['D_hi'], D_hi, dv.get('missing_days_allowance'), 2 * int(late)))
print('D_lo/D_hi mismatches:', len(bad))
for x in bad[:30]: print(x)
