"""verify.py: recounts every file in the OY Data Pack and checks that the CSV files match the original JSON.
Standard library only. Run from anywhere: python verify.py   (it reads the folders next to this file)
Checks for each table: the row count equals the count taken straight from the JSON, every flattened column of every row equals the CSV cell,
and the top-level scalar fields of the first, middle and last record equal the CSV cells. It then recomputes the counts the files state about
each other: the number of institutions listed under each finding, the counts of the list table, and the sentences and course titles of every school."""
import csv, json, os, re, sys, collections
H = os.path.dirname(os.path.abspath(__file__))

def slug(k):
    return re.sub(r'[^A-Za-z0-9]+', '_', str(k)).strip('_')

def flatten(rec, prefix=''):
    out = {}
    for k, v in rec.items():
        name = (prefix + '_' if prefix else '') + slug(k)
        if isinstance(v, dict):
            out.update(flatten(v, name))
        elif isinstance(v, list):
            out[name + '_json'] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
        else:
            out[name] = v
    assert len(out) >= len(rec) or not rec
    return out

def cell(v):
    if v is None: return ''
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, str): return v
    return json.dumps(v)

def flat_meta(d, prefix=''):
    out = {}
    for k, v in d.items():
        name = (prefix + '.' if prefix else '') + str(k)
        if isinstance(v, dict): out.update(flat_meta(v, name))
        elif isinstance(v, list): out[name] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
        else: out[name] = v
    return out

def finding_rows(d):
    return [{k: v for k, v in f.items() if k != 'institutions'} for f in d['findings']]

def finding_institutions(d):
    return [dict({'finding': f['finding']}, **i) for f in d['findings'] for i in f['institutions']]

def school_items(key):
    def rows(d):
        return [{'unitid': s['unitid'], 'school': s['school'], 'state': s['state'], 'item_index': i, 'text': x['text'], 'url': x['url']} for s in d['schools'] for i, x in enumerate(s[key])]
    return rows

# name: (json file, rows(d), independent row count(d))
TABLES = {
    'oy_chatbot_citations': ('oy_chatbot_citations.json', lambda d: d['rows'], lambda d: len(d['rows'])),
    'oy_findings': ('oy_findings.json', finding_rows, lambda d: len(d['findings'])),
    'oy_finding_institutions': ('oy_findings.json', finding_institutions, lambda d: sum(len(f['institutions']) for f in d['findings'])),
    'oy_list': ('oy_list.json', lambda d: d['rows'], lambda d: len(d['rows'])),
    'oy_schools': ('oy_schools.json', lambda d: d['schools'], lambda d: len(d['schools'])),
    'oy_school_sentences': ('oy_schools.json', school_items('sentences'), lambda d: sum(len(s['sentences']) for s in d['schools'])),
    'oy_school_course_titles': ('oy_schools.json', school_items('course_titles'), lambda d: sum(len(s['course_titles']) for s in d['schools'])),
}
META = {'oy_text': ('oy_text.json', None)}   # every key of the file goes to oy_text_meta.csv as key,value rows

def eq(csv_val, v):
    if v is None or v == '': return csv_val == ''
    if isinstance(v, bool): return csv_val == ('true' if v else 'false')
    if isinstance(v, (int, float)): return csv_val != '' and float(csv_val) == float(v)
    return csv_val == v

