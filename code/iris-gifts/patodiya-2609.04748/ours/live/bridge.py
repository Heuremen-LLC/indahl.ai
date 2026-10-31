#!/usr/bin/env python3
"""Live GSM8K bridge on Metal (PLAN.md 5d3a336, written before any request). Our client; her harness is not run.
usage: bridge.py FORMAT SESSION    FORMAT in Q4_K_M Q8_0 Q3_K_M (or check: L0 only); SESSION 1 or 2. Starts llama-server b10434 with her flags, runs items 0-199,
four passes each (cold, cold2, warm, warm2), saves every response whole, stops the server. Refuses to start if any prompt hash differs from hers."""
import os, sys, json, glob, gzip, hashlib, time, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); T = G + '/theirs'
FMT, SES = sys.argv[1], int(sys.argv[2]); N = 200; PORT = 18434
MODEL = '%s/models/Qwen2.5-7B-Instruct-%s.gguf' % (G, FMT); SRV = H + '/llamacpp/build/bin/llama-server'
OUT = H + '/runs'; os.makedirs(OUT, exist_ok=True); tag = '%s_s%d' % (FMT, SES)
SYSTEM = ("You are a helpful assistant. Solve the math problem step by step and "
          "end your response with the final answer on its own line in the form "
          "#### <number>")
rows = {}
for f in sorted(glob.glob(T + '/gsm8k_test_rows/rows_*.json')):
    for r in json.load(open(f))['rows']: rows[r['row_idx']] = r['row']
render = lambda q: "<|im_start|>system\n" + SYSTEM + "<|im_end|>\n<|im_start|>user\n" + q + "<|im_end|>\n<|im_start|>assistant\n"
hers = {}
with gzip.open(T + '/repo_bc0551d/results/bridge-qwen7b-q4km-n500/cache_on/raw_requests.jsonl.gz', 'rt') as fh:
    for l in fh:
        r = json.loads(l); hers.setdefault(r['item_idx'], set()).add(r['prompt_sha256'])
P = {i: render(rows[i]['question']) for i in range(N)}
bad = [i for i in range(N) if hers.get(i) != {hashlib.sha256(P[i].encode()).hexdigest()}]
print('L0 prompt sha256 equal to hers: %d of %d' % (N - len(bad), N), flush=True)
if bad: sys.exit('REFUSED: prompt hash differs on items %s' % bad[:10])
if FMT == 'check': sys.exit(0)
if os.path.exists('%s/%s.jsonl' % (OUT, tag)): sys.exit('REFUSED: %s exists; a session is never resumed or appended' % tag)
def get(path, timeout=10):
    with urllib.request.urlopen('http://127.0.0.1:%d%s' % (PORT, path), timeout=timeout) as r: return json.loads(r.read())
def post(body):
    q = urllib.request.Request('http://127.0.0.1:%d/v1/completions' % PORT, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(q, timeout=600) as r: return json.loads(r.read())
log = open('%s/server_%s.log' % (OUT, tag), 'w')
cmd = [SRV, '-m', MODEL, '--alias', 'qwen7b-' + FMT.lower(), '--host', '127.0.0.1', '--port', str(PORT), '--parallel', '1', '-c', '16384', '-ngl', '99', '--seed', '42', '--slots']
srv = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
try:
    for _ in range(600):
        try:
            if get('/health').get('status') == 'ok': break
        except Exception: pass
        time.sleep(1)
    else: sys.exit('REFUSED: server not healthy after 600 s')
    meta = {'cmd': cmd, 'props': get('/props'), 'models': get('/v1/models'), 'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    h = hashlib.sha256()
    with open(MODEL, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 24), b''): h.update(b)
    meta['model_sha256'] = h.hexdigest()
    json.dump(meta, open('%s/%s.meta.json' % (OUT, tag), 'w'), indent=1)
    out = open('%s/%s.jsonl' % (OUT, tag), 'a'); t00 = time.time()
    for i in range(N):
        for ps in ('cold', 'cold2', 'warm', 'warm2'):
            body = {'model': 'qwen7b-' + FMT.lower(), 'prompt': P[i], 'temperature': 0.0, 'max_tokens': 1024, 'logprobs': 1, 'seed': 42, 'cache_prompt': ps.startswith('warm')}
            t0 = time.time(); resp = post(body)
            out.write(json.dumps({'item_idx': i, 'pass': ps, 'prompt_sha256': hashlib.sha256(P[i].encode()).hexdigest(), 'latency_s': time.time() - t0, 'response': resp}) + '\n'); out.flush()
        if (i + 1) % 20 == 0: print('%s: %d of %d items, %d s' % (tag, i + 1, N, time.time() - t00), flush=True)
    out.close(); print('DONE %s in %d s' % (tag, time.time() - t00), flush=True)
finally:
    srv.terminate()
    try: srv.wait(30)
    except Exception: srv.kill()
