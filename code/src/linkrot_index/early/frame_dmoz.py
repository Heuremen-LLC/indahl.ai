#!/usr/bin/env python3
"""frame_dmoz.py: the final Open Directory (DMOZ) dump (PLAN.md Addendum 3, sample E2). Frame statistics and, once the seed exists, the draw.
Frame: every ExternalPage address in content.rdf.u8.gz generated 2017-03-12, the last capture the Wayback Machine holds of
http://rdf.dmoz.org/rdf/content.rdf.u8.gz (capture 20170312160530, SHA-1 digest FATJCOXLKJQAL5DL5IMCVQ75SWEXFXLQ, checked on
download). http and https only. Unit: one distinct address. Draw: the 1,500 units with the smallest key, read in one pass with a
bounded heap. Era: the year of the address's earliest 200 capture in the Wayback Machine, read at check time (1996-2001, 2002-2008,
2009-2017, and a row for addresses with no 200 capture before 2017-03-13).
Usage: python3 -I frame_dmoz.py draw"""
import os, sys, re, json, gzip, heapq, html, hashlib, base64
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import frames_common as F
DUMP = os.path.join(F.DATA, 'dmoz_dump', 'content.rdf.u8.gz'); OUT = os.path.join(F.DATA, 'dmoz'); N = 1500
DIGEST = 'FATJCOXLKJQAL5DL5IMCVQ75SWEXFXLQ'
EP = re.compile(rb'<ExternalPage about="([^"]*)">')

def draw():
    h = hashlib.sha1()
    with open(DUMP, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
    dg = base64.b32encode(h.digest()).decode()
    if dg != DIGEST: raise SystemExit('dump digest %s does not match %s' % (dg, DIGEST))
    sd = F.seed(); heap, seen_keys, entries, nonhttp = [], set(), 0, 0
    with gzip.open(DUMP, 'rb') as fh:
        for line in fh:
            m = EP.search(line)
            if not m: continue
            entries += 1
            u = F.norm(html.unescape(m.group(1).decode('utf-8', 'replace')))
            if not u: nonhttp += 1; continue
            k = F.key(sd, 'dmoz', u)
            if k in seen_keys: continue
            if len(heap) < N: heapq.heappush(heap, (-int(k, 16), k, u)); seen_keys.add(k)
            elif int(k, 16) < -heap[0][0]:
                old = heapq.heappushpop(heap, (-int(k, 16), k, u)); seen_keys.discard(old[1]); seen_keys.add(k)
    # distinct count needs a second, lighter pass over hashed addresses
    distinct = set()
    with gzip.open(DUMP, 'rb') as fh:
        for line in fh:
            m = EP.search(line)
            if m:
                u = F.norm(html.unescape(m.group(1).decode('utf-8', 'replace')))
                if u: distinct.add(hashlib.md5(u.encode()).digest()[:8])
    units = [dict(id='dmoz|' + u, url=u, era=None, key=k) for _, k, u in sorted(heap, key=lambda x: x[1])]
    F.write_json(os.path.join(OUT, 'sample_dmoz.json'), dict(units=units, entries=entries, non_http=nonhttp, frame_count=len(distinct), dump_digest=dg))
    print('entries', entries, 'distinct http(s)', len(distinct), 'drawn', len(units))

if __name__ == '__main__':
    draw()
