#!/usr/bin/env python3
"""now_log.py: the append-only NOW log (PLAN.md "The log"). Python 3.9 compatible.
  rows      data/log.jsonl, one JSON object per line: seq, at (UTC), prev (sha256 of the previous line's bytes, '' for the first), kind, ...
  append    append(rows) adds rows in order, never rewrites a line, then stamps a copy with OpenTimestamps
  verify    python3 now_log.py verify  -> checks every seq and every prev link; prints the head sha256
  stamp     python3 now_log.py stamp   -> stamps the current log if its sha256 has no stamp yet
  upgrade   python3 now_log.py upgrade -> ots upgrade on every pending log stamp
  view      current(): entries with their newest corrections applied, and the outcome/due rows per entry"""
import os, sys, json, time, hashlib, subprocess, shutil, glob, fcntl

H = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(H, 'data', 'log.jsonl'); ST = os.path.join(H, 'data', 'stamps')
OTS = os.path.expanduser('~/bones-forge/archive/venv/bin/ots')
KINDS = ('entry', 'outcome', 'due', 'correction')
os.makedirs(ST, exist_ok=True)


def lines():
    if not os.path.exists(LOG): return []
    with open(LOG, 'rb') as f: return [l for l in f.read().split(b'\n') if l.strip()]


def load():
    return [json.loads(l) for l in lines()]


def sha(b): return hashlib.sha256(b).hexdigest()


def head_sha():
    return sha(open(LOG, 'rb').read()) if os.path.exists(LOG) else ''


def verify():
    """(ok, message). Every line parses, seq runs 1..n, and each prev is the sha256 of the line before it."""
    ls = lines(); prev = ''
    for i, l in enumerate(ls, 1):
        try: r = json.loads(l)
        except ValueError: return False, 'line %d does not parse' % i
        if r.get('seq') != i: return False, 'line %d has seq %r' % (i, r.get('seq'))
        if r.get('prev') != prev: return False, 'line %d: prev does not match the line before it' % i
        if r.get('kind') not in KINDS: return False, 'line %d: unknown kind %r' % (i, r.get('kind'))
        prev = sha(l)
    return True, '%d rows, chain intact, last line sha256 %s' % (len(ls), prev[:16])


def append(rows, stamp_after=True):
    ok, msg = verify()
    if not ok: raise SystemExit('log chain broken, nothing appended: ' + msg)
    lk = open(LOG + '.lock', 'w'); fcntl.flock(lk, fcntl.LOCK_EX)
    try:
        ls = lines(); prev = sha(ls[-1]) if ls else ''; seq = len(ls); now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); out = []
        for r in rows:
            assert r.get('kind') in KINDS, r
            seq += 1; row = dict(seq=seq, at=now, prev=prev); row.update(r)
            b = json.dumps(row, ensure_ascii=False, sort_keys=False, separators=(',', ':')).encode('utf-8')
            out.append(b); prev = sha(b)
        with open(LOG, 'ab') as f:
            for b in out: f.write(b + b'\n')
    finally:
        fcntl.flock(lk, fcntl.LOCK_UN); lk.close()
    if stamp_after and out: stamp()
    return len(out)


def stamp():
    """Copies the log to data/stamps/log_<sha16>.jsonl and stamps it. Returns the stamp path or None. Never raises."""
    if not os.path.exists(LOG): return None
    h = head_sha(); dst = os.path.join(ST, 'log_%s.jsonl' % h[:16])
    if os.path.exists(dst + '.ots'): return dst + '.ots'
    shutil.copy2(LOG, dst)
    ok = None   # 13 Nov 2026 (Wayfinder: 'i just would prefer to not be a part of that chain'): no OpenTimestamps, no Bitcoin, from today. Past .ots files stay as they were. The copy and its sha256 are still kept.
    idx = os.path.join(ST, 'index.json'); d = json.load(open(idx)) if os.path.exists(idx) else []
    d.append(dict(file=os.path.basename(dst), sha256=h, rows=len(lines()), at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), ots='none' if ok is None else ('pending' if ok else 'failed')))
    json.dump(d, open(idx, 'w'), indent=1)
    return dst if ok is None else (dst + '.ots' if ok else None)


def ots_state(p):
    """'bitcoin <block>' once anchored, 'pending' while only calendar attestations (same reading as ledger/stamps.py)."""
    import re
    if not os.path.exists(p): return 'missing'
    try: r = subprocess.run([OTS, 'info', p], capture_output=True, text=True, timeout=60)
    except Exception: return 'unreadable'
    if r.returncode: return 'unreadable'
    blocks = re.findall(r'BitcoinBlockHeaderAttestation\((\d+)\)', r.stdout)
    return ('bitcoin ' + min(blocks, key=int)) if blocks else 'pending'


def upgrade():
    return 0   # no chain since 13 Nov 2026
    idx = os.path.join(ST, 'index.json'); d = json.load(open(idx)) if os.path.exists(idx) else []; n = 0
    for s in d:
        if str(s.get('ots', '')).startswith('bitcoin') or s.get('ots') == 'failed': continue
        p = os.path.join(ST, s['file'] + '.ots')
        try: subprocess.run([OTS, 'upgrade', p], capture_output=True, text=True, timeout=120)
        except Exception: continue
        st = ots_state(p)
        if st != s.get('ots'): n += 1
        s['ots'] = st
        for b in glob.glob(p + '.bak'): os.remove(b)
    json.dump(d, open(idx, 'w'), indent=1)
    return n


def current():
    """Entries (newest correction of each field applied, corrections listed), and per entry its outcome rows and due rows in log order."""
    ents, order = {}, []
    for r in load():
        k = r['kind']
        if k == 'entry':
            e = dict(r); e['kind'] = r.get('claim'); e['corrections'] = []; e['outcomes'] = []; e['dues'] = []; ents[r['id']] = e; order.append(r['id'])
        elif k == 'correction':
            e = ents.get(r['entry'])
            if e is None: continue
            e['corrections'].append(r)
            if r.get('field') == 'outcome' and e['outcomes']: e['outcomes'][-1] = dict(e['outcomes'][-1], **{'outcome': r['to'], 'corrected_by': r['seq']})
            elif r.get('field'): e[r['field']] = r['to']
        elif k == 'outcome':
            if r['entry'] in ents: ents[r['entry']]['outcomes'].append(r)
        elif k == 'due':
            if r['entry'] in ents: ents[r['entry']]['dues'].append(r)
    return [ents[i] for i in order]


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'verify'
    if a == 'verify': ok, m = verify(); print(('OK ' if ok else 'BROKEN ') + m); sys.exit(0 if ok else 1)
    if a == 'stamp': print(stamp())
    if a == 'upgrade': print('upgraded', upgrade())
