#!/usr/bin/env python3
"""promote.py (Flight Mode v2): serve a trained seat and route the council to it, or roll it back.
  promote.py up <seat-model> <adapter-dir> <port>   start mlx_lm.server for the seat's base + adapter, then put "mlx:<seat-model>@<port>"
                                                    first in every seats.json list that holds <seat-model> (the old model stays as fallback)
  promote.py down <seat-model>                      roll back: drop the mlx: entry from seats.json and stop its server
Every change is a dated row in promotions.jsonl."""
import json, os, sys, time, subprocess, signal
H = os.path.dirname(os.path.abspath(__file__)); PY = os.path.expanduser('~/sage-v/venv/bin/python'); SEATS = H + '/seats.json'
BASES = json.load(open(SEATS))['mlx_bases']   # same map the trainer uses
def rewrite(fn):
    c = json.load(open(SEATS))
    for t in c['triangles'].values():
        t['voices'] = [[v, fn(ms), tag] for v, ms, tag in t['voices']]
        t['ear'] = fn(t['ear']); t['judge'] = fn(t.get('judge', []))
    json.dump(c, open(SEATS, 'w'), indent=1)
def row(d): open(H + '/promotions.jsonl', 'a').write(json.dumps({'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **d}) + '\n')
act, seat = sys.argv[1], sys.argv[2]
if act == 'up':
    ad, port = sys.argv[3], sys.argv[4]
    log = open(H + f'/mlx_{port}.log', 'a')
    p = subprocess.Popen([PY, '-m', 'mlx_lm', 'server', '--model', BASES[seat], '--adapter-path', ad, '--port', port], stdout=log, stderr=log, start_new_session=True)
    open(H + f'/mlx_{port}.pid', 'w').write(str(p.pid))
    open(H + f'/mlx_{port}.adapter', 'w').write(os.path.abspath(ad))   # read by sage_v.chat_mlx: the server ignores --adapter-path (mlx_lm 0.31.3 bug)
    import urllib.request
    for _ in range(90):   # 8 Nov: wait for the server to answer (an 8B load can pass 20 s), up to 3 min, instead of a fixed 20 s
        try: urllib.request.urlopen(f'http://127.0.0.1:{port}/v1/models', timeout=3); break
        except Exception: time.sleep(2)
    # Sage lineage: the mlx_lm generate CLI once ignored --adapter-path silently (byte-identical output). Same check for the server:
    # one fixed prompt at temp 0, adapter server vs base weights; identical output means the adapter is not loaded -> do not route to it.
    try:
        import urllib.request
        # 8 Nov: the check prompt is now the adapter's OWN job (first held-back row of its run's valid.jsonl), 200 tokens. A generic 40-token
        # question gave byte-identical text from a real, clean Granite adapter (round 3 refused 21:00Z): light LoRA on a narrow task does not
        # move an unrelated greedy answer, so that prompt could not tell "not loaded" from "not relevant".
        vf = os.path.join(os.path.dirname(ad.rstrip('/')), 'data', 'valid.jsonl'); msgs = [{'role': 'user', 'content': 'Name one thing a careful reader checks first. One sentence.'}]
        if os.path.exists(vf):
            r0 = json.loads(open(vf).readline()); msgs = [m for m in r0['messages'] if m['role'] != 'assistant']
        json.dump(msgs, open(H + f'/mlx_{port}_check.json', 'w'))
        q = json.dumps({'messages': msgs, 'max_tokens': 200, 'temperature': 0, 'adapters': os.path.abspath(ad)}).encode()
        got = json.loads(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions', q, {'Content-Type': 'application/json'}), timeout=300).read())['choices'][0]['message']['content']
        ref = subprocess.run([PY, '-c', f"import json;from mlx_lm import load,generate;m,t=load({BASES[seat]!r});print(generate(m,t,t.apply_chat_template(json.load(open({H + f'/mlx_{port}_check.json'!r})),add_generation_prompt=True),max_tokens=200))"], capture_output=True, text=True).stdout.strip()
        open(H + f'/mlx_{port}_check.txt', 'w').write('SERVED:\n' + got + '\n\nBASE:\n' + ref + '\n')
        if got.strip() == ref.strip():
            os.remove(H + f'/mlx_{port}.adapter'); os.kill(p.pid, signal.SIGTERM); row({'action': 'refused', 'seat': seat, 'adapter': ad, 'why': 'identical_to_base: adapter named in the request, served output equals base (not applied OR zero effect; this check cannot tell those apart)'}); print('REFUSED: identical to base'); sys.exit(1)
    except SystemExit: raise
    except Exception as e: row({'action': 'adapter_check_skipped', 'seat': seat, 'why': str(e)[:160]})
    if '--check-only' in sys.argv:   # 8 Nov (Sage: prove the check both ways): run the load check, never route, stop the server
        os.remove(H + f'/mlx_{port}.adapter'); os.kill(p.pid, signal.SIGTERM); row({'action': 'check_only_pass', 'seat': seat, 'adapter': ad}); print('CHECK PASS: served output differs from base'); sys.exit(0)
    tag = f'mlx:{seat}@{port}'
    rewrite(lambda ms: ([tag] + [m for m in ms if not str(m).startswith('mlx:')]) if seat in ms else ms)
    try:   # 8 Nov: the Ollama copy is now only a fallback; free its memory (it reloads on its own if the fallback is ever used)
        import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11500/api/generate', json.dumps({'model': seat, 'keep_alive': 0}).encode()), timeout=60)
    except Exception: pass
    row({'action': 'up', 'seat': seat, 'adapter': ad, 'route': tag, 'pid': p.pid}); print('promoted', tag)
elif act == 'down':
    rewrite(lambda ms: [m for m in ms if not str(m).startswith(f'mlx:{seat}@')])
    port = str(8801 + list(BASES).index(seat))   # 8 Nov: stop THIS seat's server only (was: every mlx server)
    f = H + f'/mlx_{port}.pid'
    if os.path.exists(H + f'/mlx_{port}.adapter'): os.remove(H + f'/mlx_{port}.adapter')
    if os.path.exists(f):
        try: os.kill(int(open(f).read()), signal.SIGTERM)
        except Exception: pass
        os.remove(f)
    row({'action': 'down', 'seat': seat}); print('rolled back', seat)
