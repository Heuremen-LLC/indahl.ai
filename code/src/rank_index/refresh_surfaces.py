#!/usr/bin/env python3
"""RANK, run inside the locked ship command after rank_body_next.html is copied to rank_body.html: the listing rows' check cell now carries
each school's tally, so the rank.list.* snippets (first and last row of each list) are read again from the body that will ship.
Then every staged rank.* row is set live. Heuremen LLC."""
import json, os, re, sys
B = os.path.expanduser('~/bones-forge'); sys.path.insert(0, B + '/ledger')
import ledger as LG
from check_ledger import norm
body = open(B + '/rank_index/rank_body.html', encoding='utf-8').read()
D = json.load(open(B + '/rank_index/data/rank.json', encoding='utf-8'))
rows = LG.load(); nb = norm(body)
# split the body at each list heading, take the first table after it (the listing table)
for l in D['lists']:
    rid = f"rank.list.{l['key']}"
    if l['scope'] == 'none' or rid not in rows: continue
    h = body.index(f'<h2>{l["title"].replace("&", "&amp;")}</h2>') if f'<h2>{l["title"]}</h2>' not in body else body.index(f'<h2>{l["title"]}</h2>')
    tbs = [t.split('</tbody>', 1)[0] for t in body[h:].split('<tbody>')[1:4]]
    tb = next(t for t in tbs if 'respond?u=rank-' in t)   # the listing table carries the answer links, the sources table does not
    trs = re.findall(r'<tr>.*?</tr>', tb, flags=re.S)
    snips = [re.sub(r'\s*Respond$', '', norm(t)) for t in (trs[0], trs[-1])]
    for s_ in snips: assert s_ in nb, s_
    r = rows[rid]; old = [x['text'] for x in r['surfaces']]
    if old != snips:
        r['surfaces'] = [dict(surface='desk_rank', text=t) for t in snips]
        r['history'].append(dict(at=LG.now(), change='surfaces: check cell now shows the step two tally', evidence='rank_index/data/checks.json'))
        print('surfaces refreshed', rid)
for r in rows.values():
    if r['id'].startswith('rank.') and r['status'] == 'staged':
        r['status'] = 'live'; r['history'].append(dict(at=LG.now(), change="status: 'staged' -> 'live'", why='RANK step two page in this ship', evidence='rank_index/CHECKS.md'))
        print('live', r['id'])
LG.save(rows)
