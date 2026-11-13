#!/usr/bin/env python3
"""activity_check.py: tick-bus rider (every tick). Finds which public desks are being read or evaluated right now, or finished in the last 10 minutes,
and publishes the list of desk names (nothing else) to the KV key 'activity', read by indahl.ai/activity.json for the LIVE tags on the pages."""
import os, re, json, time, subprocess, hashlib, glob
B = os.path.expanduser('~/bones-forge'); W = B + '/cloudflare-workers/heuremen-door'; NS = 'ecb59d96b07c43bdac14271687eae5af'
MAP = {'caca_index': 'cada', 'bts_index': 'airline', 'status_index': 'uptime', 'qia_queue': 'qia', 't1t2_check': 'qia', 'iris_index': 'iris', 'oy_index': 'oy', 'model_index': 'model', 'coin_index': 'coin', 'launch_index': 'launch'}
SLUGS = {'tape', 'hosts', 'oldest', 'qia', 'iris', 'oy', 'atlas', 'hermes', 'stack', 'time', 'coin', 'cada', 'uptime', 'forecast', 'cadence', 'trials', 'launch', 'linkrot', 'arxivdrift', 'support', 'pkglicense', 'pkginstall', 'hflicense', 'hfsize', 'change', 'secrecords', 'seat', 'revise', 'fedsep', 'hpt', 'airline', 'weights', 'ailuminate', 'airq', 'campus', 'model'}
now = time.time(); live = {}
ps = subprocess.run(['ps', '-axo', 'etime=,command='], capture_output=True, text=True).stdout
def _secs(e):   # ps etime: [[dd-]hh:]mm:ss
    d, _, hms = e.rpartition('-'); p = [int(x) for x in hms.split(':')]
    while len(p) < 3: p.insert(0, 0)
    return (int(d) if d else 0) * 86400 + p[0] * 3600 + p[1] * 60 + p[2]
_lines = []
for _l in ps.split('\n'):
    _e, _, _c = _l.strip().partition(' ')
    try: _age = _secs(_e)
    except ValueError: continue
    # 31 Oct 2026 (his "these all say live, are they doing something that looks live?"): a rider that only checks whether its pass is due
    # exits within seconds; it was being tagged "being read now". A process counts as reading only once it has run 45 seconds.
    if _age >= 45: _lines.append(_c.strip())
for line in _lines:
    m = re.search(r'/bones-forge/([A-Za-z0-9_]+)/[^ ]+\.(py|sh)\b', line)
    d = m.group(1) if m else None
    if d and ('_tick' in line or '_collect' in line or 'run_' in line or d.endswith('_index') or d in MAP):
        slug = MAP.get(d, d.replace('_index', ''))
        if slug in SLUGS: live[slug] = 'evaluating' if d == 'iris_index' else 'reading'
    if 'mlx_lm' in line and ' lora' in line: live['iris'] = 'training'
    elif 'mlx_lm' in line and ('evaluate' in line or 'train' in line): live.setdefault('iris', 'evaluating')
    if re.search(r'(^|/)(weights_tick|campus_tick|ailuminate_tick|oldest_tick|airq_tick|airq_live_tick|nas_tick)\.py', line):
        s = re.search(r'(\w+)_tick\.py', line).group(1); s = {'airq_live': 'airq', 'nas': 'airline'}.get(s, s)
        if s in SLUGS: live[s] = 'reading'
# 30 Oct 2026 (his 'live is live'): an IRIS eval or training run counts as live only if its output moved in the last 30 minutes.
# A process that exists but has stopped writing is not live (Guard 32: liveness by recent completed work, never by a running process).
if live.get('iris') in ('evaluating', 'training'):
    _moved = [f for f in glob.glob(B + '/iris_index/**/*.log', recursive=True) + glob.glob(B + '/iris_index/**/*.jsonl', recursive=True) + glob.glob(B + '/yo/*.log') + glob.glob(B + '/yo/*.out') if now - os.path.getmtime(f) < 1800 and '/seats/' not in f]   # 31 Oct: YO v2 writes in yo/   # the model server's own log moves on any request, not a run
    if not _moved: del live['iris']
