#!/usr/bin/env python3
"""capacity_watch.py (11 Nov 2026, Wayfinder: "It's money out the window when we're not working the metal man").

Tick-bus rider (every 3 ticks). Reads how hard the Mac and Armature are working and what the training pipeline is waiting on,
keeps a short history, and says plainly when metal sits idle and why:
  Mac      GPU busy % (ioreg), load average, MLX seat servers, harvest/train processes
  Armature GPU busy % and VRAM (nvidia-smi), CPU load %, models loaded in Ollama
  pipeline seconds since each harvest log last moved, judge reply time (every 6th run, one tiny request per judge)
Writes watch/capacity.json (latest + 48 readings) and watch/CAPACITY.md (plain advice). When a machine has been idle for 30 min
while work is waiting, or a harvest has been silent 45 min, it appends one line to alerts/ALERTS_OPEN.txt (once per condition per 3 h).
Read-only on everything else. Python 3.9, standard library only."""
import json, os, re, subprocess, time, urllib.request

B = os.path.expanduser('~/bones-forge'); W = B + '/watch'; OUT = W + '/capacity.json'; MD = W + '/CAPACITY.md'
ALERTS = B + '/alerts/ALERTS_OPEN.txt'; SV = B + '/sage_library/sage_v'
ARM_SSH = ['ssh', '-o', 'ConnectTimeout=6', '-o', 'BatchMode=yes', 'armature']
JUDGES = {'mac': 'http://127.0.0.1:8892', 'armature': 'http://192.168.8.158:8892', 'laptop': 'http://192.168.8.145:8892'}


def sh(cmd, t=20):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=t).stdout
    except Exception: return ''


def mac():
    o = sh(['ioreg', '-r', '-d', '1', '-w', '0', '-c', 'IOAccelerator'])
    m = re.search(r'"Device Utilization %"=(\d+)', o)
    la = sh(['sysctl', '-n', 'vm.loadavg']).split()
    ps = sh(['ps', '-axo', 'etime=,%cpu=,command='])
    procs = {k: sum(1 for l in ps.splitlines() if k in l) for k in ('harvest.py', 'train_live.py', 'mlx_lm lora', 'mlx_lm server', 'dpo')}
    return {'gpu_pct': int(m.group(1)) if m else None, 'load1': float(la[1]) if len(la) > 1 else None, 'procs': procs}


def armature():
    g = sh(ARM_SSH + ['nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits'])
    c = sh(ARM_SSH + ['powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"'])
    r = {'reachable': bool(g.strip())}
    try:
        u, mu, mt = [float(x) for x in g.strip().split(',')[:3]]; r.update(gpu_pct=u, vram_used_gb=round(mu / 1024, 1), vram_total_gb=round(mt / 1024, 1))
    except Exception: pass
    try: r['cpu_pct'] = float(c.strip().splitlines()[-1])
    except Exception: pass
    try:
        d = json.load(urllib.request.urlopen('http://192.168.8.158:11434/api/ps', timeout=6))
        r['ollama'] = [{'name': x['name'], 'on_gpu': bool(x.get('size_vram'))} for x in d.get('models', [])]
    except Exception: r['ollama'] = None
    return r


def pipeline(run_n):
    now = time.time(); logs = {}
    for f in sorted(os.listdir(SV + '/train')):
        if f.startswith('harvest_out_') and f.endswith('.log'):
            logs[f[12:-4]] = int(now - os.path.getmtime(SV + '/train/' + f))
    running = sh(['ps', '-axo', 'command=']); live = {s for s in logs if ('harvest.py ' + s.replace('_', ':', 1).split(':')[0]) in running or s.split('_')[0] in running}
    out = {'harvest_silent_s': {s: v for s, v in logs.items() if s in live}}
    if run_n % 6 == 0:
        jt = {}
        for k, u in JUDGES.items():
            t0 = time.time()
            try:
                urllib.request.urlopen(urllib.request.Request(u, json.dumps({'doc': 'The pump runs at night.', 'claim': 'The pump runs at night %d.' % int(now)}).encode(), {'Content-Type': 'application/json'}), timeout=90)
                jt[k] = round(time.time() - t0, 1)
            except Exception: jt[k] = None
        out['judge_reply_s'] = jt
    return out


