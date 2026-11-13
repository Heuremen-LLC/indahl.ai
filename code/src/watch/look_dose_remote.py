"""look_test.v1 poller -- runs ON Armature via ssh stdin. Registered in watch/look_test_claim.v1.json BEFORE it ran.
Arms per 900 s slot: 0 / 30 / 120 extra polls a minute, each poll the sampler's own per-step work. Kernel counters at
both slot edges; xmrig's 15-min average read once at each slot's end (every arm). Prints one JSON line per slot."""
import hashlib, json, re, time, urllib.request
import psutil
SEED, T0, SLOT, N, DOSES = '23e470db7e0e5ba500ae04c5', 1791950400, 900.0, 32, (0, 30, 120)
TOKEN = None
try:
    _m = re.search(r"^TOKEN\s*=\s*'([0-9a-f]{32})'", open(r'C:/Users/Heure/xmrig_wow/wow_guard.py', encoding='utf-8').read(), re.M)
    TOKEN = _m.group(1) if _m else None
except Exception:
    pass
URL = 'http://127.0.0.1:18088/2/summary'
def api():
    rq = urllib.request.Request(URL, headers={'Authorization': 'Bearer ' + TOKEN} if TOKEN else {})
    return json.loads(urllib.request.urlopen(rq, timeout=5).read())
def counters():
    o = {'miner': 0.0, 'her': 0.0, 'pids': []}
    for p in psutil.process_iter(['name']):
        n = (p.info['name'] or '').lower()
        try:
            if n.startswith('xmrig'):
                c = p.cpu_times(); o['miner'] += c.user + c.system; o['pids'].append(p.pid)
            elif 'llama' in n or 'ollama' in n:
                c = p.cpu_times(); o['her'] += c.user + c.system
        except Exception:
            pass
    t = psutil.cpu_times(); me = psutil.Process().cpu_times()
    o.update(busy=t.user + t.system, me=me.user + me.system, t=time.time()); return o
def poll():
    try: api()
    except Exception: pass
    for p in psutil.process_iter(['name']):
        try: p.cpu_times()
        except Exception: pass
    psutil.cpu_times()
for k in range(N):
    s0 = T0 + k * SLOT; s1 = s0 + SLOT
    if time.time() >= s1: continue
    if time.time() < s0: time.sleep(s0 - time.time())
    arm = int(hashlib.sha256(('%s|%d' % (SEED, k)).encode()).hexdigest(), 16) % 3; dose = DOSES[arm]
    a = counters(); n = 0
    if dose:
        period, nxt = 60.0 / dose, time.time()
        while True:
            t = time.time()
            if t >= s1: break
            if t >= nxt: poll(); n += 1; nxt += period
            else: time.sleep(min(nxt - t, s1 - t))
    else:
        time.sleep(max(0.0, s1 - time.time()))
    b = counters()
    try:
        s = api(); h = (s.get('hashrate') or {}).get('total') or [None, None, None]; paused, up = s.get('paused'), s.get('uptime')
    except Exception as e:
        h, paused, up = [None, None, None], 'unread: %s' % type(e).__name__, None
    dt = b['t'] - a['t']
    print(json.dumps({'slot': k, 's0': s0, 's1': s1, 'arm': arm, 'dose_per_min': dose, 'polls': n, 'achieved_per_min': round(n * 60.0 / dt, 2),
                      'dt': round(dt, 2), 'R15': h[2], 'R60': h[1], 'R10': h[0], 'paused_at_end': paused, 'xmrig_uptime': up,
                      'miner_cores': round((b['miner'] - a['miner']) / dt, 4), 'her_cores': round((b['her'] - a['her']) / dt, 4),
                      'busy_cores': round((b['busy'] - a['busy']) / dt, 4), 'poller_cores': round((b['me'] - a['me']) / dt, 5),
                      'miner_pids_same': a['pids'] == b['pids']}), flush=True)
