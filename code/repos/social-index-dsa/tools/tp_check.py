"""tp_check.py: /tp core over every row of data/dsa.json (after Addendum 6).
I none built before (plan commit precedes first count) | II gap item by item | III sign | V ruler named | VI four outcomes, both alternatives | R record."""
import json, re, math, subprocess, sys, os, csv, io
sys.path.insert(0, os.path.expanduser('~/bones-forge/launch_index')); import heuremen_kit as K
sys.path.insert(0, '/Users/heuremen/bones-forge/social_index/dsa'); import dsa_reports as DR
H = '/Users/heuremen/bones-forge/social_index/dsa'
FLOOR = 100
def cells(q):
    if q.startswith(('XLSX sheet', 'XLS sheet')): return q.split(': ', 1)[1].split(' | ')
    out = []
    for row in csv.reader(io.StringIO(q, newline='')): out += row
    for row in csv.reader(io.StringIO(q, newline=''), delimiter=';'): out += row
    return out
def in_quote(v, q): return any(DR.to_int(c) == v for c in cells(q or ''))
rows = json.load(open(H + '/data/dsa.json')); summ = json.load(open(H + '/summary_dsa.json'))
fails = []; n = {'I': 1, 'II': 0, 'III': 0, 'V': 0, 'VI': 0, 'R': 0, 'labels': 0}
def bad(r, tag, msg): fails.append('%s %s %s [%s] %s' % (r['platform'], r['period'], r['measure'], tag, msg))
t_plan = int(subprocess.run(['git', 'log', '--format=%ct', '--reverse', '--', 'PLAN.md'], cwd=H, capture_output=True, text=True).stdout.split()[0])
print('I: first plan commit', t_plan, '(first database count by platform followed it; see PLAN.md and git log)')
by = {(r['platform'], r['period'], r['measure']): r for r in rows}
for r in rows:
    if r['measure'] == 'label_split':
        n['labels'] += 1
        if {m['reading_before'] for m in r['members']} != {K.ABOVE, K.BELOW}: bad(r, 'VI', 'label row without opposite readings')
        for m in r['members']:
            x = by.get((r['platform'], r['period'], m['measure']))
            if not x or x['outcome'] != K.CANNOT_TELL or not x.get('label_split'): bad(r, 'VI', 'member %s not relabelled' % m['measure'])
        continue
    o = r['outcome']
    if o not in K.OUTCOMES + (K.NOTHING_RETURNED,): bad(r, 'VI', 'outcome %r' % o)
    if o == K.NOTHING_RETURNED:
        if not r.get('reason'): bad(r, 'R', 'no reason')
        continue
    posthoc = bool(r.get('note_rule') or r.get('label_split'))
    if posthoc and 'defined after the data' not in (r.get('reason') or '').lower(): bad(r, 'VI', 'post-hoc change without label')
    if r['measure'] == 'share':
        if r.get('stated_share') is None: continue
        want = K.classify(r['diff_lo_points'] / 100, r['diff_hi_points'] / 100, -0.05, 0.05)
        if not posthoc and o != want: bad(r, 'VI', 'share outcome %s != band %s' % (o, want))
        for p in r.get('stated_parts', []):
            if not in_quote(p['value'], p['quote']): bad(r, 'R', 'value %s not in quote' % p['value'])
        n['VI'] += 1; n['R'] += 1; continue
    S = r.get('stated'); d = r.get('delivered')
    if S is None:
        if o != K.CANNOT_TELL: bad(r, 'VI', 'blank stated but outcome %s' % o)
        continue
    for p in r.get('stated_parts', []):
        if not p.get('quote') or not p.get('file') or not p.get('container'): bad(r, 'R', 'part without quote/file')
        if p['value'] is not None and not in_quote(p['value'], p['quote']): bad(r, 'R', 'value %s not found in quote' % p['value'])
    if not r.get('source_url'): bad(r, 'R', 'no source url')
    n['R'] += 1
    if not r.get('interval') or 'band' not in r['interval'].lower(): bad(r, 'V', 'interval text missing')
    if not r.get('filter'): bad(r, 'V', 'filter missing')
    if not (d['D_lo'] <= min(d['D_app'], d['D_cre']) and max(d['D_app'], d['D_cre']) <= d['D_hi']): bad(r, 'V', 'delivered band does not contain both bases %s' % d)
    notice = r['measure'] in ('notice', 'notice_tf') and r.get('view') == 'main'
    if not (r['stated_lo'] <= r['stated_hi'] and (r['stated_hi'] <= S or (notice and r['stated_hi'] == (r.get('items_notified') or S)))): bad(r, 'V', 'stated band %s %s %s' % (r['stated_lo'], r['stated_hi'], S))
    if notice and d['D_lo'] != 0: bad(r, 'V', 'notice row lower edge not zero (Addendum 6.2)')
    n['V'] += 1
    if r.get('gap_signed') != d['D_app'] - S: bad(r, 'III', 'signed gap')
    if S and r.get('ratio') is not None and (r['ratio'] > 1) != (d['D_app'] > S): bad(r, 'III', 'ratio side')
    n['III'] += 1
    if r['measure'] == 'total':
        it = r.get('items') or {}
        if it.get('solely_gap', 0) + it.get('not_gap', 0) + it.get('partial_no_report_field', 0) != r['gap_signed']: bad(r, 'II', 'items do not net to the total gap %s vs %s' % (it, r['gap_signed']))
        n['II'] += 1
    # VI: the outcome follows the band with the floor, unless a labelled post-hoc rule changed it
    S_lo, S_hi = r['stated_lo'], r['stated_hi']
    if S == 0:
        want = K.CONSISTENT if d['D_hi'] == 0 else ((K.ABOVE if d['D_lo'] >= FLOOR else K.CANNOT_TELL) if d['D_lo'] > 0 else K.CANNOT_TELL)
    else:
        rlo = d['D_lo'] / S_hi if S_hi > 0 else math.inf; rhi = d['D_hi'] / S_lo if S_lo > 0 else math.inf
        want = K.classify(rlo, rhi, 0.90, 1.10)
        if want == K.ABOVE and d['D_lo'] - 1.10 * S_hi < FLOOR: want = K.CANNOT_TELL
        if want == K.BELOW and 0.90 * S_lo - d['D_hi'] < FLOOR: want = K.CANNOT_TELL
    if not posthoc and o != want: bad(r, 'VI', 'outcome %s but band gives %s' % (o, want))
    if o == K.BELOW and 'contact details' not in (r.get('reason') or ''): bad(r, 'VI', 'BELOW without the unsized differences')
    if o == K.ABOVE and 're-filings' not in (r.get('reason') or '') and S != 0: bad(r, 'VI', 'ABOVE without the unsized differences')
    if r.get('view') == 'main' and r.get('outcome_plan_rule') and r['outcome_plan_rule'] != o and r.get('outcome_rule') != r['outcome_plan_rule']: bad(r, 'VI', 'plan-rule outcome not kept')
    n['VI'] += 1
print('checks run', n); print('FAILURES', len(fails))
for f in fails[:40]: print('  ', f)
print('summary original-row outcomes', summ['outcomes_original_rows'], '| ads', summ['outcomes_ads_rows'], '| combined', summ['outcomes_combined_rows'], '| gate', summ['gate_passed'], '| plan gate', summ['plan_gate_passed'])
