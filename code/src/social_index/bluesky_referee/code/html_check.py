"""Referee page check: every number in section_bluesky.html against the referee recount, and the copy rules.
Usage: python3 -I html_check.py DESKDIR RECOUNT.json OUT.json"""
import re, json, sys, html, os
d, rc_path, outp = sys.argv[1:4]
page = open(os.path.join(d, 'section_bluesky.html'), encoding='utf-8').read()
desk = json.load(open(os.path.join(d, 'data', 'bsky.json')))
rc = json.load(open(rc_path)); RC = {r['id']: r for r in rc['rows']}
WORD = {'ABOVE': 'above', 'BELOW': 'below', 'CONSISTENT': 'consistent', 'CANNOT_TELL': 'cannot tell', 'NOTHING_RETURNED': 'nothing returned'}
def n(x): return '{:,}'.format(int(x))
def p(x): return '%.2f%%' % (100 * x)
out = dict(table=[], diffs=[], copy=[])
# main table rows: 5 cells
trs = re.findall(r'<tr><td>(.*?)</td><td class="n">(.*?)</td><td class="n">(.*?)</td><td class="n">(.*?)</td><td>(.*?)</td></tr>', page)
what2id = {r['what']: r['id'] for r in desk['rows']}
for what, stated, deliv, rng, oc in trs:
    what = html.unescape(what); rid = what2id.get(what)
    r = RC.get(rid)
    if r is None: out['diffs'].append(dict(row=what, issue='no recount row')); continue
    if r.get('delivered') is None: want = ('not in the stream', '', 'cannot tell')
    elif rid.startswith('share'): want = (p(r['delivered']), '%s to %s' % (p(r['interval'][0]), p(r['interval'][1])), WORD[r['outcome']])
    else: want = (n(r['delivered']), '%s to %s' % (n(r['interval'][0]), n(r['interval'][1])), WORD[r['outcome']])
    got = (html.unescape(deliv), html.unescape(rng), html.unescape(oc))
    out['table'].append(dict(id=rid, stated=html.unescape(stated), page=got, referee=want, equal=got == want))
    if got != want: out['diffs'].append(dict(row=rid, page=got, referee=want))
# every number on the page, as a list, for the report
text = html.unescape(re.sub(r'<[^>]+>', ' ', page))
out['numbers_on_page'] = re.findall(r'\d[\d,]*(?:\.\d+)?%?', text)
# copy rules
body = re.sub(r'<(svg|code)[^>]*>.*?</\1>', ' ', page, flags=re.S)
vis = html.unescape(re.sub(r'<[^>]+>', ' ', body))
if ';' in vis: out['copy'].append('semicolon in visible text: ' + ' | '.join(m.group(0) for m in re.finditer(r'.{0,60};.{0,60}', vis)))
for h in re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', page):
    if re.search(r'\d', h): out['copy'].append('digit in heading: ' + h)
for w in (r'\bAI\b', r'Claude', r'artificial intelligence', r'language model', r'\bbecause\b', r'\bdue to\b', r'\bcaused?\b', r'\bdriven by\b', r'\bsince\b', r'\bso\b', r'\bwhy\b'):
    for m in re.finditer(w, vis): out['copy'].append('word %s: ...%s...' % (w, vis[max(0, m.start() - 80):m.end() + 80].strip()))
json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
print('rows', len(out['table']), 'diffs', len(out['diffs']))
for x in out['diffs']: print(x)
for x in out['copy']: print('COPY', x)
