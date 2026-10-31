#!/usr/bin/env python3
"""trials_tick.py: TRIALS rider for the HST tick bus (every 48 ticks). Re-reads ClinicalTrials.gov per PLAN.md, scores per the fixed rule, publishes trials_live."""
import os, json, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
for s in ('trials_collect.py', 'trials_summary.py', 'trials_cancelled.py'):
    r = subprocess.run([sys.executable, '-I', s], capture_output=True, text=True)
    if r.returncode: print('trials:', s, 'FAILED', r.stderr[-300:]); sys.exit(0)
import urllib.request as _U
def _has(n):
    d = json.load(_U.urlopen(_U.Request('https://clinicaltrials.gov/api/v2/studies/%s?fields=HasResults' % n, headers={'User-Agent': 'heuremen-trials/0.1'}), timeout=60)); return d.get('hasResults')
try: _kg = _has('NCT03515551') is True and _has('NCT04537429') is False   # 29 Oct (audit): the plan's known-good records, run before every publish
except Exception: _kg = False
if not _kg: print('trials: the known-good records did not read as the plan says, publishing nothing'); sys.exit(0)
S = json.load(open('data/summary.json')); rd = open('data/read_at.txt').read().split('\n')
S['read'] = rd[0][:10] + ' ' + rd[0][11:16] + ' UTC'; S['cutoff'] = rd[1].split('=')[1]; S['excluded'] = S.pop('excluded_phase1_drug_only')
S['cancelled'] = json.load(open('data/cancelled.json')) if os.path.exists('data/cancelled.json') else None
json.dump(S, open('summary_trials.json', 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'trials_live', '--path', os.path.join(H, 'summary_trials.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('trials:', S['all']['n'], 'records;', 'published' if p.returncode == 0 else 'publish FAILED')
