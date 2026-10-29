#!/usr/bin/env python3
"""publish_results.py: collects runs/results_*.json, applies the plan's failed-fit clause (Note 3: a fit sitting on its own bound reads CANNOT_TELL) to the stored fits without re-bootstrapping,
and publishes KV qia_t1t2 for the QIA page. The printed outcome is kept beside the reading. A processor with no results file is shown as submitted and queued."""
import json, os, glob, subprocess, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
def onb(v, b): return v is not None and abs(v - b) <= 1e-6 * max(1.0, b)
out = dict(updated=D.datetime.now(D.timezone.utc).strftime('%d %b %H:%M'), processors=[])
for b in ('ibm_boston', 'ibm_kingston', 'ibm_fez'):
    f = 'runs/results_%s.json' % b
    if not os.path.exists(f): out['processors'].append(dict(backend=b, state='submitted, waiting in the processor queue')); continue
    d = json.load(open(f)); qs = []
    for q, r in d['qubits'].items():
        t1d = [x[0] for x in r['counts_t1']]; t2d = [x[0] for x in r['counts_t2']]
        lb1, ub1, lb2, ub2 = t1d[1] * 0.05, t1d[-1] * 50, t2d[1] * 0.05, t2d[-1] * 50
        vals1 = [r.get('t1_us')] + list(r.get('t1_ci') or []); vals2 = [r.get('t2_us')] + list(r.get('t2_ci') or [])
        bound = any(onb(v, lb1) or onb(v, ub1) for v in vals1 if v is not None) or any(onb(v, lb2) or onb(v, ub2) for v in vals2 if v is not None)
        printed = r['outcome']; reading = 'CANNOT_TELL' if bound else printed
        g = lambda x: None if x is None else round(x, 3)
        qs.append(dict(qubit=int(q), control=int(q) == d['control'], printed=printed, reading=reading, fit_on_bound=bound, t1=g(r.get('t1_us')), t1_ci=[g(x) for x in (r.get('t1_ci') or [])], t2=g(r.get('t2_us')), t2_ci=[g(x) for x in (r.get('t2_ci') or [])],
                       ratio=g(r.get('ratio')), ratio_ci=[g(x) for x in (r.get('ratio_ci') or [])], pub_t1=g(r['published_t1_us']), pub_t2=g(r['published_t2_us']), pub_t1_date=str(r['published_t1_date'])[:16], pub_t2_date=str(r['published_t2_date'])[:16]))
    out['processors'].append(dict(backend=b, state='ran', ran=d['ran'][:16].replace('T', ' '), known_good=d['known_good'], qubits=qs))
json.dump(out, open('summary_t1t2.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'qia_t1t2', '--path', os.path.join(H, 'summary_t1t2.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
for pr in out['processors']:
    print(pr['backend'], pr['state'], [(q['qubit'], q['printed'], q['reading']) for q in pr.get('qubits', [])])
print('qia_t1t2', 'published' if p.returncode == 0 else 'publish FAILED')
