#!/usr/bin/env python3
"""bq_publish.py: BIGQUERY rider per PLAN.md. Loads the public history files, the STACK rows, the hash chain and the queue readings into one public BigQuery dataset.
Uses the Google Cloud tools' bq command with the account signed in on this Mac. BQ_SETUP=1 creates the project, the dataset and its public access once."""
import os, sys, re, json, time, glob, subprocess, urllib.request, tempfile
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('bigquery: plan not committed'); sys.exit(0)
SDK = '/opt/homebrew/share/google-cloud-sdk/bin'; GC = SDK + '/gcloud'; BQ = SDK + '/bq'; PROJECT = open(os.path.join(H, 'PROJECT')).read().strip() if os.path.exists(os.path.join(H, 'PROJECT')) else 'heuremen-llc-data'; DS = 'heuremen_public'
PUB = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai/code')
TERMS = 'Heuremen LLC public data. Free to read, run and cite with attribution. Use to train machine learning models is not permitted. Source: github.com/Heuremen-LLC/indahl.ai, plans in code/SLUG/PLAN.md. https://indahl.ai'
def run(cmd, to=300): return subprocess.run(cmd, capture_output=True, text=True, timeout=to)
def legal(k): return re.sub(r'[^A-Za-z0-9_]', '_', k.replace('.', '__'))[:128] or 'col'
def clean_file(src, dst):
    n = 0
    with open(src) as f, open(dst, 'w') as o:
        for l in f:
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: continue
            o.write(json.dumps({legal(k): v for k, v in d.items() if not isinstance(v, (dict, list))}) + '\n'); n += 1
    return n
def load(table, path, desc, replace=True):
    r = run([BQ, 'load', '--project_id=' + PROJECT, '--autodetect', '--source_format=NEWLINE_DELIMITED_JSON'] + (['--replace'] if replace else []) + ['%s.%s' % (DS, table), path])
    if r.returncode: print('bigquery: load failed for', table, (r.stderr or r.stdout)[-200:]); return False
    run([BQ, 'update', '--project_id=' + PROJECT, '--description', desc, '%s.%s' % (DS, table)]); return True
def count(table):
    r = run([BQ, 'query', '--project_id=' + PROJECT, '--use_legacy_sql=false', '--format=json', 'SELECT COUNT(*) AS n FROM `%s.%s.%s`' % (PROJECT, DS, table)])
    try: return int(json.loads(r.stdout)[0]['n'])
    except Exception: return None
if os.environ.get('BQ_SETUP'):
    r = run([GC, 'projects', 'create', PROJECT, '--name=Heuremen LLC data']); print('project:', (r.stderr or r.stdout).strip()[-160:])
    r = run([GC, 'services', 'enable', 'bigquery.googleapis.com', '--project=' + PROJECT]); print('api:', (r.stderr or r.stdout).strip()[-120:])
    r = run([BQ, 'mk', '--project_id=' + PROJECT, '--dataset', '--location=US', '--description', TERMS.replace('SLUG', '<page>'), DS]); print('dataset:', (r.stderr or r.stdout).strip()[-120:])
    acc = run([BQ, 'show', '--project_id=' + PROJECT, '--format=prettyjson', DS]); d = json.loads(acc.stdout)
    if not any(a.get('specialGroup') == 'allAuthenticatedUsers' for a in d.get('access', [])):
        d['access'].append({'role': 'READER', 'specialGroup': 'allAuthenticatedUsers'}); json.dump(d, open('/tmp/bq_ds.json', 'w'))
        r = run([BQ, 'update', '--project_id=' + PROJECT, '--source', '/tmp/bq_ds.json', DS]); print('access:', (r.stderr or r.stdout).strip()[-120:])
    sys.exit(0)
ok = True; report = {}
tmp = tempfile.mkdtemp(prefix='bq_')
for f in sorted(glob.glob(PUB + '/*/history.jsonl')):
    slug = os.path.basename(os.path.dirname(f)).replace('-', '_'); dst = os.path.join(tmp, slug + '.jsonl'); n = clean_file(f, dst)
    if n and load('history_' + slug, dst, TERMS.replace('SLUG', os.path.basename(os.path.dirname(f)))): c = count('history_' + slug); report['history_' + slug] = (n, c); ok &= (c == n)
for name, rel in (('archive_chain', 'archive/chain.jsonl'),):
    f = PUB + '/' + rel; dst = os.path.join(tmp, name + '.jsonl'); n = clean_file(f, dst)
    if n and load(name, dst, TERMS.replace('SLUG', 'archive')): c = count(name); report[name] = (n, c); ok &= (c == n)
# tests_history: append the current STACK rows, once per load
try:
    st = json.loads(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/stack/live.json', headers={'User-Agent': 'heuremen-bq/0.1'}), timeout=40).read())
    lt = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); dst = os.path.join(tmp, 'tests.jsonl')
    with open(dst, 'w') as o:
        for r in st['rows']: o.write(json.dumps(dict(load_time=lt, page=r['page'], test=r['test'], compared=r['of'], failed=r['n'], share=r['share'], share_lo=r['share_lo'], share_hi=r['share_hi'], outcome=r['outcome'])) + '\n')
    before = count('tests_history') or 0
    if load('tests_history', dst, TERMS.replace('SLUG', 'stack'), replace=False): after = count('tests_history'); report['tests_history'] = (len(st['rows']), after - before); ok &= (after - before == len(st['rows']))
except Exception as e: print('bigquery: STACK feed not read', type(e).__name__); ok = False
print('bigquery:', 'LOAD OK' if ok else 'LOAD CHECK FAILED', {k: v for k, v in list(report.items())[:6]}, '...', len(report), 'tables')
json.dump(dict(t=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), ok=ok, tables=report), open('last_load.json', 'w'))
