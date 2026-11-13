"""Referee second pass: an independent implementation of PLAN.md Addendum 6 (as written) for the rows under re-referee:
Google main and ads rows, Facebook / Instagram / combined rows, every notice row, and every row Addendum 6.5 touches.
Inputs: out2/red2.parquet (referee reduction with the ads flag and the X alias), out2/stated_all2.json (referee read of the reports),
db_status.json (shortfall values, verified in pass one), dsa.json (only to compare). Output: printed diffs and out2/second_pass.json."""
import sys, os, site, json, math, collections as C
sys.path.append(site.getusersitepackages())
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); DSA = '/Users/heuremen/bones-forge/social_index/dsa'
PER = {'2025H2': ('2025-07-01', '2025-12-31'), '2026H1': ('2026-01-01', '2026-06-30')}
NAMES = {'Facebook': 'Facebook', 'Instagram': 'Instagram', 'TikTok': 'TikTok', 'YouTube': 'YouTube', 'X': 'X', 'LinkedIn': 'LinkedIn', 'Snapchat': 'Snapchat',
         'Pinterest': 'Pinterest', 'Amazon Store': 'Amazon', 'AliExpress': 'AliExpress', 'Temu': 'Temu', 'Shein': 'Shein', 'Zalando': 'Zalando', 'Booking.com': 'Booking.com',
         'Apple App Store': 'App Store', 'Google Maps': 'Google Maps', 'Google Play': 'Google Play', 'Google Shopping': 'Google Shopping', 'Pornhub': 'Pornhub',
         'XVideos': 'XVideos', 'XNXX': 'XNXX', 'Stripchat': 'Stripchat', 'WhatsApp Channels': 'WhatsApp Channels'}
ADS = ('YouTube', 'Google Maps', 'Google Play')
FU, PA, NA = 'AUTOMATED_DECISION_FULLY', 'AUTOMATED_DECISION_PARTIALLY', 'AUTOMATED_DECISION_NOT_AUTOMATED'
VOL, A16, TF, OTH = 'SOURCE_VOLUNTARY', 'SOURCE_ARTICLE_16', 'SOURCE_TRUSTED_FLAGGER', 'SOURCE_TYPE_OTHER_NOTIFICATION'
ILL, INC = 'DECISION_GROUND_ILLEGAL_CONTENT', 'DECISION_GROUND_INCOMPATIBLE_CONTENT'
F = {'all': lambda d: d.n >= 0, 'FU': lambda d: d.ad == FU, 'NA': lambda d: d.ad == NA, 'PA': lambda d: d.ad == PA, 'VOL': lambda d: d.src == VOL,
     'VOL_ILL': lambda d: (d.src == VOL) & (d.gr == ILL), 'VOL_INC': lambda d: (d.src == VOL) & (d.gr == INC), 'OTH': lambda d: d.src == OTH,
     'OTH_ILL': lambda d: (d.src == OTH) & (d.gr == ILL), 'OTH_INC': lambda d: (d.src == OTH) & (d.gr == INC), 'NOT': lambda d: d.src.isin([A16, TF]),
     'NOT_ILL': lambda d: d.src.isin([A16, TF]) & (d.gr == ILL), 'NOT_INC': lambda d: d.src.isin([A16, TF]) & (d.gr == INC), 'TF': lambda d: d.src == TF,
     'VOL_FU': lambda d: (d.src == VOL) & (d.ad == FU), 'VOL_FUPA': lambda d: (d.src == VOL) & d.ad.isin([FU, PA]), 'VOL_DET': lambda d: (d.src == VOL) & (d.det == 'Yes')}
BASE = {'total': 'all', 'solely': 'FU', 'not': 'NA', 'own': 'VOL', 'own_illegal': 'VOL_ILL', 'own_tc': 'VOL_INC', 'own_auto': 'VOL_FU', 'notice': 'NOT', 'notice_tf': 'TF'}
ADD = {'solely': ['PA'], 'not': ['PA'], 'own': ['OTH'], 'own_illegal': ['OTH_ILL', 'VOL_INC'], 'own_tc': ['OTH_INC', 'VOL_ILL']}
SRC = {'own': 'NOT', 'own_illegal': 'NOT_ILL', 'own_tc': 'NOT_INC'}
COLSUM_NOTE = {('TikTok', '2025H2'): 'sum', ('TikTok', '2026H1'): 'sum', ('X', '2025H2'): 'sum', ('X', '2026H1'): 'sum', ('Snapchat', '2026H1'): 'sum', ('Snapchat', '2025H2'): 'outside'}

