#!/usr/bin/env python3
"""manifold.py: the two fixed Manifold sets of PLAN.md (source 3). Keyless, paced, every response kept in data/raw/manifold/.
  python3 manifold.py resolved   -> data/research/manifold_resolved.json (+ counts of what was not read and why)
  python3 manifold.py open       -> data/research/manifold_open.json
  python3 manifold.py market ID  -> prints one market's resolution (used by now_tick.py)"""
import os, sys, json, time, urllib.request, urllib.parse, datetime as D

H = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(H, 'data', 'raw', 'manifold'); OUT = os.path.join(H, 'data', 'research')
API = 'https://api.manifold.markets/v0'; UA = 'heuremen-now/1 (+https://indahl.ai)'
TOPIC = 'ai'; MIN_BETTORS = 50; LEAD_DAYS = 30
WIN_LO = D.datetime(2025, 1, 1, tzinfo=D.timezone.utc); WIN_HI = D.datetime(2026, 10, 31, 23, 59, 59, tzinfo=D.timezone.utc)
OPEN_LO = D.datetime(2026, 11, 17, tzinfo=D.timezone.utc); OPEN_HI = D.datetime(2027, 12, 31, 23, 59, 59, tzinfo=D.timezone.utc)
os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)


def get(path, params, keep=None):
    url = API + path + ('?' + urllib.parse.urlencode(params) if params else '')
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            body = urllib.request.urlopen(req, timeout=60).read()
            if keep:
                with open(os.path.join(RAW, keep), 'wb') as f: f.write(body)
            time.sleep(0.15); return json.loads(body)
        except Exception as e:
            if i == 3: raise
            time.sleep(3 * (i + 1))


def ms(dt): return int(dt.timestamp() * 1000)
def iso(m): return D.datetime.fromtimestamp(m / 1000, D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def search(filt):
    """Every binary market in the topic for a filter, paged by offset."""
    out, before, i = [], None, 0   # the API pages by beforeTime with sort=newest (offset is capped at 1000)
    while True:
        q = {'term': '', 'topicSlug': TOPIC, 'filter': filt, 'contractType': 'BINARY', 'sort': 'newest', 'limit': 1000}
        if before: q['beforeTime'] = before
        page = get('/search-markets', q, keep='search_%s_%03d.json' % (filt, i)); i += 1
        out += page
        if len(page) < 1000: break
        before = min(m['createdTime'] for m in page)
    seen, uniq = set(), []
    for m in out:
        if m['id'] not in seen: seen.add(m['id']); uniq.append(m)
    return uniq


def prob_before(cid, t_ms):
    bets = get('/bets', {'contractId': cid, 'beforeTime': t_ms, 'limit': 20}, keep='bets_%s_%d.json' % (cid, t_ms))
    for b in bets:
        if b.get('isCancelled'): continue
        if b.get('probAfter') is None: continue
        if b.get('createdTime', 0) >= t_ms: continue
        return b['probAfter'], b['createdTime'], b.get('id')
    return None


def resolved():
    ms_all = search('resolved'); counts = dict(found=len(ms_all)); rows, skipped = [], []
    for m in ms_all:
        why = None
        if m.get('outcomeType') != 'BINARY': why = 'not binary'
        elif m.get('uniqueBettorCount', 0) < MIN_BETTORS: why = 'fewer than %d unique bettors' % MIN_BETTORS
        else:
            ref = min(x for x in (m.get('closeTime'), m.get('resolutionTime')) if x)
            if not (ms(WIN_LO) <= ref <= ms(WIN_HI)): why = 'reference time outside the window'
            elif m.get('resolution') not in ('YES', 'NO'): why = 'resolved %s' % m.get('resolution')
            elif m['createdTime'] > ref - LEAD_DAYS * 86400000: why = 'created less than 30 days before the reference time'
        if why: counts[why] = counts.get(why, 0) + 1; continue
        t = ref - LEAD_DAYS * 86400000; pb = prob_before(m['id'], t)
        if pb is None: counts['no bet before the stated moment'] = counts.get('no bet before the stated moment', 0) + 1; skipped.append(m['id']); continue
        rows.append(dict(id=m['id'], question=m['question'], url=m['url'], creator=m.get('creatorUsername'), created=iso(m['createdTime']), close=iso(m['closeTime']) if m.get('closeTime') else None,
                         resolution_time=iso(m['resolutionTime']), reference=iso(ref), stated_at=iso(t), probability=round(pb[0], 6), last_bet_before=iso(pb[1]), bet_id=pb[2],
                         resolution=m['resolution'], bettors=m.get('uniqueBettorCount')))
        counts['read'] = counts.get('read', 0) + 1
    json.dump(dict(rule='PLAN.md source 3, resolved set', read_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), counts=counts, rows=rows),
              open(os.path.join(OUT, 'manifold_resolved.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(counts, indent=1))


def open_set():
    ms_all = search('open'); counts = dict(found=len(ms_all)); rows = []; now = time.time() * 1000
    for m in ms_all:
        why = None
        if m.get('outcomeType') != 'BINARY': why = 'not binary'
        elif m.get('uniqueBettorCount', 0) < MIN_BETTORS: why = 'fewer than %d unique bettors' % MIN_BETTORS
        elif not m.get('closeTime') or not (ms(OPEN_LO) <= m['closeTime'] <= ms(OPEN_HI)): why = 'close time outside the window'
        elif m.get('isResolved'): why = 'already resolved'
        if why: counts[why] = counts.get(why, 0) + 1; continue
        full = get('/market/' + m['id'], None, keep='market_%s.json' % m['id'])
        rows.append(dict(id=m['id'], question=m['question'], url=m['url'], creator=m.get('creatorUsername'), created=iso(m['createdTime']), close=iso(m['closeTime']),
                         probability=round(full.get('probability', m.get('probability')), 6), read_at=iso(now), bettors=m.get('uniqueBettorCount'),
                         description=(full.get('textDescription') or '')[:4000]))
        counts['read'] = counts.get('read', 0) + 1
    json.dump(dict(rule='PLAN.md source 3, open set', read_at=iso(now), counts=counts, rows=rows), open(os.path.join(OUT, 'manifold_open.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(counts, indent=1))


def market(cid):
    m = get('/market/' + cid, None, keep='market_%s_%s.json' % (cid, time.strftime('%Y%m%d')))
    return dict(id=cid, isResolved=m.get('isResolved'), resolution=m.get('resolution'), resolutionTime=iso(m['resolutionTime']) if m.get('resolutionTime') else None, closeTime=iso(m['closeTime']) if m.get('closeTime') else None)


if __name__ == '__main__':
    a = sys.argv[1:] or ['resolved']
    if a[0] == 'resolved': resolved()
    elif a[0] == 'open': open_set()
    elif a[0] == 'market': print(json.dumps(market(a[1])))
