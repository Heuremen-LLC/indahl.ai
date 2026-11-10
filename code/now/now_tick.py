#!/usr/bin/env python3
"""now_tick.py: the NOW rider and scorer (PLAN.md "Rider" and "Readings"). Python 3.9 compatible.
  (default)   due check: every entry whose deadline has passed with no outcome row gets one. Manifold entries are read from the platform.
              Other entries take a reading from data/readings.json (written by Bones with evidence) or get one due row.
              Then verifies the chain, stamps the log if rows were appended, upgrades pending stamps, writes summary_now.json and data/now_live.json.
  --publish   also puts data/now_live.json in the site KV as predictions_live (served at /predictions/live.json)
  --score     scoring only, no network, no rows written
  --selftest  rule checks on planted rows, no network"""
import os, sys, json, time, math, random, subprocess, datetime as D

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import now_log as NL
import heuremen_kit as K

PUB = '--publish' in sys.argv; SCORE_ONLY = '--score' in sys.argv
READINGS = os.path.join(H, 'data', 'readings.json'); FORTUNE = os.path.join(H, 'data', 'fortune.json')
LOGF = os.path.join(H, 'data', 'tick.log'); STALE = []
BINARY = ('RIGHT', 'WRONG', 'CANNOT_TELL'); EVENT = ('HAPPENED', 'DID_NOT_HAPPEN', 'CANNOT_TELL')
NOT_RESOLVED_GRACE_DAYS = 30; MIN_BIN = 30; MIN_BRIER = 30; BOOT = 2000; SEED = 20261110
BIN_WORD = ['zero to one tenth', 'one tenth to two tenths', 'two tenths to three tenths', 'three tenths to four tenths', 'four tenths to five tenths',
            'five tenths to six tenths', 'six tenths to seven tenths', 'seven tenths to eight tenths', 'eight tenths to nine tenths', 'nine tenths to one']
SET_WORD = {'manifold_resolved': 'Manifold AI markets, resolved set', 'manifold_open': 'Manifold AI markets, open set', 'ai': 'AI timeline statements with a stated probability'}


def log(*a):
    line = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + ' ' + ' '.join(str(x) for x in a)
    print(line)
    with open(LOGF, 'a') as f: f.write(line + '\n')


def utcnow(): return D.datetime.now(D.timezone.utc)


def deadline_dt(s):
    """A deadline is a date (end of that day, 23:59:59 UTC) or a full UTC time."""
    if not s: return None
    if len(s) == 10: return D.datetime.fromisoformat(s).replace(hour=23, minute=59, second=59, tzinfo=D.timezone.utc)
    return D.datetime.fromisoformat(s.replace('Z', '+00:00'))


def bin_of(p):
    return min(9, int(math.floor(p * 10 + 1e-9)))


# ------------------------------------------------------------------ due check (writes rows)
def due_rows(ents, now, readings):
    rows = []
    for e in ents:
        dl = deadline_dt(e.get('deadline'))
        if e['outcomes'] or dl is None or dl > now: continue
        if e['kind'] == 'pdoom': continue
        if e.get('set') in ('manifold_resolved', 'manifold_open'):
            try:
                import manifold as M
                m = M.market(e['platform_id'])
            except Exception as ex:
                STALE.append('manifold ' + e['id']); log('manifold read failed', e['id'], ex); continue
            if m.get('isResolved') and m.get('resolution') in ('YES', 'NO'):
                rows.append(dict(kind='outcome', entry=e['id'], outcome='HAPPENED' if m['resolution'] == 'YES' else 'DID_NOT_HAPPEN', read_by='rider, Manifold API',
                                 evidence=[dict(url=e['source_url'], what='market resolved %s at %s' % (m['resolution'], m.get('resolutionTime')))], reason='the market resolved %s' % m['resolution']))
            elif m.get('isResolved'):
                rows.append(dict(kind='outcome', entry=e['id'], outcome='CANNOT_TELL', read_by='rider, Manifold API', evidence=[dict(url=e['source_url'], what='market resolved %s' % m.get('resolution'))],
                                 reason='the market resolved %s, not YES or NO' % m.get('resolution')))
            elif now > dl + D.timedelta(days=NOT_RESOLVED_GRACE_DAYS):
                rows.append(dict(kind='outcome', entry=e['id'], outcome='CANNOT_TELL', read_by='rider, Manifold API', evidence=[dict(url=e['source_url'], what='market not resolved')],
                                 reason='not resolved 30 days after its close'))
            continue
        rd = readings.get(e['id'])
        if rd:
            want = EVENT if e['kind'] == 'probability' else BINARY
            if rd.get('outcome') not in want or not rd.get('evidence'): log('reading refused (outcome or evidence missing)', e['id']); continue
            rows.append(dict(kind='outcome', entry=e['id'], outcome=rd['outcome'], read_by=rd.get('read_by', 'Bones'), evidence=rd['evidence'], reason=rd.get('reason', '')))
        elif not e['dues']:
            rows.append(dict(kind='due', entry=e['id'], note='deadline passed, no reading with evidence yet'))
    return rows


