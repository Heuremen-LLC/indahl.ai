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
TS = re.compile(r'^(?:\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?\s*(?:Z|UTC|[+-]\d{2}:?\d{2})?)?|\d{1,2} [A-Z][a-z]{2}(?: \d{4})? \d{2}:\d{2}(?: UTC)?)$')   # 14 Nov (Sage 4th): the whole string is a time, nothing after it

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
    """body: the feed's raw bytes. -> dict(format, content, no_stamp, keys, clock_missing). A feed that is not a JSON object cannot have its
    clock separated from its content (Sage 4th): it is format raw and its events are CHANGED_RAW."""
    try: d = json.loads(body)
    except Exception: d = None
    if not isinstance(d, dict): h = hashlib.sha256(body).hexdigest(); return dict(format='raw', content=h, no_stamp=h, keys={}, clock_missing=[])
    cp = clock_paths(feed); c = _drop_paths(d, set(cp))
    return dict(format='json', content=_h(c), no_stamp=_h(_drop_stamps(c)), keys={k: _h(_drop_stamps(v)) for k, v in c.items()}, clock_missing=[p for p in cp if p not in d])

def update(store, feed, body, now, entry_n):
    """Record one read of one feed in store (a dict kept in changes.json). Returns the event kind or None.
    last_content_change, last_stamp_only and the counts are stored fields, never derived from the capped event list (Sage 4th)."""
    f = fingerprints(feed, body); r = store.get(feed)
    if r is None:
        store[feed] = dict(format=f['format'], content=f['content'], no_stamp=f['no_stamp'], keys=f['keys'], watched_since=now, clock_paths=clock_paths(feed),
                           events=[], reads=1, counts=dict(CONTENT=0, STAMP_ONLY=0, CHANGED_RAW=0), last_content_change=None, last_stamp_only=None, last_changed_raw=None,
                           clock_path_missing=f['clock_missing'])
        return None
    if f['format'] == 'raw': kind = 'CHANGED_RAW' if r['content'] != f['content'] else None
    else: kind = 'CONTENT' if r['no_stamp'] != f['no_stamp'] else ('STAMP_ONLY' if r['content'] != f['content'] else None)
    r['reads'] = r.get('reads', 0) + 1; r.setdefault('counts', dict(CONTENT=0, STAMP_ONLY=0, CHANGED_RAW=0))
    if kind:
        ev = dict(t=now, entry_n=entry_n, kind=kind)
        if kind == 'CONTENT': ev['changed_keys'] = sorted(k for k in set(f['keys']) | set(r.get('keys', {})) if f['keys'].get(k) != r.get('keys', {}).get(k))[:12]
        r['events'] = (r.get('events', []) + [ev])[-20:]; r['counts'][kind] = r['counts'].get(kind, 0) + 1
        r[{'CONTENT': 'last_content_change', 'STAMP_ONLY': 'last_stamp_only', 'CHANGED_RAW': 'last_changed_raw'}[kind]] = now
    r.update(format=f['format'], content=f['content'], no_stamp=f['no_stamp'], keys=f['keys'], clock_paths=clock_paths(feed), clock_path_missing=f['clock_missing']); return kind

def publish(store):
    out = {}
    for k, v in store.items():
        rd = v.get('reads', 0); c = v.get('counts', {})
        out[k] = dict(format=v.get('format', 'json'), watched_since=v['watched_since'], clock_paths=v['clock_paths'], clock_path_missing=v.get('clock_path_missing', []),
                      reads=rd, counts=c, content_rate=round(c.get('CONTENT', 0) / (rd - 1), 3) if rd > 1 else None,
                      last_content_change=v.get('last_content_change'), last_stamp_only=v.get('last_stamp_only'), last_changed_raw=v.get('last_changed_raw'), events=v.get('events', [])[-20:])
    return out

def _clone(st): return json.loads(json.dumps(st))