red = pq.read_table(os.path.join(HERE, 'out2', 'red2.parquet')).to_pandas()
red['cre'] = red['cre'].astype(str); red['app'] = red['app'].astype(str)
ST = json.load(open(os.path.join(HERE, 'out2', 'stated_all2.json')))
SF = {k: v.get('shortfall', 0) for k, v in json.load(open(os.path.join(DSA, 'data', 'db_status.json')))['shortfall_addendum3'].items()}

def sub_db(names, scope):
    d = red[red.platform.isin(names)]
    if scope == 'ads': d = d[d.isad]
    elif scope == 'nonads': d = d[~d.isad]
    return d

def delivered(names, scope, per, m, sf, items=None, main=True):
    a0, b0 = PER[per]; d = sub_db(names, scope)
    app = d[(d.app >= a0) & (d.app <= b0)]; cre = d[(d.cre >= a0) & (d.cre <= b0)]
    lates = [app[app.cre == x] for x in ('2026-10-31', '2026-11-03')]
    s = lambda df, k: int(df.n[F[k](df)].sum())
    base = BASE[m]
    if m in ('notice', 'notice_tf'):
        hi = max(s(app, 'all'), s(cre, 'all')); lt = max(s(l, 'all') for l in lates)
        return dict(D_app=s(app, base), D_lo=0, D_hi=hi + 2 * lt + sf)
    if m == 'own_auto':
        lo_k = 'VOL_FU' if s(app, 'VOL_FU') <= s(app, 'VOL_DET') else 'VOL_DET'
        eea = int(app.n[F[lo_k](app) & (app.sc == 'NONEU_ONLY')].sum())
        lo = min(s(app, 'VOL_FU'), s(app, 'VOL_DET'), s(cre, 'VOL_FU'), s(cre, 'VOL_DET')) - eea
        hi = max(max(s(x, 'VOL_FUPA'), s(x, 'VOL_DET')) for x in (app, cre)); lt = max(max(s(l, 'VOL_FUPA'), s(l, 'VOL_DET')) for l in lates)
        return dict(D_app=s(app, base), D_lo=max(0, lo), D_hi=hi + 2 * lt + sf)
    adds = ADD.get(m, [])
    eea = int(app.n[F[base](app) & (app.sc == 'NONEU_ONLY')].sum())
    lo = min(s(app, base), s(cre, base)) - eea
    ex = lambda x: max(0, s(x, SRC[m]) - items) if (main and m in SRC and items is not None) else 0
    hi = max(s(x, base) + sum(s(x, k) for k in adds) + ex(x) for x in (app, cre))
    lt = max(s(l, base) + sum(s(l, k) for k in adds) for l in lates)
    return dict(D_app=s(app, base), D_cre=s(cre, base), D_lo=max(0, lo), D_hi=hi + 2 * lt + sf)

def colq(sh, note=None):
    """(qualifies, largest column, sum of columns, total) for a sheet dict from stated_all2."""
    if not sh or sh.get('F') is None: return False, None, None, None
    cols = [x for x in sh['cols'].values() if isinstance(x, int)]
    if not cols: return False, sh['F'], None, sh['F']
    arith = sum(cols) == sh['F'] and sh['F'] > 0
    if note == 'outside': return True, max(cols), sum(cols), sh['F']
    return (arith or note == 'sum'), max(cols), sum(cols), sh['F']

def classify(S, S_lo, S_hi, D_lo, D_hi, floor=True):
    if S == 0:
        if D_hi == 0: return 'CONSISTENT', None, None
        if D_lo > 0: return ('CANNOT_TELL' if floor and D_lo < 100 else 'ABOVE'), None, None
        return 'CANNOT_TELL', None, None
    rlo = D_lo / S_hi if S_hi else math.inf; rhi = D_hi / S_lo if S_lo else math.inf
    oc = 'ABOVE' if rlo > 1.1 else ('BELOW' if rhi < 0.9 else ('CONSISTENT' if rlo >= 0.9 and rhi <= 1.1 else 'CANNOT_TELL'))
    if floor and oc == 'ABOVE' and D_lo - 1.1 * S_hi < 100: oc = 'CANNOT_TELL'
    if floor and oc == 'BELOW' and 0.9 * S_lo - D_hi < 100: oc = 'CANNOT_TELL'
    return oc, rlo, rhi

