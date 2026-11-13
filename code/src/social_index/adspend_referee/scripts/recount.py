# Referee recount engine for ADSPEND. Written from PLAN.md text (patterns copied from PLAN.md, not from adspend_tick.py).
# Usage: imported by analysis scripts. build(opts) returns rows keyed by (group_key, cycle) with every number and outcome.
import re, pickle, os, bisect, datetime as D, collections as C

HERE = os.path.dirname(os.path.abspath(__file__))
CYC = (2020, 2022, 2024, 2026)
_cache = None
def raw():
    global _cache
    if _cache is None: _cache = pickle.load(open(os.path.join(HERE, 'raw_cache.pkl'), 'rb'))
    return _cache

def norm(s):
    s = (s or '').upper().replace('&', ' AND ')
    return ' '.join(re.sub(r'[^A-Z0-9]', ' ', s).split())

# ---- PLAN.md patterns, copied from the plan text (lines 39-46, 57)
P_G = re.compile(r'GOOGLE|YOUTUBE|YOU ?TUBE|ADWORDS|DOUBLECLICK|ALPHABET INC|\bG ?-?SUITE\b|\bGSUITE\b')
P_EX = re.compile(r'TOP OF GOOGLE')
P_MIX = re.compile(r'FACEBOOK|\bFB\b|\bMETA\b|TIKTOK|\bWIX\b|YAHOO|\bBING\b|MICROSOFT|AMAZON|TWITTER')
P_ADP = re.compile(r'ADVERTI|ADVERTIZ|\bADS?\b|\bAD-|AD ?BUY|MEDIA BUY|PLACEMENT|PAID MEDIA|DIGITAL MEDIA|ONLINE FUNDRAISING|ACQUISITION|LIST BUILDING|DIGITAL ADVOCACY|ELECTIONEERING|PROMOTION|PROMOTED|MARKETING|YOUTUBE|PRE-?ROLL|\bSEM\b|\bPPC\b|PAY PER CLICK')
P_NAP = re.compile(r'SOFTWARE|SUBSCRIPTION|E-?MAIL|HOSTING|WEB ?SITE|WEB SERVICE|DOMAIN|G-?SUITE|GSUITE|WORKSPACE|CLOUD|STORAGE|COMPUTER|\bIT\b|TECHNOLOGY|TECH SUPPORT|OFFICE|PHONE|VOICE|INTERNET SERVICE|INTERNET UTILITY|UTILIT|DATA ?BASE|DATA SERVICE|LICENS|\bAPPS?\b|PRODUCTIVITY|ORGANIZATIONAL TOOLS|DIGITAL TOOLS|PAYROLL|EQUIPMENT|SUPPLIES|WIRE SERVICE|SERVER|VOTER FILE|FIBER|CATERING|TRAVEL|RECRUIT|EMPLOYMENT|REFUND')
P_NAPAY = re.compile(r'WORKSPACE|G ?-?SUITE|GSUITE|SUITES?\b|CLOUD|DOMAINS?|FIBER|\bFI\b|F1 PHONE|VOICE|\bPLAY\b|STORE|STORAGE|PHOTOS|\bNEST\b|GMAIL|\bTV\b|YOUTUBETV|PREMIUM|\bPRO\b|\bAPPS?\b|\bAPS\b|\bPAY\b|WALLET|LOOKER|CHATGPT|OTTER|CLASH|FOOTBALL|PHONE|MERCHANDISE|CATERING|OPERACIONES')
P_ADPAY_NOYT = re.compile(r'\bADS?\b|ADWORDS|\bADX\b|ADVERTIS|\bAD SERVICES|LEADS|DOUBLECLICK')
P_YT = re.compile(r'YOUTUBE')
# the builder's extra AD-payee alternatives that PLAN.md does not carry (for the deviation test only)
CODE_EXTRA_ADPAY = re.compile(r'\*ADS|GOOGLEADS|ADS\d|ADWRDS|\bADDS\b|YOU TUBE')
P_POOLX = re.compile(r'DIGITAL|MEDIA|ONLINE|INTERNET|\bWEB\b|SOCIAL|SEARCH|VIDEO|STREAMING|\bCTV\b|\bOTT\b|PROGRAMMATIC|CONNECTED TV')

