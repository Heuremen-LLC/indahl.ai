#!/usr/bin/env python3
"""petrol_rider.py (12 Nov 2026): tick-bus rider for ATLAS PETROL. At most one run a day.
Thursday (after Wednesday's EIA release) or 7+ days since the last EIA pull: run_petrol.sh --refresh (re-pulls the two EIA files).
13th to 16th of the month: run_petrol.sh (tries the new OPEC MOMR). Other days: nothing.
summary_petrol.json moves only when the readings move, and auto_ship.py ships when it does. A failed run writes an alert line, no retry loop."""
import json, os, subprocess, time
H = os.path.dirname(os.path.abspath(__file__)); ST = H + '/data/rider_state.json'; AL = os.path.expanduser('~/bones-forge/alerts/ALERTS_OPEN.txt')
st = json.load(open(ST)) if os.path.exists(ST) else {}
now = time.time(); lt = time.localtime(); today = time.strftime('%Y-%m-%d', lt)
if st.get('last_day') == today: print('petrol rider: already ran today'); raise SystemExit(0)
eia = lt.tm_wday == 3 or now - st.get('last_eia', 0) > 7 * 86400
momr = 13 <= lt.tm_mday <= 16
if not (eia or momr): print('petrol rider: nothing due today'); raise SystemExit(0)
cmd = ['bash', H + '/run_petrol.sh'] + (['--refresh'] if eia else [])
r = subprocess.run(cmd, cwd=H, capture_output=True, text=True, timeout=1800, env=dict(os.environ, PATH='/opt/homebrew/bin:/usr/bin:/bin'))
st['last_day'] = today
if eia and r.returncode == 0: st['last_eia'] = now
json.dump(st, open(ST, 'w'))
if r.returncode == 0: subprocess.run(['/opt/homebrew/bin/python3', '-I', H + '/push_live.py'], cwd=H, capture_output=True, text=True, timeout=300)   # /petrol/live.json follows each good run
if r.returncode != 0:
    with open(AL, 'a') as f: f.write('%s PETROL: run_petrol.sh failed (rc %d): %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), r.returncode, (r.stdout + r.stderr)[-200:].replace('\n', ' ')))
print('petrol rider: ran %s, rc %d' % (' '.join(cmd[1:]), r.returncode))