# a corner that finished in the last 10 minutes
for lg in glob.glob(B + '/*_index/data/last_run*.log') + glob.glob(B + '/*_index/summary_*.json') + glob.glob(B + '/qia_queue/data/*.jsonl') + glob.glob(B + '/qia_mirror/*.json') + glob.glob(B + '/*_index/history.jsonl'):
    try:
        if now - os.path.getmtime(lg) < 600:
            d = lg.split('/bones-forge/')[1].split('/')[0]; slug = MAP.get(d, d.replace('_index', ''))
            if slug in SLUGS: live.setdefault(slug, 'just read')
    except OSError: pass
# 30 Oct 2026 (his "weights is live but has no live tag"): a desk is also live while its public feed is current within its own limit (the
# same feed list and limits the watch uses, nodes_repo/drift/targets.json). A desk whose feed goes stale loses the tag. Feeds are read from the
# live site, at most every 10 minutes (cache in watch/activity_feeds.json).
import urllib.request as _ur, datetime as _D
def _stamp(d, sk):
    for k in (sk.split('.') if sk else []): d = d.get(k) if isinstance(d, dict) else None
    v = d if isinstance(d, str) else ((d.get('updated') or d.get('read')) if isinstance(d, dict) else None)
    if not isinstance(v, str): return None
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})', v)
    if m: return _D.datetime(*map(int, m.groups()), tzinfo=_D.timezone.utc).timestamp()
    m = re.match(r'(\d{1,2}) ([A-Za-z]{3}) (\d{2}):(\d{2})', v)
    if m:
        n = _D.datetime.now(_D.timezone.utc); mo = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'].index(m.group(2).lower()) + 1
        t = _D.datetime(n.year, mo, int(m.group(1)), int(m.group(3)), int(m.group(4)), tzinfo=_D.timezone.utc)
        return (t if t <= n + _D.timedelta(hours=1) else t.replace(year=n.year - 1)).timestamp()
    return None
_FC = B + '/watch/activity_feeds.json'
try: _fc = json.load(open(_FC))
except Exception: _fc = {}
if now - _fc.get('t', 0) > 600:
    _T = json.load(open(B + '/nodes_repo/drift/targets.json')); _sk = _T.get('stamps', {}); _fresh = {}; _read = {}; _every = {}
    for _f, _lim in _T['feeds']:
        _slug = _f.split('/')[0]
        if '/' not in _f or _slug not in SLUGS: continue
        try:
            _d = json.loads(_ur.urlopen(_ur.Request('https://indahl.ai/%s?a=%d' % (_f, now), headers={'User-Agent': 'heuremen-activity/0.1'}), timeout=20).read())
            _ts = _stamp(_d, _sk.get(_f))
        except Exception: _ts = None
        _ok = _ts is not None and (now - _ts) / 3600 <= float(_lim)
        _fresh[_slug] = _fresh.get(_slug, True) and _ok   # a desk with several feeds (qia) is current only if all of them are
        # 31 Oct 2026 (his "these all say live, are they doing something that looks live?"): keep when each desk was last read and its
        # limit, so the page can say "read 3 h ago" instead of a bare "live". A desk with several feeds gets its oldest stamp and longest limit.
        if _ts is not None:
            # 1 Nov: the desk was last read when ANY of its feeds last updated (newest stamp), to pair like for like with the fastest rider's
            # schedule shown beside it; each feed's own staleness stays in _fresh above. (Oldest stamp against fastest schedule warned falsely.)
            _read[_slug] = max(_read.get(_slug, _ts), _ts); _every[_slug] = max(_every.get(_slug, 0.0), float(_lim))
    _fc = {'t': now, 'fresh': _fresh, 'read': _read, 'every': _every}
    try: json.dump(_fc, open(_FC, 'w'))
    except Exception: pass
