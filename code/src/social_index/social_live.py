#!/usr/bin/env python3
"""social_live.py: the SOCIAL live feed (indahl.ai/social/live.json, 10 Nov 2026).
Builds data/social_live.json from summary_social.json only (desk, updated, read_at, built_utc, checked, headline, outcomes per section).
It copies numbers, it computes none. With --publish it puts the file in the site KV as social_live (the worker serves it at /social/live.json)."""
import os, sys, json, subprocess, datetime as D
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, 'summary_social.json')))
b = S['built_utc']   # "2026-11-10 12:34 UTC"
t = D.datetime.strptime(b, '%Y-%m-%d %H:%M UTC').replace(tzinfo=D.timezone.utc)
hl = S['headline']
now = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
# updated/read_at/built_utc = when the summary was built (the data's read). checked = when this keeper last put the feed (the seat reads checked, targets.json stamps)
live = dict(desk='SOCIAL', updated=b, read_at=t.strftime('%Y-%m-%dT%H:%M:%SZ'), built_utc=b, checked=now, status=S.get('status'), page=S.get('page'),
            headline=dict(big=hl['big'], line=hl['line'], href=hl.get('href'), section=hl.get('section')),
            outcomes={k: dict(rows=v['rows'], scored=v.get('scored'), outcomes=v['outcomes'], anchor=v.get('anchor')) for k, v in S['sections'].items()})
# guard: every count in the feed is the summary's own value
for k, v in live['outcomes'].items():
    assert v['outcomes'] == S['sections'][k]['outcomes'] and v['rows'] == S['sections'][k]['rows'], k
os.makedirs(os.path.join(H, 'data'), exist_ok=True); P = os.path.join(H, 'data', 'social_live.json')
json.dump(live, open(P, 'w'), separators=(',', ':'))
print('social: data/social_live.json', b, flush=True)
if '--publish' in sys.argv:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'social_live', '--path', P, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    print('social: ' + b + (' published' if p.returncode == 0 else ' publish FAILED ' + p.stderr[-300:]), flush=True)
    sys.exit(p.returncode)
