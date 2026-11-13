"""publish_train_status.py: reply COUNTS per arm to the IRIS page (KV key train). No reply text, no scores while a set is unread."""
import json, os, subprocess, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
ROWS = [('falcon3_base', 'Base model'), ('falcon3_trained', 'Trained on the Standards'), ('falcon3_mixed', 'Trained with mixed labels (control)')]
def cnt(S, k, arm):
    p = os.path.join(B, f'faultsbench_{S}', 'out', k, arm + '.jsonl'); return sum(1 for _ in open(p)) if os.path.exists(p) else 0
logs = {}
for k, name in (('true', 'trained'), ('mixed', 'mixed')):
    p = os.path.join(HERE, f'train_{k}.log'); step = None
    if os.path.exists(p):
        import re
        for l in open(p, errors='ignore'):
            m = re.match(r'^\s*(\d+)\s+[\d.]+', re.sub(r'\x1b\[[0-9;]*m', '', l))
            if m: step = m.group(1)
    logs[name] = step
d = dict(model='Falcon3 3B Instruct', updated=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %H:%M'), of=170, steps=600, step=logs,
         sets={S: [dict(name=name, bare=cnt(S, k, 'bare'), bare_copy=cnt(S, k, 'bare_copy'), guard=cnt(S, k, 'guard')) for k, name in ROWS] for S in ('tA', 'tB')})
f = os.path.join(HERE, 'status_train.json'); json.dump(d, open(f, 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894')
r = subprocess.run(['npx', 'wrangler', 'kv', 'key', 'put', 'train', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=os.path.join(B, '..', 'cloudflare-workers', 'heuremen-door'), env=env, capture_output=True, text=True)
print('published' if r.returncode == 0 else 'publish failed', file=sys.stderr)