# 31 Oct 2026: riders write their run log on every tick, also when the pass is not due, so a fresh log alone is not a read. "just read"
# stands only when the desk's own public feed stamp is under 20 minutes old; otherwise the desk shows its last read time (if current).
for _slug in list(live):
    _rs = (_fc.get('read') or {}).get(_slug)
    if live[_slug] == 'just read' and _rs is not None and now - _rs > 1200:
        if (_fc.get('fresh') or {}).get(_slug): live[_slug] = 'on schedule'
        else: del live[_slug]
for _slug, _ok in (_fc.get('fresh') or {}).items():
    if _ok: live.setdefault(_slug, 'on schedule')
import ast as _ast
_src = open(B + '/indahl-ai/build_site.py').read(); _m = re.search(r'^HOME = (\{.*?\})\n', _src, flags=re.S | re.M)
HOME = {k.strip('/'): v.strip('/') for k, v in _ast.literal_eval(_m.group(1)).items()}
HOME.update({'hermes': 'hermes', 'iris': 'iris', 'atlas': 'atlas', 'oy': 'oy', 'qia': 'qia', 'model': 'hermes'})
def label(m): return 'live' if m in ('reading', 'just read') else (None if m == 'on schedule' else ('train' if m == 'training' else 'eval'))
divs = {}
for slug, mode in live.items():
    dv = HOME.get(slug)
    if not dv or label(mode) is None: continue   # 31 Oct: a division says live only while one of its desks is being read or was just read
    cur = divs.get(dv)
    if cur is None or (cur != 'live' and label(mode) == 'live') or (cur == 'eval' and label(mode) == 'train'): divs[dv] = label(mode)
# 31 Oct 2026 (his "anything that we label live should look live"): each desk's schedule, from its rider's interval on the tick bus times the
# median tick length of the last 60 ticks, so the page can show a clock and a bar filling toward the next scheduled read.
_sched = {}
try:
    import statistics as _st
    # 3 Nov 2026: tick_bus writes a caught-up cycle as '<c> none none ...' (tick 25306, ~21:05 UTC); float('none') raised, the except below
    # swallowed it, and every_min went out empty for every desk (watch BAD "no clock or schedule"). Skip rows whose clock field is not a number.
    _tt = []
    for l in open(B + '/watch/ticks.log').read().splitlines()[-60:]:
        try: _tt.append(float(l.split()[3]))
        except (IndexError, ValueError): pass
    _tick = _st.median([b - a for a, b in zip(_tt, _tt[1:])]) / 60
    for _line in open(B + '/watch/tick_bus.py').read().splitlines():
        if _line.strip().startswith('#'): continue
        _m = re.search(r"\((\d+),\s*\[.*?expanduser\('~/bones-forge/([A-Za-z0-9_]+)/[^']+'\)\]", _line)
        if not _m: continue
        _d = _m.group(2); _sl = {'qia_mirror': 'qia', **MAP}.get(_d, _d.replace('_index', ''))
        if _sl in SLUGS: _sched[_sl] = min(_sched.get(_sl, 1e9), round(int(_m.group(1)) * _tick))
except Exception as _e: print('activity: schedule not computed:', type(_e).__name__, _e)   # never silent again
_rd = {k: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(v)) for k, v in (_fc.get('read') or {}).items() if k in live}
_ev = {k: v for k, v in (_fc.get('every') or {}).items() if k in live}
out = dict(updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)), live=live, divisions=divs, read=_rd, every=_ev, every_min={k: v for k, v in _sched.items() if k in live})
fp = hashlib.sha256(json.dumps([live, divs, _rd, _sched], sort_keys=True).encode()).hexdigest()[:16]
st = B + '/watch/activity_state.json'; prev = json.load(open(st)) if os.path.exists(st) else {}
if prev.get('fp') != fp or now - prev.get('t', 0) > 1500:
    p = B + '/watch/activity.json'; json.dump(out, open(p, 'w'))
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'activity', '--path', p, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
    if r.returncode == 0: json.dump(dict(fp=fp, t=now), open(st, 'w'))
    print('activity:', sorted(live), 'published' if r.returncode == 0 else 'publish FAILED')
else: print('activity:', sorted(live), 'unchanged')