def advise(hist):
    cur = hist[-1]; tips = []
    recent = hist[-10:]   # about 30 min at 3 ticks a run
    mg = [h['mac'].get('gpu_pct') for h in recent if h['mac'].get('gpu_pct') is not None]
    ag = [h['arm'].get('gpu_pct') for h in recent if h['arm'].get('gpu_pct') is not None]
    ac = [h['arm'].get('cpu_pct') for h in recent if h['arm'].get('cpu_pct') is not None]
    silent = cur['pipe'].get('harvest_silent_s', {})
    stuck = {s: v for s, v in silent.items() if v > 45 * 60}
    if len(mg) >= 6 and max(mg) < 10:
        tips.append(('mac_idle', 'Mac GPU under 10% for the last %d readings. %s' % (len(mg), 'Harvests are waiting (%s), so the judge is the bottleneck: serve the judge model on the Mac GPU.' % ', '.join(sorted(stuck)) if stuck else 'Nothing is queued for it: start the next training turn or an eval on the Mac.')))
    if len(ag) >= 6 and max(ag) < 10:
        tips.append(('arm_gpu_idle', 'Armature GPU under 10%% for the last %d readings (VRAM %s of %s GB). Put a judge or a training job on it.' % (len(ag), cur['arm'].get('vram_used_gb'), cur['arm'].get('vram_total_gb'))))
    if ac and len(ag) >= 3 and max(ac[-3:]) > 80 and max(ag[-3:]) < 15:
        tips.append(('arm_cpu_bound', 'Armature CPU above 80% while its GPU is under 15%: a model is running on CPU there (check Ollama: %s).' % ', '.join(x['name'] + (' GPU' if x['on_gpu'] else ' CPU') for x in (cur['arm'].get('ollama') or []))))
    for s, v in stuck.items(): tips.append(('stall_' + s, 'Harvest %s silent for %d min.' % (s, v // 60)))
    jt = next((h['pipe']['judge_reply_s'] for h in reversed(hist) if 'judge_reply_s' in h['pipe']), {})
    slow = {k: v for k, v in jt.items() if v is None or v > 20}
    if slow: tips.append(('judge_slow', 'Judge replies slow or timing out: ' + ', '.join('%s %s' % (k, ('timeout' if v is None else '%.0f s' % v)) for k, v in slow.items()) + '. One tiny request should take under 5 s.'))
    if not cur['arm'].get('reachable'): tips.append(('arm_down', 'Armature not reachable over ssh.'))
    return tips


def main():
    st = json.load(open(OUT)) if os.path.exists(OUT) else {'hist': [], 'n': 0, 'alerted': {}}
    st['n'] = st.get('n', 0) + 1
    r = {'t': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'mac': mac(), 'arm': armature(), 'pipe': pipeline(st['n'])}
    st['hist'] = (st['hist'] + [r])[-48:]; tips = advise(st['hist']); st['advice'] = [t for _, t in tips]
    now = time.time()
    for k, t in tips:
        if now - st['alerted'].get(k, 0) > 3 * 3600 and k != 'judge_slow' or (k == 'judge_slow' and now - st['alerted'].get(k, 0) > 3 * 3600):
            with open(ALERTS, 'a') as f: f.write('%s CAPACITY: %s\n' % (r['t'], t))
            st['alerted'][k] = now
    json.dump(st, open(OUT, 'w'), indent=1)
    m, a = r['mac'], r['arm']
    open(MD, 'w').write('# Capacity, %s UTC\n\n- Mac: GPU %s%%, load %s, processes %s\n- Armature: GPU %s%%, CPU %s%%, VRAM %s of %s GB, Ollama %s\n- Harvest logs silent (s): %s\n\n## Advice\n%s\n'
                        % (r['t'], m.get('gpu_pct'), m.get('load1'), m.get('procs'), a.get('gpu_pct'), a.get('cpu_pct'), a.get('vram_used_gb'), a.get('vram_total_gb'),
                           a.get('ollama'), r['pipe'].get('harvest_silent_s'), '\n'.join('- ' + t for t in st['advice']) or '- Both machines are working.'))
    print('capacity: ' + ('; '.join(st['advice']) if st['advice'] else 'both machines working'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
