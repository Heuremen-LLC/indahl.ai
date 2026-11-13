#!/usr/bin/env python3
"""bfix_apply.py [--write]  (site pass 30 Oct 2026, lane B). Rebuilds book_calibrated.json, qia_body.html and the row sources from the pristine
pre-sitepass copies plus the approved edit files (approved/*.json) plus the mechanical passes below. Idempotent.
Writes a change log (changes.json) and the ledger commands (LEDGER_TODO_B.rows.md) when --write is given."""
import sys, os, re, json, glob, html, unicodedata, shlex, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rowtool as R
from texclean import tex_plain
from nine import TITLES
WRITE = '--write' in sys.argv
MP = R.MP; SFX = R.SFX
rows = R.Rows(); body_items = []; problems = []; subs = []
# ---------- 1. approved agent edits
for f in sorted(glob.glob(HERE + '/approved/*.json')):
    d = json.load(open(f))
    for it in d.get('items', []):
        if 'new' in it:
            cur = rows.orig[it['id']][it['field']]
            if 'old' in it and it['old'] != cur: problems.append(('old differs', f, it['finding'], it['id'], it['field']))
            rows.set(it['id'], it['field'], it['new'], it['finding'])
        else: subs.append((f, it))
    body_items += [(f, b) for b in d.get('body_items', [])]
for f, it in subs:
    if not rows.sub(it['id'], it['field'], it['old_sub'], it['new_sub'], it['finding']): problems.append(('sub failed', os.path.basename(f), it['finding'], it['id'], it['field'], it['old_sub'][:60]))

# ---------- 2. own edits
# C-20 / B-24: study titles
for r in rows.bk:
    ax = r['study_id']
    if ax in TITLES and r['study'].strip() == f'arXiv {ax}': rows.set(r['id'], 'study', TITLES[ax], 'C-20')
    elif re.search(r'[$\\]|--', r['study']): rows.set(r['id'], 'study', tex_plain(r['study']), 'B-24')
# spaced double hyphens (a TeX dash from the register) become an en dash
for r in rows.bk:
    for f in ('published', 'measured', 'qia_calibration', 'how'):
        if ' -- ' in r[f]: rows.set(r['id'], f, r[f].replace(' -- ', ' \u2013 '), 'B-24')
# the last three semicolons in row text (two sit inside suggested wording, one in a description cell with a superscript the renderer would drop)
rows.sub('kipu_qcrllm', 'qia_calibration', 'classical SA; quantum hardware adds', 'classical SA, and quantum hardware adds', 'B-25/C-23')
rows.sub('ionq_9999', 'qia_calibration', 'N <= 200 Cliffords; 1.16e-4', 'N <= 200 Cliffords, 1.16e-4', 'B-25/C-23')
rows.byid['ionq_9999']['study'] = rows.byid['ionq_9999']['study'].replace('5 Nov 2025; not IBM', '5 Nov 2025, not IBM'); rows.log.append(('B-25/C-23', 'ionq_9999', 'study'))
body_items.append(('own', dict(finding='B-25/C-23', where='ionq description cell', old='(Form 8-K filed 5 Nov 2025; not IBM hardware)', new='(Form 8-K filed 5 Nov 2025, not IBM hardware)')))
# C-24: displayed organisation names go back into the rows (the page already shows them)
for r in rows.bk:
    disp = R.txt(rows.cells[r['id']][0]).strip()
    if disp != r['organisation']: r['organisation'] = disp; rows.log.append(('C-24', r['id'], 'organisation'))

# B-25 / C-23: semicolons in our own words become full stops (quoted words are left alone)
from semi import de_semi
n_semi = 0
for r in rows.bk:
    for f in ('published', 'measured', 'qia_calibration', 'how'):
        if ';' in r[f]:
            new = de_semi(r[f])
            if new != r[f]: rows.set(r['id'], f, new, 'B-25/C-23'); n_semi += 1