def U(s): return ' '.join((s or '').upper().split())
def is_g(p): p = U(p); return bool(P_G.search(p)) and not P_EX.search(p)

def gclass(payee, purpose, variant='plan'):
    """PLAN.md class of a Schedule B Google row. variant 'code' adds the builder's extra AD-payee words and its
    tie rule (payee that is both an AD and a NONAD product counts as neutral)."""
    p, u = U(payee), U(purpose)
    if P_MIX.search(p): return 'MIXED'
    nap = bool(P_NAPAY.search(p))
    adp = bool(P_ADPAY_NOYT.search(p)) or (bool(P_YT.search(p)) and not nap)
    if variant == 'code':
        adp = adp or bool(re.search(r'\*ADS|GOOGLEADS|ADS\d|ADWRDS|\bADDS\b', p)) or (bool(re.search(r'YOU TUBE', p)) and not nap)
        if adp and nap: adp = nap = False
    pa, pn = bool(P_ADP.search(u)), bool(P_NAP.search(u))
    if pa and not pn: return 'UNCLEAR' if nap else 'AD'
    if pn and not pa: return 'UNCLEAR' if adp else 'NONAD'
    if pa and pn: return 'UNCLEAR'
    if adp and nap: return 'UNCLEAR'
    return 'AD' if adp else ('NONAD' if nap else 'UNCLEAR')

def pool_purpose(purpose):
    u = U(purpose); return bool(P_ADP.search(u) or P_POOLX.search(u))

def iso(o): return D.date.fromordinal(o).isoformat()

