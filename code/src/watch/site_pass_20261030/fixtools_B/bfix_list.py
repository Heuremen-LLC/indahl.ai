#!/usr/bin/env python3
"""bfix_list.py (site pass 30 Oct 2026, lane B): rebuilds list.json and the /qia/list page body from the pristine pre-sitepass list.json.
Idempotent. Fixes: B-21/C-20 (nine calibrated studies added), B-23 (receipt lines cut at 240 characters), B-24 (raw TeX), C-22 (internal term),
B-25 (semicolon in the first receipt line), B-22 (page titles), code sync with the calibrated rows. Run: python3 bfix_list.py [--write]"""
import json, re, sys, os, html, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from texclean import tex_plain
MP = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/'); PUB = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/public/qia/list.json')
SFX = '.pre-sitepass-20261030'
E = html.escape
base = json.load(open(MP + 'list.json' + SFX)); L = base['studies']
bk_old = json.load(open(MP + 'book_calibrated.json' + SFX)); bk_new = json.load(open(MP + 'book_calibrated.json'))

def repair(t):
    if len(t) != 240 or re.search(r'[.!?)"”\]]$', t): return t
    u = t.rsplit(' ', 1)[0].rstrip(' ,;:-(')
    while u.count('(') > u.count(')'):
        k = u.rfind('('); u = u[:k].rstrip(' ,;:-')
    while u.count('{') > u.count('}') and ' ' in u:
        u = u.rsplit(' ', 1)[0].rstrip(' ,;:-(')
    return u + ('..."' if u.count('"') % 2 else ' ...')
def semis(t):
    return t
from semi import de_semi
n_cut = n_tex = n_df = n_semi = 0
for x in L:
    if re.search(r'[$\\]|--', x['study']): x['study'] = tex_plain(x['study']); n_tex += 1
    nb = {}
    for c, ts in x['basis'].items():
        out = []
        for t in ts:
            r = repair(t)
            if r != t: n_cut += 1
            if re.search(r'\$|\\[a-zA-Z]|_\{|T 1 T', r): r = tex_plain(r); n_tex += 1
            if r.count('{') > r.count('}'):
                while r.count('{') > r.count('}') and ' ' in r: r = r.rsplit(' ', 1)[0].rstrip(' ,;:-(')
                r = r + ('..."' if r.count('"') % 2 else ' ...'); n_cut += 1
            if 'dumb-fast' in r: r = r.replace('dumb-fast baseline', 'simple classical method').replace('dumb-fast comparator', 'simple classical comparator').replace('dumb-fast', 'simple classical'); n_df += 1
            if ';' in r: r = de_semi(r); n_semi += 1
            out.append(r)
        nb[c] = out
    x['basis'] = nb

def ax_of(link):
    m = re.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', link) or None
    if m: return m.group(1)
    z = re.search(r'zenodo\.(\d{6,9})', link)
    return 'zenodo:' + z.group(1) if z else None
def codes_of(r):
    return re.findall(r'^((?:[QF]\d+\s*)+)', r['qia_calibration'])[0].split() if re.match(r'^[QF]\d', r['qia_calibration']) else []
old_codes = {}; new_codes = {}
for src, dst in ((bk_old, old_codes), (bk_new, new_codes)):
    for r in src:
        for k in (r['study_id'], r.get('also')):
            if k: dst.setdefault(k, set()).update(codes_of(r))
n_sync = 0
for x in L:
    k = ax_of(x['link'])
    if not k or not x['calibrated']: continue
    if k in old_codes and k in new_codes and old_codes[k] != new_codes[k]:
        gone = old_codes[k] - new_codes[k]; new = new_codes[k] - old_codes[k]
        cs = (set(x['codes']) - {c for c in gone if c not in x['basis']}) | new
        cs = sorted(cs, key=lambda c: (c[0] != 'Q', int(c[1:])))
        if cs != x['codes']: x['codes'] = cs; n_sync += 1

