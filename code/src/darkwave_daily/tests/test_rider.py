#!/usr/bin/env python3
"""Tests of table_daily.py with a stub daily_table.py and stub push script in a temp folder. Run: python3 -I tests/test_rider.py"""
import os, sys, shutil, tempfile, subprocess, json, time
T = os.path.dirname(os.path.abspath(__file__)); H = os.path.dirname(T); FAIL = []
def check(n, c, d=''):
    print(('ok    ' if c else 'FAIL  ') + n + (' ' + d if d else '')); 
    if not c: FAIL.append(n)
tmp = tempfile.mkdtemp(prefix='dwd_rider_'); clock = os.path.join(tmp, 'clock'); os.makedirs(clock); work = os.path.join(tmp, 'w'); os.makedirs(work)
shutil.copy(os.path.join(H, 'table_daily.py'), work)
open(os.path.join(work, 'daily_table.py'), 'w').write('''import sys, os, json
chip = sys.argv[1]; rem = int(os.environ.get("STUB_REM", "1500"))
if "--fire" not in sys.argv:
    print(chip + ": circuits 8; checks PASS; durations (dt) {}; est 12 s, remaining", rem); sys.exit(0)
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "day_20261102_1300_" + chip); os.makedirs(d, exist_ok=True)
json.dump({"jobs": [{"status": "DONE"}]}, open(d + "/job_daily_table.json", "w")); open(d + "/kick_table_x.json", "w").write("{}")
''')
open(os.path.join(work, 'push_tables.py'), 'w').write('import os\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)), "push_ran"), "a").write("x")\n')
def rider(hour, env=None, minute=5):
    e = dict(os.environ, DWD_CLOCK_DIR=clock, DWD_PY=sys.executable, DWD_NOW=f'2026-11-02T{hour:02d}:{minute:02d}:00+00:00', **(env or {}))
    return subprocess.run([sys.executable, '-I', os.path.join(work, 'table_daily.py')], capture_output=True, text=True, env=e, cwd=work).stdout.strip()
def wait(path, s=5):
    t = time.time()
    while time.time() - t < s and not os.path.exists(path): time.sleep(0.1)
    return os.path.exists(path)
check('off without gates', 'off' in rider(13))
open(os.path.join(clock, 'DAILY_ON'), 'w').write('x'); check('off with only the clock gate', 'off' in rider(13))
open(os.path.join(work, 'TABLE_ON'), 'w').write('x')
check('waits for the clock marker before 18:00 UTC', rider(13) == '' and not os.path.exists(os.path.join(work, 'fired_20261102_ibm_kingston')))
open(os.path.join(clock, 'fired_20261102_ibm_kingston'), 'w').write('x')
check('does not fire before 12:00 UTC', rider(11) == '')
out = rider(13); check('fires kingston once the clock marker is there', 'fired ibm_kingston' in out and 'marrakesh' not in out, out)
check('marker written before launch', os.path.exists(os.path.join(work, 'fired_20261102_ibm_kingston')) and wait(os.path.join(work, 'day_20261102_1300_ibm_kingston', 'kick_table_x.json')))
check('no second fire the same day', rider(14) == '')
out = rider(19); check('fires marrakesh from 18:00 UTC without a clock marker', 'fired ibm_marrakesh' in out, out)
wait(os.path.join(work, 'day_20261102_1300_ibm_marrakesh', 'kick_table_x.json')); os.remove(os.path.join(work, 'fired_20261102_ibm_marrakesh')); shutil.rmtree(os.path.join(work, 'day_20261102_1300_ibm_marrakesh'))
shutil.rmtree(os.path.join(work, 'day_20261102_1300_ibm_kingston')); os.remove(os.path.join(work, 'fired_20261102_ibm_kingston'))
out = rider(19, {'STUB_REM': '59'}); check('no fire below the 60 s floor', 'only 59 s left' in out and not os.path.exists(os.path.join(work, 'fired_20261102_ibm_kingston')), out)
check('no push without PUSH_ON', not os.path.exists(os.path.join(work, 'push_ran')))
os.makedirs(os.path.join(work, 'day_20261102_1300_ibm_kingston')); json.dump({'jobs': [{'status': 'DONE'}]}, open(os.path.join(work, 'day_20261102_1300_ibm_kingston', 'job_daily_table.json'), 'w')); open(os.path.join(work, 'day_20261102_1300_ibm_kingston', 'kick_table_x.json'), 'w').write('{}')
open(os.path.join(work, 'PUSH_ON'), 'w').write('x'); out = rider(20, {'STUB_REM': '59'}); check('push runs once with PUSH_ON', 'published 1' in out and open(os.path.join(work, 'push_ran')).read() == 'x', out)
rider(21, {'STUB_REM': '59'}); check('push not repeated', open(os.path.join(work, 'push_ran')).read() == 'x')
shutil.rmtree(tmp); print('ALL PASSED' if not FAIL else 'FAILED ' + ', '.join(FAIL)); sys.exit(1 if FAIL else 0)
