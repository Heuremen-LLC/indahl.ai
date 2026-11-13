#!/usr/bin/env python3
"""build_page.py: writes fidelity.html (draft, git-ignored) from summary_fidelity.json and data/fidelity.json. Reads no network. Every figure comes from those files.
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import json, os, html
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
S = json.load(open('summary_fidelity.json')); ROWS = json.load(open('data/fidelity.json')); e = html.escape
EVN = {'DIVORCE': 'Divorces and annulments', 'MARRIAGE': 'Marriages'}
RD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'inside', 'MIXED': 'mixed', 'CANNOT_TELL': 'cannot tell'}
def n(x): return '{:,}'.format(int(x))
def rd(c): return RD[c['read']] + (' (%s)' % c['read_reason'] if c['read'] == 'CANNOT_TELL' and c.get('read_reason') else '')   # 12 Nov 2026: Faults and Guards 2.0, the reason sits beside the word
def codes(c): return ', '.join('%d %s' % (v, k) for k, v in sorted(c['req13']['cannot_tell_by_reason'].items())) or 'none'
def trow(label, c, extra=''):
    return '<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td>%s</tr>' % (e(label), c['ABOVE'], c['BELOW'], c['CONSISTENT'], c['CANNOT_TELL'], rd(c), extra)
TH = '<th>%s</th><th>NCHS above</th><th>NCHS below</th><th>Inside</th><th>Cannot tell</th><th>Reading</th>'
def why(c): return ', '.join('%d %s' % (v, k) for k, v in sorted(c['by_reason'].items(), key=lambda kv: -kv[1])) or 'none'
def table(head, body, extra_head=''): return '<div class="tw"><table class="bench"><tr>%s%s</tr>%s</table></div>' % (TH % head, extra_head, body)
def sc(ev): return [r for r in ROWS if r['event'] == ev and r['outcome'] in ('ABOVE', 'BELOW', 'CONSISTENT')]
def cnt(R, key): return {k: sum(1 for r in R if r[key] == k) for k in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
def both(R): return {k: sum(1 for r in R if r['outcome'] == k and r['outcome_men'] == k) for k in ('ABOVE', 'BELOW', 'CONSISTENT')}
NCHS = json.load(open('data/nchs_counts.json')); SW = json.load(open('data/gate2_swap_check.json'))
def baseline(ev, y=2022):
    k, tab = ev.lower(), ('B12503' if ev == 'DIVORCE' else 'B12501'); R = [r for r in ROWS if r['event'] == ev and r['year'] == y and r['nchs'] is not None and r['acs_women'] is not None and r['acs_men'] is not None]
    t = sum(r['nchs'] for r in R); return t / sum(r['acs_women'] for r in R), t / sum(r['acs_men'] for r in R)
def cell_of(R, key):
    c = cnt(R, key); sc_ = c['ABOVE'] + c['BELOW'] + c['CONSISTENT']
    if sc_ < 5: return 'CANNOT_TELL'
    top = max(('ABOVE', 'BELOW', 'CONSISTENT'), key=lambda k: c[k]); return top if c[top] >= 0.8 * sc_ else 'MIXED'
def both_below(ev):
    st = sorted({r['state'] for r in ROWS if r['event'] == ev}); return [s for s in st if cell_of([r for r in ROWS if r['event'] == ev and r['state'] == s], 'outcome') == 'BELOW' and cell_of([r for r in ROWS if r['event'] == ev and r['state'] == s], 'outcome_men') == 'BELOW']
def srow(ev, s): return [r for r in sc(ev) if r['state'] == s]
def jn(L): return ', '.join(L[:-1]) + ' and ' + L[-1] if len(L) > 1 else L[0]
def line(ev):
    o = C[ev]['overall']; x = C[ev]['excluding_destination']; R = sc(ev); m = cnt(R, 'outcome_men'); b = both(R); w = cnt(R, 'outcome')
    assert m['CANNOT_TELL'] == 0 and w['ABOVE'] == o['ABOVE'] and w['BELOW'] == o['BELOW'] and w['CONSISTENT'] == o['CONSISTENT']
    return ('%s: of %d rows, %d are scored. Under the women\'s estimate, the scored reading, the NCHS count sits above the ACS interval in %d, below it in %d and inside it in %d. Under the men\'s estimate it sits above in %d, below in %d and inside in %d. '
            'Both sexes read below in %d rows, inside in %d and above in %d. Cannot tell holds %d, %s (%s). Without the destination cells the women\'s reading is %d above, %d below and %d inside.') % (
        EVN[ev], o['rows'], len(R), w['ABOVE'], w['BELOW'], w['CONSISTENT'], m['ABOVE'], m['BELOW'], m['CONSISTENT'], b['BELOW'], b['CONSISTENT'], b['ABOVE'], o['CANNOT_TELL'], codes(o), why(o), x['ABOVE'], x['BELOW'], x['CONSISTENT'])
C = S['cells']; D, M = C['DIVORCE'], C['MARRIAGE']; g = S['gates']
BB = both_below('DIVORCE'); TX = srow('DIVORCE', 'Texas'); txb = sum(1 for r in TX if r['outcome'] == 'BELOW' and r['outcome_men'] == 'BELOW')
assert txb == len(TX) and 'Texas' in BB
bw, bm = baseline('DIVORCE'); mw, mm = baseline('MARRIAGE')
dw, dm = cnt(sc('DIVORCE'), 'outcome'), cnt(sc('DIVORCE'), 'outcome_men')
HB = '%d of %d' % (txb, len(TX))
HLINE = ('In Texas the CDC count of divorces and annulments sits below the ACS interval in %d of %d years, under the women\'s estimate and under the men\'s. %s read below under both sexes as well. '
         'These are the jurisdictions where the divorce reading holds whichever sex is used. It says only that the two counts differ by more than the survey\'s stated margin. It cannot show that any records are missing or that either source is mistaken. '
         'Nationally in 2022 the CDC divorce total was %.2f of the ACS women\'s total and %.2f of the men\'s, so a state reads against that ratio and not against 1.0. For the Texas rows, %s') % (txb, len(TX), jn([s for s in BB if s != 'Texas']), bw, bm, S['headline_req13']['line'])
HL = 'The CDC and the Census Bureau count different things, so a gap between them is a reading of that difference and not a claim that either number is mistaken. CDC NCHS counts the events that states report, where they happened. The ACS estimates the persons who say they married or divorced in the last year, where they live now.'
hl = '<section id="hl-slot" class="hl-slot hl"><div class="hl-big">%s</div><p class="hl-line">%s</p></section>' % (e(HB), e(HLINE))
body = []
A = body.append
A('<p class="meta crumb">Division: <a href="/census">CENSUS</a></p>')
A('<h2>Does the CDC count of divorces and marriages in a state sit inside the Census estimate?</h2>')
A('<p>This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>')
A('<p>%s</p>' % e(HL))
A('<p>%s</p>' % e(line('DIVORCE')))
A('<p>%s</p>' % e(line('MARRIAGE')))
A('<p>%s</p>' % e('The women\'s reading is the scored one and was fixed in the plan before the comparison. The men\'s counts are shown beside it. For divorces the count below falls from %d under the women\'s estimate to %d under the men\'s, so the divorce reading depends on which sex is used and the both-sexes line is the part that does not. Marriages move far less, with %d below under the women\'s estimate and %d under the men\'s.' % (dw['BELOW'], dm['BELOW'], cnt(sc('MARRIAGE'), 'outcome')['BELOW'], cnt(sc('MARRIAGE'), 'outcome_men')['BELOW'])))
ms = [(s_, sum(1 for r in srow('DIVORCE', s_) if r['outcome'] == 'BELOW'), sum(1 for r in srow('DIVORCE', s_) if r['outcome_men'] == 'BELOW'), len(srow('DIVORCE', s_))) for s_ in ('Massachusetts', 'Iowa', 'Kansas')]
A('<p>%s</p>' % e('Massachusetts, Iowa and Kansas hold under one sex and not the other. Their divorce counts sit below the women\'s interval in %s of their scored years and below the men\'s in %s, so they read below under the women\'s estimate and not under the men\'s.' % (jn(['%d of %d' % (a, d) for _, a, _, d in ms]), jn(['%d' % b for _, _, b, _ in ms]))))
A('<p>%s</p>' % e('In 2022 the NCHS total for the reporting states was %.2f of the ACS women\'s total and %.2f of the men\'s for divorces, and %.2f of the women\'s and %.2f of the men\'s for marriages. The two sources do not count the same thing, so a state sits against that ratio and not against 1.0. These readings cannot show that any state\'s records are missing or that either source is mistaken. They show that the two counts differ by more than the survey\'s stated margin.' % (bw, bm, mw, mm)))
A('<h2>What each source counts</h2>')
nr = {s: [y for y in range(2010, 2024) if y != 2020 and NCHS['divorce'][s][y - 2000] is None] for s in NCHS['divorce'] if s != 'United States'}
nr = {s: v for s, v in nr.items() if v}
FR = [y for y in range(2010, 2024) if y != 2020]
def yrs(v): return 'in all frame years' if len(v) == 13 else ('%d to %d' % (v[0], v[-1]) if v == [y for y in FR if v[0] <= y <= v[-1]] else ', '.join(map(str, v)))
blanks = jn(['%s %s' % (s_, yrs(v)) for s_, v in sorted(nr.items(), key=lambda kv: (len(kv[1]) < 13, kv[0]))])
A('<p>NCHS publishes one count of marriages and one of divorces and annulments for each state that reports, by state of occurrence. NCHS says of its rate tables: &ldquo;Rates are based on provisional counts of divorces by state of occurrence.&rdquo; The divorce table carries the footnotes &ldquo;Includes annulments.&rdquo; and &ldquo;Includes divorce petitions filed or legal separations for some counties or States.&rdquo; The marriage table says &ldquo;Rates are based on provisional counts of marriages by state of occurrence.&rdquo; and &ldquo;Marriage data includes nonlicensed marriages registered.&rdquo; California, Hawaii, Indiana, Minnesota and New Mexico do not report divorce counts in some or all years of the frame, and Georgia and Louisiana have blank runs. The blanks in the frame years are %s. Georgia has no marriage count for 2013 and 2014. The ACS 1-year tables B12501 and B12503 give persons 15 years and over who married or divorced in the last 12 months, with a 90 percent margin. The last 12 months roll before each interview and are not the calendar year. NCHS counts are by place of the event, ACS by place of residence.</p>' % blanks)
A('<h2>How we turned persons into events</h2>')
A('<p>Each marriage or divorce between a woman and a man has one woman in it, so we read the women\'s ACS estimate as the number of events and put its published 90 percent margin on it as the interval. We chose the women\'s estimate before the full comparison but not before seeing any data. A scout of 16 state-year-events had already shown the women\'s and the men\'s estimates for Texas, Florida, New York and Pennsylvania, and the plan lists them. The ACS pulls for all years came in the minute before the plan was committed and were not read before it. The code that applies the plan\'s rule was committed after the first comparison. The rule it applies is the one in the plan text, and an independent recount from the plan text equals every reading. The reader gate\'s rate tolerance first ran at 0.15 and was reset to the plan\'s 0.1 before any reading was written. The men\'s estimate is shown beside the women\'s in every headline line and is not scored. Rows where the women\'s and the men\'s intervals give different readings are counted apart as sex splits: %d divorce rows and %d marriage rows. A marriage or divorce of two women is counted twice by the women\'s estimate, which overcounts it, and one of two men is not counted at all, which undercounts it. The net sign is not known. The 95 percent scale of the margin is computed for display and does not set any outcome.</p>' % (D['overall']['sex_split'], M['overall']['sex_split']))
A('<h2>Occurrence against residence</h2>')
mab = sorted([(v['ABOVE'], s) for s, v in M['by_state'].items() if s not in ('Nevada', 'Hawaii')], reverse=True)[:3]
assert sorted(s for _, s in mab) == ['Arkansas', 'Florida', 'New York'], mab
A('<p>This is the main limit. A couple can marry or divorce in a state where they do not live, and NCHS counts the event where it happened while ACS counts the person where they live. We name Nevada for both events and Hawaii for marriage as destination states and print them apart. For marriages these destination rows are %d above and %d inside or below, and for divorces %d above and %d inside. Every other state has some of the same crossing, so the other rows are not free of it. %s marriages also read above in most scored years (%s), so the destination states are not the only rows above.</p>' % (
    M['destination']['ABOVE'], M['destination']['BELOW'] + M['destination']['CONSISTENT'], D['destination']['ABOVE'], D['destination']['BELOW'] + D['destination']['CONSISTENT'],
    jn([s for _, s in mab]), jn(['%d of %d' % (v, len(srow('MARRIAGE', s_))) for v, s_ in mab])))
def texas(ev):
    return ', '.join('%d: NCHS %s, ACS %s, %s' % (r['year'], n(r['nchs']), n(r['acs_women']), RD[r['outcome']]) for r in ROWS if r['event'] == ev and r['state'] == 'Texas' and r['outcome'] in ('ABOVE', 'BELOW', 'CONSISTENT') and r['year'] >= 2021)
def gaps(ev, up):
    R = [r for r in ROWS if r['event'] == ev and r['outcome'] in ('ABOVE', 'BELOW')]
    R = [r for r in R if (r['nchs'] > r['acs_women']) == up]
    R.sort(key=lambda r: -abs(r['nchs'] - r['acs_women']))
    return ''.join('<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(r['state']), r['year'], n(r['nchs']), n(r['acs_women']), n(r['acs_women_moe']), '{:,}'.format(int(round(r['acs_women'] - r['nchs'])))) for r in R[:6])
def table2(ev):
    R = sc(ev); w = cnt(R, 'outcome'); m = cnt(R, 'outcome_men'); b = both(R)
    return '<div class="tw"><table class="bench"><tr><th>Scored rows</th><th>Women\'s estimate</th><th>Men\'s estimate</th><th>Both sexes agree</th></tr>%s</table></div>' % ''.join(
        '<tr><td>NCHS %s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (lab, w[k], m[k], b[k]) for k, lab in (('ABOVE', 'above'), ('BELOW', 'below'), ('CONSISTENT', 'inside')))
for ev in ('DIVORCE', 'MARRIAGE'):
    c = C[ev]
    A('<h2>%s</h2>' % EVN[ev])
    A(table('Rows', trow('All jurisdictions', c['overall']) + trow('Without destination states', c['excluding_destination']) + trow('Destination states only', c['destination'])))
    A(table2(ev))
    A('<p class="bench-note">The first table is the women\'s estimate, the scored reading. The second sets the men\'s estimate beside it for the same scored rows. Both sexes agree counts the rows where the two give the same reading.</p>')
    A('<p>Texas, ACS women against the NCHS count: %s.</p>' % e(texas(ev)))
    A('<h3>By year</h3>')
    A(table('Year', ''.join(trow(y, v) for y, v in c['by_year'].items())))
    A('<p>2024 rows are all cannot tell with the reason NO_INTERVAL_FORMABLE, as NCHS has not published 2024 state counts, only rates. The ACS 2024 estimates are in the data file. They stay cannot tell until NCHS publishes 2024 state counts.</p>')
    A('<h3>By jurisdiction</h3>')
    A('<p>A jurisdiction reads above, below or inside when at least 5 of its rows are scored and one outcome holds at least 80 percent of them. Otherwise it reads mixed. With fewer than 5 scored rows it reads cannot tell with the reason TOO_WIDE_TO_RESOLVE, and with no scored row with the reason NO_INTERVAL_FORMABLE. Each row compares one published count with one published interval, so a row read is exact and carries no sampling of its own. A row that cannot be compared reads cannot tell with the reason NO_INTERVAL_FORMABLE, and the plain cause is in the Cannot tell counts. The last column is the median of the NCHS count divided by the ACS women\'s estimate.</p>')
    A(table('Jurisdiction', ''.join(trow(s, v, '<td>%s</td>' % ('' if v['median_ratio'] is None else '%.2f' % v['median_ratio'])) for s, v in c['by_state'].items()), '<th>Median ratio</th>'))
    GH = '<tr><th>Jurisdiction</th><th>Year</th><th>NCHS count</th><th>ACS women, estimate</th><th>ACS 90 percent margin</th><th>ACS estimate minus NCHS count</th></tr>'
    A('<h3>Largest gaps, NCHS count below the ACS estimate</h3><div class="tw"><table class="bench">%s%s</table></div>' % (GH, gaps(ev, False)))
    A('<h3>Largest gaps, NCHS count above the ACS estimate</h3><div class="tw"><table class="bench">%s%s</table></div>' % (GH, gaps(ev, True)))
    A('<p class="bench-note">The gap is the ACS women\'s point estimate minus the NCHS count, in persons read as events. It is a point estimate and carries the margin shown beside it.</p>')
la = NCHS['divorce']['Louisiana']; ga = NCHS['divorce']['Georgia']
A('<h2>Notes on the NCHS series</h2>')
A('<p>The Louisiana divorce count NCHS prints falls from %s in 2021 to %s in 2022 and %s in 2023, and the printed rate falls with it. The Georgia count falls from %s in 2017 to %s in 2018. NCHS prints these counts, so the rows stay scored as printed and none is re-read.</p>' % (n(la[21]), n(la[22]), n(la[23]), n(ga[17]), n(ga[18])))
fl = SW['flips_if_swapped']
fls = ['%s %d from %s to %s' % (f['state'], f['year'], RD[f['as_printed']], RD[f['swapped']]) for f in fl]
A('<p>In %d divorce state-years of 2016 and 2017 the NCHS count table and the NCHS rate table do not agree to within 0.1 per 1,000 (%s). The counts for %s fit both years\' printed rates when the 2016 and 2017 counts are swapped. Texas 2016 also differs, and NCHS footnotes the Texas 2016 divorce rate as revised. Illinois 2016 differs as well and is not footnoted for divorces. Every outcome here is read from the count table as printed. Under the swap %d rows would change reading: %s. No row has been re-read.</p>' % (
    len(SW['divorce_2016_17_misses']), ', '.join('%s %d' % (s, y) for s, y in SW['divorce_2016_17_misses']), jn([x['state'] for x in SW['swap_test'] if x['swapped_counts_fit_both_rates']]), len(fl), jn(fls)))
A('<h2>Checks that gate every reading</h2>')
rc = g['2_reader']['rate_check']
A('<p>Four state-years were read in full from the NCHS tables and the ACS summary files and equal the parsed rows: Texas 2022 divorces, Florida 2023 divorces, New York 2022 marriages and Pennsylvania 2023 marriages. The NCHS state counts add up to the printed United States figure in every year of both tables. NCHS counts over ACS population round to the printed NCHS rate within 0.1 in %s of %s state-years. The %d that miss are listed in data/gate2_rate_misses.csv in the public desk folder. ACS API values equal the Census table-based summary files in %s of %s values for 2022 and 2023. The rule passed synthetic rows for each outcome. A failed check would have turned every reading into cannot tell. Gates passed in this run: %s.</p>' % (n(rc['within_tenth']), n(rc['compared']), rc['compared'] - rc['within_tenth'], n(g['3_join']['equal']), n(g['3_join']['compared']), 'yes' if S['gates_passed'] else 'no'))
A('<h2>What this does not say</h2>')
A('<p>A row above or below names no cause. NCHS labels its rate tables as based on provisional counts, and we keep a dated copy of the NCHS tables from %s so a provisional against revised reading becomes possible later. ACS estimates are a sample, and consecutive years of a state and the two sexes share that sample, so rows are not independent and we print no share or test over rows. The margin covers the ACS sampling only. It does not cover the NCHS side or the conversion from persons to events, so an inside reading means not distinguishable at this margin. NCHS divorce counts include annulments and in some states petitions. 2020 is left out as the Census did not publish standard 1-year estimates for it.</p>' % e(S['run'][:10]))
A('<h2>Sources</h2>')
A('<p>CDC National Center for Health Statistics, National Vital Statistics System, marriage and divorce state tables and counts, 2000 to 2023 and rates to 2024, <a href="https://www.cdc.gov/nchs/nvss/marriage-divorce.htm">cdc.gov/nchs/nvss/marriage-divorce.htm</a>. U.S. Census Bureau, American Community Survey 1-year estimates, tables B12501, B12503 and B01003, through the Census Data API, <a href="https://www.census.gov/data/developers/data-sets/acs-1year.html">census.gov</a>. The plan was committed on %s before any state-year was compared.</p>' % e(S['plan_seal']['plan_commit_time']))
A('<p>This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.</p>')
A('<p class="meta">Plan and code for this page are public: <a href="https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/fidelity">fidelity</a>. The plan was fixed before the comparison it describes. This desk was run once on the NCHS tables of %s and does not refresh the readings. Dated copies of the NCHS workbooks are kept.</p>' % e(S['run'][:10]))
page = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FIDELITY | State Counts Against the ACS | Heuremen LLC</title>
<meta name="description" content="FIDELITY: state divorce and marriage counts reported to the CDC, set beside the Census American Community Survey.">
<meta name="tdm-reservation" content="1">
<meta name="author" content="Heuremen LLC">
<link rel="stylesheet" href="/style.css">
<style>.tw{overflow-x:auto}table.bench{border-collapse:collapse;font-size:.86rem}table.bench th,table.bench td{padding:.3rem .55rem;border-bottom:1px solid #ccc;text-align:left;white-space:nowrap}</style>
</head>
<body>
<header class="top"><div class="wrap bar"><a class="brand" href="/"><span>Heuremen LLC</span></a></div></header>
<section class="hero slim"><div class="wrap"><h1><b class="ac">FIDELITY</b> &middot; State Counts Against the ACS</h1></div></section>
<main class="wrap">%s
%s</main>
</body>
</html>
''' % (hl, '\n'.join(body))
open('fidelity.html', 'w').write(page); print('fidelity.html', len(page))