# ------------------------------------------------------------------ scoring (no network)
def calib(items):
    """items: list of (p, y). Bins, Brier, base-rate Brier and skill with a bootstrap interval."""
    bins = []
    for b in range(10):
        xs = [(p, y) for p, y in items if bin_of(p) == b]
        n = len(xs)
        if not n: bins.append(dict(bin=b, label=BIN_WORD[b], n=0)); continue
        k = sum(y for _, y in xs); mean = sum(p for p, _ in xs) / n; lo, hi = K.wilson(k, n)
        out = K.CANNOT_TELL if n < MIN_BIN else (K.ABOVE if lo > mean else K.BELOW if hi < mean else K.CONSISTENT)
        bins.append(dict(bin=b, label=BIN_WORD[b], n=n, happened=k, mean_stated=round(mean, 4), share=round(k / n, 4), lo=round(lo, 4), hi=round(hi, 4), outcome=out))
    res = dict(n=len(items), bins=bins)
    if len(items) >= MIN_BRIER:
        def brier(xs):
            base = sum(y for _, y in xs) / len(xs)
            b = sum((p - y) ** 2 for p, y in xs) / len(xs); r = sum((base - y) ** 2 for _, y in xs) / len(xs)
            return b, r, (1 - b / r) if r > 0 else None
        b, r, s = brier(items); rng = random.Random(SEED); sk = []
        for _ in range(BOOT):
            xs = [items[rng.randrange(len(items))] for _ in items]; v = brier(xs)[2]
            if v is not None: sk.append(v)
        sk.sort()
        res.update(brier=round(b, 4), brier_base=round(r, 4), base_rate=round(sum(y for _, y in items) / len(items), 4), skill=None if s is None else round(s, 4),
                   skill_lo=round(sk[int(0.025 * len(sk))], 4) if sk else None, skill_hi=round(sk[int(0.975 * len(sk)) - 1], 4) if sk else None)
    return res


def score(ents, now):
    S = dict(entries=len(ents), by_set={}, by_kind={}, binary={}, probability={}, pdoom=[], open=[], due_unread=[], chain=NL.verify()[1])
    for e in ents:
        S['by_set'][e['set']] = S['by_set'].get(e['set'], 0) + 1; S['by_kind'][e['kind']] = S['by_kind'].get(e['kind'], 0) + 1
    # binary: one tally for all, one for criteria written before the deadline, one for criteria written after it
    for lab, f in (('all', lambda e: True), ('criterion_before', lambda e: e.get('criterion_before_deadline')), ('criterion_after', lambda e: not e.get('criterion_before_deadline'))):
        xs = [e for e in ents if e['kind'] == 'binary' and e['outcomes'] and f(e)]
        S['binary'][lab] = dict(read=len(xs), **{o: sum(1 for e in xs if e['outcomes'][-1]['outcome'] == o) for o in BINARY})
    S['binary']['by_set'] = {}
    for st in sorted({e['set'] for e in ents if e['kind'] == 'binary'}):
        xs = [e for e in ents if e['kind'] == 'binary' and e['set'] == st and e['outcomes']]
        S['binary']['by_set'][st] = dict(read=len(xs), **{o: sum(1 for e in xs if e['outcomes'][-1]['outcome'] == o) for o in BINARY})
    for st in sorted({e['set'] for e in ents if e['kind'] == 'probability'}):
        xs = [e for e in ents if e['kind'] == 'probability' and e['set'] == st]
        read = [e for e in xs if e['outcomes'] and e['outcomes'][-1]['outcome'] in ('HAPPENED', 'DID_NOT_HAPPEN') and isinstance(e.get('probability'), (int, float))]
        items = [(float(e['probability']), 1 if e['outcomes'][-1]['outcome'] == 'HAPPENED' else 0) for e in read]
        c = calib(items); c.update(logged=len(xs), cannot_tell=sum(1 for e in xs if e['outcomes'] and e['outcomes'][-1]['outcome'] == 'CANNOT_TELL'),
                                   waiting=sum(1 for e in xs if not e['outcomes']))
        S['probability'][st] = c
    S['pdoom'] = [e['id'] for e in ents if e['kind'] == 'pdoom']
    for e in ents:
        dl = deadline_dt(e.get('deadline'))
        if not e['outcomes'] and e['kind'] != 'pdoom' and dl is not None:
            (S['open'] if dl > now else S['due_unread']).append(dict(id=e['id'], deadline=e['deadline']))
    S['open'].sort(key=lambda x: x['deadline']); S['next_due'] = S['open'][:10]
    S['resolved'] = sum(1 for e in ents if e['outcomes'])
    # the block indahl.ai/forecasters reads (rows 'feed'). Item text holds no digit. Display only.
    fc = []
    for st, c in S['probability'].items():
        for b in c['bins']:
            if b['n'] >= 1:
                fc.append(dict(kind='probability', item='%s, stated chance %s' % (SET_WORD.get(st, st), b['label']), counts='share of questions that resolved yes',
                               stated=b['mean_stated'], n=b['happened'], of=b['n'], delivered=b['share'], lo=b['lo'], hi=b['hi'], outcome=b['outcome'], interval='Wilson, as the desk gives it'))
        if c.get('skill') is not None and fc:
            fc[-1].update(brier_skill=c['skill'], brier_skill_lo=c['skill_lo'], brier_skill_hi=c['skill_hi'])
    S['forecasters'] = dict(rows=fc)
    return S


