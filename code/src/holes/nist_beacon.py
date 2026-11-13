#!/usr/bin/env python3
"""OUTSIDE HOLES #1 -- NIST Randomness Beacon 2.0 (beacon.nist.gov), 2026-09-26.

The beacon emits one signed, hash-chained pulse every 60 s. NIST's own record marks its holes two ways:
  * time gaps: pulseIndex is consecutive per EMITTED pulse, so a gap shows as
      time(b) - time(a) > (b - a) * period       (NISTIR 8213 eq: time_{i+1} = time_i + (1+g_i)*period)
  * statusCode bit flags on the pulse AFTER the event (NISTIR 8213 draft, Table 5):
      1 = rndloc: randLocal has no matching preCom (lost pre-image / chain start)
      2 = gap:    time gap before this pulse
      4 = certid: signing certificate changed
      8 = end:    last pulse of the chain
  * chain restarts: chain N+1 pulse 1 (new chainIndex) after chain N's last pulse.

No range endpoint exists, so we BISECT on pulse index: excess(a,b) = time(b)-time(a)-(b-a)*period is a sum of
non-negative per-step gaps, so any sub-range with excess 0 (and the same certificateId at both ends) is clean and
is never fetched. Cost ~ (#gaps) * log2(N) single-pulse fetches, cached forever under cache/nist/.

Holes appended to outside_holes.jsonl (dedup by id):
  provider 'nist-beacon', device 'chain-<c>', at = first missing pulse time, ended = time of the pulse that resumed,
  status = statusCode of the resuming pulse, reason = decoded flags, kind = 'beacon-gap' | 'chain-restart' | 'cert-change'
  | 'status-flag' (non-zero status seen without a time gap). shots = number of missing 60-s pulses.

Usage:  python3 nist_beacon.py            (re-run any time; only new pulses cost requests)
Limits: ~6 requests/s, 6 in flight, backoff on 429/5xx. Beacon 1.0 (2013-2018, no pulse index) is NOT walked.
"""
import json, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache', 'nist')
OUT = os.path.join(HERE, 'outside_holes.jsonl')
BASE = 'https://beacon.nist.gov/beacon/2.0'
FLAGS = {1: 'randLocal without matching preCommitment (lost pre-image)', 2: 'time gap in chain',
         4: 'certificate changed', 8: 'end of chain'}
_lock = threading.Lock(); _last = [0.0]; MIN_INTERVAL = 0.15
stats = {'fetched': 0, 'cached': 0}


def _get(url):
    for attempt in range(8):
        with _lock:                                   # global pacing, ~6 req/s
            wait = _last[0] + MIN_INTERVAL - time.time()
            if wait > 0: time.sleep(wait)
            _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'absence-ledger/1.0'}), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code in (429, 500, 502, 503, 504): time.sleep(2 ** attempt); continue
            raise
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError('giving up on ' + url)


def pulse(c, i):
    """Pulse (chain c, index i); cached raw JSON. i may be 'last'."""
    d = os.path.join(CACHE, f'c{c}'); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, f'p{i}.json')
    if i != 'last' and os.path.exists(fn):
        stats['cached'] += 1
        return json.load(open(fn))['pulse']
    if i != 'last' and os.path.exists(fn + '.404'): return None
    raw = _get(f'{BASE}/chain/{c}/pulse/{i}'); stats['fetched'] += 1
    if raw is None:                                   # confirm a 404 once more before believing it
        time.sleep(2); raw = _get(f'{BASE}/chain/{c}/pulse/{i}'); stats['fetched'] += 1
    if raw is None:
        if i != 'last' and i != 1: open(fn + '.404', 'w').close()
        return None
    p = raw['pulse']
    json.dump(raw, open(os.path.join(d, f"p{p['pulseIndex']}.json"), 'w'))
    return p


