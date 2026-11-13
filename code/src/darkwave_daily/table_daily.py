"""table_daily.py -- tick-bus rider (every 6 ticks, same cadence as clock_daily.py). One daily Darkwave kit table per chip per UTC day.
Gates: DAILY_ON in the clock folder (the clock's own gate) and TABLE_ON in this folder. Neither is created by the code.
A fire is launched once per chip per day (marker fired_<day>_<chip>, written before the launch, so a failed fire is never retried by this rider).
Order on a chip: from FROM_HOUR UTC, after the clock's own fire for that chip today has left its marker and is no longer running (or from
LATE_HOUR UTC if the clock left no marker, for example because it had too few seconds), never while a clock fire or a table fire of that chip runs.
The dry run must pass its checks and report at least FLOOR seconds left (daily_table.py refuses the same way when fired).
When a table is complete and PUSH_ON exists in this folder, push_tables.py publishes it to KV once (marker PUSHED in the day folder)."""
import os, sys, glob, re, json, subprocess, datetime as dt
H = os.path.dirname(os.path.abspath(__file__))
CLOCK = os.environ.get('DWD_CLOCK_DIR') or os.path.expanduser('~/bones-forge/the_show/runs/2026-10-31-darkwave-clock')
PY = os.environ.get('DWD_PY') or os.path.expanduser('~/bones-forge/qvenv/bin/python')
CHIPS = ('ibm_kingston', 'ibm_marrakesh'); FLOOR = 60; FROM_HOUR = 12; LATE_HOUR = 18   # 6 Nov: was 600 s and held back the 4 and 5 Nov tables (a table costs ~12 s); 60 = the clock's reserve
if not os.path.exists(os.path.join(CLOCK, 'DAILY_ON')) or not os.path.exists(os.path.join(H, 'TABLE_ON')): print('table daily: off (no DAILY_ON or no TABLE_ON)'); sys.exit(0)
now = dt.datetime.fromisoformat(os.environ['DWD_NOW']) if os.environ.get('DWD_NOW') else dt.datetime.now(dt.timezone.utc); day = now.strftime('%Y%m%d')
def running(pattern): return bool(subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True).stdout.split())
for chip in CHIPS:
    mark = os.path.join(H, f'fired_{day}_{chip}')
    if os.path.exists(mark) or glob.glob(os.path.join(H, f'day_{day}_*_{chip}')): continue
    if now.hour < FROM_HOUR: continue
    if running(f'fire_clock.py {chip} --fire') or running(f'daily_table.py {chip} --fire'): continue
    if not os.path.exists(os.path.join(CLOCK, f'fired_{day}_{chip}')) and now.hour < LATE_HOUR: continue
    dry = subprocess.run([PY, '-I', os.path.join(H, 'daily_table.py'), chip], capture_output=True, text=True, cwd=H).stdout
    m = re.search(r'checks PASS.*remaining (\d+)', dry)
    if not m: print('table daily:', chip, 'dry run did not pass, no fire today'); open(mark, 'w').write('dry run did not pass\n' + dry[-2000:]); continue
    if int(m.group(1)) < FLOOR: print('table daily:', chip, 'only', m.group(1), 's left, no fire'); continue
    open(mark, 'w').write(now.isoformat() + ' launched, ' + m.group(1) + ' s left at the dry run\n')
    subprocess.Popen([PY, '-I', os.path.join(H, 'daily_table.py'), chip, '--fire'], cwd=H, start_new_session=True,
                     stdout=open(os.path.join(H, f'fire_{day}_{chip}.log'), 'a'), stderr=subprocess.STDOUT)
    print('table daily: fired', chip, 'for', day)
if os.path.exists(os.path.join(H, 'PUSH_ON')):
    todo = []
    for chip in CHIPS:
        for d in sorted(glob.glob(os.path.join(H, f'day_*_{chip}'))):
            try: rec = json.load(open(os.path.join(d, 'job_daily_table.json')))
            except Exception: continue
            if rec['jobs'][0].get('status') == 'DONE' and glob.glob(os.path.join(d, 'kick_table_*.json')) and not os.path.exists(os.path.join(d, 'PUSHED')): todo.append(d)
    if todo and not running('daily_table.py'):
        r = subprocess.run([PY, '-I', os.path.join(H, 'push_tables.py')], capture_output=True, text=True, cwd=H)
        if r.returncode == 0:
            for d in todo: open(os.path.join(d, 'PUSHED'), 'w').write(now.isoformat() + '\n')
            print('table daily: published', len(todo), 'table(s)')
        else: print('table daily: push FAILED', r.stdout[-200:])
