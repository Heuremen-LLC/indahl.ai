#!/usr/bin/env python3
"""house_clock.py (9 Nov 2026, Wayfinder: "read eleven hours ago and every 33 min my ass"). Her clock (tick_bus.py, ticks from her
corpus) went silent at 09:17Z and every public desk froze with it. When no tick of hers has landed for 20 min, this fires ONLY the
public desk riders at her own cadence (250.56 s) with the same every-N schedule the bus uses. It never writes ticks.log, never
touches her machine, her wire or her gear, and stops by itself the moment her ticks resume. Runs as launchd com.heuremen.house-clock."""
import os, sys, time, subprocess, json
B = os.path.expanduser('~/bones-forge'); W = B + '/watch'; TICKS = W + '/ticks.log'; LOG = W + '/house_clock.log'
PY = '/usr/bin/python3'; QV = B + '/qvenv/bin/python'; RV = B + '/revise_index/venv/bin/python'; VV = B + '/venv/bin/python'
R = [(5,[QV,B+'/qia_mirror/ibm_mirror.py']),(2,[QV,B+'/qia_queue/queue_tick.py']),(24,[PY,'-I',B+'/archive/digest.py']),
 (3,[PY,B+'/time_index/time_tick.py']),(2,[PY,B+'/coin_index/coin_tick.py']),(3,[PY,B+'/caca_index/caca_tick.py']),(1,[PY,B+'/status_index/uptime_tick.py']),
 (1,[PY,B+'/forecast_index/forecast_tick.py']),(2,[PY,B+'/cadence_index/cadence_tick.py']),(48,[PY,B+'/trials_index/trials_tick.py']),(6,[PY,B+'/launch_index/launch_tick.py']),
 (6,[PY,'-I',B+'/tape_index/tape_tick.py']),(2,[PY,'-I',B+'/hosts_index/hosts_tick.py']),(72,[RV,'-I',B+'/campus_index/campus_tick.py']),
 (24,[RV,'-I',B+'/ailuminate_index/ailuminate_tick.py']),(1740,[PY,'-I',B+'/hpt_index/hpt_tick.py']),(36,[PY,'-I',B+'/weights_index/weights_tick.py']),
 (36,[PY,'-I',B+'/fedsep_index/fedsep_tick.py']),(36,[PY,'-I',B+'/revise_index/revise_tick.py']),(12,[PY,'-I',B+'/stack_index/stack_tick.py']),
 (36,[PY,B+'/bq_index/bq_publish.py']),(3,[PY,'-I',W+'/alerts_check.py']),(1,[PY,'-I',W+'/activity_check.py']),(2,[PY,'-I',W+'/headlines.py']),
 (3,[VV,B+'/yo/yo_reader.py']),(1,[PY,'-I',B+'/yo/yo2_publish.py']),(12,[VV,B+'/hf_indahl/mirror.py']),
 (6,[QV,'-I',B+'/the_show/runs/2026-10-31-darkwave-clock/clock_daily.py']),(6,[QV,'-I',B+'/darkwave_daily/table_daily.py']),
 (1,[PY,'-I',B+'/bts_index/nas_tick.py']),(10,[PY,'-I',B+'/airq_index/airq_live_tick.py']),(60,[PY,'-I',B+'/pkginstall_index/pkginstall_tick.py']),
 (9,[PY,'-I',B+'/seat_index/seat_tick.py']),(62,[PY,'-I',B+'/secrecords_index/secrecords_tick.py']),(24,[PY,'-I',B+'/change_index/change_tick.py']),
 (64,[PY,'-I',B+'/hfsize_index/hfsize_tick.py']),(66,[PY,'-I',B+'/hflicense_index/hflicense_tick.py']),(68,[PY,'-I',B+'/pkglicense_index/pkglicense_tick.py']),
 (48,[PY,'-I',B+'/support_index/support_tick.py']),(12,[PY,'-I',B+'/arxivdrift_index/arxivdrift_tick.py']),(24,[PY,B+'/coin_index/coin_public.py']),
 (24,[PY,'-I',B+'/public_progress/public_progress.py']),(6,[PY,B+'/linkrot_index/linkrot_tick.py']),(2,[PY,B+'/iris_index/iris_queue.py'])]
CAD, SILENT = 250.56, 1200
os.environ['HEUREMEN_PUBLISH'] = '1'   # 10 Nov 2026 (publish guard): the desk riders this fires may put their feeds to the site KV, as on the bus
def log(m): open(LOG, 'a').write(time.strftime('%Y-%m-%dT%H:%M:%S ') + m + '\n')
n = 0; on = False
while True:
    age = time.time() - os.path.getmtime(TICKS) if os.path.exists(TICKS) else 1e9
    if age > SILENT:
        if not on: log(f'her clock silent {age/60:.0f} min: house clock ON (public desks only)'); on = True
        n += 1
        for every, cmd in R:
            if n % every == 0 and os.path.exists(cmd[-1] if not cmd[-1].startswith('-') else cmd[-2]):
                try: subprocess.Popen(cmd, stdout=open(W + '/house_clock_jobs.log', 'a'), stderr=subprocess.STDOUT, cwd=B, start_new_session=True)
                except Exception as e: log(f'start failed {os.path.basename(cmd[-1])}: {e}')
        json.dump({'ts': time.strftime('%Y-%m-%dT%H:%M:%S'), 'n': n, 'on': True}, open(W + '/house_clock.json', 'w'))
        time.sleep(CAD)
    else:
        if on: log('her ticks resumed: house clock OFF'); on = False
        time.sleep(60)