def view_vals(view, per):
    """Stated inputs for a view: main (service name), ads (service), combined."""
    if view[0] == 'combined':
        vs = [ST['%s|%s' % (x, per)] for x in ('Facebook', 'Instagram')]
        g = lambda k: None if any(v.get(k) is None for v in vs) else sum(v[k] for v in vs)
        out = dict(solely=g('solely'), not_=g('not'), orders=sum((v.get('orders') or 0) for v in vs), nL=g('nL'), nN=g('nN'))
        for sh in ('s5', 's6'):
            Fs = [v[sh]['F'] for v in vs]
            colss = [[x for x in v[sh]['cols'].values() if isinstance(x, int)] for v in vs]
            q = all(cs and sum(cs) == f for cs, f in zip(colss, Fs) if f is not None) and all(f is not None for f in Fs)
            out[sh] = dict(F=None if any(f is None for f in Fs) else sum(Fs), spam=sum(v[sh]['spam'] for v in vs),
                           q=q, maxcol=max(max(cs) for cs in colss if cs) if all(colss) else None, G=None if any(v[sh]['G'] is None for v in vs) else sum(v[sh]['G'] for v in vs))
        return out
    v = ST['%s|%s' % (view[1], per)]
    if view[0] == 'ads':
        sh6 = v['s6a']; q, mx, cs, Ft = colq(sh6)
        return dict(solely=v['ads_solely'], not_=v['ads_not'], orders=0, s5=None, s6=dict(F=sh6['F'], spam=sh6['spam'], q=q, maxcol=mx, G=sh6['G']), nL=None, nN=None)
    note = COLSUM_NOTE.get((view[1], per))
    out = dict(solely=v.get('solely'), not_=v.get('not'), orders=v.get('orders') or 0, nL=v.get('nL'), nN=v.get('nN'), nM=v.get('nM'), nO=v.get('nO'), nH=v.get('nH'), nI=v.get('nI'))
    for sh, key in (('s5', None), ('s6', note)):
        q, mx, cs, Ft = colq(v[sh], key if sh == 's6' else None)
        out[sh] = dict(F=v[sh]['F'], spam=v[sh]['spam'], q=q, maxcol=mx, colsum=cs, G=v[sh]['G'], outside=(key == 'outside' and sh == 's6'))
    return out

def inherit(vals):
    """Addendum 6.5 as written: sheet 8 total within 0.1% of 5+6 [+ notices] [+ orders], at least one TOTAL a column sum."""
    if vals['solely'] is None or vals['not_'] is None: return None
    T8 = vals['solely'] + vals['not_']; s5, s6 = vals.get('s5'), vals['s6']
    if not s6 or s6['F'] is None or not T8: return None
    t5 = (s5 or {}).get('F') or 0; q5 = bool(s5 and s5.get('F') is not None and s5['q']); q6 = s6['q']
    if not (q5 or q6): return None
    lo5 = (s5['maxcol'] if q5 else t5) if s5 and s5.get('F') is not None else 0; lo6 = s6['maxcol'] if q6 else s6['F']
    Nn = (vals.get('nL') or 0) + (vals.get('nN') or 0); O = vals.get('orders') or 0
    for lab, cand, extra in (('5+6', t5 + s6['F'], 0), ('5+6+N', t5 + s6['F'] + Nn, Nn), ('5+6+N+O', t5 + s6['F'] + Nn + O, Nn + O)):
        if cand and abs(T8 - cand) / T8 <= 0.001: return dict(identity=lab, T8=T8, rel=(T8 - cand) / T8, lo_total=lo5 + lo6 + extra)
    return None

