"""Parse the claim tables from each live source page; compare with claims.json; verbatim check vs raw vendor text; python-repr and semicolon counts."""
import re, json, html, os, collections
D = '/Users/heuremen/bones-forge/watch/site_pass_20261030/scratch_E'
MI = '/Users/heuremen/bones-forge/mlperf_index'
cl = json.load(open(f'{D}/claims_live.json'))
claims = cl['claims']; summ = cl['summary']
def slug(k): return re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-')
# source key -> raw text file, from build_sad.py SRC (exec just the dict part)
src = open(f'{MI}/build_sad.py').read()
m = re.search(r"^SRC=\{.*?\n(?=# claims whose)", src, re.S | re.M)
ns = {}
exec('import os\n' + m.group(0).replace('\nSRC=', '\nSRC=', 1), ns)
SRC = ns['SRC']
# supp keys
for k, s, v in [('AMD','amd','AMD'),('Crusoe','crusoe','Crusoe'),('ASUS','asus','ASUS'),('Cisco','cisco','Cisco'),('CoreWeave','coreweave','CoreWeave'),('Fujitsu','fujitsu','Fujitsu'),('HPE v6.1','hpe_v6_1','HPE'),('Intel','intel','Intel'),('MangoBoost','mangoboost','MangoBoost'),('NVIDIA','nvidia','NVIDIA'),('Lambda','lambda','Lambda'),('ScitiX','scitix','ScitiX'),('VibeHPC','vibehpc','VibeHPC'),('Wiwynn','wiwynn','Wiwynn'),('Orrick Industries','orrick_industries','x'),('Individual contributor','individual_contributor','x'),('Nebius','nebius','Nebius'),('Oracle','oracle','Oracle'),('GigaComputing','gigacomputing','GigaComputing')]:
    SRC['Supp ' + k + ' v6.1'] = dict(text='raw/supp61.txt')
def norm_loose(s): return re.sub(r'\s+', ' ', s.replace('’', "'").replace('“', '"').replace('”', '"').replace('‘', "'")).strip().lower()
def norm_strict(s): return re.sub(r'\s+', ' ', s.replace('’', "'").replace('“', '"').replace('”', '"').replace('‘', "'")).strip()
tag = re.compile(r'<[^>]+>')
out = {}
srckeys = {slug(k): k for k in [s['key'] for s in summ['sources']]}
bysrc = collections.defaultdict(list)
for c in claims: bysrc[c['source_key']].append(c)
rep = []
tot = dict(pages=0, rows=0, mism=0, nonverb_loose=0, nonverb_strict=0)
pyrepr = collections.Counter(); semi_cells = collections.Counter(); pyexamples = collections.defaultdict(list)
for sl, key in sorted(srckeys.items()):
    p = f'{D}/pages/hermes__model__source__{sl}.html'
    if not os.path.exists(p): rep.append(('MISSINGPAGE', sl)); continue
    t = open(p, encoding='utf-8').read(); tot['pages'] += 1
    rows = re.findall(r'<tr>(.*?)</tr>', t[t.find('<tbody>'):t.find('</tbody>')], re.S)
    cells = [[html.unescape(tag.sub('', c)) for c in re.findall(r'<td>(.*?)</td>', r, re.S)] for r in rows]
    exp = sorted(bysrc[key], key=lambda c: ({'ABOVE':0,'BELOW':1,'CONSISTENT':2,'CANNOT_TELL':3}[c['outcome']], c['id']))
    if len(cells) != len(exp): rep.append(('ROWCOUNT', sl, len(cells), len(exp)))
    # tally line
    mt = re.search(r'(\d+) statements checked: ([^<]*)\.', t); tally_page = mt.group(0) if mt else None
    cnt = collections.Counter(c['outcome'] for c in exp)
    want = f"{sum(cnt.values())} statements checked: " + ', '.join(f"{cnt[k]} {k}" for k in ('ABOVE','BELOW','CONSISTENT','CANNOT_TELL') if k in cnt) + '.'
    if tally_page != want: rep.append(('TALLY', sl, tally_page, want))
    # fetched line / source line
    # raw text
    rawp = f"{MI}/{SRC[key]['text']}"
    raw_l = norm_loose(open(rawp, encoding='utf-8', errors='replace').read()); raw_s = norm_strict(open(rawp, encoding='utf-8', errors='replace').read())
    for row, c in zip(cells, exp):
        tot['rows'] += 1
        if len(row) != 6: rep.append(('CELLS', sl, c['id'], len(row))); continue
        st, comp, stated, infile, oc, note = row
        quoted = st.startswith('“') and st.endswith('”')
        if quoted != c['verbatim']: rep.append(('QUOTEFLAG', sl, c['id'])); 
        want_note = c['note'] + (' The entry named in the post is listed in the file with a different accelerator.' if c['label_mismatch'] else '')
        if (comp, stated, infile, oc, note) != (c['compared'], c['stated'], c['in_file'], c['outcome'], want_note): tot['mism'] += 1; rep.append(('CELLMISMATCH', sl, c['id']))
        if quoted:
            q = st[1:-1]
            parts = [x for x in re.split(r'\s*\.\.\.\s*', q) if x]
            if not all(norm_loose(x) in raw_l for x in parts): tot['nonverb_loose'] += 1; rep.append(('NOTVERBATIM_LOOSE', sl, c['id'], q[:200]))
            elif not all(norm_strict(x) in raw_s for x in parts): tot['nonverb_strict'] += 1; rep.append(('NOTVERBATIM_CASE', sl, c['id'], q[:200]))
        for name, txt in (('compared', comp), ('stated', stated), ('in_file', infile), ('note', note)):
            if ';' in txt: semi_cells[(sl, name)] += 1
            for pat, lab in ((r"\['", 'listrepr'), (r"\[\]", 'emptylist'), (r"\(\'", 'tuplerepr'), (r'\bNone\b', 'None'), (r'\bTrue\b|\bFalse\b', 'bool'), (r'\d\.\d+e[+-]\d+', 'enotation'), (r"\{'", 'dictrepr'), (r"\bnan\b|\bNaN\b", 'nan')):
                if re.search(pat, txt): pyrepr[(lab)] += 1; pyexamples[lab].append((sl, c['id'], name, txt[:160]))
print(tot)
for r in rep: print(r)
print('semicolon cells by column:', collections.Counter(k[1] for k in semi_cells), 'pages with semicolon cells', len({k[0] for k in semi_cells}), 'cells total', sum(semi_cells.values()))
print('python repr leaks', dict(pyrepr))
for lab, ex in pyexamples.items():
    print('---', lab, len(ex), 'rows in', len({e[0] for e in ex}), 'pages')
    for e in ex[:4]: print('   ', e)
json.dump({lab: ex for lab, ex in pyexamples.items()}, open(f'{D}/pyrepr_examples.json', 'w'), indent=1)
