# Stated-side checks. python3 -I
import random
src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
print('parsed files (2021+):', sum(1 for r in allparsed if r['day'] >= dt.date(2021,1,1)), 'stated days', len(stated))
# issued time distribution
dist = C.Counter(); late_after_mid = []
for r in allparsed:
    if r['day'] < dt.date(2021,1,1): continue
    delta = r['iss'] - dt.datetime.combine(r['day'], dt.time(22, 0))
    dist[int(delta.total_seconds() // 60) if abs(delta.total_seconds()) < 3600 * 6 else 'other'] += 1
    if r['iss'].date() != r['day']: late_after_mid.append((str(r['day']), str(r['iss'])))
print('issued minus 2200 of report day (minutes) top:', dist.most_common(8))
print('reports whose :Issued: date != SDF day:', len(late_after_mid), late_after_mid)
# dates gate failures
bad = [(str(d), str(r['d1']), r['src']) for d, r in stated.items() if r['d1'] != d + dt.timedelta(1)]
print('Part III header d1 != SDF day + 1:', bad)
# missing report days
miss = [str(dt.date(2021,1,1) + dt.timedelta(i)) for i in range((RUN - dt.date(2021,1,1)).days + 1) if (dt.date(2021,1,1) + dt.timedelta(i)) not in stated]
print('days with no report:', len(miss), miss[:10], '...', miss[-3:])
# issued late (iss >= target 00:00) by lead
late = C.Counter()
for d, r in stated.items():
    for L in (1, 2, 3):
        if r['iss'] >= dt.datetime.combine(d + dt.timedelta(L + 0) if False else r['d1'] + dt.timedelta(L - 1), dt.time()): late[L] += 1
print('issued-late (by report) per lead:', dict(late))
for d, r in sorted(stated.items()):
    if r['iss'] >= dt.datetime.combine(r['d1'], dt.time()): print('  late report', d, r['iss'], 'SDF day', r['day'])
# value sanity
odd = []
for d, r in stated.items():
    for k in ('M','X','P','mid_mi','mid_ma','hi_mi','hi_ma'):
        v = r[k]
        if v is None or any(x < 0 or x > 100 for x in v): odd.append((str(d), k, v))
print('missing/out-of-range triples:', odd[:5], len(odd))
print('capped sums:', [(str(d), k, r[k + '_mi'], r[k + '_ma']) for d, r in stated.items() for k in ('mid','hi') if any(r[k+'_mi'][i] + r[k+'_ma'][i] > 100 for i in range(3))])
# monotone check: major <= minor+major trivial. check K>=5 sum < = 100 + Active ordering: Active+Minor+Major vs 100?
# does Active+Minor+Major-severe ever exceed 100 or not? (tests the 'categories add' reading)
tot = []
for ln_src, tx in rsga_files():
    m = re.search(r'^VI\.\s+Geomagnetic Activity Probabilities', tx, re.M)
    if not m: continue
    A = tx[m.start(): tx.find('B.  High', m.start())]
    ac = tri(A, 'Active'); mi = tri(A, 'Minor storm'); ma = tri(A, 'Major-severe storm')
    if ac and mi and ma: tot.append(max(ac[i]+mi[i]+ma[i] for i in range(3)))
print('Part VI A: files', len(tot), 'with Active+Minor+Major > 100:', sum(1 for t in tot if t > 100), ' max', max(tot))
# report-day keying old vs new (Addendum 1 item 1): old = key by :Issued: date, earliest wins
old = {}
for r in allparsed:
    k = r['iss'].date()
    if k < dt.date(2021,1,1): continue
    if k not in old or r['iss'] < old[k]['iss']: old[k] = r
chg = [(str(k), str(old[k]['day']) if k in old else None, str(stated[k]['day']) if k in stated else None) for k in set(old) | set(stated) if (k in old) != (k in stated) or (k in old and k in stated and old[k]['src'] != stated[k]['src'])]
print('days where old-key report differs from SDF-key report:', len(chg), sorted(chg)[:20])
# scored rows affected: new rule scored (issue day, lead) set vs old rule; compute for M/day1
def scoredset(S, ev='M', L=1):
    out = {}
    for d, r in S.items():
        tg = d + dt.timedelta(L)
        if r['d1'] != d + dt.timedelta(1): continue
        if r['iss'] >= dt.datetime.combine(tg, dt.time()): continue
        p = pstated(r, ev, L - 1); o, w = obs(ev, tg)
        if p is not None and o is not None: out[str(d)] = (p, o)
    return out
for ev in ('M', 'MID5'):
  for L in (1, 2, 3):
    a, b = scoredset(old, ev, L), scoredset(stated, ev, L)
    print(ev, 'lead', L, 'scored old-key', len(a), 'new-key', len(b), 'only old', len(set(a) - set(b)), 'only new', len(set(b) - set(a)), 'same-day different p/o', sum(1 for k in set(a) & set(b) if a[k] != b[k]))
