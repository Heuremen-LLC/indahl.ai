#!/usr/bin/env python3
"""sample_seed.py PLAN_FILE [N K]: the seed for a hand-check sample, and optionally the draw. PLAN.md Addendum 3 rule 2.
The seed is the root of the first beacon entry on the public tape whose time is later than the last commit of PLAN_FILE. The draw ranks item i by SHA-256 of seed:i and takes the K lowest."""
import os, sys, json, hashlib, subprocess, datetime as D
H = os.path.dirname(os.path.abspath(__file__))
def commit_time(plan):
    d = os.path.dirname(os.path.abspath(plan)); f = os.path.basename(plan)
    return int(subprocess.run(['git', 'log', '-1', '--format=%ct', '--', f], cwd=d, capture_output=True, text=True, check=True).stdout.strip())
def seed(plan, tape=os.path.join(H, 'tape.jsonl')):
    t = commit_time(plan)
    for l in open(tape):
        e = json.loads(l)
        if e['kind'] == 'beacon' and D.datetime.strptime(e['t'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=D.timezone.utc).timestamp() > t: return e['n'], e['root']
    return None, None
def draw(sd, n, k): return sorted(sorted(range(n), key=lambda i: hashlib.sha256(('%s:%d' % (sd, i)).encode()).hexdigest())[:k])
if __name__ == '__main__':
    n, sd = seed(sys.argv[1])
    if not sd: sys.exit('no beacon entry after that plan commit yet')
    print('beacon entry %d seed %s' % (n, sd))
    if len(sys.argv) == 4: print(draw(sd, int(sys.argv[2]), int(sys.argv[3])))