print('semicolon fields rewritten', n_semi)
# ---------- output pieces
body = rows.body()
for f, b in body_items:
    if body.count(b['old']) != 1: problems.append(('body item', os.path.basename(f), b.get('finding'), b['where'][:50], body.count(b['old'])))
    else: body = body.replace(b['old'], b['new'])
# C-24: sort the Research table by displayed organisation name (stable)
def skey(org):
    t = unicodedata.normalize('NFKD', R.txt(org)); t = ''.join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r'^[^a-z0-9]+', '', t)
i = body.index('<h2>Calibrated Studies: Research') if '<h2>Calibrated Studies: Research' in body else body.index('Calibrated Studies: Research')
j = body.index('</tbody>', i); k = body.index('<tbody>', i) + len('<tbody>')
trs = re.findall(r'<tr>(?:(?!</tr>).)*</tr>', body[k:j], re.S)
assert ''.join(trs) == body[k:j]
srt = sorted(trs, key=lambda t: skey(re.findall(r'<td>(.*?)</td>', t, re.S)[0]))
body = body[:k] + ''.join(srt) + body[j:]
# book_calibrated.json order follows the page (corporate rows, then research rows in table order)
order = {}
for n, t in enumerate(re.findall(r'<tr>(?:(?!</tr>).)*</tr>', body, re.S)):
    cs = re.findall(r'<td>(.*?)</td>', t, re.S)
    if len(cs) == 6: order[(R.key(R.txt(cs[2])), R.key(R.txt(cs[3])))] = n
bk_sorted = sorted(rows.bk, key=lambda r: order[(R.key(r['published']), R.key(r['measured']))])

# ---------- sources kept in step (best effort: the frozen builder cannot run, these files are the record of what a rebuild would say)
def forms(t):
    h = html.escape(t, quote=False)
    for a, b in (('“', '&ldquo;'), ('”', '&rdquo;'), ('’', '&rsquo;'), ('‘', '&lsquo;'), ('–', '&ndash;'), ('—', '&mdash;'), ('±', '&plusmn;'), ('×', '&times;'), ('µ', '&micro;'), ('≤', '&le;'), ('−', '&minus;')): h = h.replace(a, b)
    return [(t, lambda x: x), (h, lambda x: x)]
def bare(field, t): return re.sub(r'^((?:[QF]\d+\s+)+)', '', t) if field == 'qia_calibration' else t
SRC = {p: open(MP + p + SFX).read() for p in ('research_rows.py', 'corp_rows.py', 'norun_rows.py', 'qia_key.py', 'abc_reports.json')}
src_hits = {}
def to_form(t, kind):
    h = html.escape(t, quote=False)
    for a, b in (('“', '&ldquo;'), ('”', '&rdquo;'), ('’', '&rsquo;'), ('‘', '&lsquo;'), ('–', '&ndash;'), ('—', '&mdash;'), ('±', '&plusmn;'), ('×', '&times;'), ('µ', '&micro;'), ('≤', '&le;'), ('−', '&minus;')): h = h.replace(a, b)
    return h if kind == 'html' else t
for (finding, rid, field) in dict.fromkeys(rows.log):
    if field not in ('published', 'measured', 'qia_calibration', 'how', 'organisation'): continue
    o = bare(field, rows.orig[rid][field]); n = bare(field, rows.byid[rid][field])
    if o == n: continue
    hit = 0
    for p in list(SRC):
        for kind in ('plain', 'html'):
            for esc_q in (False, True):
                oo, nn = to_form(o, kind), to_form(n, kind)
                if p.endswith('.json'):
                    oo, nn = json.dumps(oo, ensure_ascii=False)[1:-1], json.dumps(nn, ensure_ascii=False)[1:-1]
                else:
                    nn = nn.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
                    if esc_q: oo = oo.replace("'", "\\'")
                if oo in SRC[p] and SRC[p].count(oo) >= 1:
                    SRC[p] = SRC[p].replace(oo, nn); hit += 1
    src_hits[(rid, field)] = hit
