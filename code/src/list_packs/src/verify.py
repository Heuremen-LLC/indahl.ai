"""verify.py: checks this list pack is consistent. Run: python3 verify.py (from the unpacked folder)."""
import csv, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
bad = []
def https(u): return 'https://' + u[7:] if u.startswith('http://') else u
def need(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
studies = json.load(open(H + '/list.json', encoding='utf-8'))['studies']
rows = list(csv.DictReader(open(H + '/list.csv', encoding='utf-8', newline='')))
bib = open(H + '/references.bib', encoding='utf-8').read()
ris = open(H + '/references.ris', encoding='utf-8').read()
def parse_bib(txt):
    """Tiny BibTeX reader: returns [(key, body)]; raises on unbalanced braces."""
    out = []; i = 0
    for m in re.finditer(r'^@(\w+)\{([^,\s]+),', txt, re.M):
        j = txt.index('{', m.start()); depth = 0; k = j
        while k < len(txt):
            c = txt[k]
            if c == '\\': k += 2; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        if depth != 0: raise ValueError('unbalanced braces in ' + m.group(2))
        out.append((m.group(2), txt[j + 1:k]))
    return out
try:
    ents = parse_bib(bib); ok = True
except ValueError as e:
    ents = []; ok = False; print(e)
need(ok, 'every references.bib entry has balanced braces')
need((bib.count('\n@') + (1 if bib.startswith('@') else 0) == len(ents)), 'every @ in references.bib starts a parsed entry')
keys = [k for k, _ in ents]
need(len(keys) == len(set(keys)), 'bib keys are unique')
n = len(studies)
ris_n = len(re.findall(r'^ER  - ', ris, re.M))
need(n == len(rows) == len(ents) == ris_n, f'row counts equal: json {n}, csv {len(rows)}, bib {len(ents)}, ris {ris_n}')
need(all(re.search(r'\burl = \{https://', b) and re.search(r'\btitle = \{', b) for _, b in ents), 'every bib entry has title and an https url')
need(sorted(re.findall(r'\burl = \{([^}]*)\}', bib)) == sorted(https(s['link']) for s in studies), 'bib urls equal the json links')
need(sorted(re.findall(r'^UR  - (.*)$', ris, re.M)) == sorted(https(s['link']) for s in studies), 'ris urls equal the json links')
need([r['study'] for r in rows] == [' '.join(s['study'].split()) for s in studies], 'csv study titles equal json titles, same order')
need(all(r['link'].startswith('https://') and r['indahl_url'].startswith('https://') for r in rows), 'every url in list.csv starts with https://')
need(all(s['link'].startswith(('https://', 'http://')) for s in studies), 'every json link is a web link (http links are written as https in the other files)')
key = list(csv.DictReader(open(H + '/KEY.csv', encoding='utf-8', newline='')))
need(len(key) > 0 and all(r['code'] and r['meaning'] for r in key), 'KEY.csv has a code and a meaning on every row')
used = {c for s in studies for c in s.get('codes', [])}
need(used <= {r['code'] for r in key}, 'every code used in list.csv is defined in KEY.csv' + ('' if used <= {r['code'] for r in key} else ': missing ' + str(sorted(used - {r['code'] for r in key}))))
cite = open(H + '/CITE_THE_LIST.bib', encoding='utf-8').read()
need(len(parse_bib(cite)) == 1, 'CITE_THE_LIST.bib holds one entry')
try:
    import bibtexparser
    db = bibtexparser.parse_string(bib) if hasattr(bibtexparser, 'parse_string') else bibtexparser.loads(bib)
    got = len(db.entries); fail = len(getattr(db, 'failed_blocks', []))
    need(got == n and fail == 0, f'bibtexparser parses {got} entries with {fail} failed blocks')
except ImportError:
    print('skip bibtexparser not installed, own reader used')
print('PASS' if not bad else 'FAILED: %d' % len(bad)); sys.exit(1 if bad else 0)
