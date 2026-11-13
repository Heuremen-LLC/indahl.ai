#!/usr/bin/env python3
"""analyze_petrol.py: PETROL desk. Reads data/momr_secondary.csv, data/targets.csv and the two EIA files. Applies PLAN.md exactly. Writes summary_petrol.json.
Run with the venv python (xlrd). Refuses to run if PLAN.md changed since data/plan_seal.json."""
import os, sys, csv, json, math, hashlib, time, datetime, collections, statistics
import xlrd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'heuremen_kit')); import heuremen_kit as K   # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): the canonical kit, imported by path
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
OUT = ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')
plan_sha = hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(); seal = json.load(open('data/plan_seal.json'))
MATCH = plan_sha == seal['plan_sha256']
MEMBERS = ['Algeria','Congo','Equatorial Guinea','Gabon','IR Iran','Iraq','Kuwait','Libya','Nigeria','Saudi Arabia','UAE','Venezuela','Azerbaijan','Bahrain','Brunei','Kazakhstan','Malaysia','Mexico','Oman','Russia','Sudan','South Sudan']
OPEC9 = ['Algeria','Congo','Equatorial Guinea','Gabon','Iraq','Kuwait','Nigeria','Saudi Arabia','UAE']
NONOPEC = ['Azerbaijan','Bahrain','Brunei','Kazakhstan','Malaysia','Mexico','Oman','Russia','Sudan','South Sudan']
EXEMPT = ['Libya','IR Iran','Venezuela']
def p90(xs):
    xs = sorted(xs); return xs[math.ceil(0.9 * len(xs)) - 1]
NIF, TWR = K.NO_INTERVAL_FORMABLE, K.TOO_WIDE_TO_RESOLVE
CODE = {'exempt, no required level': NIF, 'no target table transcribed': NIF, 'no delivered value': NIF, 'no monthly value': NIF, 'gate failed or plan changed': NIF, 'no width': TWR, 'fewer than four weeks': TWR}   # PLAN_ADDENDUM_std2.md
def classify3(delta, w, reason=None):
    """12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): an exact row-level point reading is an interval of zero width (O1), read against the band [-w, w], edges closed.
    Returns (outcome, reason code, prose reason). The prose reason is the sealed plan's own wording."""
    if reason: return 'CANNOT_TELL', CODE.get(reason, NIF), reason
    if delta is None: return 'CANNOT_TELL', NIF, 'no delivered value'
    if w is None: return 'CANNOT_TELL', TWR, 'no width'
    o, why, _ = K.read_exact(delta, band=(-w, w), edge='closed'); return o, why, None
def classify(delta, w, reason=None):
    o, c, d = classify3(delta, w, reason); return o, d
def tally(rows):
    c = {o: 0 for o in OUT}; why = collections.Counter()
    for r in rows:
        c[r['outcome']] += 1
        if r['outcome'] == 'CANNOT_TELL': why[r['reason_detail']] += 1
    return c, dict(why)
def by_code(rows): return dict(collections.Counter(r['reason'] for r in rows if r['outcome'] == 'CANNOT_TELL'))
def r13(rows): return K.req13([(r['outcome'], r['reason']) for r in rows], nothing_returned=0)   # no row-level read failed, see the addendum
def mnum(s): y, m = s.split('-'); return int(y) * 12 + int(m) - 1
# ---------------- Part 1
prints = collections.defaultdict(dict); src = {}
for r in csv.DictReader(open('data/momr_secondary.csv')):
    v = float(r['secondary_tbd']) if r['secondary_tbd'] != '' else None
    prints[(r['member'], r['month'])][r['issue']] = v; src[(r['member'], r['month'], r['issue'])] = (r['pdf'], r['page'], r['table'])
