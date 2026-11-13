"""build.py -- 'Receipts, Not Verdicts': an AI's own logged misses, each with the wrong read, what the record showed, and the right read.
Sources (all already public or physics-only): the trail's correction log (thetrailtothepast.com), the fuckups list, the run ledger's owned-fuckup entries.
Output: data/receipts.jsonl (one record per miss) and data/pairs.jsonl (prompt / rejected / chosen, for preference training)."""
import html, json, os, re
H = os.path.expanduser('~/bones-forge/')
MODES = [('skipped_the_bonefish', r'bonefish'), ('binary_verdict', r'binary|yes/no|two-lane|chance count|can the .{0,10} stand|graded each error alone|alone as ordinary'),
         ('wrong_ruler', r'ruler|rulers they were not built|method they were built|different fit windows|wrong method|other ruler'),
         ('after_the_fact_label', r'label|post hoc|after the fact|chosen .{0,30}because|picked on looks|cheap match|nearest'),
         ('floor_as_judge', r'shuffle|floor|pure noise|noise shrinkage'), ('miscount_or_scope', r'counted|miscount|\b121\b|one key|one chip|five chips'),
         ('instrument_not_testing_the_claim', r'never waited|unfenced|timed only|did not test|not tested by this run|edge|dropped scraps'),
         ('unmeasured_claim', r'never measured|cited for weeks|toy|from a toy'), ('wrong_statistic', r'per qubit|per bit|mean over|middle bit|median'),
         ('overclaim', r'proves?|confirmed|universal|exactly|too small|too wide')]
def mode(t):
    for m, p in MODES:
        if re.search(p, t, re.I): return m
    return 'other'
clean = lambda s: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
recs = []
# 1. trail corrections
t = open(H + 'trail-site/corrections.html', encoding='utf-8').read(); day = ''
for part in re.split(r'(<h2 class="day">.*?</h2>)', t):
    m = re.match(r'<h2 class="day">(.*?)</h2>', part)
    if m: day = clean(m.group(1)); continue
    for a in re.findall(r'<article>(.*?)</article>', part, re.S):
        title = clean(re.search(r'<h3>(.*?)</h3>', a, re.S).group(1)); dd = [clean(x) for x in re.findall(r'<dd>(.*?)</dd>', a, re.S)]
        if len(dd) < 3: continue
        recs.append({'source': 'trail correction log', 'date': day, 'title': title, 'wrong_read': dd[0], 'record_showed': dd[1], 'right_read': dd[2], 'receipt': 'https://thetrailtothepast.com'})
# 2. the fuckups list
f = open(H + 'parallax/darkwave_disco/for_indahl_ai/fuckups/THE_FUCKUPS.md', encoding='utf-8').read(); sec = ''
for line in f.split('\n'):
    if line.startswith('## '): sec = line[3:].strip(); continue
    m = re.match(r'\d+\. \*\*(.+?)\*\*\s*(.*)', line)
    if m: recs.append({'source': 'fuckups list', 'date': sec, 'title': m.group(1).rstrip('.'), 'wrong_read': m.group(1).rstrip('.'), 'record_showed': m.group(2).strip(), 'right_read': '', 'receipt': 'fuckups list, ' + sec})
# 3. the ledger's owned fuckups
L = open(H + 'parallax/THIRD_RUNG_20260928.md', encoding='utf-8').read()
for e in re.split(r'\n(?=§\d+ )', L):
    n = re.match(r'§(\d+) ([^(\n]+)', e)
    if not n or 'FUCKUP' not in e: continue
    i = e.index('FUCKUP'); body = re.sub(r'\s+', ' ', e[i:i + 900]); body = re.sub(r'^FUCKUPS?,? (owned)?:?\s*', '', body).replace('indahl.ai', 'our site')
    recs.append({'source': 'run ledger', 'date': '§' + n.group(1), 'title': n.group(2).strip().rstrip(':'), 'wrong_read': body.split('. ')[0], 'record_showed': body, 'right_read': '', 'receipt': 'run ledger §' + n.group(1)})
for k, r in enumerate(recs, 1):
    r['id'] = f'R{k:03d}'; r['failure_mode'] = mode(' '.join([r['title'], r['wrong_read'], r['record_showed']]))
os.makedirs('data', exist_ok=True)
with open('data/receipts.jsonl', 'w') as o:
    for r in recs: o.write(json.dumps({k: r[k] for k in ('id', 'source', 'date', 'title', 'failure_mode', 'wrong_read', 'record_showed', 'right_read', 'receipt')}, ensure_ascii=False) + '\n')
pairs = [r for r in recs if r['right_read']]
with open('data/pairs.jsonl', 'w') as o:
    for r in pairs:
        o.write(json.dumps({'id': r['id'], 'prompt': f"A result came back: {r['title']}. Report it.", 'rejected': r['wrong_read'], 'chosen': f"{r['record_showed']} {r['right_read']}".strip(), 'failure_mode': r['failure_mode']}, ensure_ascii=False) + '\n')
import collections
print(len(recs), 'records,', len(pairs), 'pairs', dict(collections.Counter(r['failure_mode'] for r in recs)), dict(collections.Counter(r['source'] for r in recs)))
