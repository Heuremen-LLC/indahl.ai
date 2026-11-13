# Referee audits for ADSPEND, from the raw cache (run load_raw.py first, from this folder): payee rule, Nothing returned,
# neutrality by filed party field, and the payments outside the pool behind each Below row. Prints only; writes nothing.
import sys, re, json, collections as C, datetime as D
sys.path.insert(0, '.')
import recount
R = recount.raw(); cm = R['cm']
base, meta = recount.build('plan', keep_rows=True)
P = lambda m: m['party'] or '(blank)'

print('== payee rule (every oppexp row whose payee a broad Google-ish net catches, all committees)')
rows = R['broad']; caught = [r for r in rows if recount.is_g(r[4])]; missed = [r for r in rows if not recount.is_g(r[4])]
print('rows', len(rows), 'caught', len(caught), round(sum(r[3] for r in caught)), 'not caught', len(missed), round(sum(r[3] for r in missed)))
mc = C.defaultdict(lambda: [0, 0.0])
for r in missed:
    if r[4] != '<IND>': mc[r[4]][0] += 1; mc[r[4]][1] += r[3]
for p, (n, s) in sorted(mc.items(), key=lambda kv: -kv[1][1])[:30]: print(f'   not caught {n:5d} ${s:>10,.0f}  {p}')
cc = C.defaultdict(lambda: [0, 0.0])
for r in caught: cc[r[4]][0] += 1; cc[r[4]][1] += r[3]
for p, (n, s) in sorted(cc.items(), key=lambda kv: -kv[1][1]):
    if not re.match(r'^(GOOGLE|YOUTUBE|YOU TUBE)\b', p): print(f'   caught, not starting GOOGLE/YOUTUBE {n:5d} ${s:>10,.0f}  {p}')

print('\n== Nothing returned')
nr = [m for m in base.values() if m['outcome'] == 'NOTHING_RETURNED']
reg = lambda m: any(m['cycle'] in cm[x] for x in m['members'])
print('rows', len(nr), '| Google stated in window = 0:', sum(m['G_pt'] == 0 for m in nr), '| no member in that cycle\'s cm file:', sum(not reg(m) for m in nr),
      '| either:', sum((not reg(m)) or m['G_pt'] == 0 for m in nr), '| neither:', sum(reg(m) and m['G_pt'] > 0 for m in nr))

print('\n== outcomes by filed party field (cycle rows)')
tab = C.defaultdict(C.Counter)
for m in base.values(): tab[m['outcome']][P(m)] += 1
for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED'): print('  ', o, dict(tab[o]))
cls = C.defaultdict(C.Counter)
for m in base.values():
    for r in m['ggrows']: cls[P(m)][r[3]] += r[2]
for p in ('DEM', 'REP', '(blank)'):
    t = sum(cls[p].values()); print(f'   Google dollars by class {p}: total ${t:,.0f} ' + ', '.join(f'{k} {100 * v / t:.1f}%' for k, v in sorted(cls[p].items())))
for p in ('DEM', 'REP'):
    s = [m for m in base.values() if P(m) == p]; print(f'   {p}: rows {len(s)}, rows with any reported Google payment {sum(m["D_hi"] > 0 for m in s)}')

print('\n== Below rows: positive non-memo payments in the window outside the pool and not to Google, by purpose family')
CAT = [('card', re.compile(r'CREDIT CARD|\bCC\b|AMEX|AMERICAN EXPRESS|VISA|MASTERCARD|CARD PAYMENT|CHARGE CARD|CAPITAL ONE|CHASE')), ('reimb', re.compile(r'REIMB')),
       ('consult', re.compile(r'CONSULT|STRATEG|COMMUNICATIONS|CAMPAIGN SERVICES|POLITICAL SERVICES')), ('fundraising', re.compile(r'FUNDRAIS|SOLICIT|LIST RENTAL|DONOR|TEXT|SMS|EMAIL|E-MAIL'))]
for k, m in sorted(base.items(), key=lambda kv: (kv[1]['cycle'], kv[1]['name'])):
    if m['outcome'] != 'BELOW': continue
    a = D.date.fromisoformat(m['window'][0]).toordinal(); b = D.date.fromisoformat(m['window'][1]).toordinal()
    gap = m['G_lo'] - (max(m['D_hi'], 0) + m['pool'] + m['unseen']); size = max(1000, 0.1 * m['G_lo']); s = C.Counter()
    for x in m['members']:
        for r in R['opp'].get(x, []):
            if not (a <= r[1] <= b) or r[5] or r[2] <= 0 or (r[3] and recount.is_g(r[3])) or recount.pool_purpose(r[4]): continue
            for nm, rx in CAT:
                if rx.search(r[4]): s[nm] += r[2]; break
            else: s['other'] += r[2]
    print(f"   {m['cycle']} {m['cid']} {m['name'][:36]:36} gap {gap:>9,.0f} size {size:>7,.0f} | card+reimb {s['card'] + s['reimb']:>10,.0f} consult+fundraising {s['consult'] + s['fundraising']:>10,.0f}"
          + ('  CARD/REIMB COULD CLOSE' if s['card'] + s['reimb'] > gap - size else ''))
