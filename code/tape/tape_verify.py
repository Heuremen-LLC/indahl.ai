#!/usr/bin/env python3
"""tape_verify.py [DIR]: recompute the TAPE chain, every leaves file root and every beacon from its inputs. DIR holds tape.jsonl and leaves/ (default: this folder).
Prints OK or each place it breaks. Needs only the Python standard library."""
import os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from tapelib import merkle, beacon, entry_hash
def verify(d):
    bad = []; prev = '0' * 64; n_prev = 0
    lines = [json.loads(l) for l in open(os.path.join(d, 'tape.jsonl')) if l.strip()]
    for e in lines:
        if e['n'] != n_prev + 1: bad.append('n %s: out of order' % e['n'])
        if e['prev'] != prev: bad.append('n %s: prev does not match the entry before it' % e['n'])
        if entry_hash(e) != e['entry']: bad.append('n %s: entry hash does not match its fields' % e['n'])
        lp = os.path.join(d, 'leaves', '%d.json' % e['n'])
        if not os.path.exists(lp): bad.append('n %s: leaves file missing' % e['n'])
        else:
            L = json.load(open(lp)); leaves = [tuple(x) for x in L['leaves']]
            if e['kind'] == 'beacon':
                inp = dict(leaves)
                if beacon(inp['drand_randomness'], inp['feeds_root'], inp['prev_entry'], inp.get('qbits_root')) != e['root']: bad.append('n %s: beacon does not match its inputs' % e['n'])
                if inp['prev_entry'] != e['prev']: bad.append('n %s: beacon input prev differs from the chain' % e['n'])
            elif merkle(leaves) != e['root']: bad.append('n %s: leaves do not give the root' % e['n'])
        prev = e['entry']; n_prev = e['n']
    return bad, len(lines)
if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else H
    bad, n = verify(d)
    print('tape', 'OK' if not bad else 'BROKEN', n, 'entries'); [print(' ', b) for b in bad[:20]]; sys.exit(1 if bad else 0)
