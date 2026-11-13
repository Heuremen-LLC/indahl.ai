"""make_rows.py: FIDELITY desk. NCHS state counts against ACS women/men estimates. See PLAN.md (sealed). `python3 -I make_rows.py --selftest` runs offline checks. Never touches the network, never reads the Census key."""
import json, os, re, sys, glob, zipfile, shutil, time, statistics, subprocess, hashlib
sys.path.insert(0, '../census_index')
import heuremen_kit as K
ABOVE, BELOW, CONSISTENT, CT = K.ABOVE, K.BELOW, K.CONSISTENT, K.CANNOT_TELL
YEARS = [y for y in range(2010, 2025) if y != 2020]
DEST = {'DIVORCE': {'Nevada'}, 'MARRIAGE': {'Nevada', 'Hawaii'}}
EV = {'DIVORCE': ('divorce', 'B12503'), 'MARRIAGE': ('marriage', 'B12501')}
R_NOREP, R_NOSTATED, R_NOACS = 'state does not report', 'no stated count', 'no ACS interval'

def interval(e, m, scale=1.0):
    """Published estimate and 90 percent margin to [lo, hi], lower end not below zero. Coded or missing values give None."""
    try: e = float(e); m = float(m)
    except (TypeError, ValueError): return None
    if e < 0 or m < 0: return None
    return (max(0.0, e - m * scale), e + m * scale)

def outcome(n, iv, year=None, stated_ok=True):
    """Row rule from PLAN.md. n is the NCHS count or None. Returns (outcome, reason)."""
    if year == 2024: return CT, R_NOSTATED
    if n is None: return CT, R_NOREP
    if iv is None: return CT, R_NOACS
    if n > iv[1]: return ABOVE, None
    if n < iv[0]: return BELOW, None
    return CONSISTENT, None

def cell_read(c):
    sc = c[ABOVE] + c[BELOW] + c[CONSISTENT]
    if sc < 5: return CT
    top = max((ABOVE, BELOW, CONSISTENT), key=lambda k: c[k])
    return top if c[top] >= 0.8 * sc else 'MIXED'