# code overrides in qia_key.py
def codes_of_text(t): return re.findall(r'^((?:[QF]\d+\s+)+)', t + ' ')[0].split() if re.match(r'^[QF]\d', t) else []
for r in rows.bk:
    oc, nc = codes_of_text(rows.orig[r['id']]['qia_calibration']), codes_of_text(r['qia_calibration'])
    if oc != nc:
        m = re.search(r"'%s': \[([^\]]*)\]" % re.escape(r['id']), SRC['qia_key.py'])
        if m: SRC['qia_key.py'] = SRC['qia_key.py'].replace(m.group(0), "'%s': [%s]" % (r['id'], ', '.join("'%s'" % c for c in nc)))
        else: problems.append(('code override not found in qia_key.py', r['id'], oc, nc))
# C-24: names into the row sources
import ast
for r in rows.bk:
    if r['organisation'] != rows.orig[r['id']]['organisation']:
        m = re.search(r"dict\(id='%s', org='([^']*)'" % re.escape(r['id']), SRC['research_rows.py'])
        if m: SRC['research_rows.py'] = SRC['research_rows.py'].replace(m.group(0), m.group(0).replace("org='" + m.group(1) + "'", "org='" + to_form(r['organisation'], 'html').replace("'", "\\'") + "'"), 1)
NAMES = {r['id']: r['organisation'] for r in rows.bk if r['organisation'] != rows.orig[r['id']]['organisation'] and ("id='%s'" % r['id']) not in open(MP + 'research_rows.py').read()}
if NAMES and 'NAMES = {' not in SRC['norun_rows.py']:
    SRC['norun_rows.py'] = SRC['norun_rows.py'].replace("HOW = {r['id']: r['how'] for r in ROWS}",
        "# 30 Oct 2026 (site pass C-24): the page names these authors as published (27 Oct), so a rebuild keeps the names. Ids and names as on the page.\nNAMES = " + json.dumps(NAMES, ensure_ascii=False, indent=1) + "\nfor _r in ROWS:\n    if _r['id'] in NAMES: _r['org'] = NAMES[_r['id']]\nHOW = {r['id']: r['how'] for r in ROWS}", 1)
    assert 'NAMES = {' in SRC['norun_rows.py']

# ---------- row dates for the study pages (C-17)
pre_pub = {r['id']: r for r in json.load(open(MP + 'book_calibrated.json.pre-pubrecount-20261030'))}
def slug_base(sid): return ('zenodo-' + sid[7:]) if str(sid).startswith('zenodo:') else str(sid)
row_dates = {}
for r in rows.bk:
    changed = r['id'] in {l[1] for l in rows.log} or any(pre_pub.get(r['id'], {}).get(f) != r[f] for f in ('published', 'measured', 'qia_calibration', 'how', 'study')) if r['id'] in pre_pub else True
    row_dates[slug_base(r['study_id'])] = '2026-10-30' if changed else row_dates.get(slug_base(r['study_id']), '2026-10-27')
for r in rows.bk:   # a slug shared by two rows takes the later date
    if r['id'] in {l[1] for l in rows.log} or (r['id'] in pre_pub and any(pre_pub[r['id']].get(f) != r[f] for f in ('published', 'measured', 'qia_calibration', 'how', 'study'))): row_dates[slug_base(r['study_id'])] = '2026-10-30'
print('row dates changed 30 Oct:', sum(1 for v in row_dates.values() if v == '2026-10-30'), 'of', len(row_dates))

# ---------- ledger: every live qia.* snippet whose text left the page body
L = [json.loads(l) for l in open(os.path.expanduser('~/bones-forge/ledger/ledger.jsonl')) if l.strip()]
def lnorm(x):
    x = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', x, flags=re.S); x = re.sub(r'<[^>]+>', ' ', x); x = html.unescape(x)
    x = x.replace('−', '-').replace('–', '-').replace('—', '-').replace('\u2009', ' ').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', x).strip()
