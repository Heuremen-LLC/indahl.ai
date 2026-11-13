#!/usr/bin/env python3
"""shelly_mains.py -- 14 Oct, HIS: add the mains seat; "Nothing resolves cleanly bones.....don't make a ruler just to
throw out what doesn't fit the ruler. Ride."  So this is a RECORDER, not a ruler: every one of her ticks it reads the
Shelly Plug US Gen4 (192.168.8.159, MAC E8F60A7DDA80) and writes EVERYTHING it says, whole -- volts, hertz, watts, amps,
energy counters, its temperature, its own clock and uptime -- beside our clock and her cycle. Nothing is filtered,
nothing is excluded, no reading is judged. A value identical to the last one is kept and COUNTED (repeat_run), never
dropped: its first 12 reads (14 Oct 10:12, 30 s) were all identical, and that is a row, not a fault. An unreachable plug
is its own row (the absence is the data), never a skipped tick."""
import json, os, sys, time, urllib.request
W = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, W)
HOST = 'http://192.168.8.159'; LEDGER = os.path.join(W, 'shelly_mains.jsonl')

def get(path):
    return json.loads(urllib.request.urlopen(HOST + path, timeout=5).read())

def tick():
    row = {'t': round(time.time(), 3), 'iso': time.strftime('%Y-%m-%dT%H:%M:%S')}
    try: row['her_cycle'] = max(__import__('nova_stamp').recent(limit=8))
    except Exception as e: row['her_cycle'] = None
    got = 0
    for k, path in (('switch', '/rpc/Switch.GetStatus?id=0'), ('sys', '/rpc/Sys.GetStatus')):
        try: row[k] = get(path); got += 1
        except Exception as e: row[k + '_why'] = str(e)[:100]
    row['answered'] = got                                         # 15 Oct 05:3x: no labels -- how many of its two endpoints answered, and the
    try:                                                          # count of ticks the four values have sat identical (a frozen-sensor tell)
        last = json.loads(open(LEDGER).readlines()[-1])
        key = lambda r: tuple((r.get('switch') or {}).get(k) for k in ('voltage', 'freq', 'apower', 'current'))
        same = got and key(row) == key(last) and None not in key(row)
        row['repeat_run'] = (last.get('repeat_run', 0) + 1) if same else 0
    except Exception: row['repeat_run'] = 0
    open(LEDGER, 'a').write(json.dumps(row) + '\n'); return row

if __name__ == '__main__':
    r = tick(); s = r.get('switch') or {}
    print(r['iso'], 'answered', r['answered'], s.get('voltage'), s.get('freq'), s.get('apower'), 'repeat', r['repeat_run'])