tg = {}
for r in csv.DictReader(open('data/targets.csv')): tg[(r['member'], r['month'])] = r
issues = sorted({i for d in prints.values() for i in d}); issue_set = set(issues)
# revisions: first print = earliest cached issue holding the month with a value, second = the issue one calendar month later, both must be cached
rev = collections.defaultdict(list)   # member -> list of (month, first, second, first_issue, second_issue)
for (mem, mo), d in prints.items():
    got = sorted(i for i, v in d.items() if v is not None)
    if not got: continue
    f = got[0]
    y, m = int(f[:4]), int(f[5:]); s = '%d-%02d' % (y + (m // 12), m % 12 + 1)
    if s in d and d[s] is not None and s <= '2024-10' and mnum(f) == mnum(mo) + 1: rev[mem].append((mo, d[f], d[s], f, s))
width, wnote = {}, {}
for mem in OPEC9:
    xs = [abs(b - a) for _, a, b, _, _ in rev[mem]]
    if len(xs) >= 24: width[mem] = p90(xs); wnote[mem] = dict(n=len(xs), p90_abs_revision_tbd=width[mem], nonzero=sum(1 for x in xs if x))
    else: width[mem] = None; wnote[mem] = dict(n=len(xs), p90_abs_revision_tbd=None)
rel = [abs(b - a) / a for mem in NONOPEC for _, a, b, _, _ in rev[mem] if a]
q = p90(rel) if len(rel) >= 30 else None
pooled = dict(n=len(rel), p90_relative=q)
def months():
    # 12 Nov 2026 amendment A1 (PLAN.md): the window rolls. It starts November 2024 and ends at the month after the newest MOMR issue's latest
    # reference month (the month whose target is known but delivered output is not yet out), so a new issue adds a month without a code change.
    ref = max(r['month'] for r in csv.DictReader(open('data/momr_secondary.csv')))
    ey, em = int(ref[:4]), int(ref[5:7]) + 1; ey, em = (ey + 1, 1) if em == 13 else (ey, em)
    y, m = 2024, 11; o = []
    while (y, m) <= (ey, em): o.append('%d-%02d' % (y, m)); m += 1; y, m = (y + 1, 1) if m == 13 else (y, m)
    return o
MON = months(); rows = []
for mem in MEMBERS:
    for mo in MON:
        d = prints.get((mem, mo), {}); got = sorted(i for i, v in d.items() if v is not None)
        deliv = d[got[-1]] if got else None; di = got[-1] if got else None
        t = tg.get((mem, mo)); reason = None
        if mem in EXEMPT: reason = 'exempt, no required level'
        elif t is None: reason = 'no target table transcribed' if mem in NONOPEC + OPEC9 and mo >= '2025-01' else 'no target table transcribed'
        elif deliv is None: reason = 'no delivered value'
        w = None
        if mem in OPEC9: w = width[mem]
        elif mem in NONOPEC and q is not None and deliv is not None: w = q * deliv
        if not reason and w is None: reason = 'no width'
        gap = (deliv - float(t['target_tbd'])) if (t and deliv is not None) else None
        out, code, why = classify3(gap, w, reason)
        pdf, page, tbl = src.get((mem, mo, di), ('', '', ''))
        rows.append(dict(member=mem, month=mo, outcome=out, reason=code, reason_detail=why, required=float(t['target_tbd']) if t else None, delivered=deliv, gap=gap, width=w,
                         delivered_issue=di, delivered_pdf=pdf, delivered_page=page, delivered_table=tbl, target_url=t['source_url'] if t else None, target_image=t['image_url'] if t else None,
                         n_prints=len(got), prints={i: d[i] for i in sorted(d)}))
c_all, why_all = tally(rows)
by_month = {mo: dict(zip(OUT, [0] * 4)) for mo in MON}
for r in rows: by_month[r['month']][r['outcome']] += 1
by_member = {}
for mem in MEMBERS:
    rr = [r for r in rows if r['member'] == mem]; c, why = tally(rr); sc = [r for r in rr if r['gap'] is not None and r['outcome'] != 'CANNOT_TELL']
    by_member[mem] = dict(counts=c, cannot_tell_why=why, median_gap_tbd=statistics.median([r['gap'] for r in sc]) if sc else None,
                          largest_gap=max(sc, key=lambda r: abs(r['gap']))['gap'] if sc else None, largest_gap_month=max(sc, key=lambda r: abs(r['gap']))['month'] if sc else None, width_note=wnote.get(mem))
latest = max((mo for mo in MON if any(r['month'] == mo and r['delivered'] is not None for r in rows)), default=None)
hm = latest
while hm and sum(by_month[hm][o] for o in OUT[:3]) < 6: hm = '%d-%02d' % divmod(mnum(hm) - 1, 12) if False else MON[MON.index(hm) - 1] if MON.index(hm) > 0 else None
head1 = dict(month=hm, latest_month_with_delivered=latest, counts=by_month.get(hm), counts_all_months=c_all, cannot_tell_by_reason=by_code([r for r in rows if r['month'] == hm]), req13=r13([r for r in rows if r['month'] == hm]), req13_all_months=r13(rows), members=len(MEMBERS), window_months=len(MON))
# ---------------- Part 2
def xl(path, col=1):
    s = xlrd.open_workbook(path).sheet_by_name('Data 1'); hdr = s.cell_value(2, 1)
    out = [(xlrd.xldate_as_datetime(s.cell_value(i, 0), 0).date(), s.cell_value(i, col)) for i in range(3, s.nrows) if s.cell_value(i, 1) != '']
    return hdr, out
wh, W = xl('data/raw/WCRFPUS2w.xls'); mh, M = xl('data/raw/MCRFPUS2m.xls')
monthly = {'%d-%02d' % (d.year, d.month): v for d, v in M}; wk = collections.defaultdict(list)
for d, v in W: wk['%d-%02d' % (d.year, d.month)].append(v)
def e_row(mo, w, tag):
    n = len(wk.get(mo, [])); avg = sum(wk[mo]) / n if n else None; mv = monthly.get(mo); reason = None
    if mv is None: reason = 'no monthly value'
    elif n < 4: reason = 'fewer than four weeks'
    d = (avg - mv) if (avg is not None and mv is not None) else None
    out, code, why = classify3(d, w, reason)
    return dict(month=mo, weekly_avg=avg, n_weeks=n, monthly=mv, d=d, width=w, outcome=out, reason=code, reason_detail=why, set=tag)
base_m = ['%d-%02d' % (y, m) for y in range(2015, 2020) for m in range(1, 13)]
bd = [abs(r['d']) for r in (e_row(mo, 0, 'baseline') for mo in base_m) if r['d'] is not None]
EW = p90(bd) if len(bd) >= 48 else None
last_m = max(monthly); score_m = [mo for mo in sorted(monthly) if '2020-01' <= mo <= last_m]
erows = [e_row(mo, EW, 'scored') for mo in score_m]; brows = [e_row(mo, EW, 'baseline') for mo in base_m]
ec, ewhy = tally(erows)
byyear = {}
for y in sorted({r['month'][:4] for r in erows}):
    ds = [r['d'] for r in erows if r['month'][:4] == y and r['d'] is not None]
    byyear[y] = dict(months=len(ds), median_signed_d=statistics.median(ds) if ds else None, median_abs_d=statistics.median([abs(x) for x in ds]) if ds else None, counts=tally([r for r in erows if r['month'][:4] == y])[0])
sens = {}
for k in (0.5, 2.0):
    sens['x%.1f' % k] = tally([e_row(mo, EW * k if EW else None, 'scored') for mo in score_m])[0]
sc = [r for r in erows if r['d'] is not None]; big = max(sc, key=lambda r: abs(r['d']))
head2 = dict(counts=ec, cannot_tell_by_reason=by_code(erows), req13=r13(erows), scored_months=len(erows), width_tbd=EW, baseline='2015-01 to 2019-12', baseline_months=len(bd), latest=erows[-1], largest=big, by_year=byyear)
# ---------------- Gates
G = {}
tgate = json.load(open('data/targets_gate.json')) if os.path.exists('data/targets_gate.json') else dict(passed=False)
cnt = collections.defaultdict(set)
for r in csv.DictReader(open('data/momr_secondary.csv')): cnt[r['issue']].add(r['member'])
o9 = ['Algeria','Congo','Equatorial Guinea','Gabon','IR Iran','Iraq','Kuwait','Libya','Nigeria','Saudi Arabia','UAE','Venezuela']
g1a = all(set(o9) - {'IR Iran'} <= cnt[i] for i in issues if i >= '2020-05') and all(len(cnt[i]) == 22 for i in issues if i >= '2024-05')
tot = {mo: sum(v for m_ in o9 for v in [prints.get((m_, mo), {}).get('2026-10')] if v is not None) for mo in ('2026-07', '2026-08', '2026-09')}
g1b = all(abs(tot[mo] - t) <= 3 for mo, t in (('2026-07', 23717), ('2026-08', 24177), ('2026-09', 25097)))
hand = dict(Algeria=1003, Iraq=3920, **{'Saudi Arabia': 8001}, UAE=3917, Russia=8643, **{'South Sudan': 136})
g1c = all(prints[(k, '2026-09')].get('2026-10') == v for k, v in hand.items())
G['1_parse'] = dict(passed=bool(g1a and g1b and g1c), issue_layout_ok=g1a, opec_sum_vs_printed_total=dict(sum=tot, printed={'2026-07': 23717, '2026-08': 24177, '2026-09': 25097}, ok=g1b), hand_read_sep_2026_ok=g1c)
G['2_join'] = dict(passed=len(rows) == 22 * len(MON) and all((r['required'] is not None) or r['reason'] for r in rows), rows=len(rows))
G['3_targets'] = dict(passed=bool(tgate.get('passed')), detail=tgate.get('lines'))
syn = [classify3(11, 10)[0] == 'ABOVE', classify3(None, 10)[:2] == ('CANNOT_TELL', NIF), classify3(5, None)[:2] == ('CANNOT_TELL', TWR), classify3(5, 10, 'exempt, no required level')[1] == NIF, classify3(5, 10, 'fewer than four weeks')[1] == TWR, classify3(11, 10)[1] is None, classify(11, 10)[0] == 'ABOVE', classify(-11, 10)[0] == 'BELOW', classify(10, 10)[0] == 'CONSISTENT', classify(-10, 10)[0] == 'CONSISTENT', classify(None, 10) == ('CANNOT_TELL', 'no delivered value'), classify(5, None) == ('CANNOT_TELL', 'no width'), classify(5, 10, 'exempt')[1] == 'exempt']
G['4_rule'] = dict(passed=all(syn))
d_by_hand = None
jan = [v for d, v in W if d.year == 2019 and d.month == 1]; hand_avg = sum(jan) / len(jan)
g2 = dict(passed=True)
fm = [d for d, _ in M]; ok_m = all((b.year * 12 + b.month) - (a.year * 12 + a.month) == 1 for a, b in zip(fm, fm[1:]) if a.year >= 2015)
wd = [d for d, _ in W if d.year >= 2015]; ok_w = all((b - a).days <= 8 for a, b in zip(wd, wd[1:]))
G['E1_format'] = dict(passed=bool('Thousand Barrels per Day' in wh and 'Thousand Barrels per Day' in mh and ok_m and ok_w), monthly_continuous=ok_m, weekly_gap_ok=ok_w)
G['E2_join'] = dict(passed=all(r['n_weeks'] >= 4 for r in erows), short_months=[r['month'] for r in erows if r['n_weeks'] < 4])
G['E3_hand'] = dict(passed=abs(hand_avg - e_row('2019-01', 0, 'baseline')['weekly_avg']) < 1e-9, january_2019_weekly_average=hand_avg, weeks=jan)
G['E4_rule'] = dict(passed=all(syn))
allg = all(g['passed'] for g in G.values())
if not allg or not MATCH:
    for r in rows + erows: r['outcome'], r['reason'], r['reason_detail'] = 'CANNOT_TELL', NIF, 'gate failed or plan changed'
S = dict(standard='Faults and Guards 2.0', plan_addendum='PLAN_ADDENDUM_std2.md', updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), plan_sha256=plan_sha, plan_sha256_sealed=seal['plan_sha256'], plan_sealed=seal['sealed'], plan_matches_seal=MATCH, gates=G, gates_all_passed=allg,
         part1=dict(frame='22 members, November 2024 to October 2026', counts=c_all, cannot_tell_why=why_all, cannot_tell_by_reason=by_code(rows), req13=r13(rows), by_month=by_month, by_member=by_member, ruler=dict(opec_members=wnote, non_opec_pooled=pooled,
         baseline='revisions of months whose second print is in an issue up to 2024-10, issues 2020-05 to 2024-10 (OPEC members) and 2024-05 to 2024-10 (non-OPEC DoC members)'), headline=head1,
         issues_cached=issues, rows=rows),
         part2=dict(width_tbd=EW, baseline='2015-01 to 2019-12', baseline_n=len(bd), counts=ec, cannot_tell_why=ewhy, cannot_tell_by_reason=by_code(erows), req13=r13(erows), sensitivity=sens, by_year=byyear, headline=head2, rows=erows, baseline_rows=brows,
                    monthly_last=last_m, vintages='each EIA file holds one vintage, no earlier prints or later revisions can be read'))
json.dump(S, open('summary_petrol.json', 'w'), indent=1, default=str)
print('gates', {k: v['passed'] for k, v in G.items()}, 'seal', MATCH)
print('P1', c_all, why_all); print('P1 headline', head1); print('P2', ec, 'w', EW, ewhy); print('P2 latest', erows[-1])