def selftest(bodies):
    """Planted cases on real feed bodies plus synthetic ones. Returns dict(fails, exercised, skipped) so a pass says what ran (Sage 4th)."""
    fails, ex, sk = [], {}, {}
    def run(name, ok, feed='synthetic'):
        ex[feed] = ex.get(feed, 0) + 1
        if not ok: fails.append(feed + ': ' + name)
    for feed, b in bodies.items():
        try: d = json.loads(b)
        except Exception: d = None
        st = {}; update(st, feed, b, 't0', 0)
        if not isinstance(d, dict):
            run('raw feed reads CHANGED_RAW', update(_clone(st), feed, b + b' ', 't1', 1) == 'CHANGED_RAW', feed); continue
        cp = [p for p in clock_paths(feed) if p in d]
        if cp:
            d1 = dict(d); [d1.__setitem__(p, '2099-01-01T00:00:00Z') for p in cp]
            run('run clock alone makes no event', update(_clone(st), feed, json.dumps(d1).encode(), 't1', 1) is None, feed)
        else: sk[feed] = sk.get(feed, []) + ['clock case: declared clock path absent (CLOCK_PATH_MISSING)']
        d2 = json.loads(b); key = next((k for k, v in d2.items() if k not in clock_paths(feed) and not (isinstance(v, str) and TS.match(v)) and isinstance(v, (int, float, str, list, dict)) and not isinstance(v, bool)), None)
        if key is not None:
            v = d2[key]; d2[key] = (v + 1) if isinstance(v, (int, float)) else (v + 'x') if isinstance(v, str) else (v + ['planted']) if isinstance(v, list) else dict(v, planted=1)
            run('content change on ' + key + ' reads CONTENT', update(_clone(st), feed, json.dumps(d2).encode(), 't2', 2) == 'CONTENT', feed)
        else: sk[feed] = sk.get(feed, []) + ['content case: no plantable field']
        d3 = json.loads(b); sk3 = next((k for k, v in d3.items() if k not in clock_paths(feed) and isinstance(v, str) and TS.match(v)), None)
        if sk3 is not None:
            d3[sk3] = '2099-01-01T00:00:00Z'; run('top-level stamp ' + sk3 + ' alone reads STAMP_ONLY', update(_clone(st), feed, json.dumps(d3).encode(), 't3', 3) == 'STAMP_ONLY', feed)
        else: sk[feed] = sk.get(feed, []) + ['stamp case: no top-level non-clock timestamp']
    def syn(a, b, name, want, feed='synthetic'):
        st = {}; update(st, feed, json.dumps(a).encode(), 't0', 0); run(name, update(st, feed, json.dumps(b).encode(), 't1', 1) == want)
    syn({'updated': '2026-11-14T00:00:00Z', 'studies': [{'study': 'a', 'read': 'Abstract only'}]}, {'updated': '2026-11-14T01:00:00Z', 'studies': [{'study': 'a', 'read': 'Full text'}]}, 'List read field reads CONTENT', 'CONTENT')
    syn({'updated': 'x', 'points': [{'x': 1}]}, {'updated': 'y', 'points': [{'x': 3}]}, 'coordinate x reads CONTENT', 'CONTENT')
    syn({'updated': 'a', 'rows': ['2026-11-14T09:20 Loom disagrees on one row']}, {'updated': 'b', 'rows': ['2026-11-14T09:20 Loom agrees on every row']}, 'text after a leading date reads CONTENT', 'CONTENT')
    syn({'updated': 'a', 'qubits': [{'q': 0, 'calibrated': '2026-11-13T22:00:00Z', 't1': 120}]}, {'updated': 'b', 'qubits': [{'q': 0, 'calibrated': '2026-11-14T08:00:00Z', 't1': 120}]}, 'nested stamp in a list row alone reads STAMP_ONLY', 'STAMP_ONLY')
    st = {}; update(st, 'roll', json.dumps({'updated': 'a', 'v': 1}).encode(), 't0', 0); update(st, 'roll', json.dumps({'updated': 'a', 'v': 2}).encode(), 'tC', 1)
    for i in range(21): update(st, 'roll', json.dumps({'updated': 'a', 'v': 2, 'as_of': '2026-11-%02dT00:00:00Z' % (i + 1)}).encode() if i else json.dumps({'updated': 'a', 'v': 2, 'as_of': '2026-11-01T00:00:00Z'}).encode(), 't%d' % i, i + 2)
    run('content time survives 21 stamp-only events', publish(st)['roll']['last_content_change'] == 'tC')
    st = {}; update(st, 'lst', b'[1, 2]', 't0', 0); run('top-level list reads CHANGED_RAW', update(st, 'lst', b'[1, 3]', 't1', 1) == 'CHANGED_RAW')
    st = {}; update(st, 'trials', json.dumps({'updated': 'x', 'n': 1}).encode(), 't0', 0); run('missing clock path is flagged', st['trials']['clock_path_missing'] == ['read'])
    return dict(fails=fails, exercised=ex, skipped=sk)
