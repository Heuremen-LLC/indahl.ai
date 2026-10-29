#!/usr/bin/env python3
"""time_tick.py: one TIME round, run by Nova's tick bus as a rider. Runs one probe round on the Pi (the GPS-disciplined reference),
pulls the rolling file, rescores T1 over the last 40 runs, and publishes summary_time.json to the page's KV key. No timers."""
import os, subprocess, json, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
os.chdir(H)   # 28 Oct: check_time_t1.py writes summary_time.json to the cwd, so both seats were read from one stale file
def sh(cmd, to=240): return subprocess.run(cmd, capture_output=True, text=True, timeout=to)
r = sh(['ssh', '-o', 'ConnectTimeout=10', 'flock-pi', 'cd ~/time_index && python3 ntp_probe.py pi probe_roll.jsonl 1 >/dev/null 2>&1; tail -n 14000 probe_roll.jsonl > probe_roll.tmp && mv probe_roll.tmp probe_roll.jsonl'])
r = sh(['scp', '-q', 'flock-pi:time_index/probe_roll.jsonl', os.path.join(H, 'data', 'probe_roll.jsonl')])
if r.returncode: print('time: pi unreachable'); sys.exit(0)
r = sh([sys.executable, os.path.join(H, 'check_time_t1.py'), 'pi', os.path.join(H, 'data', 'probe_roll.jsonl')], 120)
# second network seat: pull the last round the GitHub runner saved, score it, merge beside the Pi's, then ask the runner for the next round (event-driven, no schedule)
try:
    import json, shutil
    GH = '/opt/homebrew/bin/gh'
    raw = sh(['curl', '-s', '-m', '30', 'https://raw.githubusercontent.com/Heuremen-LLC/nodes/main/data/time/latest.jsonl', '-o', os.path.join(H, 'data', 'probe_azure.jsonl')], 60)
    if os.path.getsize(os.path.join(H, 'data', 'probe_azure.jsonl')) > 1000:
        shutil.copy(os.path.join(H, 'summary_time.json'), os.path.join(H, 'summary_time_pi.json'))
        sh([sys.executable, os.path.join(H, 'check_time_t1.py'), 'github-azure', os.path.join(H, 'data', 'probe_azure.jsonl')], 120)
        az = json.load(open(os.path.join(H, 'summary_time.json'))); pi = json.load(open(os.path.join(H, 'summary_time_pi.json'))); azs = {x['server']: x for x in az['servers']}
        for x in pi['servers']:
            y = azs.get(x['server'], {}); x['offset_ms_2'] = y.get('offset_ms'); x['half_delay_ms_2'] = y.get('half_delay_ms'); x['outcome_2'] = y.get('outcome')
        pi['seat2'] = dict(name='GitHub runner network', seat_part_ms=az.get('seat_part_ms'), updated=az.get('updated'))
        json.dump(pi, open(os.path.join(H, 'summary_time.json'), 'w'), indent=1)
    sh([GH, 'api', 'repos/Heuremen-LLC/nodes/dispatches', '-f', 'event_type=time-probe'], 60)
except Exception as e: print('time: second seat step failed', type(e).__name__)
os.chdir(H); env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'time_live', '--path', os.path.join(H, 'summary_time.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('time_live published' if p.returncode == 0 else 'time_live publish FAILED')
