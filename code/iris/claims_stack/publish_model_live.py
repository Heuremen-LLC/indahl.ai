"""publish_model_live.py: builds the live status of the model-claim rounds from claims_s1.csv and outcomes_s1.json (written by score_s1.py once a claim is read) and puts it in the KV key sad_live. Run at events (a task finishing), never on a timer. With --no-push it writes status_model_live.json and stops."""
import csv, json, os, subprocess, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
ROUNDS = [('S1', 'SmolLM2-1.7B-Instruct'), ('S2', 'Phi-4-mini-instruct'), ('S3', 'Granite 4.1 3B')]   # 30 Oct: S2 and S3 added after their full reads
now = datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %H:%M'); rounds = []
for rid, model in ROUNDS:
    r_ = rid.lower(); cf = os.path.join(HERE, f'claims_{r_}.csv')
    if not os.path.exists(cf): continue
    rows = list(csv.DictReader(open(cf)))
    out = json.load(open(os.path.join(HERE, f'outcomes_{r_}.json'))) if os.path.exists(os.path.join(HERE, f'outcomes_{r_}.json')) else {}
    state = json.load(open(os.path.join(HERE, f'state_{r_}.json'))) if os.path.exists(os.path.join(HERE, f'state_{r_}.json')) else {'status': 'Claim list and rules committed.', 'known_good': ''}
    claims = []
    for r in rows:
        cid = r['claim_id']; o = out.get(cid, {})
        if r['status'].startswith('NOT RUN'): st = r['status']; ours = ''; oc = ''
        else: st = o.get('state', 'queued'); ours = o.get('ours', ''); oc = o.get('outcome', '')
        claims.append(dict(name=r['claim_text'].rsplit(' ', 1)[0], stated=r['stated_value'], ours=ours, outcome=oc, state=st))
    rounds.append(dict(id=rid, model=model, status=state['status'], known_good=state.get('known_good', ''), claims=claims, updated=now))
d = dict(updated=now, rounds=rounds)
f = os.path.join(HERE, 'status_model_live.json'); json.dump(d, open(f, 'w'), ensure_ascii=False)
if '--no-push' in sys.argv: print('written, not published: ' + f, file=sys.stderr); sys.exit(0)   # 30 Oct (site pass): build the local file only, no KV write
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894')
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'model_live', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.join(B, '..', 'cloudflare-workers', 'heuremen-door'), env=env, capture_output=True, text=True)
print('published' if r.returncode == 0 else 'publish failed ' + r.stderr[-200:], file=sys.stderr)
