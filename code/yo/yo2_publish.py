"""yo2_publish.py -- tick-bus rider (every tick). Publishes YO v2's live status to the IRIS page (KV key yo -> /iris/yo.json): the training
step, train and validation loss as mlx-lm prints them, the null scores fixed before training (PLAN_YO_V2.md), and the TEST reading only once
yo2_result.json exists (written after the run is read). Nothing else. Pushes only when the content changed."""
import json, os, re, subprocess, hashlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
W = os.path.join(B, 'cloudflare-workers', 'heuremen-door'); NS = 'ecb59d96b07c43bdac14271687eae5af'
def rows(f): return [json.loads(l) for l in open(f)] if os.path.exists(f) else None
def mean(rs, j): s = [r['score'] for r in rs if r['job'] == j]; return round(sum(s) / len(s), 3) if s else None
def forced(rs):
    ct = [r for r in rs if r['job'] == 'C' and r['truth'] == 'CANNOT_TELL']; return round(sum(r['pred'] != 'CANNOT_TELL' for r in ct) / len(ct), 3) if ct else None
train, val, step = [], [], 0
lp = os.path.join(HERE, 'yo2_train.log')
if os.path.exists(lp):
    for l in open(lp, errors='ignore'):
        m = re.search(r'Iter (\d+): Train loss ([\d.]+)', l)
        if m: train.append([int(m.group(1)), float(m.group(2))]); step = max(step, int(m.group(1)))
        m = re.search(r'Iter (\d+): Val loss ([\d.]+)', l)
        if m: val.append([int(m.group(1)), float(m.group(2))])
nulls = {}
n, c, bi, ba = (rows(os.path.join(HERE, f'eval2_{k}.jsonl')) for k in ('nothing', 'consistent', 'binary', 'base'))
if n: nulls['A_flag_nothing'] = mean(n, 'A')
if c: nulls['C_always_consistent'] = mean(c, 'C'); nulls['C_always_consistent_forced'] = forced(c)
if bi: nulls['C_binary_rule'] = mean(bi, 'C'); nulls['C_binary_rule_forced'] = forced(bi)
if ba: nulls['A_base'] = mean(ba, 'A'); nulls['C_base'] = mean(ba, 'C'); nulls['C_base_forced'] = forced(ba)
if os.path.exists(os.path.join(HERE, 'nulls_extra.json')): nulls.update(json.load(open(os.path.join(HERE, 'nulls_extra.json'))))   # POSTHOC_BASE_A.md: the lenient reading, labelled on the page
res = json.load(open(os.path.join(HERE, 'yo2_result.json'))) if os.path.exists(os.path.join(HERE, 'yo2_result.json')) else None
trained = os.path.exists(lp) and 'Saved final weights' in open(lp, errors='ignore').read()
state = 'done' if res else ('trained' if trained else ('training' if step else ('baselines scored' if ba else 'preparing')))
d = dict(model='Qwen3-1.7B (Apache-2.0), LoRA', steps=2000, step=step, train=train[-200:], val=val, nulls=nulls, result=res, state=state,
         plan='https://github.com/Heuremen-LLC/indahl.ai/blob/main/code/yo/PLAN_YO_V2.md')
h = hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest(); st = os.path.join(HERE, '.publish_state')
import time
if os.path.exists(st) and open(st).read().strip() == h and time.time() - os.path.getmtime(st) < 3600: print('yo: unchanged'); raise SystemExit   # republished at least hourly, so the feed's stamp stays current
d['updated'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
f = os.path.join(HERE, 'status_live.json'); json.dump(d, open(f, 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'yo', '--path', f, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True)
if r.returncode == 0: open(st, 'w').write(h)
print('yo:', state, 'step', step, 'published' if r.returncode == 0 else 'publish FAILED ' + r.stderr[-200:])
