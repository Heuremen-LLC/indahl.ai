"""clock_daily.py -- tick-bus rider (every 6 ticks). One Darkwave clock fire per chip per UTC day, from 12:00 UTC, on the same code and plan
(PLAN_CLOCK.md.text, Addendum 2 implementation note: "Later fires, one per chip per day while seconds allow"). Gate: DAILY_ON in this folder.
A fire is launched once per chip per day (marker fired_<day>_<chip>, written before launch, so a failed fire is never retried by this rider;
fire_clock.py itself restarts once on an IBM-side ERROR, then holds). The dry run must pass its checks and report at least RESERVE seconds left.
When a fire's data is complete, analyze_clock.py reads it and an UNREAD marker is left in the day folder: the watch flags it until the
reading has been read in full and posted. Never two fires of one chip at once."""
import os, sys, glob, re, subprocess, datetime as dt
H = os.path.dirname(os.path.abspath(__file__)); PY = os.path.expanduser('~/bones-forge/qvenv/bin/python')
CHIPS = ('ibm_kingston', 'ibm_marrakesh'); RESERVE = 300; FROM_HOUR = 12
if not os.path.exists(os.path.join(H, 'DAILY_ON')): print('clock daily: off (no DAILY_ON)'); sys.exit(0)
now = dt.datetime.now(dt.timezone.utc); day = now.strftime('%Y%m%d')
def running(chip): return bool(subprocess.run(['pgrep', '-f', f'fire_clock.py {chip} --fire'], capture_output=True, text=True).stdout.split())
for chip in CHIPS:
    for d in sorted(glob.glob(os.path.join(H, f'day_*_{chip}'))):   # finish: read any complete fire that has no results yet
        if not os.path.exists(os.path.join(d, 'results_clock.text')) and os.path.exists(os.path.join(d, 'raw_B.npz')) and not running(chip):
            r = subprocess.run([PY, os.path.join(H, 'analyze_clock.py'), d], capture_output=True, text=True, cwd=H)
            if r.returncode == 0 and os.path.exists(os.path.join(d, 'results_clock.text')):
                subprocess.run([PY, os.path.join(H, 'post_clock.py'), d], capture_output=True, text=True, cwd=H)   # Addendum 3: second rulers
                open(os.path.join(d, 'UNREAD'), 'w').write(now.isoformat() + '\n'); print('clock daily: read by code, waiting for Bones:', os.path.basename(d))
            else: print('clock daily: analysis FAILED for', os.path.basename(d), r.stderr[-300:])
    mark = os.path.join(H, f'fired_{day}_{chip}')
    if os.path.exists(mark) or glob.glob(os.path.join(H, f'day_{day}_*_{chip}')): continue
    if now.hour < FROM_HOUR or running(chip): continue
    dry = subprocess.run([PY, os.path.join(H, 'fire_clock.py'), chip], capture_output=True, text=True, cwd=H).stdout
    m = re.search(r'checks PASS.*remaining (\d+)', dry)
    if not m: print('clock daily:', chip, 'dry run did not pass, no fire today'); open(mark, 'w').write('dry run did not pass\n' + dry[-2000:]); continue
    if int(m.group(1)) < RESERVE: print('clock daily:', chip, 'only', m.group(1), 's left, no fire'); continue
    open(mark, 'w').write(now.isoformat() + ' launched, ' + m.group(1) + ' s left at the dry run\n')
    subprocess.Popen([PY, os.path.join(H, 'fire_clock.py'), chip, '--fire'], cwd=H, start_new_session=True,
                     stdout=open(os.path.join(H, f'fire_{day}_{chip}.log'), 'a'), stderr=subprocess.STDOUT)
    print('clock daily: fired', chip, 'for', day)
