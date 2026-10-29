#!/usr/bin/env python3
"""public_progress.py: tick-bus rider (every 24 ticks). For each live corner of indahl.ai, reads the corner's public JSON, flattens its numbers into one row and appends the row to
code/<corner>/history.jsonl in the public tree, then pushes with ledger/push_public.sh. A row is skipped when nothing changed since the last one. The history is the trend, one commit at a time.
Reads only what the site already serves publicly. No keys, no raw data."""
import os, sys, json, time, urllib.request, subprocess, datetime as D
PUB = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai/code')
CORNERS = [('time', '/time/live.json', 'history.jsonl'), ('cada', '/cada/live.json', 'history.jsonl'), ('uptime', '/uptime/live.json', 'history.jsonl'), ('forecast', '/forecast/live.json', 'history.jsonl'),
           ('cadence', '/cadence/live.json', 'history.jsonl'), ('trials', '/trials/live.json', 'history.jsonl'), ('launch', '/launch/live.json', 'history.jsonl'), ('iris', '/iris/live.json', 'history.jsonl'),
           ('mirror', '/qia/audit.json', 'audit_history.jsonl'), ('mirror', '/qia/ibm.json', 'ibm_history.jsonl')]
SKIP = {'servers', 'sponsors', 'most_overdue', 'incidents', 'flagged', 'heads', 'updated', 'read', 'reference', 'seats', 'running', 'next', 'done', 'since', 'last_read', 'stamp'}
IDK = ('portal', 'backend', 'name', 'vendor', 'bin', 'resolver')
def flat(d, pre, out, depth=0):
    if depth > 3 or len(out) > 400: return
    if isinstance(d, dict):
        for k, v in d.items():
            if k in SKIP: continue
            flat(v, pre + str(k).replace(' ', '_') + '.', out, depth + 1)
    elif isinstance(d, list):
        if d and all(isinstance(x, dict) for x in d):
            for x in d:
                key = next((str(x[i]) for i in IDK if i in x), None)
                if key: flat({k: v for k, v in x.items() if k not in IDK}, pre + key.replace(' ', '_') + '.', out, depth + 1)
    elif isinstance(d, bool): pass
    elif isinstance(d, (int, float)): out[pre.rstrip('.')] = d
    elif isinstance(d, str) and pre.endswith('outcome.'): out[pre.rstrip('.')] = d
def main():
    now = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'); changed = []
    for corner, path, fn in CORNERS:
        try: d = json.load(urllib.request.urlopen(urllib.request.Request('https://indahl.ai' + path, headers={'User-Agent': 'heuremen-progress/0.1'}), timeout=40))
        except Exception as e: print('progress:', corner, 'NOTHING_RETURNED', type(e).__name__); continue
        row = {}; flat(d, '', row)
        if not row: continue
        dst = os.path.join(PUB, corner); os.makedirs(dst, exist_ok=True); f = os.path.join(dst, fn); last = None
        if os.path.exists(f):
            for l in open(f): last = json.loads(l)
        if last and {k: v for k, v in last.items() if k != 't'} == row: continue
        with open(f, 'a') as o: o.write(json.dumps(dict(t=now, **row), sort_keys=True) + '\n')
        changed.append(corner)
    print('progress: rows added for', sorted(set(changed)) or 'none')
    if changed:
        p = subprocess.run(['bash', os.path.expanduser('~/bones-forge/ledger/push_public.sh'), 'Trend rows: ' + ', '.join(sorted(set(changed)))], capture_output=True, text=True)
        print('progress:', (p.stdout.strip().splitlines() or ['no output'])[-1])
if __name__ == '__main__': main()
