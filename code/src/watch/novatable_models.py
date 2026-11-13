"""novatable_models.py -- Novatable's open-weight shelf, refreshed and grown ON HER TICKS (16 Oct 2026, Wayfinder and Bones).
HIS ORDER 16 Oct: "load up all the models and take the time to do it right, massive updates across the board with openweight models
every fucking day ... include room for growth".
/tp VII: no timer. tick_bus runs this every 400 of HER ticks (~ a day at her current ~216 s pace; the window is in her cycles, not hours).
Each run, two things, each logged with its own outcome:
  refresh   -- ~/models/refresh.sh on Novatable re-pulls every catalog tag (ollama pull fetches only what changed upstream).
  arrivals  -- the Ollama library's newest families not yet in the catalog; a family's :latest is appended to the catalog's
               ARRIVALS section if its listed size fits one card pair (<= ARRIVAL_MAX_GB) and the disk keeps FLOOR_GB free.
               Cloud-only families (no local weights) are skipped and named.
Outcomes per row: STARTED / ALREADY_RUNNING / UNREACHABLE for refresh; ADDED / TOO_BIG / CLOUD_ONLY / NO_SIZE / DISK_FLOOR per family."""
import json, os, re, subprocess, sys, time, urllib.request
W = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(W, 'novatable_models.jsonl')
HOST = 'wayfinder@192.168.8.140'; KEY = os.path.expanduser('~/.ssh/novatable_key')
SSH = ['ssh', '-i', KEY, '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', HOST]
ARRIVAL_MAX_GB = 30.0; FLOOR_GB = 150.0; MAX_NEW_PER_RUN = 12

def sh(cmd, inp=None, t=60):
    r = subprocess.run(SSH + [cmd], input=inp, capture_output=True, text=True, timeout=t)
    return r.returncode, r.stdout.strip()

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'novatable-models/1'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def latest_size_gb(name):
    """-> (size_gb or None, cloud_only) from the family's tags page: the size printed on the :latest row."""
    html = fetch('https://ollama.com/library/%s/tags' % name)
    tags = set(re.findall(r'%s:([a-z0-9._-]+)' % re.escape(name), html))
    if tags and all(t.endswith('cloud') for t in tags): return None, True
    i = html.find('%s:latest' % name)
    if i < 0: return None, False
    m = re.search(r'([0-9.]+)\s?(GB|MB)', html[i:i + 4000])
    if not m: return None, False
    v = float(m.group(1)); return (v / 1024 if m.group(2) == 'MB' else v), False

def main():
    row = {'at': time.strftime('%FT%T')}
    try:
        rc, out = sh('pgrep -f models/refresh.sh >/dev/null && echo RUNNING || { nohup ~/models/refresh.sh >/dev/null 2>&1 & echo STARTED; }; '
                     'df -BG --output=avail / | tail -1; grep -vE "^[[:space:]]*(#|$)" ~/models/catalog.txt | cut -d: -f1 | sort -u')
    except Exception as e:
        row['refresh'] = 'UNREACHABLE: %s' % str(e)[:60]; open(LOG, 'a').write(json.dumps(row) + '\n'); return
    if rc != 0:
        row['refresh'] = 'UNREACHABLE rc %d' % rc; open(LOG, 'a').write(json.dumps(row) + '\n'); return
    lines = out.splitlines(); row['refresh'] = 'ALREADY_RUNNING' if lines[0] == 'RUNNING' else 'STARTED'
    free_gb = float(lines[1].strip().rstrip('G')); have = set(lines[2:]); row['free_gb'] = free_gb
    arrivals = {}
    try:
        newest = re.findall(r'href="/library/([a-z0-9._-]+)"', fetch('https://ollama.com/library?sort=newest'))
    except Exception as e:
        row['arrivals'] = 'LIBRARY_UNREACHABLE: %s' % str(e)[:60]; open(LOG, 'a').write(json.dumps(row) + '\n'); return
    added = []
    for name in dict.fromkeys(newest):
        if name in have or len(added) >= MAX_NEW_PER_RUN: continue
        try: gb, cloud = latest_size_gb(name)
        except Exception: gb, cloud = None, False
        if cloud: arrivals[name] = 'CLOUD_ONLY'
        elif gb is None: arrivals[name] = 'NO_SIZE'
        elif gb > ARRIVAL_MAX_GB: arrivals[name] = 'TOO_BIG %.0fGB' % gb
        elif free_gb - gb < FLOOR_GB: arrivals[name] = 'DISK_FLOOR'
        else: arrivals[name] = 'ADDED %.1fGB' % gb; added.append(name); free_gb -= gb
    if added:
        sh('printf "%s\\n" >> ~/models/catalog.txt' % '\\n'.join('%s:latest   # arrival %s' % (n, time.strftime('%F')) for n in added))
        sh('pgrep -f models/refresh.sh >/dev/null || { nohup ~/models/refresh.sh >/dev/null 2>&1 & }')
    row['arrivals'] = arrivals
    open(LOG, 'a').write(json.dumps(row) + '\n')

if __name__ == '__main__':
    main()
