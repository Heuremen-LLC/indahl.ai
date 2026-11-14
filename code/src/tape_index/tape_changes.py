"""tape_changes.py (14 Nov 2026): when each live feed last changed in what it says. Kept beside the TAPE chain, never in it.

The chain hashes each feed whole, and every feed carries the time of our own run, so the chain hash moves on every run. Here only the
run-clock fields are removed, by exact path per feed (CLOCK_PATHS, read from the feeds on 14 Nov), never by key name. Every other field,
including every other timestamp, is content. Two fingerprints per feed:
  content   the feed with its run-clock paths removed
  no_stamp  the same, with every remaining timestamp-shaped string also removed
A run where content moved and no_stamp did not is a STAMP_ONLY event (a source stamp moved, nothing else did). A run where no_stamp moved
is a CONTENT event. Nothing is ever recorded as "no change" when a stamp moved. Refereed by Sage (third pass MOVES: strip by path, plant
a positive per feed type, record stamp-only moves as their own event)."""
import hashlib, json, re

CLOCK_PATHS = {'trials': ['read'], 'airline': ['updated', 'read'], 'neo': ['generated', 'updated']}   # every other feed: ['updated']
DEFAULT_CLOCK = ['updated']
TS = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}|^\d{1,2} [A-Z][a-z]{2} \d{2}:\d{2}')

def clock_paths(feed): return CLOCK_PATHS.get(feed, DEFAULT_CLOCK)

def _drop_paths(d, paths):
    if not isinstance(d, dict): return d
    return {k: v for k, v in d.items() if k not in paths}   # run-clock fields are top-level in every feed read on 14 Nov

def _drop_stamps(o):
    if isinstance(o, dict): return {k: _drop_stamps(v) for k, v in o.items() if not (isinstance(v, str) and TS.match(v))}
    if isinstance(o, list): return [_drop_stamps(v) for v in o if not (isinstance(v, str) and TS.match(v))]
    return o

def _h(o): return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def fingerprints(feed, body):
    """body: the feed's raw bytes. -> (content, no_stamp), or (raw sha, raw sha) when the feed is not JSON."""
    try: d = json.loads(body)
    except Exception: h = hashlib.sha256(body).hexdigest(); return h, h
    c = _drop_paths(d, set(clock_paths(feed))); return _h(c), _h(_drop_stamps(c))

def update(store, feed, body, now, entry_n):
    """Record one read of one feed in store (a dict kept in changes.json). Returns the event kind or None."""
    c, ns = fingerprints(feed, body); r = store.get(feed)
    if r is None: store[feed] = dict(content=c, no_stamp=ns, watched_since=now, clock_paths=clock_paths(feed), events=[]); return None
    kind = 'CONTENT' if r['no_stamp'] != ns else ('STAMP_ONLY' if r['content'] != c else None)
    if kind: r['events'] = (r.get('events', []) + [dict(t=now, entry_n=entry_n, kind=kind)])[-20:]
    r.update(content=c, no_stamp=ns, clock_paths=clock_paths(feed)); return kind

def publish(store):
    return {k: dict(watched_since=v['watched_since'], clock_paths=v['clock_paths'], events=v.get('events', [])[-20:],
                    last_content_change=next((e['t'] for e in reversed(v.get('events', [])) if e['kind'] == 'CONTENT'), None),
                    last_stamp_only=next((e['t'] for e in reversed(v.get('events', [])) if e['kind'] == 'STAMP_ONLY'), None)) for k, v in store.items()}

def selftest(bodies):
    """Planted positives and negatives on real feed bodies. bodies: {feed: raw bytes}. Returns a list of failures."""
    fails = []
    for feed, b in bodies.items():
        try: d = json.loads(b)
        except Exception: continue
        if not isinstance(d, dict): continue
        st = {}; update(st, feed, b, 't0', 0)
        # 1 only the run clock moves -> no event
        d1 = dict(d); [d1.__setitem__(p, '2099-01-01T00:00:00Z') for p in clock_paths(feed) if p in d1]
        if update(dict((k, dict(v)) for k, v in st.items()), feed, json.dumps(d1).encode(), 't1', 1) is not None: fails.append(feed + ': run clock alone made an event')
        # 2 a content field moves -> CONTENT (first non-clock, non-timestamp scalar or list found)
        d2 = json.loads(b); key = next((k for k, v in d2.items() if k not in clock_paths(feed) and not (isinstance(v, str) and TS.match(v)) and isinstance(v, (int, float, str, list, dict)) and not isinstance(v, bool)), None)
        if key is not None:
            v = d2[key]; d2[key] = (v + 1) if isinstance(v, (int, float)) else (v + 'x') if isinstance(v, str) else (v + ['planted']) if isinstance(v, list) else dict(v, planted=1)
            if update(dict((k, dict(v)) for k, v in st.items()), feed, json.dumps(d2).encode(), 't2', 2) != 'CONTENT': fails.append(feed + ': content change on ' + key + ' not seen')
        # 3 a non-clock timestamp moves alone -> STAMP_ONLY
        d3 = json.loads(b); sk = next((k for k, v in d3.items() if k not in clock_paths(feed) and isinstance(v, str) and TS.match(v)), None)
        if sk is not None:
            d3[sk] = '2099-01-01T00:00:00Z'
            if update(dict((k, dict(v)) for k, v in st.items()), feed, json.dumps(d3).encode(), 't3', 3) != 'STAMP_ONLY': fails.append(feed + ': stamp move on ' + sk + ' not STAMP_ONLY')
    # 4 a `read` field inside a List row (Sage: read is content in the study Lists) -> CONTENT
    lst = {'updated': '2026-11-14T00:00:00Z', 'studies': [{'study': 'a', 'read': 'Abstract only'}]}; st = {}
    update(st, 'qia_list', json.dumps(lst).encode(), 't0', 0); lst['studies'][0]['read'] = 'Full text'
    if update(st, 'qia_list', json.dumps(lst).encode(), 't1', 1) != 'CONTENT': fails.append('List read field change not seen')
    # 5 a coordinate named x moves -> CONTENT
    pl = {'updated': '2026-11-14T00:00:00Z', 'points': [{'x': 1, 'y': 2}]}; st = {}
    update(st, 'plot', json.dumps(pl).encode(), 't0', 0); pl['points'][0]['x'] = 3
    if update(st, 'plot', json.dumps(pl).encode(), 't1', 1) != 'CONTENT': fails.append('coordinate x change not seen')
    return fails