def build(variant='plan', threshold=0.9, cap=400.0, rulers=((31, 92), (92, 183)), sched_e_mixed_in_dlo=None, itm_dedup=False, extra_pool=None, keep_rows=False):
    R = raw(); cm, wk, wa = R['cm'], R['wk'], R['wa']
    us = [g for g in R['gstats'] if g['regions'].strip() == 'US']
    principal = C.defaultdict(set); names = C.defaultdict(set)
    for cid, recs in cm.items():
        for c, r in recs.items():
            names[norm(r['name'])].add(cid)
            if r['dsgn'] == 'P' and r['cand']: principal[r['cand']].add(cid)
    adv = {}; why = C.Counter(); why_sp = C.Counter()
    for g in us:
        items = [s.strip() for s in (g['ids'] or '').split(',') if s.strip()]
        fec = [s[len('FEC ID'):].strip().upper() for s in items if s.upper().startswith('FEC ID')]
        if fec:
            cids = []; ok = True; has_c = any(re.fullmatch(r'C\d{8}', t) for t in fec)
            for t in fec:
                if re.fullmatch(r'C\d{8}', t) and t in cm: cids.append(t)
                elif re.fullmatch(r'[HSP][0-9A-Z]{8}', t) and principal.get(t): cids += sorted(principal[t])
                else: ok = False
            if ok and cids: adv[g['id']] = ('id' if has_c else 'candidate id', list(dict.fromkeys(cids)))
            else: why['fec id not in cm'] += 1; why_sp['fec id not in cm'] += g['total']
            continue
        if any(s.startswith('Registered in') for s in items): why['state registration'] += 1; why_sp['state registration'] += g['total']; continue
        hit = names.get(norm(g['name']), set())
        if len(hit) == 1: adv[g['id']] = ('name', list(hit))
        elif len(hit) > 1: why['ambiguous name'] += 1; why_sp['ambiguous name'] += g['total']
        else: why['no id no name'] += 1; why_sp['no id no name'] += g['total']
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, (t, ids) in adv.items():
        for i in ids[1:]: par[f(ids[0])] = f(i)
        f(ids[0])
    groups = C.defaultdict(lambda: dict(m=set(), a=[], t=set()))
    for a, (t, ids) in adv.items():
        g = groups[f(ids[0])]; g['m'].update(ids); g['a'].append(a); g['t'].add(t)
    advname = {g['id']: g['name'] for g in us}; advtot = {g['id']: g['total'] for g in us}
    # ---- 2026 cut (Addendum 1.3)
    months = R['months']; seq = [(2025, m) for m in range(1, 13)] + [(2026, m) for m in range(1, 13)]
    cut = seq[-1]
    for i in range(3, len(seq)):
        if months[seq[i]] < 0.7 * sum(months[seq[j]] for j in range(i - 3, i)) / 3: cut = seq[i - 1]; break
    ny, nm = (cut[0], cut[1] + 1) if cut[1] < 12 else (cut[0] + 1, 1)
    cut_end = D.date(ny, nm, 1).toordinal() - 1
    # ---- per committee Schedule B after amendment rule and memo-parent rule
    opp = R['opp']; members_all = {m for g in groups.values() for m in g['m']}
    B = {}; itm_dd = C.Counter(); n_amend = 0; n_memo = 0
    for cid in members_all:
        rs = opp.get(cid, [])
        # amendment rule: (cmte, rpt_yr, rpt_tp, tran_id) under more than one file number keeps the highest file number
        hi = {}
        for r in rs:
            if r[9]:
                k = (r[7], r[8], r[9]); fnv = int(r[10]) if r[10].isdigit() else -1
                if fnv > hi.get(k, -2): hi[k] = fnv
        keep = []
        for r in rs:
            if r[9] and (int(r[10]) if r[10].isdigit() else -1) != hi[(r[7], r[8], r[9])]: n_amend += 1; continue
            keep.append(r)
        for r in keep:
            if not r[5]: itm_dd[(cid, r[0])] += r[2]
        out = []
        gpar = set()
        for r in keep:
            if r[3] and is_g(r[3]) and not r[5]: gpar.add((r[10], r[9]))
        for r in keep:
            g = bool(r[3]) and is_g(r[3])
            if g:
                if r[5] and (r[10], r[11]) in gpar: n_memo += 1; continue
                kind = gclass(r[3], r[4], variant)
            elif pool_purpose(r[4]) or (extra_pool is not None and extra_pool.search(r[4])): kind = 'POOL'
            else: continue
            out.append((r[1], r[2], kind, r[5], r[0], r[6], r[3], r[4]))
        out.sort(key=lambda z: z[0]); B[cid] = (out, [z[0] for z in out])
    itm = itm_dd if itm_dedup else R['itm_raw']
    # ---- Schedule E
    E = {}; Ed = {}
    for cid in members_all:
        rs = []
        for r in R['ie'].get(cid, []):
            o = r['exp'] or r['dis']
            if o is None: continue
            p = U(r['pay']); g = is_g(p); mixed = g and bool(P_MIX.search(p))
            rs.append((o, r['amt'], g, mixed, r['fn'], (o, r['amt'], p, r['cand'], r['so']), r['c']))
        rs.sort(key=lambda z: z[0]); E[cid] = (rs, [z[0] for z in rs])
        per = C.defaultdict(C.Counter)
        for z in rs:
            if z[2] and (sched_e_mixed_in_dlo is not False or not z[3]): per[z[5]][z[4]] += 1
        dd = sorted([(k[0], k[1]) for k, cnt in per.items() for _ in range(max(cnt.values()))])
        Ed[cid] = (dd, [z[0] for z in dd])
    def sl(idx, cid, a, b):
        v = idx.get(cid)
        if not v: return []
        return v[0][bisect.bisect_left(v[1], a):bisect.bisect_right(v[1], b)]
    def band(weeks, a, b, P, Q):
        lo = hi = pt = 0.0; nh = 0
        for s, v in weeks:
            if s + 6 + Q >= a and s - P <= b: hi += v + 100; nh += 1
            if s >= a + P and s + 6 + Q <= b: lo += max(0.0, v - 100)
            if a <= s <= b: pt += v
        return lo, hi, pt, nh
    def cmrec(cid, c):
        r = cm.get(cid, {}); return r.get(c) or (r[max(r)] if r else {})
    def classify(Glo, Ghi, dlo, dhi, pool, unseen, scope, nothing):
        sa = max(1000.0, 0.1 * Ghi); sb = max(1000.0, 0.1 * Glo)
        if scope: return 'CANNOT_TELL', 'scope'
        if nothing: return 'NOTHING_RETURNED', ''
        if dlo - Ghi >= sa: return 'ABOVE', ''
        if Glo - (max(dhi, 0) + pool + unseen) >= sb: return 'BELOW', ''
        if Glo > 0 and Glo <= dlo and dhi + unseen <= Ghi and Ghi <= 2 * Glo: return 'CONSISTENT', ''
        if Glo > 0 and Glo <= dlo and dhi <= Ghi and Ghi <= 2 * Glo: return 'CANNOT_TELL', 'unseen'
        if dhi < Glo:
            if Glo - (max(dhi, 0) + pool) <= 0: return 'CANNOT_TELL', 'agency'
            if Glo - (max(dhi, 0) + pool) >= sb: return 'CANNOT_TELL', 'unseen'
            return 'CANNOT_TELL', 'near'
        return 'CANNOT_TELL', 'other'
    out = {}
    for gk, gv in groups.items():
        mem = sorted(gv['m']); wsum = C.defaultdict(float)
        for a in gv['a']:
            for s, v in R['weekly'].get(a, ()): wsum[s] += v
        weeks = sorted(wsum.items())
        scope = any(cmrec(m, 2026).get('tp', '') in 'ICEZ' and cmrec(m, 2026).get('tp', '') for m in mem)
        for c in CYC:
            a = D.date(c - 1, 1, 1).toordinal(); b = D.date(c, 12, 31).toordinal() if c != 2026 else cut_end
            ends = []
            for m in mem:
                if m in wk[c] and wk[c][m]['cvg']: ends.append(wk[c][m]['cvg'])
                else:
                    cd = cm.get(m, {}).get(c, {}).get('cand')
                    if cd and cd in wa[c] and wa[c][cd]['cvg']: ends.append(wa[c][cd]['cvg'])
            if ends: b = min(b, max(ends))
            b = max(a, b)
            bands = [band(weeks, a, b, P, Q) for P, Q in rulers]
            cls = C.defaultdict(float); n_ad_pos = 0; pool_b = 0.0; ggrows = []
            for m in mem:
                for r in sl(B, m, a, b):
                    if r[2] == 'POOL':
                        if r[1] > 0: pool_b += r[1]
                    else:
                        cls[r[2]] += r[1]; n_ad_pos += r[2] == 'AD' and r[1] > 0
                        if keep_rows: ggrows.append((m,) + r)
            e_rows = [z for m in mem for z in sl(E, m, a, b)]
            e_g_raw = sum(z[1] for z in e_rows if z[2]); e_pool = sum(z[1] for z in e_rows if not z[2] and z[1] > 0)
            e_dd = sum(z[1] for m in mem for z in sl(Ed, m, a, b))
            ie_tot = sum(wk[c][m]['ie'] for m in mem if m in wk[c]); coord = sum(wk[c][m]['coord'] for m in mem if m in wk[c] and cmrec(m, c).get('tp') in ('X', 'Y'))
            dlo = cls['AD'] + e_dd; dhi = cls['AD'] + cls['UNCLEAR'] + cls['NONAD'] + cls['MIXED'] + e_g_raw
            pool = pool_b + max(e_pool, max(ie_tot, 0.0)) + max(coord, 0.0)
            # unseen, Addenda 4 and 5
            u_full = u_cnt = 0.0; seen_c = set(); parts = []
            for m in mem:
                rec = cm.get(m, {}).get(c, {}); cd = rec.get('cand'); tp = rec.get('tp', '')
                if m in wk[c]:
                    w = wk[c][m]; imp = w['ttl_disb'] - w['tr_aff'] - w['ref_ind'] - w['ref_cmte'] - w['loan_rep'] - w['contrib_other'] - w['ie'] - w['coord']; src = 'webk'
                elif cd and cd in wa[c]:
                    if cd in seen_c: imp = 0.0; src = 'weball-dup'
                    else:
                        w = wa[c][cd]; imp = w['ttl_disb'] - w['tr_auth'] - w['cand_loan_rep'] - w['oth_loan_rep'] - w['ref_ind'] - w['ref_cmte']; src = 'weball'; seen_c.add(cd)
                else:
                    parts.append(dict(m=m, src='none')); continue
                it = itm.get((m, c), 0.0); u = max(0.0, imp - it); cov = it / imp if imp > 0 else None
                full = tp in ('X', 'Y') or (cov is not None and cov < threshold)
                uc = u if full else min(u, cap)
                u_full += u; u_cnt += uc; parts.append(dict(m=m, src=src, imp=imp, it=it, cov=cov, u=u, uc=uc, full=full, tp=tp))
            g1 = bands[0]
            if g1[3] == 0 and dhi == 0 and n_ad_pos == 0: continue
            anyb = any((m, c) in R['anyrow'] for m in mem)
            anye = any(z[6] == c for m in mem for z in E[m][0])
            summ = any(m in wk[c] or (cm.get(m, {}).get(c, {}).get('cand') in wa[c]) for m in mem)
            nothing = g1[1] > 0 and g1[3] > 0 and not (anyb or anye or summ)
            oc = [classify(bd[0], bd[1], dlo, dhi, pool, u_cnt, scope, nothing) for bd in bands]
            ocf = classify(g1[0], g1[1], dlo, dhi, pool, u_full, scope, nothing)
            ws = {x: sum(v for s, v in R['weekly'].get(x, ()) if a <= s <= b) for x in gv['a']}
            top = max(gv['a'], key=lambda x: (ws[x], advtot.get(x, 0)))
            prim = max(gv['a'], key=lambda x: advtot.get(x, 0))
            pid = adv[top][1][0] if ws[top] > 0 else adv[prim][1][0]
            out[('+'.join(mem), c)] = dict(group='+'.join(mem), cycle=c, members=mem, n=len(mem), tiers='+'.join(sorted(gv['t'])), advs=list(gv['a']), top_adv=top,
                                          window=(iso(a), iso(b)), G_lo=g1[0], G_hi=g1[1], G_pt=g1[2], G2=(bands[1][0], bands[1][1]), D_lo=dlo, D_hi=dhi, pool=pool,
                                          pool_parts=dict(b=pool_b, e_file=e_pool, ie_tot=ie_tot, coord=coord), unseen=u_cnt, unseen_full=u_full, parts=parts,
                                          cls=dict(cls), e_g_raw=e_g_raw, e_dd=e_dd, outcome=oc[0][0], reason=oc[0][1], outcome2=oc[1][0], outcome_full=ocf[0],
                                          cid=pid, name=cmrec(pid, c).get('name'), party=cmrec(pid, c).get('party'), tp=cmrec(pid, c).get('tp'), dsgn=cmrec(pid, c).get('dsgn'),
                                          scope=scope, ggrows=ggrows if keep_rows else None)
    meta = dict(cut=cut, cut_end=iso(cut_end), n_amend=n_amend, n_memo=n_memo, why=dict(why), why_sp=dict(why_sp), n_adv=len(adv),
                tiers=C.Counter(t for t, _ in adv.values()), groups=len(groups), committees=len(members_all), adv=adv, groups_obj=groups)
    return out, meta
