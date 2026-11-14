#!/usr/bin/env python3
"""campus_dir.py (13 Nov 2026): the school directory behind the CAMPUS desk, for the indahl.ai education connector.

Reads the newest CAMPUS pass (data/reads.jsonl, written by campus_tick.py) and writes, per institution, every published source we
read for it: the address, where it now lands, the document type, the state at the last pass (opens, moved, blocked, gone, error)
and when it was read. Links and states only: no ratings, no scores, no reading of what a school's policy says.
Writes campus_dir.json and puts it to the site KV as campus_dir (same namespace as campus_live), then reads it back from
https://indahl.ai/api/v1/education_list_schools and exits 1 if the live copy does not match (silent-failure-guard).
Usage: python3 campus_dir.py [--publish]"""
import json, os, sys, subprocess, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
PUBLISH = '--publish' in sys.argv or os.environ.get('HEUREMEN_PUBLISH') == '1'
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')

def state(it):
    s = it.get('status')
    if s == 200:
        return 'opens (moved address)' if it.get('final') and it.get('final').rstrip('/') != it.get('url', '').rstrip('/') and it.get('moved') else 'opens'
    if s in (401, 403, 429): return 'blocked (%s)' % s
    if s in (404, 410): return 'gone (%s)' % s
    return 'error' if s is None else 'other (%s)' % s

def main():
    last = None
    for l in open('data/reads.jsonl'):
        if l.strip(): last = l
    if not last: print('campus_dir: no CAMPUS pass found'); return 1
    p = json.loads(last); when = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(p['t']))
    schools = {}
    for url, it in p['items'].items():
        it = dict(it, url=url)
        for inst in it.get('institutions') or ['(no institution recorded)']:
            schools.setdefault(inst, []).append({'url': url, 'lands_at': it.get('final') or url, 'type': it.get('kind'),
                                                 'state': state(it), 'http_status': it.get('status')})
    out = {'source': 'https://indahl.ai/campus', 'read_at': when, 'pass_stamp': p.get('stamp'),
           'what': 'Where each institution publishes the AI-policy material read by the CAMPUS desk, and whether each page still opens. Links and states only: no ratings and no reading of the policies.',
           'institutions': len([k for k in schools if k != '(no institution recorded)']), 'sources': len(p['items']),
           'schools': [{'name': k, 'sources': sorted(v, key=lambda x: x['url'])} for k, v in sorted(schools.items()) if k != '(no institution recorded)'],
           'sources_without_institution': sorted(schools.get('(no institution recorded)', []), key=lambda x: x['url'])}
    json.dump(out, open('campus_dir.json', 'w'), indent=1)
    print('campus_dir: %d institutions, %d sources, pass %s' % (out['institutions'], out['sources'], when))
    if not PUBLISH: print('publish guard: campus_dir not put to the site KV (run with --publish)'); return 0
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'campus_dir', '--path', os.path.join(H, 'campus_dir.json'),
                         '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
    if pr.returncode != 0: print('campus_dir: publish FAILED ' + (pr.stderr or pr.stdout)[-200:]); return 1
    try:   # read it back from the live API, as a plain client would
        r = json.loads(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/api/v1/education_list_schools', headers={'User-Agent': 'curl/8'}), timeout=60).read())
        live = r.get('data') or {}
        ok = live.get('institutions') == out['institutions'] and live.get('read_at') == out['read_at']
    except Exception as e: print('campus_dir: published, read-back CANNOT_TELL (%s)' % type(e).__name__); return 0
    print('campus_dir: published and read back VERIFIED' if ok else 'campus_dir: published but the live copy does not match (FAILED)')
    return 0 if ok else 1

if __name__ == '__main__': sys.exit(main())