def ts(p): return datetime.strptime(p['timeStamp'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
def iso(t): return t.strftime('%Y-%m-%dT%H:%M:%SZ')
def decode(code): return '; '.join(v for k, v in FLAGS.items() if code & k) or ('ok' if code == 0 else f'undefined flags {code}')


def split(a, b):
    """Split point in (a, b): the multiple of the largest power of two that fits strictly inside. Aligned, so re-runs
    with a newer 'last' pulse reuse almost every cached interior pulse."""
    s = 1 << (b - a - 1).bit_length()
    while s > 1 and (a // s + 1) * s >= b: s >>= 1
    return (a // s + 1) * s


def walk_chain(c, pool):
    first, last = pulse(c, 1), pulse(c, 'last')
    per = timedelta(milliseconds=first['period'])
    got = {1: first, last['pulseIndex']: last}
    todo = [(1, last['pulseIndex'])]
    steps = []                                        # consecutive EXISTING pulses (a, b) with a gap, index skip or cert change
    missing = set()                                   # pulse indices NIST answers 404 for, inside the chain

    def existing_near(a, b):
        """An existing pulse index strictly inside (a, b), searching outward from the aligned split; None if none."""
        m = split(a, b)
        for k in range(0, b - a):
            for i in ((m + k, m - k) if k else (m,)):
                if a < i < b and i not in missing:
                    p = got.get(i) or pulse(c, i)
                    if p is not None: got[i] = p; return i
                    missing.add(i)
            if m + k >= b - 1 and m - k <= a + 1: break
        return None

    while todo:
        mids = sorted({split(a, b) for a, b in todo if b - a > 1} - set(got) - missing)
        for i, p in zip(mids, pool.map(lambda i: pulse(c, i), mids)):
            if p is None: missing.add(i)
            else: got[i] = p
        nxt = []
        for a, b in todo:
            pa, pb = got[a], got[b]
            excess = ts(pb) - ts(pa) - (b - a) * per
            if excess == timedelta(0) and pa['certificateId'] == pb['certificateId']: continue
            m = existing_near(a, b) if b - a > 1 else None
            if m is None: steps.append((a, b)); continue
            nxt += [(a, m), (m, b)]
        todo = nxt
        print(f'  chain {c}: {len(todo)} open ranges, {len(steps)} steps found, fetched {stats["fetched"]} cached {stats["cached"]}', flush=True)
    return first, last, got, steps, per, missing


def main():
    seen = set()
    if os.path.exists(OUT):
        seen = {json.loads(l)['id'] for l in open(OUT) if l.strip()}
    holes, chains = [], []
    with ThreadPoolExecutor(6) as pool:
        c = 1
        while pulse(c, 1) is not None:
            first, last, got, steps, per, missing = walk_chain(c, pool)
            chains.append((c, first, last))
            for a, b in sorted(steps):
                pa, pb = got[a], got[b]
                if b - a > 1:                         # pulse indices skipped (NIST returns 404 for them)
                    holes.append({'id': f'nist-beacon:c{c}:skip:{a}-{b}', 'provider': 'nist-beacon', 'device': f'chain-{c}',
                                  'status': pb['statusCode'], 'at': iso(ts(pa)), 'ended': iso(ts(pb)), 'shots': b - a - 1,
                                  'reason': f'pulse index(es) {a + 1}..{b - 1} absent (404) in chain {c}; time step {int((ts(pb) - ts(pa)) / per)} period(s); resuming pulse status {pb["statusCode"]}: {decode(pb["statusCode"])}',
                                  'kind': 'skipped-index'})
                gap = ts(pb) - ts(pa) - per           # time with no pulse at all, whatever the index says
                missing_t = int(gap / per)
                if gap > timedelta(0):
                    holes.append({'id': f'nist-beacon:c{c}:gap:{a}-{b}', 'provider': 'nist-beacon', 'device': f'chain-{c}',
                                  'status': pb['statusCode'], 'at': iso(ts(pa) + per), 'ended': iso(ts(pb)), 'shots': missing_t,
                                  'reason': f'{missing_t} pulse(s) missing between pulse {a} and {b}; resuming pulse status {pb["statusCode"]}: {decode(pb["statusCode"])}',
                                  'kind': 'beacon-gap'})
                if pa['certificateId'] != pb['certificateId']:
                    holes.append({'id': f'nist-beacon:c{c}:cert:{b}', 'provider': 'nist-beacon', 'device': f'chain-{c}',
                                  'status': pb['statusCode'], 'at': iso(ts(pa)), 'ended': iso(ts(pb)), 'shots': max(missing_t, 0),
                                  'reason': f'certificateId changed at pulse {b} ({pa["certificateId"][:12]}.. -> {pb["certificateId"][:12]}..); status {pb["statusCode"]}: {decode(pb["statusCode"])}',
                                  'kind': 'cert-change'})
            stepped = {b for _, b in steps}
            for i, p in sorted(got.items()):          # any non-zero status on a fetched pulse not already explained by a step
                if p['statusCode'] and i not in stepped and not (i == 1 and p['statusCode'] == 1):
                    holes.append({'id': f'nist-beacon:c{c}:status:{i}', 'provider': 'nist-beacon', 'device': f'chain-{c}',
                                  'status': p['statusCode'], 'at': iso(ts(p)), 'ended': iso(ts(p)), 'shots': 0,
                                  'reason': f'pulse {i} status {p["statusCode"]}: {decode(p["statusCode"])} (no time gap before it)',
                                  'kind': 'status-flag'})
            c += 1
    for (c0, _, l0), (c1, f1, _) in zip(chains, chains[1:]):
        per = timedelta(milliseconds=l0['period'])
        holes.append({'id': f'nist-beacon:restart:c{c0}-c{c1}', 'provider': 'nist-beacon', 'device': f'chain-{c1}',
                      'status': f1['statusCode'], 'at': iso(ts(l0) + per), 'ended': iso(ts(f1)),
                      'shots': int((ts(f1) - ts(l0) - per) / per),
                      'reason': f'chain {c0} ended at pulse {l0["pulseIndex"]} (status {l0["statusCode"]}: {decode(l0["statusCode"])}); chain {c1} began',
                      'kind': 'chain-restart'})
    new = [h for h in holes if h['id'] not in seen]
    with open(OUT, 'a') as f:
        for h in new: f.write(json.dumps(h) + '\n')
    for c, f0, l0 in chains:
        print(f'chain {c}: {f0["timeStamp"]} .. {l0["timeStamp"]}  pulses 1..{l0["pulseIndex"]}')
    kinds = {}
    for h in holes: kinds[h['kind']] = kinds.get(h['kind'], 0) + 1
    print(f'nist-beacon holes: {len(holes)} total {kinds}; {len(new)} new appended; http fetched {stats["fetched"]}, cache hits {stats["cached"]}')


if __name__ == '__main__':
    main()
