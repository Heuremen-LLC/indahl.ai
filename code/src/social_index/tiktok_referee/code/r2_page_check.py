"""Referee pass 2: every number in section_tiktok.html against the referee recount (eu_rows_recount.json, stated_recount.json)."""
import re, html, json, sys
R = '/Users/heuremen/bones-forge/social_index/tiktok_referee/'
H = open(sys.argv[1] if len(sys.argv) > 1 else '/Users/heuremen/bones-forge/social_index/tiktok/section_tiktok.html').read()
E = json.load(open(R + 'eu_rows_recount.json')); S = json.load(open(R + 'stated_recount.json'))
OUT = {'ABOVE': 'Above', 'BELOW': 'Below', 'CANNOT_TELL': 'Cannot tell', 'CONSISTENT': 'Consistent'}
QL = {'Jul to Sep': 3, 'Oct to Dec': 4, 'Jan to Mar': 1, 'Apr to Jun': 2}
tables = []
for t in re.findall(r'<table.*?</table>', H, re.S):
    rows = []
    for tr in re.findall(r'<tr.*?</tr>', t, re.S):
        cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
        rows.append(cells)
    tables.append(rows)
bad = []; n = 0
def num(s):
    s = s.replace(',', '').replace('%', '').replace('+', '').replace('−', '-').strip()
    return float(s)
def dec(s):
    s = s.replace('%', '').split(' ')[0]
    return len(s.split('.')[1]) if '.' in s else 0
def chk(label, txt, val, kind):
    global n
    n += 1
    if val is None:
        bad.append((label, txt, None)); return
    if kind == 'count':
        ok = abs(num(txt) - round(val)) < 0.5
    elif kind == 'pct':  # val is a fraction
        d = dec(txt); ok = abs(num(txt) - 100 * val) <= 0.5 * 10 ** (-d) + 1e-9
    elif kind == 'pts':
        d = dec(txt); ok = abs(num(txt) - 100 * val) <= 0.5 * 10 ** (-d) + 1e-9
    elif kind == 'gpct':
        d = dec(txt); ok = abs(num(txt) - 100 * val) <= 0.5 * 10 ** (-d) + 1e-9
    if not ok: bad.append((label, txt, val))
def rng(s):
    a, b = s.replace(' points', '').split(' to ')
    return a.strip(), b.strip()
def q_of(s):
    for k, v in QL.items():
        if s.startswith(k): return '%sQ%d' % (s[-4:], v)
# table 0: Apr-Jun 2026 EU total
MS = {'Videos removed': 'videos_removed', 'Automated removals': 'automated_removals', 'Automated share of removals': 'automated_share',
      'Removed before any report': 'proactive_rate', 'Removed within 24 hours of posting': 'within_24h_rate'}
for row in tables[0][1:]:
    row = [c for c in row if c != '']
    ms = MS[row[0]]; r = E['2026Q2']['rows'][ms]; cnt = ms in ('videos_removed', 'automated_removals')
    k = 'count' if cnt else 'pct'
    chk('T0 %s stated' % ms, row[1], r['S'][0], k)
    if row[2] != 'see range': chk('T0 %s D' % ms, row[2], r['Dpoint'], k)
    a, b = rng(row[3]); chk('T0 %s S_lo' % ms, a, r['S'][1], k); chk('T0 %s S_hi' % ms, b, r['S'][2], k)
    a, b = rng(row[4]); chk('T0 %s D_lo' % ms, a, r['rule']['D'][0], k); chk('T0 %s D_hi' % ms, b, r['rule']['D'][1], k)
    a, b = rng(row[5])
    if cnt: chk('T0 %s g_lo' % ms, a, r['rule']['gap'][0] / r['S'][0], 'gpct'); chk('T0 %s g_hi' % ms, b, r['rule']['gap'][1] / r['S'][0], 'gpct')
    else: chk('T0 %s g_lo' % ms, a, r['rule']['gap'][0], 'pts'); chk('T0 %s g_hi' % ms, b, r['rule']['gap'][1], 'pts')
    n += 2
    if row[6] != OUT[r['committed']]: bad.append(('T0 %s outcome' % ms, row[6], r['committed']))
    if row[7] != OUT[r['posthoc_outcome']]: bad.append(('T0 %s posthoc' % ms, row[7], r['posthoc_outcome']))
