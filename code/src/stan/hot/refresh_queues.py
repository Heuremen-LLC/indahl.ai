#!/usr/bin/env python3
"""refresh_queues.py -- tick-bus rider (12 Nov 2026). For each desk whose email search writes contacts/pdf_emails.jsonl, append newly
reachable papers (an ADS or PDF email, arXiv id known) to the END of index/queue_reachable.json, newest first among the new ones. Rows
already queued keep their positions, so batches the pipeline has cut never shift."""
import json, os, re
DESKS = {'quant_desk': 'contacts/qfin_empirical.json', 'brands': 'contacts/brands_2026.json'}
B = '/Users/heuremen/bones-forge/'
for desk, src in DESKS.items():
    d = B + desk + '/'
    if not os.path.exists(d + src): continue
    D = json.load(open(d + src)); pdf = {}
    if os.path.exists(d + 'contacts/pdf_emails.jsonl'):
        for l in open(d + 'contacts/pdf_emails.jsonl'):
            r = json.loads(l)
            if r.get('emails'): pdf[r['bibcode']] = r['emails']
    qf = d + 'index/queue_reachable.json'; q = json.load(open(qf)) if os.path.exists(qf) else []; have = {r['bibcode'] for r in q}
    EM = re.compile(r'^[^@\s]+@[^@\s]+\.[a-z]{2,}$', re.I)
    new = []
    for x in D:
        if x['bibcode'] in have: continue
        ads = [e for e in (x.get('email') or []) if e and EM.match(e.strip())]
        ax = next((i.split(':', 1)[1] for i in x.get('identifier', []) if str(i).startswith('arXiv:')), None)
        if ax and (ads or pdf.get(x['bibcode'])):
            new.append({'bibcode': x['bibcode'], 'arxiv': ax, 'doi': (x.get('doi') or [None])[0], 'pubdate': x.get('pubdate', ''),
                        'title': (x.get('title') or [''])[0], 'abstract': x.get('abstract', ''), 'brands': x.get('_brands')})
    if new:
        new.sort(key=lambda r: r['pubdate'], reverse=True); q += new
        os.makedirs(d + 'index', exist_ok=True); t = qf + '.tmp'; json.dump(q, open(t, 'w'), indent=1); os.replace(t, qf)
        open(d + 'index/queue_refresh.log', 'a').write('%s +%d -> %d\n' % (__import__('time').strftime('%Y-%m-%dT%H:%M:%S'), len(new), len(q)))
