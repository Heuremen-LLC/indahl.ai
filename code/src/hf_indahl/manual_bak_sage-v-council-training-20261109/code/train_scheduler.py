#!/usr/bin/env python3
"""train_scheduler.py (Flight Mode v2, item 3): the autonomous training loop. One pass per call (sagev_daemon.py calls it in a loop).
- When every live seat has need_n() live claims (rollback resolution, from its own record): the next seat in rotation goes harvest.py -> train_live.py -> live (one GPU job; the council pauses itself).
- After a run: judge_audit.py refreshes; if the run says PROMOTE (bootstrap rule, not a first run) AND realjob_eval.py says REAL_OK
  (the seat's untrained real council prompts, base vs adapter, nothing wholly worse, no plant class down > 0.10), promote.py up serves it from MLX.
- Auto-rollback (Sage's review): if a promoted seat's real-job grounded rate over its last 40 claims falls more than 0.15 below its
  pre-promotion rate, promote.py down. Daily: spotcheck.py writes the day's 10-claim file. Every action is a line in scheduler.log."""
import json, os, sys, time, sqlite3, subprocess
H = os.path.dirname(os.path.abspath(__file__)); PY = os.path.expanduser('~/sage-v/venv/bin/python'); EVERY = None   # retired 8 Nov: turns are paced by LIVE_N live claims, below
def log(m): open(H + '/scheduler.log', 'a').write(time.strftime('%Y-%m-%dT%H:%M:%SZ ', time.gmtime()) + m + '\n')
def db(): return sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=30)
def st(k, d=None):
    r = db().execute('select v from state where k=?', (k,)).fetchone(); return json.loads(r[0]) if r else d
# 8 Nov (asked to justify it, corrected the same hour): the rollback compares a seat's live grounded rate with its pre-live rate
# (last 100 rows). need_n() is the smallest live n at which the 95% half-width of that DIFFERENCE is <= DROP (0.15, the rollback size), from
# the seat's own recorded rate. Measured 8 Nov: granite 73, hermes 63, phi 71, mistral 58, llama 128. (A fixed 40 was wrong twice: a remembered
# rate of 0.3 where the record said 0.56, and a one-rate width where the watch compares two.) The rollback watch uses the same n.
import math
DROP = 0.15
def need_n(seat, ts=None):
    g = [r[0] for r in db().execute("select grounded from pq where model=? and demo=0 and (? is null or ts <= ?) order by id desc limit 100", (seat, ts, ts))]
    if len(g) < 20: return 100
    p = min(0.95, max(0.05, sum(g) / len(g))); se0 = math.sqrt(p * (1 - p) / len(g))
    if 1.96 * se0 >= DROP: return 400
    return next(n for n in range(5, 400) if 1.96 * math.sqrt(se0 ** 2 + p * (1 - p) / n) <= DROP)
