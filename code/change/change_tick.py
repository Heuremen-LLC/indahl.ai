#!/usr/bin/env python3
"""change_tick.py: CHANGE rider per PLAN.md. Reads the vendors' deprecation pages, keeps every snapshot, logs every change, publishes KV change_live.
CHANGE_SUMMARY_ONLY=1 rebuilds the summary from stored data. CHANGE_FIXTURES=1 saves the fetched pages as parser fixtures (first run only)."""
import os, sys, re, json, time, datetime as D, statistics as S, collections as C, subprocess, fcntl, urllib.request
from html.parser import HTMLParser
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/snapshots', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('change: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('change: another run holds the lock'); sys.exit(0)
UA = 'heuremen-change/0.1 (+https://indahl.ai/change)'; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); SUMMARY_ONLY = bool(os.environ.get('CHANGE_SUMMARY_ONLY'))
SRC = {'Anthropic': 'https://platform.claude.com/docs/en/about-claude/model-deprecations', 'OpenAI': 'https://developers.openai.com/api/docs/deprecations',
       'Google': 'https://ai.google.dev/gemini-api/docs/deprecations', 'Cloudflare': 'https://developers.cloudflare.com/deprecations/'}
MON = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}
# 30 Oct (site pass I-1): OpenAI writes Dec 11, 2026 and Nov 30, 2026 with three-letter months and some dates with a non-breaking hyphen. The full names alone dropped those rows, so the three-letter forms and the Unicode hyphens are read too (PLAN.md, Addendum 3).
MON.update({m[:3]: n for m, n in list(MON.items())}); MON['sept'] = 9
def pdate(s):
    s = re.sub('[\u2010-\u2015\u2212]', '-', (s or '').strip())
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m: return '%s-%s-%s' % m.groups()
    m = re.search(r'([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})', s)
    if m and m.group(1).lower() in MON: return '%04d-%02d-%02d' % (int(m.group(3)), MON[m.group(1).lower()], int(m.group(2)))
    return None
class TP(HTMLParser):
    def __init__(s): super().__init__(); s.rows = []; s.cur = None; s.cell = None
    def handle_starttag(s, t, a):
        if t == 'tr': s.cur = []
        if t in ('td', 'th'): s.cell = ''
    def handle_endtag(s, t):
        if t in ('td', 'th') and s.cell is not None and s.cur is not None: s.cur.append(re.sub(r'\s+', ' ', s.cell).strip()); s.cell = None
        if t == 'tr' and s.cur: s.rows.append(s.cur); s.cur = None
    def handle_data(s, d):
        if s.cell is not None: s.cell += d
def rows_of(t): p = TP(); p.feed(t); return p.rows
def parse(vendor, t):
    out = {}
    def put(name, dep, shut, tent=False, rel=None):
        if not name: return
        out[vendor + '|' + name] = dict(vendor=vendor, name=name, deprecated=dep, shutdown=shut, tentative=tent, released=rel)
    if vendor == 'Anthropic':
        for r in rows_of(t):
            if len(r) == 4 and r[0] != 'API model name' and re.match(r'^[a-z0-9.\-]+$', r[0]):
                put(r[0], pdate(r[2]), pdate(r[3]), bool(re.search(r'not sooner', r[3], re.I)))
            elif len(r) >= 3 and pdate(r[0]) and re.match(r'^[a-z0-9.\-]+$', r[1]): put(r[1], None, pdate(r[0]))
    elif vendor == 'OpenAI':
        mode = None   # 30 Oct (site pass I-1): a "Date | Update" table lists dated events, not shutdowns. Only a row whose text says shut down carries a shutdown date, a row that says announced carries a deprecation date, any other event keeps no date.
        for r in rows_of(t):
            if r[:2] == ['Date', 'Update']: mode = 'update'; continue
            if r and r[0] == 'Shutdown date': mode = 'shutdown'; continue
            if len(r) >= 2 and pdate(r[0]):
                if mode == 'update':
                    if re.search(r'shut ?down', r[1], re.I): put(r[1][:160], None, pdate(r[0]))
                    elif re.search(r'announced', r[1], re.I): put(r[1][:160], pdate(r[0]), None)
                    else: put(r[1][:160], None, None)
                else: put(r[1][:160], None, pdate(r[0]))
    elif vendor == 'Google':
        # 2 Nov: Google moved the page to a Markdoc layout ({% table %} blocks with "* cell" lines and "---" row breaks, no HTML tables). Rows are read from those blocks, and the old HTML table reading stays as a fallback.
        rr = rows_of(t)
        for blk in re.findall(r'\{% table %\}(.*?)\{% /table %\}', t, flags=re.S):
            for chunk in re.split(r'\n\s*---\s*\n', blk):
                cells = [re.sub(r'\s+', ' ', c.replace('`', '')).strip() for c in re.findall(r'^\s*\* (.*)$', chunk, flags=re.M)]
                if cells: rr.append(cells)
        for r in rr:
            if len(r) >= 3 and r[0] != 'Model' and re.match(r'^[a-z0-9.\-_/]+$', r[0]): put(r[0], None, pdate(r[2]), rel=pdate(r[1]))
    elif vendor == 'Cloudflare':
        x = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S); x = re.sub(r'<[^>]+>', '|', x); x = re.sub(r'[|\s]*\|[|\s]*', '|', x)
        parts = x.split('|'); 
        for i, p in enumerate(parts):
            if p.startswith('Deprecation date:'):
                title = parts[i - 1] if i else ''; e = next((q for q in parts[i + 1:i + 4] if q.startswith('End of life date:')), '')
                put(title[:160], pdate(p), pdate(e))
    return out
