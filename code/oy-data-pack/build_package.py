"""build_package.py: assembles the OY Data Pack from the published OY pages into dist/oy-data-pack/ and zips it.
Reads indahl-ai/oy.html and indahl-ai/oy/school/*.html (the pages the site serves), writes their tables as JSON and CSV with one row per record,
and writes SOURCES.md, NOTICE.txt, LICENSE.txt, README, START_HERE.html and verify.py. The text of every value is the page text.
Cross-checks the school pages against oy_index/schools.json, the file the school pages are built from.
Refuses if any file names a local path, a key file, a token, an email address, or if a text file breaks the house wording rules.
Builds locally only. Nothing is published."""
import os, shutil, re, zipfile, hashlib, html, json, csv, sys, importlib.util
B = os.path.expanduser('~/bones-forge/'); H = os.path.dirname(os.path.abspath(__file__)); D = H + '/dist/oy-data-pack'
sys.path.insert(0, H + '/tools'); import extract_oy as X
shutil.rmtree(H + '/dist', ignore_errors=True)
for s in ('json', 'csv'): os.makedirs(D + '/' + s)
sp = importlib.util.spec_from_file_location('verify', H + '/src/verify.py'); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
shutil.copy(H + '/src/verify.py', D + '/verify.py')
# 1. read the pages
page = open(X.SITE + 'oy.html', encoding='utf-8').read(); tb = X.tables(page); assert len(tb) == 4
TX = X.text_blocks(page); AS_OF = re.search(r'as of (\d+ \w+ \d{4})', TX['headline_text'] + ' ' + TX['how_these_rows_were_read']).group(1)   # 10 Nov 2026: the headline now says read once, on <date>
chat, find, lst, sch = X.chatbot(tb[0]), X.findings(tb[1]), X.lst(tb[2]), X.schools_table(tb[3])
PAGE = 'https://indahl.ai/oy'
schools = []
for r in sch:
    p = X.school_page(open(X.SITE + f"oy/school/{r['unitid']}.html", encoding='utf-8').read(), r['unitid'])
    assert p['name'] == r['school'] and p['state'] == r['state'], (p['name'], r['school'])
    schools.append({'unitid': r['unitid'], 'school': r['school'], 'state': r['state'], 'carnegie': p['carnegie'], 'page_url': p['page_url'], 'site_url': p['site_url'], 'nces_url': p['ncesid_url'],
                    'school_paragraph': p['school_paragraph'], 'site_read': p['site_read'], 'sentences_total': r['sentences'], 'course_titles_total': r['course_titles'],
                    'read_in_full_label': r['read_in_full'], 'read_in_full_note': p['read_in_full_note'], 'read_in_full_date': p['read_in_full_date'],
                    'sentences_note': p['sentences_note'], 'sentences': p['sentences'], 'course_titles_note': p['course_titles_note'], 'course_titles': p['course_titles'], 'read_on': p['read_on']})
    assert p['read_in_full_label'] == r['read_in_full'], r['unitid']
    assert r['site'] == p['site_read'].rstrip('.') or r['site'] == p['site_read'], (r['site'], p['site_read'])
assert len(schools) == len(set(s['unitid'] for s in schools)) == len(os.listdir(X.SITE + 'oy/school'))
# cross-check with the file the school pages are built from
SJ = {s['unitid']: s for s in json.load(open(B + 'oy_index/schools.json', encoding='utf-8'))}
assert set(SJ) == {s['unitid'] for s in schools}
for s in schools:
    j = SJ[s['unitid']]
    want = [(('…' if h.get('cut_start') else '') + h['sentence'] + ('…' if h.get('cut_end') else '')).strip() for h in j['sentences']]   # the page text is trimmed of outer spaces
    assert [x['text'] for x in s['sentences']] == want and [x['url'] for x in s['sentences']] == [h['url'] for h in j['sentences']], s['unitid']
    wc = [(h['line'] + (f" ({h['year']} catalog)" if h.get('year') else '')).strip() for h in j['courses']]
    assert [x['text'] for x in s['course_titles']] == wc and [x['url'] for x in s['course_titles']] == [h['url'] for h in j['courses']], s['unitid']
    assert s['carnegie'] == j['carnegie'] and s['state'] == j['state']
    assert s['sentences_total'] == (j['sentences_total'] if j['site_read'] == 'yes' else None), s['unitid']
    assert s['course_titles_total'] == (j['courses_total'] if j['catalog'] == 'readable' else None), s['unitid']
    assert (j['hand']['label'] if j.get('hand') else '') == s['read_in_full_label']
