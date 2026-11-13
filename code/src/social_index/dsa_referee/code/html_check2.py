"""Referee second pass: every number in the six page tables regenerated from dsa.json / automation_period.json and diffed."""
import re, html, json, math
D = '/Users/heuremen/bones-forge/social_index/dsa'
H = open(D + '/section_dsa.html').read()
rows = json.load(open(D + '/data/dsa.json')); autop = json.load(open(D + '/data/automation_period.json'))
PL = {'Jul to Dec 2025': '2025H2', 'Jan to Jun 2026': '2026H1'}
ML = {'All measures': 'total', 'Solely automated': 'solely', 'Not automated': 'not', 'Own initiative': 'own', 'Own initiative, illegal content': 'own_illegal',
      'Own initiative, terms and conditions': 'own_tc', 'Own initiative, solely automated': 'own_auto', 'Actions on notices': 'notice', 'Actions on trusted flagger notices': 'notice_tf',
      'Solely automated share': 'share'}
by = {(r['platform'], r['period'], r['measure']): r for r in rows if r.get('measure') != 'label_split'}
labs = {(r['platform'], r['period'], r['split']): r for r in rows if r.get('measure') == 'label_split'}
def cells(tr): return [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', c))).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
def fr(x):
    if x is None: return 'none'
    if x == 'unbounded': return 'no upper edge'
    x = float(x)
    if x == 0: return '0'
    if abs(x - 0.9) < 0.005 or abs(x - 1.1) < 0.005: return '%.5g' % x
    if x >= 100: return '{:,.0f}'.format(x)
    if x >= 10: return '%.1f' % x
    if 0.5 <= x < 2: return '%.3f' % x
    if x >= 0.1: return '%.2f' % x
    d = int(-math.floor(math.log10(x))) + 1
    return ('%.' + str(d) + 'f') % x
W = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', 'NOTHING_RETURNED': 'nothing returned'}
probs = []; n = 0; seen = set()
def ratio(cell, r, tag):
    global n
    n += 1
    if r.get('stated') is None:
        if not cell.startswith('no stated figure'): probs.append((tag, 'no stated figure expected', cell))
        return
    head = 'zero stated' if r['stated'] == 0 else '%s [%s, %s]' % (fr(r['ratio']), fr(r['ratio_lo']), fr(r['ratio_hi']))
    exp = '%s report %s, database %s' % (head, '{:,}'.format(r['stated']), '{:,}'.format(r['delivered']['D_app']))
    if cell != exp: probs.append((tag, exp, cell))
    # the printed band must sit on the right side of each edge for the printed outcome
    for v in (r.get('ratio_lo'), r.get('ratio_hi')):
        if isinstance(v, (int, float)) and fr(v) in ('0.9', '1.1', '0.90', '1.10', '0.900', '1.100', '0.90000', '1.10000') and v not in (0.9, 1.1): probs.append((tag, 'edge prints on the line', v, fr(v)))
def oc(cell, r, tag):
    w = W[r['outcome']]
    if not cell.startswith(w): probs.append((tag, 'outcome ' + w, cell))
    if r.get('outcome_rule') and 'plan rule reads ' + W[r['outcome_rule']] not in cell: probs.append((tag, 'plan-rule label missing', cell))
    if not r.get('outcome_rule') and r.get('defined_after_data') and 'defined after the data' not in cell: probs.append((tag, 'row label missing', cell))
T = re.findall(r'<table.*?</table>', H, re.S)
for tr in re.findall(r'<tr>(.*?)</tr>', T[0], re.S)[1:]:
    c = cells(tr); p, per = c[0], PL[c[1]]
    if len(c) == 3: continue
    for i, m in enumerate(('total', 'solely', 'not')):
        r = by[(p, per, m)]; ratio(c[2 + 2 * i], r, (p, per, m)); oc(c[3 + 2 * i], r, (p, per, m)); seen.add((p, per, m))
for tr in re.findall(r'<tr>(.*?)</tr>', T[1], re.S)[1:]:
    c = cells(tr); k = (c[0], PL[c[1]], ML[c[2]]); r = by[k]; ratio(c[3], r, k); oc(c[4], r, k); seen.add(k)
for tr in re.findall(r'<tr>(.*?)</tr>', T[2], re.S)[1:]:
    c = cells(tr); k = (c[0], PL[c[1]], 'share'); r = by[k]; seen.add(k); n += 1
    if r.get('stated_share') is None: continue
    exp = ['%.1f%%' % (r['stated_share'] * 100), '%.1f%% [%.1f%%, %.1f%%]' % (r['delivered_share'] * 100, r['delivered_share_lo'] * 100, r['delivered_share_hi'] * 100),
           '%+.1f [%+.1f, %+.1f]' % (r['diff_points'], r['diff_lo_points'], r['diff_hi_points'])]
    if c[2:5] != exp: probs.append((k, exp, c[2:5]))
    oc(c[5], r, k)
ap = {a['platform']: a for a in autop if a['period'] == '2026H1'}
for tr in re.findall(r'<tr>(.*?)</tr>', T[3], re.S)[1:]:
    c = cells(tr); a = ap[c[0]]; n += 1
    exp = ['{:,}'.format(a['statements'])] + ['%.1f%%' % (a[x] * 100) for x in ('fully', 'partially', 'not', 'detection_yes', 'fully_no_detection')]
    if c[1:] != exp: probs.append((c[0], exp, c[1:]))
for tr in re.findall(r'<tr>(.*?)</tr>', T[4], re.S)[1:]:
    c = cells(tr); k = (c[0], PL[c[1]], ML[c[2]]); r = by[k]; seen.add(k)
    if k[2] == 'share':
        n += 1
        exp = 'report %.1f%%, database %.1f%% [%.1f%%, %.1f%%], difference %+.1f points [%+.1f, %+.1f]' % (r['stated_share'] * 100, r['delivered_share'] * 100, r['delivered_share_lo'] * 100, r['delivered_share_hi'] * 100, r['diff_points'], r['diff_lo_points'], r['diff_hi_points'])
        if c[3] != exp: probs.append((k, exp, c[3]))
    else: ratio(c[3], r, k)
    oc(c[4], r, k)
for tr in re.findall(r'<tr>(.*?)</tr>', T[5], re.S)[1:]:
    c = cells(tr); k = (c[0], PL[c[1]], c[2]); r = labs[k]; n += 1
    for cell, mm in zip(c[3:5], r['members']):
        head = fr(mm['ratio']) if mm.get('ratio') is not None else 'zero stated'
        exp = '%s: %s report %s, database %s, read %s' % (mm['measure_label'], head, '{:,}'.format(mm['stated']), '{:,}'.format(mm['D_app']), W[mm['reading_before']])
        if cell != exp: probs.append((k, exp, cell))
missing = [k for k, r in by.items() if r['outcome'] != 'NOTHING_RETURNED' and k not in seen and not (k[2] == 'share' and r.get('stated_share') is None)]
print('cells checked', n, 'problems', len(probs))
for x in probs[:40]: print('  ', x)
print('comparison rows not shown anywhere on the page:', len(missing), missing[:20])
print('label-split rows in data', len(labs), 'on page', len(re.findall(r'<tr>', T[5])) - 1)