def main():
    now = utcnow(); ok, msg = NL.verify()
    if not ok: log('CHAIN BROKEN', msg); STALE.append('chain')
    ents = NL.current(); appended = 0
    if ok and not SCORE_ONLY:
        readings = json.load(open(READINGS)) if os.path.exists(READINGS) else {}
        rows = due_rows(ents, now, readings)
        if rows: appended = NL.append(rows); ents = NL.current(); log('appended', appended, 'rows')
        try: log('stamp upgrades', NL.upgrade())
        except Exception as ex: log('upgrade failed', ex)
    S = score(ents, now)
    idx = os.path.join(NL.ST, 'index.json'); stamps = json.load(open(idx)) if os.path.exists(idx) else []
    S.update(desk='NOW', publisher='Heuremen LLC', plan='PLAN.md', plan_unchanged_since_commit=K.plan_committed(os.path.join(H, 'PLAN.md')),
             updated=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), log_sha256=NL.head_sha(), log_rows=len(NL.lines()),
             stamps=stamps[-5:], stale=STALE, fortune=len(json.load(open(FORTUNE))) if os.path.exists(FORTUNE) else 0)
    json.dump(S, open(os.path.join(H, 'summary_now.json.tmp'), 'w'), indent=1); os.replace(os.path.join(H, 'summary_now.json.tmp'), os.path.join(H, 'summary_now.json'))
    keep = ('id', 'set', 'kind', 'who', 'quote', 'source_url', 'archive_url', 'said', 'deadline', 'criterion', 'criterion_before_deadline', 'probability')
    live = dict(S, entries_list=[dict({k: e.get(k) for k in keep}, outcome=(e['outcomes'][-1]['outcome'] if e['outcomes'] else None)) for e in ents])
    json.dump(live, open(os.path.join(H, 'data', 'now_live.json.tmp'), 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(os.path.join(H, 'data', 'now_live.json.tmp'), os.path.join(H, 'data', 'now_live.json'))
    if PUB:
        env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
        p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'predictions_live', '--path', os.path.join(H, 'data', 'now_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                           cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
        log('predictions_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    log('entries', S['entries'], 'resolved', S['resolved'], 'binary', json.dumps(S['binary']['all']), 'due unread', len(S['due_unread']), 'chain', msg)


def selftest():
    ok = True
    def check(n, c):
        nonlocal ok; ok &= bool(c); print(('OK   ' if c else 'FAIL ') + n)
    check('bin edges', bin_of(0) == 0 and bin_of(0.1) == 1 and bin_of(0.0999) == 0 and bin_of(1.0) == 9 and bin_of(0.95) == 9)
    rng = random.Random(1); items = [(p, 1 if rng.random() < p else 0) for p in [rng.random() for _ in range(3000)]]
    c = calib(items); cons = sum(1 for b in c['bins'] if b.get('outcome') == 'CONSISTENT')
    check('calibrated world reads CONSISTENT in most bins (%d of 10)' % cons, cons >= 8)
    items2 = [(p, 1 if rng.random() < min(1, p + 0.3) else 0) for p, _ in items]; c2 = calib(items2)
    check('under-stated world reads ABOVE in low bins', sum(1 for b in c2['bins'][:6] if b.get('outcome') == 'ABOVE') >= 5)
    check('skill near zero or above for calibrated world', c['skill'] is not None and c['skill'] > 0)
    check('small bin is CANNOT_TELL', calib([(0.3, 1)] * 10)['bins'][3]['outcome'] == 'CANNOT_TELL')
    check('no Brier under 30', 'brier' not in calib([(0.3, 1)] * 29))
    e = dict(id='X', kind='binary', set='onrecord', deadline='2020-12-31', outcomes=[], dues=[])
    r = due_rows([e], utcnow(), {}); check('passed deadline without reading writes one due row', len(r) == 1 and r[0]['kind'] == 'due')
    e2 = dict(e, dues=[{'kind': 'due'}]); check('no second due row', due_rows([e2], utcnow(), {}) == [])
    r = due_rows([e], utcnow(), {'X': dict(outcome='WRONG', evidence=[dict(url='u')])}); check('reading with evidence writes an outcome', r and r[0]['outcome'] == 'WRONG')
    check('reading without evidence is refused', due_rows([e], utcnow(), {'X': dict(outcome='WRONG')}) == [])
    check('future deadline writes nothing', due_rows([dict(e, deadline='2099-01-01')], utcnow(), {}) == [])
    check('pdoom never gets a due row', due_rows([dict(e, kind='pdoom')], utcnow(), {}) == [])
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() and K.selftest() else 1)
    main()