reads = {s['read_on'] for s in schools}; assert len(reads) == 1; READ_ON = reads.pop(); READ_ON_DATE = READ_ON.split(' (')[0]
rif = {s['read_in_full_date'] for s in schools if s['read_in_full_date']}; assert rif == {'28 October 2026'}, rif
TEXT = dict({'page': PAGE, 'as_of': AS_OF}, **TX)
files = {'oy_chatbot_citations.json': {'page': PAGE, 'as_of': AS_OF, 'rows': chat}, 'oy_findings.json': {'page': PAGE, 'as_of': AS_OF, 'findings': find},
         'oy_list.json': {'page': PAGE, 'as_of': AS_OF, 'rows': lst}, 'oy_schools.json': {'page': PAGE, 'read_on': READ_ON, 'schools': schools}, 'oy_text.json': TEXT}
data = {}
for f, d in files.items():
    with open(D + '/json/' + f, 'w', encoding='utf-8') as fh: json.dump(d, fh, ensure_ascii=False, indent=1); fh.write('\n')
    data[f] = json.load(open(D + '/json/' + f, encoding='utf-8')); assert data[f] == d
# 2. CSV
def put_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, lineterminator='\n'); w.writerow(header)
        for r in rows: w.writerow([V.cell(r.get(h)) for h in header])
for t, (jf, rows, count) in V.TABLES.items():
    recs = rows(data[jf]); flat = [V.flatten(r) for r in recs]; header = []
    for fr in flat:
        for k in fr:
            if k not in header: header.append(k)
    put_csv(D + f'/csv/{t}.csv', header, flat)
fm = V.flat_meta(data['oy_text.json']); put_csv(D + '/csv/oy_text_meta.csv', ['key', 'value'], [{'key': k, 'value': v} for k, v in fm.items()])
# 3. text from templates, counts from the data
tok = {'N_CHATBOT': len(chat), 'N_FINDINGS': len(find), 'N_LIST': len(lst), 'N_SCHOOLS': len(schools), 'N_SENT': sum(len(s['sentences']) for s in schools), 'N_COURSE': sum(len(s['course_titles']) for s in schools)}
tok = {k: f'{v:,}' for k, v in tok.items()}; tok.update({'AS_OF': AS_OF, 'READ_ON_DATE': READ_ON_DATE})
assert tok['N_LIST'] == '148' and tok['N_CHATBOT'] == '8', 'the page counts changed'
assert f"{len(lst)} rows" in TX['how_these_rows_were_read'] or f"{len(lst)} rows" in TX['headline_text']
def fill(t):
    for k, v in tok.items(): t = t.replace('{' + k + '}', str(v))
    left = re.findall(r'\{[A-Z_0-9]+\}', t); assert not left, left
    return t
