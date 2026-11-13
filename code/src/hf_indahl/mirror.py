"""mirror.py -- tick-bus rider (1 Nov 2026, his "nothing's been updated on hf for over a day ... can the watch get in on that too?").
Rebuilds the indahl.ai datasets from the files the site serves (build.py, unchanged) and stages the finished bench rounds
(iris_index/publish_hf_bench.py), then uploads each repo to huggingface.co/indahl. Only changed files go up; a repo with no change makes no
commit. Signs in with the stored token named oauth-indahl (the account that owns these datasets), never printed. Writes mirror_state.json
(when it ran, each repo updated / unchanged / failed) for the watch."""
import os, sys, json, time, subprocess
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge'); ST = os.path.join(H, 'mirror_state.json')
from huggingface_hub import HfApi
try: from huggingface_hub import get_stored_tokens
except ImportError: from huggingface_hub.utils import get_stored_tokens
tok = get_stored_tokens().get('oauth-indahl')
state = {'ran': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'repos': {}}
def done(): json.dump(state, open(ST, 'w'), indent=1); print('hf mirror:', ', '.join(f'{k.split("/")[1]} {v["result"]}' for k, v in sorted(state['repos'].items())) or state.get('error'))
if not tok: state['error'] = 'no stored token named oauth-indahl'; done(); sys.exit(1)
api = HfApi(token=tok)
try:
    w = api.whoami(); state['account'] = w['name']; state['token_expires'] = w.get('auth', {}).get('expiresAt') or (w.get('auth', {}).get('accessToken', {}) or {}).get('expiresAt')   # OAuth sign-ins keep it at auth.expiresAt
except Exception as e: state['error'] = 'sign-in failed: ' + type(e).__name__; done(); sys.exit(1)
r = subprocess.run([sys.executable, os.path.join(H, 'build.py')], capture_output=True, text=True)
if r.returncode: state['error'] = 'build failed: ' + r.stderr[-300:]; done(); sys.exit(1)
S = os.path.join(H, 'stage')
for name in sorted(os.listdir(S)):
    rid = f'indahl/{name}'
    try:
        before = api.repo_info(rid, repo_type='dataset').sha
        api.upload_folder(folder_path=os.path.join(S, name), repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: ' + name + ' (mirror of indahl.ai)')
        after = api.repo_info(rid, repo_type='dataset').sha
        state['repos'][rid] = {'result': 'updated' if after != before else 'unchanged', 'sha': after}
    except Exception as e: state['repos'][rid] = {'result': 'failed', 'error': type(e).__name__ + ': ' + str(e)[:200]}
rid = 'indahl/iris-faults-guards-bench'
try:
    before = api.repo_info(rid, repo_type='dataset').sha
    r = subprocess.run([sys.executable, os.path.join(B, 'iris_index', 'publish_hf_bench.py')], capture_output=True, text=True, env=dict(os.environ, HF_TOKEN=tok))
    after = api.repo_info(rid, repo_type='dataset').sha
    state['repos'][rid] = {'result': 'failed', 'error': r.stderr[-200:]} if r.returncode else {'result': 'updated' if after != before else 'unchanged', 'sha': after}
except Exception as e: state['repos'][rid] = {'result': 'failed', 'error': type(e).__name__}
done()