def fetch(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=90); return r.read().decode('utf8', 'replace')
# 29 Oct (internal audit): the plan's fixture gate. Each saved page must still parse to the row count and the three named rows recorded when the plan was written, or the pass stops.
FIXOK = True
if not SUMMARY_ONLY:
    ex = json.load(open('fixtures/EXPECTED.json')) if os.path.exists('fixtures/EXPECTED.json') else None
    fx = {v: parse(v, open('fixtures/%s.html' % v).read()) for v in SRC if os.path.exists('fixtures/%s.html' % v)}
    if ex is None: json.dump({v: dict(rows=len(g), names=sorted(g)[:3]) for v, g in fx.items()}, open('fixtures/EXPECTED.json', 'w'), indent=1)
    else: FIXOK = all(v in fx and len(fx[v]) >= ex[v]['rows'] and all(n in fx[v] for n in ex[v]['names']) for v in ex)
    if not FIXOK: print('change: the parser no longer reads the saved fixtures, stopping'); sys.exit(0)
today = D.datetime.now(D.timezone.utc).date().isoformat(); now = time.time()
store = json.load(open('data/rows.json')) if os.path.exists('data/rows.json') else {'first_snapshot': today, 'rows': {}, 'parser': 2}
ok = True; snap = {}
# 30 Oct (site pass I-1, PLAN.md Addendum 3): one-time repair of the store after the month-name fix. Rows the old parser missed or misread are set from the pages as saved at the first reading on 29 Oct (fixtures/), so they enter as part of the first reading and no NEW or date-change line is written for them. Any later difference from the live page is logged as usual.
if not SUMMARY_ONLY and store.get('parser', 1) < 2 and store['rows']:
    for v in SRC:
        if not os.path.exists('fixtures/%s.html' % v): continue
        for k, r in parse(v, open('fixtures/%s.html' % v).read()).items():
            o = store['rows'].get(k)
            if o is None: store['rows'][k] = dict(r, first_seen=store['first_snapshot'], present=True, history=[[store['first_snapshot'], r['shutdown']]])
            elif len(o['history']) == 1 and (o['shutdown'], o['deprecated']) != (r['shutdown'], r['deprecated']): o.update(shutdown=r['shutdown'], deprecated=r['deprecated'], history=[[store['first_snapshot'], r['shutdown']]])
    store['parser'] = 2
if not SUMMARY_ONLY:
    for v, u in SRC.items():
        try:
            t = fetch(u); fx = 'fixtures/%s.html' % v
            if os.environ.get('CHANGE_FIXTURES') or not os.path.exists(fx): open(fx, 'w').write(t)
            got = parse(v, t); prev = [k for k, r in store['rows'].items() if r['vendor'] == v and r.get('present')]
            if prev and len(got) < 0.8 * len(prev): print('change: parser for', v, 'returned', len(got), 'of', len(prev), '- stopping'); ok = False; break
            if len(got) == 0: print('change:', v, 'returned no rows - stopping'); ok = False; break
            snap.update(got)
        except Exception as e: print('change: fetch failed for', v, type(e).__name__); ok = False; break
    if not ok: print('change: the pass stopped, publishing nothing'); sys.exit(0)
    if ok:
        json.dump(snap, open('data/snapshots/%s.json' % time.strftime('%Y%m%dT%H%MZ', time.gmtime(now)), 'w'))
        ch = open('data/changes.jsonl', 'a'); first_run = not store['rows']
        for k, r in snap.items():
            o = store['rows'].get(k)
            if o is None:
                store['rows'][k] = dict(r, first_seen=today, present=True, history=[[today, r['shutdown']]])
                if not first_run: ch.write(json.dumps(dict(t=today, kind='NEW', key=k, shutdown=r['shutdown'], deprecated=r['deprecated'])) + '\n')
                continue
            if not o.get('present'): o['present'] = True
            if o['shutdown'] != r['shutdown']:
                kind = 'DATE_ADDED' if not o['shutdown'] else ('MOVED_LATER' if r['shutdown'] and r['shutdown'] > o['shutdown'] else ('MOVED_EARLIER' if r['shutdown'] else 'DATE_REMOVED'))
                ch.write(json.dumps(dict(t=today, kind=kind, key=k, old=o['shutdown'], new=r['shutdown'])) + '\n'); o['history'].append([today, r['shutdown']]); o['shutdown'] = r['shutdown']
            o['deprecated'] = r['deprecated'] or o['deprecated']; o['tentative'] = r['tentative']; o['released'] = r.get('released') or o.get('released')
        for k, o in store['rows'].items():
            if o.get('present') and k not in snap and o['vendor'] in {r['vendor'] for r in snap.values()}:
                o['present'] = False; o['removed_on'] = today; ch.write(json.dumps(dict(t=today, kind='REMOVED', key=k, shutdown=o['shutdown'], early=bool(o['shutdown'] and today < o['shutdown']))) + '\n')
        store['last_pass'] = time.strftime('%d %b %H:%M', time.gmtime(now)); ch.close(); json.dump(store, open('data/rows.json.tmp', 'w')); os.replace('data/rows.json.tmp', 'data/rows.json')