def read_csv(p):
    with open(p, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def main():
    cache, fails, summary = {}, [], []
    def J(name):
        if name not in cache:
            with open(os.path.join(H, 'json', name), encoding='utf-8') as f: cache[name] = json.load(f)
        return cache[name]
    for t, (jf, rows, count) in TABLES.items():
        d = J(jf); recs = rows(d); n = count(d)
        got = read_csv(os.path.join(H, 'csv', t + '.csv'))
        ok = len(got) == n == len(recs)
        if not ok: fails.append(f'{t}: csv rows {len(got)}, json rows {n}')
        bad = 0
        for i, (r, c) in enumerate(zip(recs, got)):
            for col, v in flatten(r).items():
                if col not in c or not eq(c[col], v):
                    bad += 1
                    if bad < 4: fails.append(f'{t} row {i} column {col}: csv {c.get(col)!r} json {v!r}')
        for i in sorted({0, len(recs) // 2, len(recs) - 1}):
            for k, v in recs[i].items():
                if not isinstance(v, (dict, list)) and not eq(got[i][slug(k)], v): fails.append(f'{t} sample row {i} field {k}: csv {got[i][slug(k)]!r} json {v!r}')
        summary.append(f'{t}.csv: {len(got)} rows, {len(got[0]) if got else 0} columns, {"OK" if ok and not bad else "FAIL"}')
    for ds, (jf, keys) in META.items():
        want = flat_meta(J(jf))
        got = {r['key']: r['value'] for r in read_csv(os.path.join(H, 'csv', ds + '_meta.csv'))}
        bad = [k for k, v in want.items() if k not in got or not eq(got[k], v)]
        if len(got) != len(want) or bad: fails.append(f'{ds}_meta: {len(got)} rows, expected {len(want)}, mismatched {bad[:3]}')
        summary.append(f'{ds}_meta.csv: {len(got)} rows, {"OK" if not bad and len(got) == len(want) else "FAIL"}')
    # the files state counts about each other: recompute them
    n0 = len(fails)
    F = J('oy_findings.json')['findings']; L = J('oy_list.json')['rows']; C = J('oy_chatbot_citations.json')['rows']; S = J('oy_schools.json')['schools']
    for f in F:
        if f['count'] != len(f['institutions']): fails.append(f'finding {f["finding"]!r}: count {f["count"]}, institutions listed {len(f["institutions"])}')
    byname = {f['finding']: f for f in F}
    vc = collections.Counter(r['measures_own_policy'] for r in L)
    for name, label in (('Measured its own policy or tool', 'Measured its own policy or tool'), ('Outcome reported without counts', 'Outcome reported without counts'), ('Plans to measure', 'Plans to measure'),
                        ('Usage or attitude surveys only', 'Usage or attitude surveys only')):
        if byname[name]['count'] != vc[label]: fails.append(f'{name}: finding says {byname[name]["count"]}, the list has {vc[label]}')
    if byname['None found']['count'] != sum(1 for r in L if r['measures_own_policy'].startswith('None found')): fails.append('None found: finding and list differ')
    rc = collections.Counter(r['released_own_data'] for r in L)
    if byname['Released nothing (of 114 read)']['count'] != rc['Nothing'] or byname['Released summary tables or an instrument only (of 114 read)']['count'] != rc['Summary tables or an instrument only']: fails.append('released data counts differ between findings and list')
    if len(C) != byname['Chatbot cited as a source']['count']: fails.append('chatbot rows differ between the table and the finding')
    for f, v in byname.items():
        if v['of'] is not None and v['of'] not in (len(L), rc['Nothing'] + rc['Summary tables or an instrument only']): fails.append(f'{f}: denominator {v["of"]}')
    if len({s['unitid'] for s in S}) != len(S): fails.append('a federal ID repeats in oy_schools.json')
    for s in S:
        m = re.search(r'Showing (\d+) of (\d+)\.', s['sentences_note'])
        want = int(m.group(2)) if m else len(s['sentences'])
        if m and int(m.group(1)) != len(s['sentences']): fails.append(f'{s["unitid"]}: sentences shown differ from the note')
        if s['sentences_total'] is not None and s['sentences_total'] != want: fails.append(f'{s["unitid"]}: sentences_total {s["sentences_total"]}, page lists {want}')
        m = re.search(r'Showing (\d+) of (\d+)\.', s['course_titles_note'])
        want = int(m.group(2)) if m else len(s['course_titles'])
        if m and int(m.group(1)) != len(s['course_titles']): fails.append(f'{s["unitid"]}: course titles shown differ from the note')
        if s['course_titles_total'] is not None and s['course_titles_total'] != want: fails.append(f'{s["unitid"]}: course_titles_total {s["course_titles_total"]}, page lists {want}')
    summary.append(f'cross-checks: findings against list and chatbot rows, sentences and course titles of {len(S)} schools against their totals: {"OK" if len(fails) == n0 else "FAIL"}')
    print('OY Data Pack verification'); print('\n'.join(summary))
    print('JSON files: ' + ', '.join(sorted(os.listdir(os.path.join(H, 'json')))))
    if fails:
        print('FAILURES'); print('\n'.join(fails[:40])); sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main()