def xlsx_rows(f):
    z = zipfile.ZipFile(f)
    ss = [re.sub('<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode(), re.S)]
    out = []
    for row in re.findall(r'<row.*?</row>', z.read('xl/worksheets/sheet1.xml').decode(), re.S):
        r = []
        for a, b in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
            v = re.search(r'<v>(.*?)</v>', b or '')
            r.append('' if not v else (ss[int(v.group(1))] if 't="s"' in a else v.group(1)))
        out.append(r)
    return out

def load_rates(f):
    rows = xlsx_rows(f); hdr = next(r for r in rows if r and r[1:2] == ['2024']); yrs = [int(x) for x in hdr[1:] if x.strip().isdigit()]
    d = {}
    for r in rows[rows.index(hdr) + 1:]:
        if r and r[0] and len(r) > 2:
            d[r[0].strip()] = {y: (float(v) if re.fullmatch(r'[\d.]+', v or '') else None) for y, v in zip(yrs, r[1:])}
    return d

def load_acs():
    acs = {}
    for y in YEARS:
        p = 'data/raw/acs_%d.json' % y
        if not os.path.exists(p): continue
        rows = json.load(open(p))['rows']; h = rows[0]
        for r in rows[1:]:
            d = dict(zip(h, r)); nm = d['NAME']
            if nm == 'Puerto Rico': continue
            acs[(nm, y)] = d
    return acs

def read_sf(y, t):
    f = 'raw/%d-%s.dat' % (y, t.lower())
    if not os.path.exists(f): return None
    L = open(f).read().splitlines(); h = L[0].split('|'); return {l.split('|')[0]: dict(zip(h, l.split('|'))) for l in L[1:]}

def build(nchs, acs):
    rows = []
    for ev, (k, tab) in EV.items():
        for st in sorted(nchs[k]):
            if st == 'United States': continue
            for y in YEARS:
                d = acs.get((st, y)); n = nchs[k][st][y - 2000] if y <= 2023 else None
                row = dict(event=ev, state=st, year=y, nchs=n)
                if d:
                    fe, fm, me, mm = d[tab + '_010E'], d[tab + '_010M'], d[tab + '_005E'], d[tab + '_005M']
                    iv = interval(fe, fm); ivm = interval(me, mm); iv95 = interval(fe, fm, 1.96 / 1.645)
                    row.update(acs_women=float(fe) if iv else None, acs_women_moe=float(fm) if iv else None, acs_men=float(me) if ivm else None, acs_men_moe=float(mm) if ivm else None, pop=d['B01003_001E'])
                else: iv = ivm = iv95 = None
                oc, rs = outcome(n, iv, y); om, rm = outcome(n, ivm, y); o95, _ = outcome(n, iv95, y)
                row.update(outcome=oc, reason=rs, outcome_men=om, outcome_95=o95, sex_split=(oc in (ABOVE, BELOW, CONSISTENT) and om in (ABOVE, BELOW, CONSISTENT) and oc != om),
                           ratio=(round(n / row['acs_women'], 3) if n and iv and row.get('acs_women') else None), destination=st in DEST[ev])
                rows.append(row)
    return rows

def tally(rows):
    c = {ABOVE: 0, BELOW: 0, CONSISTENT: 0, CT: 0, 'by_reason': {}, 'sex_split': 0, 'rows': len(rows)}
    for r in rows:
        c[r['outcome']] += 1; c['sex_split'] += bool(r['sex_split'])
        if r['reason']: c['by_reason'][r['reason']] = c['by_reason'].get(r['reason'], 0) + 1
    c['read'] = cell_read(c); return c

def cells(rows):
    out = {}
    for ev in EV:
        R = [r for r in rows if r['event'] == ev]
        out[ev] = dict(overall=tally(R), excluding_destination=tally([r for r in R if not r['destination']]), destination=tally([r for r in R if r['destination']]),
                       by_state={s: tally([r for r in R if r['state'] == s]) for s in sorted({r['state'] for r in R})},
                       by_year={str(y): tally([r for r in R if r['year'] == y]) for y in YEARS})
        for s, c in out[ev]['by_state'].items():
            q = [r['ratio'] for r in R if r['state'] == s and r['ratio']]; c['median_ratio'] = round(statistics.median(q), 3) if q else None
    return out

def gates(nchs, acs, rates, rows):
    g = {}
    ok = True; det = {}
    for k in ('divorce', 'marriage'):
        n = len(nchs[k]); badlen = [s for s, v in nchs[k].items() if len(v) != 24]; us = nchs[k]['United States']; miss = []
        for i in range(24):
            s = sum(v[i] for st, v in nchs[k].items() if st != 'United States' and v[i] is not None)
            if s != us[i]: miss.append((2000 + i, s, us[i]))
        det[k] = dict(entries=n, bad_length=badlen, us_sum_mismatch_years=miss)
        ok &= n == 52 and not badlen and not miss
    for y in YEARS:
        ns = [s for (s, yy) in acs if yy == y]; ok &= len(ns) == 51
    g['1_format'] = dict(passed=ok, detail=det)
    hand = json.load(open('data/known_good_rows.json')); ok2 = True; hd = []
    for h in hand:
        k = EV[h['event']][0]; n = nchs[k][h['state']][h['year'] - 2000]; a = acs[(h['state'], h['year'])]; tab = EV[h['event']][1]
        good = n == h['nchs'] and int(a[tab + '_010E']) == h['acs_women'] and int(a[tab + '_010M']) == h['acs_moe']; hd.append(dict(row=h['state'] + ' ' + str(h['year']) + ' ' + h['event'], equal=good)); ok2 &= good
    cmp = []
    for k, ev in (('divorce', 'DIVORCE'), ('marriage', 'MARRIAGE')):
        pass
    tot = hit = 0
    for ev, (k, tab) in EV.items():
        for st, v in nchs[k].items():
            if st == 'United States': continue
            for y in YEARS:
                if y > 2023 or v[y - 2000] is None or (st, y) not in acs: continue
                rate = rates[k].get(st, {}).get(y)
                if rate is None: continue
                pop = float(acs[(st, y)]['B01003_001E']); tot += 1; hit += abs(v[y - 2000] / pop * 1000 - rate) <= 0.1 + 1e-9
    share = hit / tot if tot else 0
    g['2_reader'] = dict(passed=bool(ok2 and share >= 0.90), hand_rows=hd, rate_check=dict(compared=tot, within_tenth=hit, share=round(share, 4)))
    tot = eq = 0
    for y in (2022, 2023):
        for t, vs in (('B12503', ('005', '010')), ('B12501', ('005', '010')), ('B01003', ('001',))):
            sf = read_sf(y, t)
            if sf is None: continue
            for gid, d in sf.items():
                if not gid.startswith('0400000US'): continue
                for c in vs:
                    for s in ('E', 'M'):
                        key = '%s_%s%s' % (t, s, c); fips = gid[-2:]
                        nm = next((nm for (nm, yy), a in acs.items() if yy == y and a['state'] == fips), None)
                        if nm is None: continue
                        tot += 1; eq += str(acs[(nm, y)]['%s_%s%s' % (t, c, s)]) == str(d[key]).strip()
    g['3_join'] = dict(passed=bool(tot and eq / tot >= 0.99), compared=tot, equal=eq)
    g['4_rule'] = dict(passed=rule_selftest()[0], detail=rule_selftest()[1])
    return g

def rule_selftest():
    iv = (100.0, 200.0); chk = []
    for n, i, y, want in ((250, iv, 2023, (ABOVE, None)), (50, iv, 2023, (BELOW, None)), (150, iv, 2023, (CONSISTENT, None)), (200, iv, 2023, (CONSISTENT, None)), (100, iv, 2023, (CONSISTENT, None)),
                          (None, iv, 2023, (CT, R_NOREP)), (150, None, 2023, (CT, R_NOACS)), (150, iv, 2024, (CT, R_NOSTATED)), (None, None, 2023, (CT, R_NOREP))):
        chk.append(outcome(n, i, y) == want)
    chk.append(interval(-555555555, 100) is None and interval(100, -1) is None and interval(100, None) is None and interval(10, 30) == (0.0, 40.0))
    c = {ABOVE: 9, BELOW: 1, CONSISTENT: 0, CT: 0}; chk.append(cell_read(c) == ABOVE)
    chk.append(cell_read({ABOVE: 3, BELOW: 3, CONSISTENT: 0, CT: 5}) == 'MIXED' and cell_read({ABOVE: 2, BELOW: 2, CONSISTENT: 0, CT: 0}) == CT)
    return all(chk), chk

def snapshot():
    os.makedirs('data/snapshots', exist_ok=True); day = time.strftime('%Y%m%d', time.gmtime()); n = 0
    for f in glob.glob('raw/*.xlsx'):
        b = os.path.basename(f)
        if b.startswith('old-'): continue
        dst = 'data/snapshots/%s_%s' % (day, b)
        if not os.path.exists(dst): shutil.copy(f, dst); n += 1
    return n

def main():
    seal = json.load(open('data/plan_seal.json'))
    assert K.plan_committed('PLAN.md'), 'PLAN.md not committed'
    assert hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest() == seal['plan_sha256'], 'plan changed after seal'
    lock = '.run.lock'
    if os.path.exists(lock): raise SystemExit('run lock present')
    open(lock, 'w').write(str(os.getpid()))
    try:
        nchs = json.load(open('data/nchs_counts.json')); acs = load_acs(); rates = {'divorce': load_rates('raw/state-divorce-rates-90-95-00-24.xlsx'), 'marriage': load_rates('raw/state-marriage-rates-90-95-00-24.xlsx')}
        seal.setdefault('first_comparison', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())); json.dump(seal, open('data/plan_seal.json', 'w'), indent=1)
        rows = build(nchs, acs); g = gates(nchs, acs, rates, rows)
        passed = all(v['passed'] for v in g.values())
        rows = K.apply_gate(passed, rows)
        sn = snapshot()
        summ = dict(plan_seal=seal, run=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), gates=g, gates_passed=passed, rows=len(rows), cells=cells(rows), snapshot_files_copied=sn)
        json.dump(rows, open('data/fidelity.json', 'w')); json.dump(summ, open('summary_fidelity.json', 'w'), indent=1)
        for ev in EV:
            c = summ['cells'][ev]['overall']; print(ev, {k: c[k] for k in (ABOVE, BELOW, CONSISTENT, CT, 'by_reason', 'sex_split')})
        print('gates', {k: v['passed'] for k, v in g.items()})
    finally: os.remove(lock)

def selftest():
    ok, chk = rule_selftest(); print('rule', 'OK' if ok else 'FAIL', chk)
    rates = {}; r = [dict(event='DIVORCE', state='X', year=2023, outcome=ABOVE, reason=None, sex_split=False, destination=False, ratio=1.0)]
    print('tally', tally(r)[ABOVE] == 1)
    return ok

if __name__ == '__main__':
    if '--selftest' in sys.argv:
        a = selftest(); sys.exit(0 if a else 1)
    main()
