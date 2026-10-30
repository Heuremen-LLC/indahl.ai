"""publish_model_live.py: builds the live status of the model-claim rounds from claims_s1.csv and outcomes_s1.json (written by score_s1.py once a claim is read) and puts it in the KV key sad_live. Run at events (a task finishing), never on a timer."""
import csv, json, os, subprocess, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
rows = list(csv.DictReader(open(os.path.join(HERE, 'claims_s1.csv'))))
out = json.load(open(os.path.join(HERE, 'outcomes_s1.json'))) if os.path.exists(os.path.join(HERE, 'outcomes_s1.json')) else {}
state = json.load(open(os.path.join(HERE, 'state_s1.json'))) if os.path.exists(os.path.join(HERE, 'state_s1.json')) else {'status': 'Claim list and rules committed. Known-good check queued.', 'known_good': 'queued'}
claims = []
for r in rows:
    cid = r['claim_id']; o = out.get(cid, {})
    if r['status'].startswith('NOT RUN'): st = r['status']; ours = ''; oc = ''
    else: st = o.get('state', 'queued'); ours = o.get('ours', ''); oc = o.get('outcome', '')
    claims.append(dict(name=r['claim_text'].rsplit(' ', 1)[0], stated=r['stated_value'], ours=ours, outcome=oc, state=st))
d = dict(updated=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %H:%M'), rounds=[dict(id='S1', model='SmolLM2-1.7B-Instruct', status=state['status'], known_good=state.get('known_good', ''), claims=claims, updated=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %H:%M'))])
f = os.path.join(HERE, 'status_model_live.json'); json.dump(d, open(f, 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894')
r = subprocess.run(['npx', 'wrangler', 'kv', 'key', 'put', 'model_live', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.join(B, '..', 'cloudflare-workers', 'heuremen-door'), env=env, capture_output=True, text=True)
print('published' if r.returncode == 0 else 'publish failed ' + r.stderr[-200:], file=sys.stderr)
