#!/usr/bin/env python3
"""alerts_check.py: tick-bus rider. Looks for real failures in our own streams and writes alerts/open.json and alerts/ALERTS_OPEN.txt.
The alert goes to Bones (every session start and every prompt show the open list), not to a phone. An alert closes itself when its condition stops holding."""
import os, sys, json, time, glob, re, shutil, subprocess, urllib.request
B = os.path.expanduser('~/bones-forge'); A = B + '/alerts'; os.makedirs(A, exist_ok=True)
now = time.time(); found = {}
def j(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u + ('&' if '?' in u else '?') + 'x=%d' % now, headers={'User-Agent': 'heuremen-alerts/0.1'}), timeout=30).read())
    except Exception: return None
def flag(i, what): found[i] = what
# 1 tick bus alive
try:
    age = (now - os.path.getmtime(B + '/watch/ticks.log')) / 60
    if age > 20: flag('tickbus', 'tick bus has not ticked for %d minutes' % age)
except OSError: flag('tickbus', 'tick log missing')
# 2 SEAT: outside runner view of pages and feeds
s = j('https://indahl.ai/seat/live.json')
if s is None: flag('seat:unreachable', 'indahl.ai/seat/live.json could not be read')
else:
    for f in s.get('feeds', []):
        if f.get('state') not in ('FRESH',): flag('feed:' + f['feed'], 'feed %s is %s (age %s h, limit %s h)' % (f['feed'], f.get('state'), f.get('age_h'), f.get('limit_h')))
    for m in s.get('not_matching', []): flag('page:' + m.get('page', '?'), 'page %s: %s' % (m.get('page'), m.get('state')))
    ch = s.get('now', {}).get('Archive chain', {})
    if ch.get('state') not in (None, 'OK'): flag('archive:chain', 'archive chain state %s' % ch.get('state'))
    for v in (s.get('rolling') or {}).values():
        if v.get('newest_probe_hours') is not None and v['newest_probe_hours'] > 3: flag('seat:stale', 'SEAT newest probe is %.1f hours old' % v['newest_probe_hours'])
# 2b CI on the org's repos (30 Oct: the heuremen.org paper workflow sat red four hours unseen): the latest run of each workflow on main
try:
    GH = '/opt/homebrew/bin/gh'
    _rl = subprocess.run([GH, 'repo', 'list', 'Heuremen-LLC', '--limit', '50', '--json', 'name', '--jq', '.[].name'], capture_output=True, text=True, timeout=60)
    if _rl.returncode != 0 or not _rl.stdout.split(): flag('ci:unreadable', 'GitHub repo list returned nothing (rc %s): %s' % (_rl.returncode, (_rl.stderr or '')[-120:]))   # 13 Nov trust-but-verify: an empty list read as no failures
    for rp in _rl.stdout.split():
        seen = set()
        for r in json.loads(subprocess.run([GH, 'run', 'list', '-R', 'Heuremen-LLC/' + rp, '-L', '30', '--branch', 'main', '--json', 'workflowName,conclusion,status,url'], capture_output=True, text=True, timeout=60).stdout or '[]'):
            if r['workflowName'] in seen: continue
            seen.add(r['workflowName'])
            if r['status'] == 'completed' and r['conclusion'] not in ('success', 'skipped', 'neutral'): flag('ci:%s/%s' % (rp, r['workflowName']), 'CI %s/%s %s: %s' % (rp, r['workflowName'], r['conclusion'], r['url']))
except Exception as e: flag('ci:unreadable', 'GitHub Actions could not be read: ' + type(e).__name__)
# 2c (10 Nov, owner: "every update gets a full public commit"): the last ship's public mirror. ship.sh step 5b writes ledger/public_push_status.json.
# rc 3 = the site deployed but push_public.sh skipped the pages (code only). Stays open until a ship mirrors the pages again.
try:
    ps = json.load(open(B + '/ledger/public_push_status.json'))
    if ps.get('rc') == 3: flag('public:pages', 'the ship at %s deployed the site but the public indahl.ai repo got code only, no site pages (ledger/deploy_hash.sh vs the deploy stamp)' % ps.get('at'))
    elif ps.get('ok') is False: flag('public:refused', 'the public repo push at %s was refused or failed: %s' % (ps.get('at'), str(ps.get('last'))[:160]))