for f in ('README.md', 'SOURCES.md', 'TESTED.md', 'LICENSE.txt', 'NOTICE.txt'): open(D + '/' + f, 'w').write(fill(open(H + '/src/' + f).read()))
shutil.copy(H + '/src/CITATION.cff', D + '/CITATION.cff')
_paths = lambda f: set(re.findall(r'(?:json|csv)/[A-Za-z0-9_]+\.(?:jsonl|json|csv)', open(D + '/' + f).read()))
assert _paths('LICENSE.txt') == _paths('NOTICE.txt'), ('LICENSE and NOTICE list different files', _paths('LICENSE.txt') ^ _paths('NOTICE.txt'))
assert all(os.path.exists(D + '/' + p) for p in _paths('LICENSE.txt')), 'a listed file is missing from the pack'
_all = {f'{x}/{y}' for x in ('json', 'csv') for y in os.listdir(D + '/' + x)}
assert _all == _paths('LICENSE.txt'), ('files not covered by LICENSE.txt', _all ^ _paths('LICENSE.txt'))
_readme = open(D + '/README.md').read()
for p in _all: assert p in _readme or p.endswith('_meta.csv') or p.split('/')[1] in _readme, ('README does not mention', p)
# 4. START_HERE.html from README.md, with the logo
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
md = open(D + '/README.md').read(); body = []
for blk in md.split('\n\n'):
    if blk.strip().startswith('```'): body.append('<pre>' + html.escape(blk.strip().strip('`').strip()) + '</pre>'); continue
    b = html.escape(blk.strip()); b = re.sub(r'`([^`]+)`', r'<code>\1</code>', b); b = re.sub(r'(?<![\w/"])(https://[^\s<·]*[^\s<·.,;:)])', r'<a href="\1">\1</a>', b)
    if b.startswith('# '): continue
    if b.startswith('## '): body.append('<h2>' + b[3:] + '</h2>')
    elif re.match(r'^- ', b): body.append('<ul>' + ''.join('<li>' + re.sub(r'^- ', '', l.strip()) + '</li>' for l in re.split(r'\n(?=- )', b)) + '</ul>')
    else: body.append('<p>' + b.replace('\n', ' ') + '</p>')
css = ('body{font:16px/1.55 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:860px;margin:0 auto;padding:24px 16px}header{display:flex;gap:12px;align-items:center;'
       'border-bottom:2px solid #c9a227;padding-bottom:12px}header h1{font-size:24px;margin:0}code{background:#efe4cf;padding:1px 4px;font-size:14px;word-break:break-all}pre{background:#efe4cf;padding:10px;overflow-x:auto;font-size:14px}a{color:#7a5a12}.note{color:#5a4d3a;font-size:14px}')
open(D + '/START_HERE.html', 'w').write(f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>OY Data Pack</title>\n<style>{css}</style>\n</head>\n<body>\n<main>\n'
    f'<header>{LOGO}<div><h1>OY Data Pack</h1><span class="note">Heuremen LLC &middot; <a href="https://indahl.ai/oy">indahl.ai/oy</a></span></div></header>\n' + '\n'.join(body) + '\n</main>\n</body>\n</html>\n')
# 5. gate: nothing private, house wording
bad = re.compile(r'bones-forge|/Users/|\.ibm_quantum_key|wrangler|(api|secret|access)[_-]?key\s*[=:]\s*\S{8}|(token|password)\s*[=:]\s*["\']?[A-Za-z0-9]{12}|hf_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|pypi-[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20}|BEGIN [A-Z ]*PRIVATE KEY|[\w.+-]+@[\w-]+\.[a-z]{2,}', re.I)
wording = re.compile(r';|by hand|hand-checked|hand-read|AI-assisted|AI assistant|generated by|written by an AI|Kory', re.I)
for r, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(r, f); txt = open(p, errors='replace').read(); m = bad.search(txt)
        assert not m, f'REFUSED: {os.path.relpath(p, D)} contains {m.group(0)!r}'
        if f in ('README.md', 'SOURCES.md', 'NOTICE.txt', 'LICENSE.txt', 'TESTED.md'):
            m = wording.search(re.sub(r'&[a-z]+;|&#\d+;', '', txt)); assert not m, f'REFUSED wording: {f} contains {m.group(0)!r}'
# 6. zip
z = H + '/dist/oy-data-pack.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for r, _, fs in os.walk(D):
        for f in sorted(fs):
            if '__pycache__' in r or f.endswith('.pyc'): continue
            p = os.path.join(r, f); zf.write(p, os.path.relpath(p, H + '/dist'))
h = hashlib.sha256(open(z, 'rb').read()).hexdigest(); open(z + '.sha256', 'w').write(f'{h}  oy-data-pack.zip\n')
print('files', sum(len(fs) for _, _, fs in os.walk(D)), '| zip', round(os.path.getsize(z) / 1048576, 2), 'MB | sha256', h)
