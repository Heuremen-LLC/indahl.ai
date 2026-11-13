#!/usr/bin/env python3
"""chain.py -- the house pipeline: stages cued one after another by events, on HER ticks (Wayfinder 12 Nov 2026 night: "a pipeline isn't
a reading, it's a series of events cued one after another"). A tick_bus rider, period 1. Never a timer.
chain.json lists stages: {id, after: [ids], ready: optional shell check (exit 0 = ready), machine: cpu|mac|arm, cmd, cwd}.
- A stage starts when every stage in `after` is done (exit 0) and its `ready` check passes.
- cpu stages run here. mac/arm stages are cued to the hot lane (stan/hot/cue/<id>.json), which runs them before its routine sweeps,
  one GPU job per machine.
- Every stage runs through run_stage.py, which writes rc/<id>.rc with its exit code. done = rc 0; failed = anything else.
  A failed stage stops everything downstream of it and is a line in chain.log; nothing retries on its own.
New stages can be appended to chain.json at any time; finished ones stay as the record."""
import json, os, subprocess, sys, time
C = os.path.dirname(os.path.abspath(__file__)); HOT = '/Users/heuremen/bones-forge/stan/hot'
CH = os.path.join(C, 'chain.json'); ST = os.path.join(C, 'state.json'); LOG = os.path.join(C, 'chain.log'); RC = os.path.join(C, 'rc')
PY = '/opt/homebrew/bin/python3'
def log(m): open(LOG, 'a').write(time.strftime('%Y-%m-%dT%H:%M:%S ') + m + '\n')
def load(f, d):
    try: return json.load(open(f))
    except Exception: return d
def save(f, o): t = f + '.tmp'; json.dump(o, open(t, 'w'), indent=1); os.replace(t, f)
def alive(pid):
    try: os.kill(pid, 0); return True
    except Exception: return False
if os.path.exists(os.path.join(C, 'PAUSED')): sys.exit(0)
os.makedirs(RC, exist_ok=True); os.makedirs(os.path.join(HOT, 'cue'), exist_ok=True); os.makedirs(os.path.join(C, 'logs'), exist_ok=True)
stages = load(CH, []); st = load(ST, {})
for s in stages:
    k = s['id']; cur = st.get(k, {}).get('status', 'waiting')
    rcf = os.path.join(RC, k + '.rc')
    if cur in ('cued', 'running') and os.path.exists(rcf):
        rc = open(rcf).read().strip(); st[k] = {'status': 'done' if rc == '0' else 'failed', 'rc': rc, 'at': time.strftime('%FT%T')}
        log(f"{st[k]['status'].upper()} {k} rc {rc}"); continue
    if cur == 'running' and not alive(st[k].get('pid', -1)):
        st[k] = {'status': 'failed', 'rc': 'vanished', 'at': time.strftime('%FT%T')}; log(f'FAILED {k} (process gone, no rc)'); continue
    if cur != 'waiting': continue
    deps = [st.get(d, {}).get('status') for d in s.get('after', [])]
    if s.get('finally'):
        if any(x not in ('done', 'failed', 'blocked') for x in deps): continue
    elif 'failed' in deps or 'blocked' in deps:
        st[k] = {'status': 'blocked', 'at': time.strftime('%FT%T')}; log(f'BLOCKED {k}: upstream failed'); continue
    if not s.get('finally') and any(x != 'done' for x in deps): continue
    if s.get('ready') and subprocess.run(['/bin/zsh', '-c', s['ready']], capture_output=True).returncode != 0: continue
    wrapped = [PY, os.path.join(C, 'run_stage.py'), rcf, '--'] + s['cmd']
    if s.get('machine', 'cpu') == 'cpu':
        lf = open(os.path.join(C, 'logs', k + '.log'), 'a')
        p = subprocess.Popen(wrapped, cwd=s.get('cwd', C), stdout=lf, stderr=lf, start_new_session=True)
        st[k] = {'status': 'running', 'pid': p.pid, 'at': time.strftime('%FT%T')}; log(f'START {k} cpu pid {p.pid}')
    else:
        save(os.path.join(HOT, 'cue', k + '.json'), {'id': k, 'machine': s['machine'], 'cmd': wrapped, 'cwd': s.get('cwd', C), 'env': s.get('env', {})})
        st[k] = {'status': 'cued', 'at': time.strftime('%FT%T')}; log(f"CUED {k} -> hot lane {s['machine']}")
save(ST, st)