rows = list(store['rows'].values()); td = D.date.fromisoformat(today); first = store['first_snapshot']
def days(a, b): return (D.date.fromisoformat(b) - D.date.fromisoformat(a)).days
upcoming = sorted([r for r in rows if r.get('present') and r['shutdown'] and 0 <= days(today, r['shutdown']) <= 60], key=lambda r: r['shutdown'])
notice = {}
for r in rows:
    if r.get('present') and r['deprecated'] and r['shutdown'] and not r['tentative']: notice.setdefault(r['vendor'], []).append(days(r['deprecated'], r['shutdown']))
lrows = [r for r in rows if r.get('present') and r.get('released') and r['shutdown'] and not r['tentative']]
def life_of(rs):
    x = [days(r['released'], r['shutdown']) for r in rs]; m = S.median(x)
    return dict(n=len(x), median=int(m) if m == int(m) else m, shortest=min(x), under180=len([y for y in x if y < 180]), share=round(len([y for y in x if y < 180]) / len(x), 3))
# 30 Oct (site pass I-2): on 30 Oct the Google rows that ran under six months were all names with "preview" in them, so the lifespan table shows those apart from the other names. The key 'Google' stays the sum of both.
lifespan = {}
if lrows:
    lifespan['Google'] = life_of(lrows)
    pv = [r for r in lrows if 'preview' in r['name'].lower()]; ot = [r for r in lrows if 'preview' not in r['name'].lower()]
    if pv: lifespan['Google, names with preview'] = life_of(pv)
    if ot: lifespan['Google, other names'] = life_of(ot)
nrows = {v: dict(n=len(x), median=int(S.median(x)), shortest=min(x), under30=len([y for y in x if y < 30]), share=round(len([y for y in x if y < 30]) / len(x), 3)) for v, x in notice.items() if x}
chg = [json.loads(l) for l in open('data/changes.jsonl')] if os.path.exists('data/changes.jsonl') else []
kinds = C.Counter(c['kind'] for c in chg)
# the test: stated, non-tentative shutdown dates that passed after the first snapshot
tested = [r for r in rows if r['shutdown'] and not r['tentative'] and first < r['shutdown'] <= today and r['first_seen'] <= r['shutdown']]
def state(r):
    if not r.get('present') and r.get('removed_on') and r['removed_on'] < r['shutdown']: return 'REMOVED_EARLY'
    return 'HELD' if len({h[1] for h in r['history']}) == 1 else 'MOVED'
cnt = C.Counter(state(r) for r in tested); nh = cnt['MOVED'] + cnt['REMOVED_EARLY']; lo, hi = K.wilson(nh, len(tested))
oc = K.CANNOT_TELL if len(tested) < 30 else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
byv = C.Counter(r['vendor'] for r in rows if r.get('present'))
out = dict(updated=store.get('last_pass') or time.strftime('%d %b %H:%M', time.gmtime(now)), first_snapshot=first, rows=len(rows), sources=[dict(vendor=v, rows=byv[v], url=SRC[v]) for v in SRC],
           test=dict(of=len(tested), held=cnt['HELD'], moved=cnt['MOVED'], removed_early=cnt['REMOVED_EARLY'], share=round(nh / len(tested), 4) if tested else None, share_lo=round(lo, 4) if tested else None, share_hi=round(hi, 4) if tested else None, outcome=oc),
           upcoming=[dict(vendor=r['vendor'], url=SRC[r['vendor']], item=r['name'], shutdown=r['shutdown'] + (' (not sooner than)' if r['tentative'] else ''), days_left=days(today, r['shutdown']), deprecated=r['deprecated'] or '', notice=days(r['deprecated'], r['shutdown']) if r['deprecated'] else None) for r in upcoming],
           notice={v: x for v, x in nrows.items()}, lifespan=lifespan, changes={k: dict(n=n) for k, n in sorted(kinds.items())},
           change_list=[dict(url=SRC[c['key'].split('|')[0]], date=c['t'], kind=c['kind'], item=c['key'].split('|', 1)[1], vendor=c['key'].split('|')[0], was=c.get('old') or c.get('shutdown') or '', now=c.get('new') or '', note=hc.get(c['key'] + '|' + c['t'], '')) for c in chg[-40:][::-1]])
json.dump(out, open('summary_change.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'change_live', '--path', os.path.join(H, 'summary_change.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('change:', len(rows), 'rows;', dict(byv), 'changes', dict(kinds), 'test n', len(tested), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
