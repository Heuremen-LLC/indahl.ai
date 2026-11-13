"""verify.py (10 Nov 2026): run BEFORE EVERY BATCH of the QIA corporate notices. Re-reads the live QIA pages into a fresh folder and checks
each queued body against them:
  1. every quoted string (notices.json 'quoted') is still on the live /qia page or /qia/list.json, word for word (whitespace folded),
  2. the IBM deviations, Q17 gate table and Braket table have the same rows as when the body was built (row count, every cell),
     so a corrected run count (Q17) or Braket figure (B1/B2) flags the IBM / AWS / Rigetti bodies,
  3. every indahl.ai link in the body answers 200,
  4. each corporate study and List entry quoted is still on the page.
Any failure: the key is written to VERIFY_HOLD.json and listed. send_guarded.py reads PREFLIGHT_HOLD.json only, so verify.py also
merges its holds into PREFLIGHT_HOLD.json (after preflight.py has run, or alone). Fix by rebuilding:
  python3 -I build/scrape_live.py && python3 -I build/collect.py && python3 -I build/build_queue.py && python3 -I verify.py
Options: --keys k1,k2 (check only those), --no-links (skip the link fetches). Read only against the site. Sends nothing."""
import json, os, re, sys, tempfile, urllib.request, html, concurrent.futures as CF
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H + '/build')
import scrape_live
def fold(s): return re.sub(r'\s+', ' ', html.unescape(s)).strip()
tmp = tempfile.mkdtemp(prefix='qcorp_verify_'); scrape_live.main(tmp)
T = json.load(open(tmp + '/qia_tables.json')); L = json.load(open(tmp + '/list.json'))['studies']
OLD = json.load(open(H + '/build/qia_tables.json'))
page_text = fold(' '.join(c['main'] + ' ' + c['text'] for t in T for r in t['rows'] for c in r['cells']))
list_titles = {fold(s['study']) for s in L}; anchors = {s['anchor'] for s in L}
N = {x['key']: x for x in json.load(open(H + '/notices.json'))['notices']}
Qk = [json.loads(l)['key'] for l in open(H + '/queue.jsonl')]
if '--keys' in sys.argv: Qk = [k for k in Qk if k in sys.argv[sys.argv.index('--keys') + 1].split(',')]
def rows(tabs, head):
    t = next((t for t in tabs if t['heading'].startswith(head)), None)
    return [[fold(c['main']) for c in r['cells']] for r in t['rows']] if t else None
changed = {h: rows(T, h) != rows(OLD, h) for h in ('Deviations', 'Gate error', 'Hardware Deviations from Amazon')}
corp_ids = {r['id'] for t in T if t['heading'].startswith('Calibrated Studies: Corporate') for r in t['rows']}
hold = {}
for k in Qk:
    x = N[k]; bad = []
    for q in x['quoted']:
        f = fold(q)
        if f and f not in page_text and f not in list_titles: bad.append('not on live page: ' + f[:90])
    if 'IBM' == x['org'] and (changed['Deviations'] or changed['Gate error']): bad.append('IBM deviations or Q17 gate table changed since build')
    if x['org'] in ('Amazon Web Services', 'Rigetti Computing') and changed['Hardware Deviations from Amazon']: bad.append('Braket table changed since build')
    for rid in x['corp_rows']:
        if rid not in corp_ids: bad.append('corporate row gone: ' + rid)
    for a in x['list_entries']:
        if a in x['studies'] and a not in anchors: bad.append('List entry gone: ' + a)
    if bad: hold[k] = bad
links = sorted({u.rstrip('.,)') for k in Qk for u in re.findall(r'https://indahl\.ai/[^\s]+', N[k]['body'])})
dead = {}
if '--no-links' not in sys.argv:
    def code(u):
        try: return u, urllib.request.urlopen(urllib.request.Request(u.split('#')[0], headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).status
        except Exception as e: return u, str(e)[:60]
    with CF.ThreadPoolExecutor(12) as ex:
        for u, c in ex.map(code, links):
            if c != 200: dead[u] = c
    for k in Qk:
        d = [u for u in dead if u in N[k]['body']]
        if d: hold.setdefault(k, []).extend('link not 200: ' + u for u in d)
json.dump(hold, open(H + '/VERIFY_HOLD.json', 'w'), indent=1)
pf = H + '/PREFLIGHT_HOLD.json'
P = json.load(open(pf)) if os.path.exists(pf) else {}
P = {k: v for k, v in P.items() if not str(v).startswith('verify:')}
P.update({k: 'verify: ' + '; '.join(v)[:300] for k, v in hold.items()})
json.dump(P, open(pf, 'w'), indent=1)
print(f'checked {len(Qk)} bodies against the live pages read {json.load(open(tmp + "/live_read.json"))["read_utc"]}: {len(Qk) - len(hold)} clean, {len(hold)} held | links {(str(len(links)) + " checked, " + str(len(dead)) + " not 200") if "--no-links" not in sys.argv else "skipped"} | tables changed since build: {[h for h, v in changed.items() if v] or "none"}')
for k, v in hold.items(): print('  HOLD', k, v[:3])
