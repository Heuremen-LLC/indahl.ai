#!/usr/bin/env python3
"""chain.py: entries.jsonl (append-only source) -> chain.json (with prev/hash) for the public page. --verify checks a chain.json."""
import json, hashlib, sys, os, datetime as D
H = os.path.dirname(os.path.abspath(__file__))
def canon(e): return json.dumps({k: v for k, v in e.items() if k != 'hash'}, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
def build():
    prev = '0' * 64; out = []
    for i, l in enumerate(open(os.path.join(H, 'entries.jsonl'))):
        if not l.strip(): continue
        e = json.loads(l); e['n'] = len(out) + 1; e['prev'] = prev; e['hash'] = hashlib.sha256(canon(e)).hexdigest(); prev = e['hash']; out.append(e)
    c = dict(updated=D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), head=prev, count=len(out), entries=out,
             how_to_verify='python3 verify.py chain.json (in the public repository, code/qia-offchain) recomputes every hash from the first entry.')
    json.dump(c, open(os.path.join(H, 'chain.json'), 'w'), indent=1, ensure_ascii=False); return c
def verify(path):
    c = json.load(open(path)); prev = '0' * 64
    for e in c['entries']:
        assert e['prev'] == prev, ('broken link at entry', e['n']); h = hashlib.sha256(canon(e)).hexdigest(); assert h == e['hash'], ('hash mismatch at entry', e['n']); prev = h
    assert prev == c['head'], 'head does not match the last entry'; return len(c['entries']), prev
if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--verify': n, h = verify(sys.argv[2]); print('chain OK:', n, 'entries, head', h)
    else: c = build(); n, h = verify(os.path.join(H, 'chain.json')); print('built and verified:', n, 'entries, head', h[:16])
