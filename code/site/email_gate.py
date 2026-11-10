#!/usr/bin/env python3
"""email_gate.py (10 Nov 2026): no email address in any built site file. Subscriber addresses live only in the private KV, and this gate
fails the ship if any address shows up in what the site serves or mirrors: the built pages (indahl-ai, subfolders included), pages.js,
the worker's public folder and the KV copies of /week. Our own role addresses at heuremen.com, heuremen.org and indahl.ai are allowed.
Exit 1 on any hit. Hits are printed masked (first letter and domain only). Runs in ledger/ship.sh step 3."""
import os, re, sys, glob
B = os.path.expanduser('~/bones-forge'); S = os.path.join(B, 'indahl-ai'); P = os.path.join(B, 'cloudflare-workers', 'heuremen-door', 'public')
RX = re.compile(rb'[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.([A-Za-z]{2,24})\b')
OURS = re.compile(rb'@(?:[a-z0-9-]+\.)*(?:heuremen\.com|heuremen\.org|indahl\.ai)$', re.I)
NOT_TLD = {b'png', b'jpg', b'jpeg', b'gif', b'svg', b'webp', b'js', b'css', b'woff', b'woff2', b'json', b'html', b'map', b'ico', b'avif'}
TEXT = ('.html', '.js', '.json', '.txt', '.xml', '.csv', '.md', '.css', '.svg', '.webmanifest', '.text', '.tsv', '.jsonl')


def files():
    for p in glob.glob(os.path.join(S, '**', '*.html'), recursive=True):
        if '/.wrangler/' in p or '.pre-' in p or '.bak' in p or '/node_modules/' in p: continue
        yield p
    for f in ('pages.js', 'week.html', '.week_put.html'):
        if os.path.exists(os.path.join(S, f)): yield os.path.join(S, f)
    for root, _, fs in os.walk(P):
        for f in fs:
            if f.lower().endswith(TEXT): yield os.path.join(root, f)


def scan(paths):
    hits = []
    for p in paths:
        try: b = open(p, 'rb').read()
        except Exception: continue
        if b'\0' in b[:4096]: continue
        for m in RX.finditer(b):
            a = m.group(0)
            if m.group(1).lower() in NOT_TLD or OURS.search(a): continue
            hits.append((os.path.relpath(p, B), a[:1].decode('ascii', 'replace') + '***@' + a.split(b'@', 1)[1].decode('ascii', 'replace')))
    return hits


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        import tempfile
        d = tempfile.mkdtemp(); f = os.path.join(d, 'a.html')
        open(f, 'w').write('x jane.doe@example.org y Indahl@heuremen.com icon@2x.png')
        h = scan([f]); assert len(h) == 1 and h[0][1] == 'j***@example.org', h; print('email gate selftest: one planted address caught, ours and image names passed'); sys.exit(0)
    fl = sorted(set(files())); h = scan(fl)
    for rel, a in h[:40]: print('  EMAIL IN SITE FILE %s: %s' % (rel, a))
    print('email gate: %d files read, %d addresses found' % (len(fl), len(h))); sys.exit(1 if h else 0)
