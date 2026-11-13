#!/usr/bin/env python3
"""push_live.py (12 Nov 2026): puts the PETROL feed (KV petrol_live, served at /petrol/live.json) from summary_petrol.json: the headline, the latest
month's counts, the window counts and the EIA counts, with the summary's own 'updated' stamp. Numbers only, nothing written here that the summary lacks."""
import json, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
s = json.load(open(H + '/summary_petrol.json')); h = json.load(open(H + '/petrol_headline.json'))
p1 = s['part1'].get('headline') or {}; p2 = s['part2']
out = dict(updated=s['updated'], headline=dict(big=h['big'], line=h['line']), opec=dict(month=p1.get('month'), counts=p1.get('counts'), cannot_tell_by_reason=p1.get('cannot_tell_by_reason'), req13=p1.get('req13'), req13_window=p1.get('req13_all_months'), window_counts=p1.get('counts_all_months'), members=p1.get('members'), window_months=p1.get('window_months')),
           eia=dict(width_tbd=p2.get('width_tbd'), counts=p2.get('counts'), cannot_tell_by_reason=p2['headline'].get('cannot_tell_by_reason'), req13=p2['headline'].get('req13'), latest=p2.get('latest')), plan_matches_seal=s.get('plan_matches_seal'), gates_all_passed=s.get('gates_all_passed'))
f = H + '/data/petrol_live.json'; json.dump(out, open(f, 'w'), indent=1)
if '--dry' in sys.argv: print(json.dumps(out)[:300]); raise SystemExit(0)
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'petrol_live', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, capture_output=True, text=True,
                   env=dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/bin:/bin'))
print('petrol live:', 'published' if r.returncode == 0 else 'FAILED ' + (r.stderr or '')[-200:]); raise SystemExit(r.returncode)
