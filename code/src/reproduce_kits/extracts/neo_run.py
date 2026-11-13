"""neo_run.py: runs neo_index/neo_tick.py itself, unmodified, with --offline --no-sbdb, with the clock pinned to the time the published run read
(the generated field of data/neo_live.json). The desk scores an approach against the newest solution only once the approach date has passed
(NOW, line 19), so a later clock would move rows from waiting to scored. Nothing else is changed. --publish is never passed."""
import json, runpy, sys, time, os
import calendar
NOW = calendar.timegm(time.strptime(json.load(open('data/neo_live.json'))['generated'], '%Y-%m-%dT%H:%M:%SZ'))
time.time = lambda: NOW
sys.argv = ['neo_tick.py', '--offline', '--no-sbdb']
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neo_tick.py'), run_name='__main__')
