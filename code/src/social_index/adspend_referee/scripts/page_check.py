# Checks every number in section_adspend.html against summary_adspend.json and data/adspend.json. Prints problems or "none".
# Run after every tick: python3 -I page_check.py [path to the adspend folder]
import re, sys, json, html, collections as C
A = sys.argv[1] if len(sys.argv) > 1 else '/Users/heuremen/bones-forge/social_index/adspend'
H = open(A + '/section_adspend.html').read(); S = json.load(open(A + '/summary_adspend.json')); Bj = json.load(open(A + '/data/adspend.json'))
cyc = [r for r in Bj['rows'] if r['level'] == 'cycle']; by = C.defaultdict(list)
for r in cyc: by[(r['committee_id'], r['cycle'])].append(r)
text = html.unescape(re.sub(r'<[^>]+>', ' ', H)); problems = []
if ';' in text: problems.append(('semicolon in rendered text', text.count(';')))
n = lambda s: int(s.replace(',', '').replace('$', ''))
mg = S['match_gate']; cnt = mg['counts']; sp = mg['stated_spend']; f = mg['unmatched_public_id_forms']
exp = [S['google']['us_advertisers'], cnt.get('A_id', 0) + cnt.get('A_candidate_id', 0) + cnt.get('B_name', 0), cnt.get('A_id', 0) + cnt.get('A_candidate_id', 0), cnt.get('B_name', 0),
       sum(v for k, v in cnt.items() if k.startswith('unmatched')), round(sum(v for k, v in sp.items() if k.startswith('unmatched'))), f.get('EIN', 0) + f.get('state registration', 0), f.get('empty', 0)]
m = re.search(r'Of the ([\d,]+) US advertisers.*?, ([\d,]+) matched an FEC committee: ([\d,]+) through.*?and ([\d,]+) through a name.*?The other ([\d,]+) did not match and carry \$([\d,]+).*?Of those, ([\d,]+) list only.*?and ([\d,]+) list no ID', text, re.S)
if not m or [n(x) for x in m.groups()] != exp: problems.append(('match paragraph', exp, m.groups() if m else None))
for c in ('2020', '2022', '2024', '2026'):
    mm = re.search(r'<tr><td>%s</td>((?:<td class="n">[\d,]+</td>){5})</tr>' % c, H)
    vals = [n(x) for x in re.findall(r'>([\d,]+)<', mm.group(1))] if mm else None
    k = S['outcomes']['cycle_rows'][c]; d = C.Counter(r['outcome'] for r in cyc if r['cycle'] == int(c))
    for e in ([k[x] for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED')], [d[x] for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED')]):
        if vals != e: problems.append(('cycle table', c, e, vals))
OUT = {'Above': 'ABOVE', 'Below': 'BELOW', 'Consistent': 'CONSISTENT', 'Cannot tell': 'CANNOT_TELL', 'Nothing returned': 'NOTHING_RETURNED'}
def money(s):
    s = html.unescape(s); v = int(re.sub(r'[^\d]', '', s)); return -v if s.startswith('−') else v
rows = re.findall(r'<tr><td>(.*?)</td><td>(\d{4})</td><td class="n">(.*?)</td><td class="n">(.*?) to (.*?)</td><td class="n">(.*?) to (.*?)</td><td class="n">(.*?)</td><td>(.*?)</td></tr>', H)
for r in rows:
    cid = re.search(r'<span class="by">(C\d{8})</span>', r[0]).group(1); cands = by.get((cid, int(r[1])), [])
    if len(cands) != 1: problems.append(('row lookup', cid, r[1], len(cands))); continue
    d = cands[0]
    for nm, a, b in (('G', money(r[2]), round(d['google']['stated_in_window'])), ('G_lo', money(r[3]), round(d['google']['lo'])), ('G_hi', money(r[4]), round(d['google']['hi'])),
                     ('D_lo', money(r[5]), round(d['fec']['d_lo'])), ('D_hi', money(r[6]), round(d['fec']['d_hi'])), ('pool', money(r[7]), round(d['fec']['pool']))):
        if a != b: problems.append(('cell', cid, r[1], nm, a, b))
    word = re.sub(r'<span.*', '', r[8]).strip(); flags = re.findall(r'<span class="by">(.*?)</span>', r[8])
    if OUT.get(word) != d['outcome']: problems.append(('outcome', cid, r[1], word, d['outcome']))
    if d['outcome'] == 'CANNOT_TELL' and (not flags or flags[0] != d['reason'].split(':')[0]): problems.append(('reason', cid, r[1], flags, d['reason']))
    want = [x for x, on in (('depends on timing', d.get('timing_sensitive')), ('depends on the itemization rule', d.get('unseen_rule_sensitive'))) if on]
    if want != [x for fl in flags for x in fl.split(', ') if x.startswith('depends')]: problems.append(('flags', cid, r[1], want, flags))
    if html.unescape(re.sub(r'<span.*', '', r[0])).strip() != d['committee_name']: problems.append(('name', cid, r[1]))
    if ('matched by name' in r[0]) != (d['tier'] == 'name'): problems.append(('name-tier label', cid, r[1], d['tier']))
print('table rows checked', len(rows)); print('PROBLEMS:', problems if problems else 'none')
