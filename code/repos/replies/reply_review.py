#!/usr/bin/env python3
"""reply_review.py: our side of the right of reply (replies/PLAN.md). Never posts without a recount line.
  list                         pending replies from the response door (unit, host, received)
  fetch KEY                    downloads the PDF into a scratch folder for reading (python3 -I, never opened by a tool that runs code)
  post KEY --recount "text"    adds the entry to replies.json and publishes it (KV replies_public), only with a recount line
  show                         the posted entries"""
import os, sys, json, subprocess, datetime as D, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
INQ = '034b2ec99c3843099b3d5888d9e246d0'; BENCH = 'ecb59d96b07c43bdac14271687eae5af'
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
def wr(*a): return subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', *a, '--remote'], cwd=W, env=env, capture_output=True, text=True)
def pending():
    r = wr('key', 'list', '--namespace-id', INQ, '--prefix', 'resp:'); keys = [k['name'] for k in json.loads(r.stdout)] if r.returncode == 0 else []
    posted = {e['key'] for e in json.load(open(os.path.join(H, 'replies.json')))['replies']} if os.path.exists(os.path.join(H, 'replies.json')) else set()
    return [k for k in keys if k not in posted]
def get(k): return json.loads(wr('key', 'get', k, '--namespace-id', INQ).stdout)
def main():
    a = sys.argv[1:]; f = os.path.join(H, 'replies.json')
    if not os.path.exists(f): json.dump(dict(replies=[]), open(f, 'w'))
    if not a or a[0] == 'list':
        for k in pending(): v = get(k); print(k, v['unit'], v['host'], v['received'])
    elif a[0] == 'fetch':
        v = get(a[1]); d = os.path.join(H, 'scratch'); os.makedirs(d, exist_ok=True); p = os.path.join(d, a[1].replace(':', '_') + '.pdf')
        open(p, 'wb').write(urllib.request.urlopen(urllib.request.Request(v['url'], headers={'User-Agent': 'heuremen-replies/0.1'}), timeout=60).read()); print(p)
    elif a[0] == 'post':
        if '--recount' not in a or not a[a.index('--recount') + 1].strip(): sys.exit('refused: a reply is not posted without a recount line')
        v = get(a[1]); data = json.load(open(f)); data['replies'].append(dict(key=a[1], unit=v['unit'], url=v['url'], host=v['host'], received=v['received'], posted=D.datetime.now(D.timezone.utc).strftime('%Y-%m-%d'), recount=a[a.index('--recount') + 1].strip()))
        json.dump(data, open(f, 'w'), indent=1)
        pub = dict(replies=[{k: e[k] for k in ('unit', 'url', 'host', 'received', 'posted', 'recount')} for e in data['replies']]); tmp = os.path.join(H, 'replies_public.json'); json.dump(pub, open(tmp, 'w'))
        r = wr('key', 'put', 'replies_public', '--path', tmp, '--namespace-id', BENCH); print('posted' if r.returncode == 0 else 'publish FAILED')
    elif a[0] == 'show': print(json.dumps(json.load(open(f)), indent=1))
if __name__ == '__main__': main()
