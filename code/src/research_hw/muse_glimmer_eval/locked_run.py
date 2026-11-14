"""locked_run.py: the harvest.py GPU protocol around the Muse Glimmer eval (and the Hermes comparison on the same subset).
.train.lock (blocking) -> PAUSE_MAC 'muse_glimmer_eval' -> .flywheel.lock -> unload Ollama :11500 models (as harvest does) -> mlxpark.park()
-> memory check (free+inactive >= 22 GB or stop) -> muse gen -> hermes gen (subset) -> finally: unpark, remove PAUSE_MAC, release both locks."""
import fcntl, json, os, subprocess, sys, time, urllib.request, re
H = '/Users/heuremen/bones-forge/sage_library/council'
D = os.path.dirname(os.path.abspath(__file__))
PY = os.path.expanduser('~/bones-forge/venv/bin/python')
LOG = open(D + '/locked_run.log', 'a')
def log(s): LOG.write(time.strftime('%H:%M:%S ') + s + '\n'); LOG.flush(); print(s, flush=True)
def freeinact_gb():
    v = subprocess.run(['vm_stat'], capture_output=True, text=True).stdout
    ps = int(re.search(r'page size of (\d+)', v).group(1))
    g = lambda k: int(re.search(k + r':\s+(\d+)', v).group(1))
    return (g('Pages free') + g('Pages inactive')) * ps / 1e9, (g('Pages free') + g('Pages inactive') + g('Pages speculative')) * ps / 1e9
log('waiting for .train.lock')
lk = open(H + '/.train.lock', 'w'); fcntl.flock(lk, fcntl.LOCK_EX); T0 = time.time(); log('got .train.lock')
open(H + '/PAUSE_MAC', 'w').write('muse_glimmer_eval\n')
flk = open(H + '/.flywheel.lock', 'w'); fcntl.flock(flk, fcntl.LOCK_EX); log('got .flywheel.lock')
time.sleep(5)
try:
    try:
        for m in json.load(urllib.request.urlopen('http://127.0.0.1:11500/api/ps', timeout=10))['models']:
            urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11500/api/generate', json.dumps({'model': m['name'], 'keep_alive': 0}).encode()), timeout=60)
            log(f'unloaded ollama {m["name"]}')
    except Exception as e: log(f'ollama unload skipped: {e}')
    sys.path.insert(0, H); import mlxpark
    parked = mlxpark.park(); log(f'parked {[p["port"] for p in parked]}')
    time.sleep(5)
    fi, fis = freeinact_gb(); log(f'free+inactive {fi:.1f} GB (with speculative {fis:.1f})')
    if fi < 22:
        log('UNDER 22 GB after parking: stopping, no model loaded')
    else:
        deadline = T0 + 48 * 60   # muse gets until 48 min into the hold; hermes subset after (~5-8 min)
        r = subprocess.run([PY, D + '/gen.py', 'muse', D + '/muse_glimmer_raw.jsonl', str(deadline)], stdout=LOG, stderr=LOG)
        log(f'muse exit {r.returncode}')
        fi, fis = freeinact_gb(); log(f'free+inactive after muse {fi:.1f} GB')
        if time.time() - T0 < 52 * 60 and fi >= 22:
            r = subprocess.run([PY, D + '/gen.py', 'hermes', D + '/hermes3_8b_raw.jsonl', str(T0 + 62 * 60), 'subset'], stdout=LOG, stderr=LOG)
            log(f'hermes exit {r.returncode}')
        else: log('hermes skipped (time or memory)')
finally:
    try: import mlxpark; log(f'unparked {mlxpark.unpark()}')
    except Exception as e: log(f'unpark error {e}')
    try: os.remove(H + '/PAUSE_MAC')
    except FileNotFoundError: pass
    fcntl.flock(flk, fcntl.LOCK_UN); flk.close(); fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    log(f'released locks; GPU hold {(time.time()-T0)/60:.1f} min')
