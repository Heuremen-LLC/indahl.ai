"""publish_status.py: writes reply COUNTS per model and arm to the IRIS page's KV key. No reply text, no scores. Called by run.py as replies land (an event, not a timer)."""
import json, os, subprocess, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
ORDER = ['phi4-mini', 'mistral:7b', 'falcon3:3b', 'smollm2:1.7b', 'llama3.1:8b', 'gemma3:4b', 'olmo2:7b', 'granite3.3:2b', 'qwen3:4b', 'deepseek-r1:1.5b']
n = len(json.load(open(os.path.join(HERE, 'items.json'))))
def cnt(m, arm):
    p = os.path.join(OUT, m.replace(':', '_'), arm + '.jsonl')
    return sum(1 for _ in open(p)) if os.path.exists(p) else 0
d = dict(of=n, updated=datetime.datetime.utcnow().strftime('%d %b %H:%M'), models=[dict(name=m, bare=cnt(m, 'bare'), bare_copy=cnt(m, 'bare_copy'), guard=cnt(m, 'guard')) for m in ORDER])
f = os.path.join(HERE, 'status.json'); json.dump(d, open(f, 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894')
r = subprocess.run(['npx', 'wrangler', 'kv', 'key', 'put', 'status15', '--path', f, '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                   cwd=os.path.join(HERE, '..', '..', 'cloudflare-workers', 'heuremen-door'), env=env, capture_output=True, text=True)
print('published' if r.returncode == 0 else 'publish failed', file=sys.stderr)