# table 1: videos removed every quarter
Dd = json.load(open(R + 'delivered_recount.json'))
for row in tables[1][1:]:
    row = [c for c in row if c != '']
    q = q_of(row[0]); r = E[q]['rows']['videos_removed']
    if row[1] != str(len(S[q]['detail']['listed_eu'])): bad.append(('T1 %s listed' % q, row[1], len(S[q]['detail']['listed_eu'])))
    chk('T1 %s stated' % q, row[2], r['S'][0], 'count'); chk('T1 %s D' % q, row[3], r['Dpoint'], 'count')
    sub = Dd[q]['grid']['point|created']['n'] if q in Dd else None
    if q == '2023Q3':
        import duckdb, glob
        con = duckdb.connect(); fs = sorted(glob.glob('/Users/heuremen/bones-forge/social_index/tiktok/data/raw/dsa_tiktok/complete_*.parquet'))
        sub = con.execute("select sum(n) from read_parquet([%s], union_by_name=true) where dv_removed and ct_video and not ct_ad and created_day between DATE '2023-07-01' and DATE '2023-09-30'" % ','.join("'%s'" % f for f in fs)).fetchone()[0]
    chk('T1 %s Dsub' % q, row[4], sub, 'count')
    a, b = rng(row[5]); chk('T1 %s g_lo' % q, a, r['rule']['gap'][0] / r['S'][0], 'gpct'); chk('T1 %s g_hi' % q, b, r['rule']['gap'][1] / r['S'][0], 'gpct')
    n += 2
    if row[6] != OUT[r['committed']]: bad.append(('T1 %s outcome' % q, row[6], r['committed']))
    if row[7] != OUT[r['posthoc_outcome']]: bad.append(('T1 %s posthoc' % q, row[7], r['posthoc_outcome']))
for ti, ms in ((2, 'automated_share'), (3, 'proactive_rate')):
    for row in tables[ti][1:]:
        row = [c for c in row if c != '']
        q = q_of(row[0]); r = E[q]['rows'][ms]
        chk('T%d %s stated' % (ti, q), row[1], r['S'][0], 'pct'); chk('T%d %s D' % (ti, q), row[2], r['Dpoint'], 'pct')
        a, b = rng(row[3]); chk('T%d %s g_lo' % (ti, q), a, r['rule']['gap'][0], 'pts'); chk('T%d %s g_hi' % (ti, q), b, r['rule']['gap'][1], 'pts')
        n += 2
        if row[4] != OUT[r['committed']]: bad.append(('T%d %s outcome' % (ti, q), row[4], r['committed']))
        if row[5] != OUT[r['posthoc_outcome']]: bad.append(('T%d %s posthoc' % (ti, q), row[5], r['posthoc_outcome']))
# table 4: markets Apr-Jun 2026
mk = S['2026Q2']['detail']['market']
for row in tables[4][1:]:
    row = [c for c in row if c != '']
    m = row[0]
    if m in mk:
        v = mk[m]
        chk('T4 %s T' % m, row[1], v['T'], 'count'); chk('T4 %s ash' % m, row[2], (v.get('AUTO', 0) + v.get('AI', 0)) / v['T'], 'pct'); chk('T4 %s pro' % m, row[3], v['PRO'], 'pct')
        if row[4] != '0' or row[5] != 'Nothing returned': bad.append(('T4 %s' % m, row[4:], '0 / Nothing returned'))
        n += 2
    else:
        n += 1
        if m not in ('Luxembourg', 'Malta'): bad.append(('T4 unexpected market', m, None))
print('numbers and outcomes checked:', n, 'differences:', len(bad))
for b in bad: print('  ', b)
# prose numbers
txt = html.unescape(re.sub(r'<[^>]+>', ' ', H))
for pat in ['18,459,784', '1,091 of 1,138', '858,890', '184,124', '94%', '25 September 2023', '2023-09 to 2026-11']:
    print('prose', pat, pat in txt)
print('semicolons in visible text:', [m.start() for m in re.finditer(';', re.sub(r'&[a-z#0-9]+;', '', re.sub(r'<[^>]+>', ' ', H)))][:5])