pre_body = lnorm(open(MP + 'qia_body.html' + SFX).read()); new_body = lnorm(body)
fields_by_text = {}
for r in rows.bk:
    for f in ('published', 'measured', 'qia_calibration', 'how'):
        fields_by_text.setdefault(lnorm(html.escape(rows.orig[r['id']][f], quote=False)), []).append((r['id'], f))
body_pairs = [(lnorm(b['old']), lnorm(b['new'])) for _, b in body_items]
led_cmds = []; led_rows = 0
why = 'Site pass 30 Oct 2026 (lane B and C fixes): cell text changed at its source, snippet re-recorded from the new cell'
for row in L:
    if not row['id'].startswith('qia.') or row.get('status') != 'live': continue
    snips = [sf['text'] for sf in row['surfaces'] if sf['surface'] == 'qia_matrix']
    gone = [t for t in snips if lnorm(t) in pre_body and lnorm(t) not in new_body]
    if not gone: continue
    newsn = []
    for t in snips:
        if t not in gone: newsn.append(t); continue
        nt = lnorm(t); rep = None
        for ot, lst in fields_by_text.items():
            if nt in ot:
                rid, f = lst[0]; rep = html.escape(bare(f, rows.byid[rid][f]), quote=False); break
        if rep is None:
            for ot, nw in body_pairs:
                if nt in ot: rep = html.escape(nw, quote=False); break
                if ot in nt: rep = html.escape(nt.replace(ot, nw), quote=False); break
        newsn.append(rep if rep else '(CHOOSE A SNIPPET FROM THE NEW PAGE TEXT)')
    led_rows += 1
    led_cmds.append(f"python3 ~/bones-forge/ledger/ledger.py off {row['id']} qia_matrix --why {shlex.quote(why)}")
    for t in dict.fromkeys(newsn): led_cmds.append(f"python3 ~/bones-forge/ledger/ledger.py on {row['id']} qia_matrix {shlex.quote(t)}")
print('ledger rows to re-record', led_rows, 'commands', len(led_cmds))

# ---------- validate
assert len(re.findall(r'<tr[ >]', body)) == body.count('</tr>') and len(re.findall(r'<td[ >]', body)) == body.count('</td>')
assert len(bk_sorted) == 196 and len({r['id'] for r in bk_sorted}) == 196
rows_re = [c for c in (re.findall(r'<td>(.*?)</td>', t, re.S) for t in re.findall(r'<tr>(?:(?!</tr>).)*</tr>', body, re.S)) if len(c) == 6]
assert len(rows_re) == 196
miss = {k: v for k, v in src_hits.items() if v == 0}
print('source files: fields found and replaced', sum(1 for v in src_hits.values() if v), 'not found', len(miss))
print('problems', len(problems)); [print('  ', p) for p in problems]
print('changes', len(rows.log), 'fields on', len({l[1] for l in rows.log}), 'rows')
open(HERE + '/qia_body.new.html', 'w').write(body)
json.dump(bk_sorted, open(HERE + '/book_calibrated.new.json', 'w'), ensure_ascii=False, indent=1)
json.dump(dict(changes=rows.log, src_miss=[list(k) for k in miss], problems=[list(map(str, p)) for p in problems]), open(HERE + '/changes.json', 'w'), indent=0)
open(HERE + '/LEDGER_TODO_B.rows.md', 'w').write('\n'.join(led_cmds) + '\n')
json.dump(row_dates, open(HERE + '/row_dates.new.json', 'w'), indent=0)
if WRITE:
    open(MP + 'qia_body.html', 'w').write(body)
    json.dump(bk_sorted, open(MP + 'book_calibrated.json', 'w'), ensure_ascii=False, indent=1)
    for p, t in SRC.items(): open(MP + p, 'w').write(t)
    json.dump(row_dates, open(MP + 'row_dates.json', 'w'), indent=0)
    print('WRITTEN')
