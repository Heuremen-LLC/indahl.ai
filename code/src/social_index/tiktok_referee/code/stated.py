"""Referee recount of TikTok's stated side, straight from the release zips (sha256-checked). Independent of tiktok_tick.py."""
import zipfile, csv, io, hashlib, json, sys
RAW = '/Users/heuremen/bones-forge/social_index/tiktok/data/raw/tiktok_cger/'
SRC = json.load(open('/Users/heuremen/bones-forge/social_index/tiktok/data/sources.json'))['tiktok']
EU = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czech Republic','Denmark','Estonia','Finland','France','Germany','Greece','Hungary',
      'Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden']
ALIAS = {'Czechia': 'Czech Republic'}
EFTA = ['Norway','Iceland','Liechtenstein']
LAB = {1:'Jan-Mar',2:'Apr-Jun',3:'Jul-Sep',4:'Oct-Dec'}
def period(q): return '%s %s' % (LAB[int(q[5])], q[:4])
_cache = {}
def rows(rel):
    if rel in _cache: return _cache[rel]
    p = RAW + rel + '.zip'
    assert hashlib.sha256(open(p,'rb').read()).hexdigest() == SRC[rel]['sha256']
    z = zipfile.ZipFile(p)
    n = [x for x in z.namelist() if x.lower().endswith('.csv') and not x.startswith('__MACOSX')][0]
    R = list(csv.DictReader(io.TextIOWrapper(z.open(n), encoding='utf-8-sig')))
    _cache[rel] = R
    return R
def cells(rel, q):
    R = rows(rel); iss = 'Issue' if 'Issue' in R[0] else 'Issue policy'; per = period(q)
    out = {}; dup = []
    for r in R:
        if r['Period'] != per or r['Policy type'] != 'All' or r[iss] != 'All': continue
        m, tt, t = r['Metric'], r['Task type'], r['Task']
        k = None
        if m == 'Total videos removed' and tt == 'All' and t == 'All': k = 'T'
        elif m == 'Total videos removed' and t == 'Automation': k = 'AUTO'
        elif m == 'Total videos removed' and t == 'AI Moderation': k = 'AI'
        elif m == 'Proactive removal rate' and tt == 'All' and t == 'All': k = 'PRO'
        elif m == 'Removal rate within 24 hours' and tt == 'All' and t == 'All': k = 'W24'
        if not k: continue
        if r['Location'] == 'All' and r['Market'] == 'All': mk = 'GLOBAL'
        elif r['Location'] == 'Market': mk = ALIAS.get(r['Market'], r['Market'])
        else: continue
        try: v = float(r['Result'])
        except ValueError: continue
        if (mk, k) in out and out[(mk, k)] != v: dup.append((mk, k, out[(mk,k)], v))
        out[(mk, k)] = v
    return out, dup
def stated(rel, q, verbose=False):
    c, dup = cells(rel, q)
    mk = {}
    for (m, k), v in c.items():
        if m != 'GLOBAL': mk.setdefault(m, {})[k] = v
    listed = {m: v['T'] for m, v in mk.items() if 'T' in v}
    G = c.get(('GLOBAL','T'))
    B = 49999 if int(q[:4]) >= 2026 else min(listed.values())
    rem = G - sum(listed.values())
    res = {}
    for pop, names in (('EU', EU), ('EEA', EU + EFTA)):
        L = [n for n in names if n in listed]; U = [n for n in names if n not in listed]
        cap = min(len(U) * B, max(0, rem))
        T = sum(mk[n]['T'] for n in L)
        A = sum(mk[n].get('AUTO',0) + mk[n].get('AI',0) for n in L)
        missing_auto = [n for n in L if 'AUTO' not in mk[n]]
        r = dict(L=L, U=U, cap=cap, T=T, A=A, missing_auto=missing_auto)
        for k in ('PRO','W24'):
            miss = [n for n in L if k not in mk[n]]
            Tk = sum(mk[n]['T'] for n in L if k in mk[n]); Tn = sum(mk[n]['T'] for n in L if k not in mk[n])
            pt = sum(mk[n][k]*mk[n]['T'] for n in L if k in mk[n]) / Tk
            lo = sum(max(0, mk[n][k]-0.0005)*mk[n]['T'] for n in L if k in mk[n]) / (Tk + Tn + cap)
            hi = (sum(min(1, mk[n][k]+0.0005)*mk[n]['T'] for n in L if k in mk[n]) + Tn + cap) / (Tk + Tn + cap)
            r[k] = dict(point=pt, lo=lo, hi=hi, missing=miss)
        r['ASH'] = dict(point=A/T, lo=A/(T+cap), hi=(A+cap)/(T+cap))
        res[pop] = r
    e, x = res['EU'], res['EEA']
    out = dict(videos_removed=dict(point=e['T'], lo=e['T'], hi=x['T'] + x['cap']),
               automated_removals=dict(point=e['A'], lo=e['A'], hi=x['A'] + x['cap']),
               automated_share=dict(point=e['ASH']['point'], lo=min(e['ASH']['lo'], x['ASH']['lo']), hi=max(e['ASH']['hi'], x['ASH']['hi'])),
               proactive_rate=dict(point=e['PRO']['point'], lo=min(e['PRO']['lo'], x['PRO']['lo']), hi=max(e['PRO']['hi'], x['PRO']['hi'])),
               within_24h_rate=dict(point=e['W24']['point'], lo=min(e['W24']['lo'], x['W24']['lo']), hi=max(e['W24']['hi'], x['W24']['hi'])))
    det = dict(release=rel, listed_eu=e['L'], unlisted_eu=e['U'], efta_listed=[n for n in EFTA if n in listed], B=B, global_T=G,
               n_listed=len(listed), listed_sum=sum(listed.values()), remainder=rem, cap_eu=e['cap'], cap_eea=x['cap'], dup=dup,
               missing_auto=e['missing_auto'], missing_pro=e['PRO']['missing'], missing_w24=e['W24']['missing'],
               market=dict((n, mk[n]) for n in e['L']), norway=mk.get('Norway'))
    return out, det
if __name__ == '__main__':
    QS = ['2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2']
    allout = {}
    for q in QS:
        rel = q if q in SRC else '2023Q4'
        o, d = stated(rel, q)
        allout[q] = dict(stated=o, detail=d)
        print(q, rel, 'listedEU=%d' % len(d['listed_eu']), 'B=%d' % d['B'], 'G=%d' % d['global_T'], 'nlisted=%d' % d['n_listed'],
              'capEU=%d capEEA=%d' % (d['cap_eu'], d['cap_eea']), 'efta_listed', d['efta_listed'], 'missing', d['missing_auto'], d['missing_pro'], d['missing_w24'], 'dup', len(d['dup']))
        for ms, v in o.items():
            if ms in ('videos_removed','automated_removals'): print('   %-18s %12.0f  [%12.0f, %12.0f]' % (ms, v['point'], v['lo'], v['hi']))
            else: print('   %-18s %8.4f  [%8.4f, %8.4f]' % (ms, v['point'], v['lo'], v['hi']))
    json.dump(allout, open('/Users/heuremen/bones-forge/social_index/tiktok_referee/stated_recount.json','w'), indent=1)
