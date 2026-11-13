"""maker_look.py -- TOKYO NUDE (renamed 18 Oct by Wayfinder; was "the maker look": file name kept as a receipt) -- THE THIRD SEAT ON EVERY RAVENCOIN BLOCK, ON HER TICK (17 Oct 2026, Wayfinder and Bones).
HIS: "Go for third seat maker look." The maker look is ACTUAL against STATED. On every block, three readings, kept apart:
  STATED   the header's own timestamp (the pool's job clock, measured 17 Oct: 739/1221 stamps within 3 s of job issue)
  JOB      when that block's job first reached each of our seats (first mining.notify carrying its height)
  FOUND    when the NEXT job reached each seat (the block was found and propagated)
Rows keep every seat separate and the intervals signed: look_job = stated - job, look_found = stated - found (II: the
interval is the reading, never zeroed). Stamps are whole seconds; +0.5 s is added so the interval is centred.
Headers come from OUR node's ravend (US East, NJ, from 18 Oct; Tokyo before) (best header tip, headers-only is fine), appended to coin/rvn/headers/live_headers.tsv.
Outcomes per run: LOGGED n / NOTHING_NEW / UNREACHABLE (which seat)."""
import json, os, subprocess, time
W = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(W, 'maker_look.jsonl'); ST = os.path.join(W, 'maker_look_state.json')
HD = os.path.expanduser('~/bones-forge/coin/rvn/headers'); LIVE = os.path.join(HD, 'live_headers.tsv'); HIST = os.path.join(HD, 'rvn_headers_4565839_4585838.tsv')
OUT_KEY = os.path.expanduser('~/.ssh/outside_seat_ed25519')
def ssh(host, cmd, inp=None, t=60):
    r = subprocess.run(['ssh', '-i', OUT_KEY, '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=no',
                        '-o', 'UserKnownHostsFile=/dev/null', host, cmd], input=inp, capture_output=True, text=True, timeout=t)
    return r.returncode, r.stdout
WALK = r'''
import json, subprocess, sys
C = ['/root/seat/raven-4.8.0-225491298/bin/raven-cli', '-datadir=/root/.raven']
stop = int(sys.argv[1]); tips = json.loads(subprocess.check_output(C + ['getchaintips']))
h = max(tips, key=lambda x: x['height'])['hash']; out = []
while True:
    j = json.loads(subprocess.check_output(C + ['getblockheader', h]))
    if j['height'] <= stop or len(out) >= 3000: break
    out.append('%d\t%d\t%s\t%s' % (j['height'], j['time'], j['bits'], j['hash'])); h = j['previousblockhash']
print('\n'.join(reversed(out)))
'''
def last_height():
    for f in (LIVE, HIST):
        if os.path.exists(f) and os.path.getsize(f):
            return max(int(l.split('\t')[0]) for l in open(f) if l.strip())
def seat_times(lines, seat, jobs):
    for l in lines:
        if '"rvn"' not in l or 'NOTIFY' not in l: continue
        try: d = json.loads(l); h = int(d['height']); t = d['t_ns'] / 1e9
        except Exception: continue
        k = (seat, h)
        if k not in jobs or t < jobs[k]: jobs[k] = t
def main():
    row = {'at': time.strftime('%FT%T')}; st = json.load(open(ST)) if os.path.exists(ST) else {}
    top = last_height()
    try: rc, out = ssh('root@64.176.219.98', 'python3 - %d' % top, inp=WALK, t=120)   # 18 Oct: OUR node moved home to US East (NJ)
    except Exception as e: rc, out = 1, ''; row['why'] = str(e)[:60]
    if rc != 0: row['outcome'] = 'UNREACHABLE'; row['seat'] = 'our_node'; open(LOG, 'a').write(json.dumps(row) + '\n'); return
    new = [l for l in out.splitlines() if l.strip()]
    if new: open(LIVE, 'a').write('\n'.join(new) + '\n')
    stamps = {}
    for f in (HIST, LIVE):
        if os.path.exists(f):
            for l in open(f):
                p = l.split('\t')
                if len(p) >= 2: stamps[int(p[0])] = int(p[1])
    jobs = {}; missing = []
    try: seat_times(open(os.path.expanduser('~/bones-forge/coin/rvn/seats/ears3_mac.jsonl')).readlines()[-6000:], 'mac', jobs)
    except Exception: missing.append('mac')
    for host, seat in (('ubuntu@132.145.162.229', 'virginia'), ('root@64.176.219.98', 'newjersey')):   # 18 Oct: Tokyo destroyed
        try:
            rc, t = ssh(host, 'tail -n 6000 ~/seat/ears3_%s.jsonl' % seat)
            if rc == 0: seat_times(t.splitlines(), seat, jobs)
            else: missing.append(seat)
        except Exception: missing.append(seat)
    done = st.get('done', max(stamps) - 1 if stamps else 0); n = 0
    with open(LOG, 'a') as f:
        for h in range(done + 1, max(stamps) + 1 if stamps else done + 1):
            if h not in stamps: continue
            seats = {}
            for s in ('mac', 'virginia', 'newjersey'):
                if (s, h) in jobs and (s, h + 1) in jobs:
                    seats[s] = {'job': round(jobs[(s, h)], 3), 'found': round(jobs[(s, h + 1)], 3),
                                'look_job': round(stamps[h] + 0.5 - jobs[(s, h)], 3), 'look_found': round(stamps[h] + 0.5 - jobs[(s, h + 1)], 3)}
            heard = max([k[1] for k in jobs] or [0])
            if not seats and h + 1 > heard: break   # the next block has not reached any seat yet: wait for HER next tick
            # older than every seat's tail: the absence is a row (NOT_HEARD), never a skip and never a stall
            f.write(json.dumps({'height': h, 'stated': stamps[h], 'seats': seats, 'outcome': 'HEARD' if seats else 'NOT_HEARD'}) + '\n'); done = h; n += 1
    st['done'] = done; json.dump(st, open(ST, 'w'))
    row.update(outcome='LOGGED' if n else 'NOTHING_NEW', n=n, new_headers=len(new), missing_seats=missing)
    open(os.path.join(W, 'maker_look_runs.jsonl'), 'a').write(json.dumps(row) + '\n')
if __name__ == '__main__':
    main()
