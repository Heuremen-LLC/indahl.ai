#!/usr/bin/env python3
"""known_good.py: the gate in PLAN.md. Builds a synthetic chain, then the verifier must pass it clean and flag three planted breaks."""
import os, sys, json, shutil, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from tapelib import merkle, beacon, entry_hash
from tape_verify import verify
def make(d):
    os.makedirs(d + '/leaves'); prev = '0' * 64; out = []
    for n in range(1, 7):
        if n % 2:
            leaves = [('a', 'h%d' % n), ('b', 'g%d' % n), ('c', 'k%d' % n)]; e = dict(n=n, t='t%d' % n, kind='feeds', subject='s', root=merkle(leaves), prev=prev); L = dict(leaves=leaves)
        else:
            q = ('q%d' % n) if n == 6 else None
            fr = out[-1]['root']; leaves = [('drand_randomness', 'r%d' % n), ('feeds_root', fr), ('prev_entry', prev)] + ([('qbits_root', q)] if q else []); e = dict(n=n, t='t%d' % n, kind='beacon', subject='s', root=beacon('r%d' % n, fr, prev, q), prev=prev); L = dict(leaves=leaves)
        e['entry'] = entry_hash(e); prev = e['entry']; out.append(e); json.dump(L, open(d + '/leaves/%d.json' % n, 'w'))
    open(d + '/tape.jsonl', 'w').write('\n'.join(json.dumps(e) for e in out) + '\n')
res = {}
d = tempfile.mkdtemp(); make(d + '/a'); res['clean'] = len(verify(d + '/a')[0]) == 0
shutil.copytree(d + '/a', d + '/b'); L = [json.loads(l) for l in open(d + '/b/tape.jsonl')]; L[1]['subject'] = 'changed'; open(d + '/b/tape.jsonl', 'w').write('\n'.join(json.dumps(e) for e in L) + '\n'); res['old_entry_change_flagged'] = len(verify(d + '/b')[0]) > 0
shutil.copytree(d + '/a', d + '/c'); p = d + '/c/leaves/3.json'; x = json.load(open(p)); x['leaves'][0][1] = 'tampered'; json.dump(x, open(p, 'w')); res['leaf_change_flagged'] = len(verify(d + '/c')[0]) > 0
shutil.copytree(d + '/a', d + '/e'); p = d + '/e/leaves/4.json'; x = json.load(open(p)); x['leaves'][0][1] = 'wrong'; json.dump(x, open(p, 'w')); res['beacon_mismatch_flagged'] = len(verify(d + '/e')[0]) > 0
print(json.dumps(res)); sys.exit(0 if all(res.values()) else 1)