def live_claims(seat, since): return db().execute("select count(*) from pq where model like ? and ts > ?", (f'mlx:{seat}@%', since)).fetchone()[0]
if len(sys.argv) > 2 and sys.argv[1] == '--turn':   # detached turn: harvest -> train_live -> go live; result to turn_result.json
    seat = sys.argv[2]; T = H + '/train'
    import threading   # Sage 8 Nov: heartbeat so a dead detached turn is told apart from a slow one (file touched every 60 s with the stage)
    STAGE = ['start']
    def _hb():
        while True: open(T + '/turn.heartbeat', 'w').write(json.dumps({'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'seat': seat, 'stage': STAGE[0], 'pid': os.getpid()})); time.sleep(60)
    threading.Thread(target=_hb, daemon=True).start()
    st0 = json.load(open(H + '/scheduler_state.json')) if os.path.exists(H + '/scheduler_state.json') else {'promoted': {}}
    cur = st0.get('promoted', {}).get(seat, {}).get('adapter')
    STAGE[0] = 'paired set'
    if not os.path.exists(T + f"/paired_{seat.replace(':', '_')}.json"):
        r = subprocess.run([PY, H + '/prepare_paired.py', seat, '60'], capture_output=True, text=True); log(f'paired set {seat}: {r.stdout.strip()[-200:]}')
    for hn in range(3):   # Sage 8 Nov: floor 100 rows, harvest supplies the rest, at most 3 harvests a turn
        STAGE[0] = f'harvest {hn + 1}'
        with open(T + '/harvest_out.log', 'a') as f: r = subprocess.run([PY, H + '/harvest.py', seat, '48', '4'] + (['--from', cur] if cur else []), stdout=f, stderr=subprocess.STDOUT)
        n_ = subprocess.run([PY, H + '/train_live.py', seat], capture_output=True, text=True, env=dict(os.environ, COUNT_ONLY='1')).stdout.strip().splitlines()
        log(f'harvest {hn + 1} {seat} rc {r.returncode}; training rows now {n_[-1] if n_ else "?"}')
        if n_ and n_[-1].isdigit() and int(n_[-1]) >= 100: break
    STAGE[0] = 'train_live'
    with open(T + '/train_live_out.log', 'a') as f: pos = f.tell(); r = subprocess.run([PY, H + '/train_live.py', seat], stdout=f, stderr=subprocess.STDOUT)
    log(f'train_live {seat} rc {r.returncode}')
    res = {'seat': seat, 'ok': False, 'why': f'train_live rc {r.returncode}'}
    if r.returncode == 0:
        tail = open(T + '/train_live_out.log').read()[pos:].strip().splitlines()
        try: info = json.loads(tail[-1])
        except Exception: info = {}
        pre = [x[0] for x in db().execute("select grounded from pq where model=? order by id desc limit 100", (seat,))]
        try: pre_dis = json.load(open(H + '/scoreboard.json')).get('disagreement')
        except Exception: pre_dis = None
        res = {'seat': seat, 'ok': bool(info.get('adapter')), 'why': 'no adapter line' if not info.get('adapter') else '',
               'info': {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'pre_grounded': (sum(pre) / len(pre)) if pre else 0.3, 'pre_ids': [x[0] for x in db().execute("select id from pq where model=? and demo=0 order by id desc limit 100", (seat,))],   # Sage: baseline frozen as a fixed row set
                        'pre_disagreement': pre_dis, 'adapter': info.get('adapter'), 'port': info.get('port')}}
    json.dump(res, open(T + '/turn_result.json', 'w'))
    sys.exit(0)
S = H + '/scheduler_state.json'; state = json.load(open(S)) if os.path.exists(S) else {'last_rev': 0, 'rot': 0, 'last_spot': '', 'promoted': {}}
seats = json.load(open(H + '/seats.json')); rotation = [m for m in seats['mlx_bases']]
_st0 = json.load(open(H + '/scheduler_state.json')) if os.path.exists(H + '/scheduler_state.json') else {}
rotation = _st0.get('order') or rotation   # Sage 8 Nov: order by the eval, not by the file (phi4-mini ahead of mistral)
rev = st('fly_cycle', 0) or 0   # 8 Nov: training turns count deep cycles (revolutions are rare); 'last_rev' now holds a cycle number
subprocess.run([sys.executable, H + '/scoreboard.py'], capture_output=True)   # keep scoreboard.json fresh for the watches below
# daily spot-check
if state['last_spot'] != time.strftime('%Y%m%d'):
    subprocess.run([sys.executable, H + '/spotcheck.py'], capture_output=True); state['last_spot'] = time.strftime('%Y%m%d'); log('spotcheck written')
# auto-rollback watch
for seat, info in list(state['promoted'].items()):
    try:
        n_ = need_n(seat, info['ts'])
        g = [r[0] for r in db().execute("select grounded from pq where model like ? and ts > ? order by id desc limit ?", (f'mlx:{seat}@%', info['ts'], n_))]
        if len(g) >= n_ and sum(g) / len(g) < info['pre_grounded'] - DROP:
            subprocess.run([sys.executable, H + '/promote.py', 'down', seat]); del state['promoted'][seat]
            log(f'AUTO-ROLLBACK {seat}: real-job grounded {sum(g) / len(g):.2f} vs {info["pre_grounded"]:.2f} before promotion')
    except Exception as e: log(f'rollback watch error {e}')
# collapse rollback (gap 6): a promotion that drives council disagreement below half its pre-promotion level rolls back
try:
    sb = json.load(open(H + '/scoreboard.json'))
    for seat, info in list(state['promoted'].items()):
        if info.get('pre_disagreement') and sb.get('disagreement') is not None and sb.get('disagreement_n', 0) >= 10 and sb['disagreement'] < 0.5 * info['pre_disagreement']:
            subprocess.run([sys.executable, H + '/promote.py', 'down', seat]); del state['promoted'][seat]
            log(f"AUTO-ROLLBACK {seat}: council disagreement {sb['disagreement']} vs {info['pre_disagreement']} before promotion (collapse)")
except Exception as e: log(f'collapse watch error {e}')
# live training turn. 8 Nov fix: a turn (harvest 40-56 min + train ~43 min at 0.13 it/s) outlived the daemon's 3600 s timeout on this pass; the kill
# broke train_live's stdout pipe, so three finished Granite adapters died before going live and the rotation never saved. A turn now runs DETACHED
# (own session, output to files), this pass returns at once, and the turn's result comes back through train/turn_result.json.
TP, TR = H + '/train/turn.pid', H + '/train/turn_result.json'
def alive(pid):
    try: os.kill(pid, 0); return True
    except Exception: return False
import glob
for TR_ in sorted(glob.glob(H + '/train/turn_result*.json')):
    try:
        res = json.load(open(TR_)); os.remove(TR_)
        if res.get('ok'): state['promoted'][res['seat']] = res['info']; log(f"LIVE {res['seat']} on :{res['info'].get('port')}")
        else: log(f"turn {res.get('seat')} ended without going live: {res.get('why')}")
    except Exception as e: log(f'turn result read error {e}')
busy = os.path.exists(TP) and alive(int(open(TP).read().strip() or 0))
# 8 Nov: also busy while ANY training / promotion / harvest process runs, whoever started it (a one-shot finisher was missed at 21:00Z)
busy = busy or bool(subprocess.run(['pgrep', '-f', 'mlx_lm lora|promote.py|harvest.py|train_live.py|finish_round'], capture_output=True, text=True).stdout.strip())
ready = all(i_.get('released') or live_claims(s_, i_['ts']) >= need_n(s_, i_['ts']) for s_, i_ in state['promoted'].items())   # Sage 8 Nov: the wait is attribution only; a paired result or her ruling releases it
if ready and not busy and not os.path.exists(H + '/PAUSE') and not os.path.exists(H + '/PAUSE_MAC'):
    seat = rotation[state['rot'] % len(rotation)]; state['rot'] += 1; state['last_rev'] = rev
    log(f'LIVE turn: {seat} at revolution {rev}')
    json.dump(state, open(S, 'w'), indent=1)   # rotation saved before the turn starts
    out = open(H + f"/train/turn_{seat.replace(':', '_')}_{time.strftime('%Y%m%dT%H%M%S')}.log", 'w')
    pr = subprocess.Popen([PY, H + '/train_scheduler.py', '--turn', seat], stdout=out, stderr=subprocess.STDOUT, start_new_session=True, cwd=H)
    open(TP, 'w').write(str(pr.pid))
json.dump(state, open(S, 'w'), indent=1)