# ---- B-21 / C-20: the nine calibrated studies that were not on the List
NINE = [  # arXiv id, title (arXiv API), version read, indexed (date of our audit or run), evidence
 ('2510.17286', 'Trapped-ion two-qubit gates with >99.99% fidelity without ground-state cooling', 'v1', '2026-10-23'),
 ('2607.01037', 'Quantum-Informed Portfolio Selection: An End-to-End Pipeline Validated on Trapped-Ion Hardware with Real Market Data', 'v2', '2026-10-23'),
 ('2510.08719', 'Universal syndrome-based recovery for noise-adapted quantum error correction', 'v2', '2026-10-24'),
 ('2509.19448', 'Separate and efficient characterization of state-preparation and measurement errors using single-qubit operations', 'v2', '2026-10-24'),
 ('2512.18493', 'Cyber Threat Detection Enabled by Quantum Computing', 'v1', '2026-10-24'),
 ('2509.20127', 'A Comparison of Quadratic and Higher-Order Representations for QAOA', 'v1', '2026-10-24'),
 ('2609.16108', 'Large-scale quantum simulations of dissipative spin-1/2 Heisenberg chains', 'v1', ''),
 ('2508.16895', 'Quantum State Fidelity for Functional Neural Network Construction', 'v2', '2026-10-24'),
 ('2608.13614', 'A Quantum Optimization Framework for Data-Assimilation-Augmented Parameter Estimation', 'v1', '2026-10-24'),
]
have = {ax_of(x['link']) for x in L}
n_add = 0
for a, title, ver, idx in NINE:
    if a in have: continue
    cs = sorted(new_codes.get(a, set()), key=lambda c: (c[0] != 'Q', int(c[1:])))
    L.append(dict(study=title, link=f'https://arxiv.org/abs/{a}{ver}', version=ver, indexed=idx, read='Full text', codes=cs, basis={}, calibrated=True)); n_add += 1
L.sort(key=lambda x: re.sub(r'^[^A-Za-z0-9]+', '', x['study']).lower())

def table(head, rows, cls='mtx'):
    return (f'<div class="scroll"><table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')
def list_row(x):
    rc = '<details><summary>receipt</summary><ul>' + f'<li>Read: {E(x["read"])}{(", version " + E(x["version"])) if x["version"] else ""}, indexed {E(x["indexed"] or "date not recorded")}</li>'
    rc += ''.join(f'<li><a class="code" href="/qia/key#{c}">{c}</a> {E(t)}</li>' for c, ts in sorted(x['basis'].items()) for t in ts)
    if x['calibrated']: rc += '<li>Calibrated: see the QIA page</li>'
    rc += '</ul></details>'
    cc = ' '.join(f'<a class="code" href="/qia/key#{c}">{c}</a>' for c in x['codes']) or '&mdash;'
    return (f'<a href="{E(x["link"])}">{E(x["study"])}</a>', cc, E(x['indexed']), rc)
tbl = table(['Study', 'QIA classification', 'Indexed', 'Receipt'], [list_row(x) for x in L], 'mtx list')
print(f'semicolons {n_semi}, cut repaired {n_cut}, tex {n_tex}, dumb-fast {n_df}, code sync {n_sync}, added {n_add}, studies {len(L)}, calibrated {sum(1 for x in L if x["calibrated"])}')
if '--write' in sys.argv:
    out = dict(base, studies=L)
    json.dump(out, open(MP + 'list.json', 'w'), ensure_ascii=False, indent=0); shutil.copy(MP + 'list.json', PUB)
    pg = json.load(open(MP + 'qia_pages.json')); body = pg['/qia/list']['body']
    i = body.index('<div class="scroll">'); j = body.index('</table></div>') + len('</table></div>')
    pg['/qia/list']['body'] = body[:i] + tbl + body[j:]
    pg['/qia/list']['title'] = 'The List: Inventory of Published Studies | Quantum Idle Audit | Heuremen LLC'
    pg['/qia/key']['title'] = 'QIA Key | Quantum Idle Audit | Heuremen LLC'
    # ---- the Key page: B-25 (two semicolons in definitions), C-12 (the recount words are defined)
    kb = pg['/qia/key']['body']
    for a, b in (('IBM states P(1|0) = 0; the delivered value', 'IBM states P(1|0) = 0. The delivered value'),
                 ('untouched neighbouring qubits; no IBM field covers it.', 'untouched neighbouring qubits. No IBM field covers it.')):
        if a in kb: kb = kb.replace(a, b)
    RW = ('<section><h2>Recount words</h2><p>A number reproduces when we recompute it from what the study released and get the printed value. '
          'It does not reproduce when we get a different value. A number rebuilds in the same sense when we reconstruct it from the released data. '
          'Where what is released does not allow the recomputation we say cannot tell. '
          'A reading from one of our own runs is printed with its interval and the level of that interval, and says above, below, consistent or cannot tell against the figure it is read against.</p></section>')
    if 'Recount words' not in kb: kb += RW
    pg['/qia/key']['body'] = kb
    json.dump(pg, open(MP + 'qia_pages.json', 'w'), ensure_ascii=False)
    kp = MP + 'qia_key.py'; ks = open(kp).read()
    for a, b in (("'IBM states P(1|0) = 0; the delivered value is above what a zero allows.'", "'IBM states P(1|0) = 0. The delivered value is above what a zero allows.'"),
                 ("untouched neighbouring qubits; no IBM field covers it.", "untouched neighbouring qubits. No IBM field covers it.")):
        if a in ks: ks = ks.replace(a, b)
    open(kp, 'w').write(ks)
    print('written')