except FileNotFoundError: flag('watcher:public_status', 'ledger/public_push_status.json is missing, so the last public push cannot be checked')
except Exception as e: flag('watcher:public_status', 'public push status unreadable: ' + type(e).__name__)   # 13 Nov trust-but-verify
# 2d (10 Nov): the follow channels. websub_ping.py (after each ship and each desk feed push), webhooks_send.py and push_send.py write
# notify_state/<name>_status.json. A ping that failed, or a sender run that could not read the ledger or its list, stays open until a later run is ok.
for _n in ('websub', 'webhooks', 'push', 'alert_guard', 'canary', 'transparency'):   # 10 Nov: alert_guard = an alert refused for an unpublished number, canary = our own webhook missed, got late or mismatched an alert, transparency = the counts could not be written (indahl-ai/alert_receipts.py, canary.py, transparency.py)
    try:
        _st = json.load(open(B + '/notify_state/%s_status.json' % _n))
        if _st.get('ok') is False: flag('notify:' + _n, '%s at %s: %s' % (_n, _st.get('at'), str(_st.get('failed') or _st.get('what'))[:200]))
    except FileNotFoundError: pass   # a channel that has never run has no status file yet
    except Exception as e: flag('watcher:notify_' + _n, '%s status unreadable: %s' % (_n, type(e).__name__))   # 13 Nov trust-but-verify
# 3 STACK rows that returned nothing (some are expected for a while)
EXPECTED_EMPTY = {'WEIGHTS', 'AILUMINATE', 'HOSTS'}
st = j('https://indahl.ai/stack/live.json')
if st is None: flag('stack:unreachable', 'indahl.ai/stack/live.json could not be read')
else:
    for r in st.get('rows', []):
        if r.get('outcome') == 'NOTHING_RETURNED' and r['page'] not in EXPECTED_EMPTY: flag('stack:' + r['page'], 'STACK row %s returned nothing' % r['page'])
    for r in st.get('running', []):
        if r.get('state') == 'NOTHING_RETURNED': flag('stack-running:' + r['page'], 'STACK running line %s: %s' % (r['page'], r.get('reading')))
# 4 corner logs that ended in a failure within the last day
for lg in glob.glob(B + '/*_index/data/last_run.log') + glob.glob(B + '/*_index/data/reread.log'):
    try:
        if now - os.path.getmtime(lg) > 86400: continue
        tail = open(lg, errors='replace').read()[-1500:]
        if re.search(r'Traceback|GATE FAILED|publish FAILED|FAILED', tail) and 'GATE passed' not in tail.split('FAILED')[-1][:5]:
            flag('log:' + os.path.basename(os.path.dirname(os.path.dirname(lg))), 'a failure line in the latest run of %s' % os.path.relpath(lg, B))
    except OSError: pass
# 4b 30 Oct: a model run that is alive but has stopped writing (process present, its logs quiet for an hour)
try:
    _ps = subprocess.run(['ps', '-axo', 'pid=,command='], capture_output=True, text=True).stdout
    # 12 Nov: only a TRAINING run counts (mlx_lm lora / a trainer script); seat servers (mlx_lm server) idle for hours by design, and the council lane's PAUSE file means its log is meant to stop
    if re.search(r'mlx_lm[ .](lora|fuse)|train_stan|calib_train|train_live', _ps) and not os.path.exists(B + '/sage_library/council/PAUSE'):
        # 1 Nov: an mlx_lm process may be YO (logs in yo/), and a drive's own log is written only between arms, so liveness reads the newest of
        # the IRIS logs, the IRIS run outputs (out/*.jsonl, written per reply) and YO's logs
        _logs = [f for f in glob.glob(B + '/iris_index/**/*.log', recursive=True) + glob.glob(B + '/iris_index/**/out/**/*.jsonl', recursive=True) + glob.glob(B + '/yo/*.log') + glob.glob(B + '/sage_flock/train/*.log') + glob.glob(B + '/sage_library/council/train/**/*.log', recursive=True) + glob.glob(B + '/sage_library/council/train/*.out') if '/seats/' not in f]   # 8 Nov: the council lane's trainer (calib_train.py) is mlx_lm too   # 7 Nov: the flock trainer is mlx_lm too
        _new = max(_logs, key=os.path.getmtime) if _logs else None
        if _new and now - os.path.getmtime(_new) > 3600: flag('iris:stalled', 'an IRIS model run is alive but its newest log (%s) has not moved for %d minutes' % (os.path.relpath(_new, B), (now - os.path.getmtime(_new)) / 60))
