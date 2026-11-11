"""clock_run.py: runs a desk's own tick, unmodified, with the clock pinned to the time the published run read.
  python3 clock_run.py <tick.py> <the run's feed file> [tick arguments]
The tick reads the clock once at its top (NOW = time.time()) and uses it to tell a settled day, a passed approach or a closed window from one
still open, so a later clock can move rows between those classes. The time comes from the generated field of the feed file that run wrote.
Nothing else is changed, and --publish is never passed."""
import calendar, json, os, runpy, sys, time
script, feed = sys.argv[1], sys.argv[2]
d = json.load(open(feed)); NOW = float(calendar.timegm(time.strptime((d.get('generated') or d['updated'])[:19], '%Y-%m-%dT%H:%M:%S')))
time.time = lambda: NOW
if '--publish' in sys.argv: sys.exit('clock_run: --publish is never passed')
sys.argv = [script] + sys.argv[3:]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), script), run_name='__main__')