def row(view, per, m, use65=True, posthoc=True):
    vals = view_vals(view, per)
    names = ['Facebook', 'Instagram'] if view[0] == 'combined' else [NAMES[view[1]]]
    scope = 'ads' if view[0] == 'ads' else ('nonads' if view[0] == 'main' and view[1] in ADS else 'all')
    sf = sum(SF.get(n, 0) for n in names)
    main = view[0] == 'main'
    s5, s6 = vals.get('s5'), vals['s6']
    M5 = (s5 or {}).get('spam', 0) if s5 else 0; M6 = s6['spam'] if s6 else 0; O = vals.get('orders') or 0
    if m == 'total': S = None if vals['solely'] is None or vals['not_'] is None else vals['solely'] + vals['not_']
    elif m == 'solely': S = vals['solely']
    elif m == 'not': S = vals['not_']
    elif m == 'own_tc': S = s6['F'] if s6 else None
    elif m == 'own_illegal': S = s5['F'] if s5 else None
    elif m == 'own': S = None if not s5 or s5['F'] is None or s6['F'] is None else s5['F'] + s6['F']
    elif m == 'own_auto': S = None if not s5 or s5.get('G') is None or s6.get('G') is None else s5['G'] + s6['G']
    elif m == 'notice': S = None if vals.get('nL') is None or vals.get('nN') is None else vals['nL'] + vals['nN']
    elif m == 'notice_tf': S = None if vals.get('nM') is None or vals.get('nO') is None else vals['nM'] + vals['nO']
    d = delivered(names, scope, per, m, sf, items=vals.get('nH'), main=main)
    if S is None: return dict(S=None, D=d, oc='CANNOT_TELL')
    sub = {'total': O + M5 + M6, 'solely': O + M5 + M6, 'not': O + M5 + M6, 'own': M5 + M6, 'own_auto': M5 + M6, 'own_illegal': M5, 'own_tc': M6}.get(m, 0)
    S_lo, S_hi = max(0, S - sub), S
    if m in ('own', 'own_tc'):
        shs = [s6] if m == 'own_tc' else [s5, s6]
        if all(x and x.get('F') is not None for x in shs) and any(x['q'] for x in shs):
            lo = sum((x['maxcol'] if x['q'] else x['F']) for x in shs)
            S_lo = max(0, lo - sub)
            if s6.get('outside'): S_hi = min(S, sum((x['colsum'] if x is s6 else x['F']) for x in shs))
    inh = inherit(vals) if (use65 and m in ('total', 'solely', 'not')) else None
    if inh:
        T8 = inh['T8']; R = T8 - max(0, min(T8 - O - M5 - M6, inh['lo_total'] - O - M5 - M6))
        S_lo = max(0, S - R)
    if m == 'notice' and vals.get('nH') is not None: S_hi = max(S, vals['nH'])
    if m == 'notice_tf' and vals.get('nI') is not None: S_hi = max(S, vals['nI'])
    oc, rlo, rhi = classify(S, S_lo, S_hi, d['D_lo'], d['D_hi'])
    return dict(S=S, S_lo=S_lo, S_hi=S_hi, D=d, oc=oc, rlo=rlo, rhi=rhi, inh=inh)

if __name__ == '__main__':
    rows = json.load(open(os.path.join(DSA, 'data', 'dsa.json')))
    pub = {(r['platform'], r['period'], r['measure']): r for r in rows if r.get('measure') != 'label_split'}
    want = []
    for p in ADS:
        for per in PER:
            for m in ('total', 'solely', 'not', 'own', 'own_illegal', 'own_tc', 'own_auto', 'notice', 'notice_tf'): want.append((('main', p), p, per, m))
            for m in ('total', 'solely', 'not', 'own_tc'): want.append((('ads', p), p + ' (ads)', per, m))
    for p in ('Facebook', 'Instagram'):
        for per in PER:
            for m in ('total', 'solely', 'not', 'own', 'own_illegal', 'own_tc', 'own_auto', 'notice', 'notice_tf'): want.append((('main', p), p, per, m))
    for per in PER:
        for m in ('total', 'solely', 'not', 'own', 'own_tc', 'own_auto'): want.append((('combined', None), 'Facebook and Instagram', per, m))
    for svc in NAMES:
        if svc in ADS or svc in ('Facebook', 'Instagram'): continue
        for per in PER:
            if '%s|%s' % (svc, per) not in ST: continue
            for m in ('notice', 'notice_tf', 'total', 'solely', 'not'): want.append((('main', svc), svc, per, m))
    diffs = []; res = {}
    for view, name, per, m in want:
        r = row(view, per, m); p = pub.get((name, per, m))
        if p is None: diffs.append((name, per, m, 'no published row')); continue
        pd_ = p.get('delivered') or {}
        mine = (r['S'], r.get('S_lo'), r.get('S_hi'), r['D']['D_app'], r['D']['D_lo'], r['D']['D_hi'])
        theirs = (p.get('stated'), p.get('stated_lo'), p.get('stated_hi'), pd_.get('D_app'), pd_.get('D_lo'), pd_.get('D_hi'))
        # outcome before platform notes and 6.7: compare with the published outcome where no note or split rule fired
        res['%s|%s|%s' % (name, per, m)] = dict(mine=mine, theirs=theirs, my_outcome=r['oc'], published=p['outcome'], note_rule=p.get('note_rule'), label_split=p.get('label_split'), inh=r.get('inh'))
        if mine != theirs: diffs.append((name, per, m, 'values', mine, theirs))
        elif r['oc'] != p['outcome'] and not p.get('note_rule') and not p.get('label_split'): diffs.append((name, per, m, 'outcome', r['oc'], p['outcome']))
    print('rows compared', len(want), 'differences', len(diffs))
    for x in diffs: print('  ', x)
    json.dump(res, open(os.path.join(HERE, 'out2', 'second_pass.json'), 'w'), indent=0, default=str)
