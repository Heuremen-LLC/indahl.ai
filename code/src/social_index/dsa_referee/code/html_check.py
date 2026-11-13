import re, html, json, math
H = open('/Users/heuremen/bones-forge/social_index/dsa/section_dsa.html').read()
rows = json.load(open('/Users/heuremen/bones-forge/social_index/dsa/data/dsa.json'))
autop = json.load(open('/Users/heuremen/bones-forge/social_index/dsa/data/automation_period.json'))
PL = {'Jul to Dec 2025': '2025H2', 'Jan to Jun 2026': '2026H1'}
ML = {'All measures': 'total', 'Solely automated': 'solely', 'Not automated': 'not', 'Own initiative': 'own', 'Own initiative, illegal content': 'own_illegal',
      'Own initiative, terms and conditions': 'own_tc', 'Own initiative, solely automated': 'own_auto', 'Actions on notices': 'notice', 'Actions on trusted flagger notices': 'notice_tf'}
by = {(r['platform'], r['period'], r['measure']): r for r in rows}
def cells(tr):
    return [html.unescape(re.sub(r'<[^>]+>', ' ', c)).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
def nums(s): return [x.replace(',', '') for x in re.findall(r'[-+]?\d[\d,]*\.?\d*', s)]
def fr(x):
    if x is None: return 'none'
    if x == 'unbounded': return 'no upper edge'
    x = float(x)
    if x == 0: return '0'
    if x >= 100: return '{:,.0f}'.format(x)
    if x >= 10: return '%.1f' % x
    if 0.5 <= x < 2: return '%.3f' % x
    if x >= 0.1: return '%.2f' % x
    d = int(-math.floor(math.log10(x))) + 1
    return ('%.' + str(d) + 'f') % x
problems = []; checked = 0; boundary = []
tables = re.findall(r'<table.*?</table>', H, re.S)
def check_ratio(cell, r, tag):
    global checked
    if r.get('stated') is None:
        if 'no stated figure' not in cell: problems.append((tag, 'expected no stated figure', cell))
        return
    d = r['delivered']
    if r['stated'] == 0: exp_head = 'zero stated'
    else: exp_head = '%s [%s, %s]' % (fr(r['ratio']), fr(r['ratio_lo']), fr(r['ratio_hi']))
    exp = '%s report %s, database %s' % (exp_head, '{:,}'.format(r['stated']), '{:,}'.format(d['D_app']))
    checked += 1
    if re.sub(r'\s+', ' ', cell) != exp: problems.append((tag, exp, cell))
    # boundary: printed edge looks inside agreement band but outcome says otherwise, or vice versa
    for v, nm in ((r.get('ratio_lo'), 'lo'), (r.get('ratio_hi'), 'hi')):
        if isinstance(v, (int, float)) and fr(v) in ('0.900', '1.100', '0.90', '1.10') and abs(v - 0.9) > 0 and abs(v - 1.1) > 0:
            boundary.append((tag, nm, v, fr(v), r['outcome']))
def check_oc(cell, r, tag):
    w = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', 'NOTHING_RETURNED': 'nothing returned'}[r['outcome']]
    if not cell.startswith(w): problems.append((tag, 'outcome ' + w, cell))
    if r.get('outcome_rule') and 'plan rule reads' not in cell: problems.append((tag, 'missing post-hoc label', cell))
# table 1
for tr in re.findall(r'<tr>(.*?)</tr>', tables[0], re.S)[1:]:
    c = cells(tr)
    p, per = c[0], PL[c[1]]
    if len(c) == 3: continue
    for i, m in enumerate(('total', 'solely', 'not')):
        r = by[(p, per, m)]; check_ratio(c[2 + 2 * i], r, (p, per, m)); check_oc(c[3 + 2 * i], r, (p, per, m))
# table 2
for tr in re.findall(r'<tr>(.*?)</tr>', tables[1], re.S)[1:]:
    c = cells(tr); p, per, m = c[0], PL[c[1]], ML[c[2]]
    r = by[(p, per, m)]; check_ratio(c[3], r, (p, per, m)); check_oc(c[4], r, (p, per, m))
# table 3 share
for tr in re.findall(r'<tr>(.*?)</tr>', tables[2], re.S)[1:]:
    c = cells(tr); p, per = c[0], PL[c[1]]; r = by[(p, per, 'share')]
    if r.get('stated_share') is None: continue
    exp = ['%.1f%%' % (r['stated_share'] * 100), '%.1f%% [%.1f%%, %.1f%%]' % (r['delivered_share'] * 100, r['delivered_share_lo'] * 100, r['delivered_share_hi'] * 100),
           '%+.1f [%+.1f, %+.1f]' % (r['diff_points'], r['diff_lo_points'], r['diff_hi_points'])]
    checked += 1
    if c[2:5] != exp: problems.append(((p, per, 'share'), exp, c[2:5]))
    check_oc(c[5], r, (p, per, 'share'))
# table 4 automation A
ap = {a['platform']: a for a in autop if a['period'] == '2026H1'}
for tr in re.findall(r'<tr>(.*?)</tr>', tables[3], re.S)[1:]:
    c = cells(tr); a = ap[c[0]]
    exp = ['{:,}'.format(a['statements'])] + ['%.1f%%' % (a[k] * 100) for k in ('fully', 'partially', 'not', 'detection_yes', 'fully_no_detection')]
    checked += 1
    if c[1:] != exp: problems.append((c[0], exp, c[1:]))
print('cells checked', checked, 'problems', len(problems))
for x in problems[:30]: print('  ', x)
print('boundary-rounding cases', len(boundary))
for x in boundary: print('  ', x)