except Exception as e: flag('watcher:training_liveness', 'training liveness check failed: ' + type(e).__name__)   # 13 Nov trust-but-verify
# 4c (10 Nov, owner: "you've swept our shit four or five times, how'd you miss that?"): process sweeps only asked whether a process should exist.
# The Armature judge server was alive and wanted but its settings put qwen3:8b on the CPU (0 GPU bytes), and the CHECK rooms hung 4.5 h.
# Check placement, not just presence: a GPU-meant model loaded with less than all of itself in VRAM is an alert.
GPU_MEANT = {'http://armature.lan:11434': ['qwen3:8b']}
for host, names in GPU_MEANT.items():
    ps_ = j(host + '/api/ps')
    if ps_ is None: flag('ollama:' + host, 'ollama %s did not answer /api/ps' % host); continue
    for m in ps_.get('models', []):
        if m.get('name') in names and int(m.get('size_vram') or 0) < 0.95 * int(m.get('size') or 1):
            flag('vram:%s:%s' % (host, m['name']), '%s on %s is only %.0f%% in GPU memory (%s of %s bytes): it is running on the CPU' % (m['name'], host, 100.0 * int(m.get('size_vram') or 0) / int(m.get('size') or 1), m.get('size_vram'), m.get('size')))
# 4d (11 Nov): the private ledger backup push at the end of every ship (ship.sh 7c) writes ledger_backup_status.json only on failure
try:
    lb = json.load(open(B + '/ledger/ledger_backup_status.json'))
    if not lb.get('ok', True): flag('ledger:backup', 'ledger backup push to Heuremen-LLC/ledger-private failed at %s' % lb.get('at'))
except FileNotFoundError: pass
except Exception as e: flag('ledger:backup', 'ledger backup status unreadable: ' + type(e).__name__)
# 4e (11 Nov): the private archive push (ship.sh 7d) and the Zenodo sync (ship.sh 7e) write a status file only on failure
for fn, key, what in (('archive_backup_status.json', 'archive:backup', 'archive push to Heuremen-LLC/backup-private failed'), ('zenodo_status.json', 'zenodo:sync', 'Zenodo sync reported an error'), ('auto_ship_status.json', 'auto:ship', 'the automatic ship was refused by a gate')):
    try:
        zb = json.load(open(B + '/ledger/' + fn))
        if not zb.get('ok', True): flag(key, '%s at %s %s' % (what, zb.get('at'), zb.get('error', '')))
    except FileNotFoundError: pass
    except Exception as e: flag(key, fn + ' unreadable: ' + type(e).__name__)
# 5 disk and launchd jobs
free = shutil.disk_usage('/').free / 1e9
if free < 15: flag('disk', 'only %.1f GB free on the system disk' % free)
try:
    for line in subprocess.run(['launchctl', 'list'], capture_output=True, text=True).stdout.split('\n'):
        p = line.split('\t')
        if len(p) == 3 and p[2] in ('com.heuremen.qia-audit', 'com.heuremen.tick-bus') and p[1] not in ('0', '-') and p[0] == '-':   # 30 Oct: a running job (PID present) keeps its last exit code after a restart; only a job that is down counts
            flag('launchd:' + p[2], '%s last exit status %s' % (p[2], p[1]))
except Exception as e: flag('watcher:launchd', 'launchctl list could not be read: ' + type(e).__name__)   # 13 Nov trust-but-verify
# state: open, closed, with history
op = json.load(open(A + '/open.json')) if os.path.exists(A + '/open.json') else {}
hist = open(A + '/history.jsonl', 'a')
for i, w in found.items():
    if i not in op: op[i] = dict(since=time.strftime('%Y-%m-%d %H:%M', time.localtime(now)), what=w); hist.write(json.dumps(dict(t=now, event='open', id=i, what=w)) + '\n')
    else: op[i]['what'] = w
for i in list(op):
    if i not in found: hist.write(json.dumps(dict(t=now, event='closed', id=i)) + '\n'); del op[i]
json.dump(op, open(A + '/open.json', 'w'), indent=1)
open(A + '/ALERTS_OPEN.txt', 'w').write(('OPEN ALERTS FOR BONES (%d), fix these before anything else unless Wayfinder says otherwise:\n' % len(op) + '\n'.join('- [%s] since %s: %s' % (i, v['since'], v['what']) for i, v in sorted(op.items())) + '\n') if op else '')
print('alerts:', len(op), 'open')
open(A + '/last_check', 'w').write(time.strftime('%Y-%m-%dT%H:%M:%S'))   # 30 Oct: heartbeat read by alerts/hook.sh
