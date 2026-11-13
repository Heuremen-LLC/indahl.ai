#!/usr/bin/env python3
"""prereg.py -- Heuremen LLC (https://indahl.ai). Standard library plus git. Plan: plans/prereg/PLAN.md and PLAN_v2.md in
github.com/Heuremen-LLC/indahl.ai (claude-plugins/). Answers "was the plan written before the first run?" with the git host's own record of the push,
and "did the plan cover what ran?". No outside timestamp chain is used.

  prereg.py seal FILE... [--tolerance 120] [--kind ibm_job|ci_log|wrapper|user_stated] [--commit]
  prereg.py witness SEAL [--host-record FILE]      read the host's push record (GitHub repository activity) and bind it to the seal
  prereg.py check SEAL (--job-record FILE | --wrapper RUN.json | --first-run TIME)
  prereg.py verify SEAL                            blob drift and working-tree drift since the seal
  prereg.py run -- CMD...                          run CMD and record what was there when it started (prereg/runs/RUN_*.json)
  prereg.py cover SEAL RUN.json                    files the run touched or named that the seal does not cover
  prereg.py selftest

Outcomes (check): BEFORE, AFTER, CANNOT_TELL (STRADDLES_EDGE, NOT_RELEASED, METHOD_UNSTATED), NOTHING_RETURNED. Each carries the run time's
witness class: host_read, user_file, wrapper, user_stated. BEFORE means the witnessed push precedes the first run in the supplied record,
never that it precedes any run."""
import json, os, sys, subprocess, hashlib, datetime as dt, glob, socket, re, tempfile, shutil, urllib.request, argparse

KINDS = ('ibm_job', 'ci_log', 'wrapper', 'user_stated'); CODE_EXT = ('.py', '.sh', '.bash', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.r', '.jl', '.ipynb', '.ps1', '.bat', '.cmd', '.env', '.mk')
CODE_NAMES = ('Makefile', 'Dockerfile', 'Justfile', '.env'); CI_HEAD_LINES = 50
def git(*a, cwd=None, check=True):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode: raise SystemExit(f'git {" ".join(a)}: {r.stderr.strip()}')
    return r.stdout
def root(cwd=None): return os.path.realpath(git('rev-parse', '--show-toplevel', cwd=cwd).strip())
def now(): return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def utc(s):
    """an instant with an offset; a time with no offset is refused (None)"""
    try:
        d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
        return None if d.tzinfo is None else d.astimezone(dt.timezone.utc)
    except Exception: return None
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def seal(files, tolerance=120, kind='wrapper', commit=False, cwd=None):
    R = root(cwd); rel = [os.path.relpath(os.path.realpath(f), R) for f in files]
    if kind not in KINDS: raise SystemExit(f'kind must be one of {KINDS}')
    dirty = [l[3:] for l in git('status', '--porcelain', '--', *rel, cwd=R).splitlines()]
    if dirty: raise SystemExit('refused: these files have uncommitted changes, commit them first: ' + ', '.join(dirty))
    head = git('rev-parse', 'HEAD', cwd=R).strip(); entries = []
    for f in rel:
        blob = git('rev-parse', f'HEAD:{f}', cwd=R).strip()
        data = subprocess.run(['git', 'cat-file', 'blob', blob], cwd=R, capture_output=True).stdout
        entries.append({'path': f, 'blob': blob, 'sha256_committed': sha_bytes(data)})
    remote = git('remote', 'get-url', 'origin', cwd=R, check=False).strip()
    os.makedirs(os.path.join(R, 'prereg', 'seals'), exist_ok=True)
    n = len(glob.glob(os.path.join(R, 'prereg', 'seals', 'SEAL_*.json'))) + 1
    doc = {'version': n, 'files': entries, 'files_commit': head, 'remote': remote, 'tolerance_s': tolerance, 'run_record_kind': kind,
           'written_at_self_set': now(), 'note': 'written_at is this machine\'s clock (self-set); the witness is the host\'s record of the push',
           'autocrlf': git('config', '--get', 'core.autocrlf', cwd=R, check=False).strip() or None,
           'lfs_note': 'files tracked by Git LFS are sealed as their pointer, which carries the content sha256 oid'}
    p = os.path.join(R, 'prereg', 'seals', f'SEAL_{n:03d}.json'); json.dump(doc, open(p, 'w'), indent=1)
    if commit:
        git('add', p, cwd=R); git('commit', '-qm', f'prereg seal {n:03d}', cwd=R)   # the user's own configured identity
    return p

def seal_commit(sealp):
    R = root(os.path.dirname(os.path.realpath(sealp))); rel = os.path.relpath(os.path.realpath(sealp), R)
    c = git('log', '--diff-filter=A', '--format=%H', '--', rel, cwd=R).strip().splitlines()
    return (c[-1] if c else None), R

def gh_activity(remote, since=None):
    """GitHub repository activity, paged until the oldest event predates `since` (the seal commit's date) or pages run out.
    Returns (list of events, raw bytes per page, source, pages_read, private)"""
    m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote or '')
    if not m: return None, [], 'not a github remote', 0, None
    o, r = m.group(1), m.group(2); H = {'User-Agent': 'prereg/1.0', 'Accept': 'application/vnd.github+json'}
    try: priv = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://api.github.com/repos/{o}/{r}', headers=H), timeout=30).read()).get('private')
    except Exception: priv = None
    ev, raws, url, pages = [], [], f'https://api.github.com/repos/{o}/{r}/activity?per_page=100', 0
    while url and pages < 30:
        try: resp = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30)
        except Exception as e: return (ev or None), raws, f'{url}: {type(e).__name__}', pages, priv
        b = resp.read(); raws.append(b); pages += 1; page = json.loads(b); ev += page
        if not page or (since and min(x.get('timestamp', '') for x in page) < since): break
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', resp.headers.get('Link', '') or ''); url = nxt.group(1) if nxt else None
    try: urllib.request.urlopen(urllib.request.Request('https://web.archive.org/save/' + f'https://api.github.com/repos/{o}/{r}/activity', headers={'User-Agent': 'prereg/1.0'}), timeout=60)
    except Exception: pass   # an outside copy is requested, best effort
    return ev, raws, f'https://api.github.com/repos/{o}/{r}/activity', pages, priv

def bind(events, sc, R):
    """first push whose head has the seal commit as ancestor; counts pushes not checkable locally; force pushes after the hit"""
    hit = None; nolocal = 0
    for a in sorted([a for a in events if a.get('activity_type') in ('push', 'force_push', 'pr_merge', 'branch_creation')], key=lambda a: a.get('timestamp', '')):
        after = a.get('after')
        if not after: continue
        if subprocess.run(['git', 'cat-file', '-e', after], cwd=R, capture_output=True).returncode: nolocal += 1; continue
        if subprocess.run(['git', 'merge-base', '--is-ancestor', sc, after], cwd=R).returncode == 0 and hit is None: hit = a
    fp = [a.get('timestamp') for a in events if hit and a.get('activity_type') == 'force_push' and a.get('timestamp', '') > hit['timestamp']
          and subprocess.run(['git', 'cat-file', '-e', a.get('after') or '0'], cwd=R, capture_output=True).returncode == 0
          and subprocess.run(['git', 'merge-base', '--is-ancestor', sc, a['after']], cwd=R).returncode != 0]
    return hit, nolocal, fp

def witness(sealp, host_record=None):
    sc, R = seal_commit(sealp)
    if not sc: raise SystemExit('the seal file is not committed yet')
    doc = json.loads(git('show', f'{sc}:{os.path.relpath(os.path.realpath(sealp), R)}', cwd=R))
    since = git('show', '-s', '--format=%cI', sc, cwd=R).strip()
    wdir = os.path.dirname(os.path.realpath(sealp)); stem = os.path.basename(sealp).replace('SEAL_', 'WITNESS_').replace('.json', '')
    if host_record:
        raws = [open(host_record, 'rb').read()]; events = json.loads(raws[0]); src = 'file:' + host_record; wclass = 'user_file'; pages = 1; priv = None
    else:
        events, raws, src, pages, priv = gh_activity(doc.get('remote'), since); wclass = 'host_read'
        if events is None: return dict(outcome='NOTHING_RETURNED', source=src, witness_class=wclass)
    rawpaths = []
    for i, b in enumerate(raws):   # the bytes as received, and their sha256
        rp = os.path.join(wdir, f'{stem}_raw{i + 1}.json'); open(rp, 'wb').write(b); rawpaths.append([os.path.basename(rp), sha_bytes(b)])
    hit, nolocal, fp = bind(events, sc, R)
    out = dict(seal=os.path.basename(sealp), seal_commit=sc, source=src, witness_class=wclass, pages_read=pages, raw_files=rawpaths,
               pushes_not_checkable_locally=nolocal, force_pushes_after_hit_without_seal=fp,
               private_repository=priv, note=('private repository: the record is held by the host but not publicly checkable' if priv else ''))
    if not hit: out.update(outcome='CANNOT_TELL', reason='NOT_RELEASED', note2='no push in the host record carries the seal commit')
    else: out.update(pushed_at=hit['timestamp'], pushed_head=hit['after'], ref=hit.get('ref'), actor=(hit.get('actor') or {}).get('login'))
    wp = os.path.join(wdir, stem + '.json'); json.dump(out, open(wp, 'w'), indent=1); out['witness_file'] = wp
    return out

def run_start(args_kind, value, time_kind='start'):
    """-> (start datetime or None, witness class, error, detail). The class comes from how prereg got the time, never from the record."""
    if args_kind == 'user_stated':
        t = utc(value); return (t, 'user_stated', None if t else 'time has no offset or does not parse (refused)', dict(time_kind=time_kind))
    if args_kind == 'wrapper':
        d = json.load(open(value)); t = utc(d.get('started_at')); return (t, 'wrapper', None if t else 'METHOD_UNSTATED', dict(time_kind='start', key='started_at'))
    if args_kind == 'ibm_job':
        d = json.load(open(value)); ts = (d.get('metrics', {}) or {}).get('timestamps', {}) or {}
        for key, v in (('running', d.get('running')), ('metrics.timestamps.running', ts.get('running')), ('start', d.get('start')), ('created', d.get('created')), ('creation_date', d.get('creation_date'))):
            if v:
                t = utc(v); return (t, 'user_file', None if t else 'METHOD_UNSTATED', dict(time_kind='start', key=key, note='created is queue time, earlier than the run' if key in ('created', 'creation_date') else ''))
        return (None, 'user_file', 'METHOD_UNSTATED', dict(time_kind='start'))
    if args_kind == 'ci_log':
        for i, line in enumerate(open(value, errors='replace')):
            if i >= CI_HEAD_LINES: break
            m = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})', line)
            if m: return (utc(m.group(0)), 'user_file', None, dict(time_kind='start', line_number=i + 1, line=line.strip()[:200]))
        return (None, 'user_file', 'METHOD_UNSTATED', dict(time_kind='start', note=f'no timestamp with an offset in the first {CI_HEAD_LINES} lines'))
    return (None, None, 'unknown kind', {})

def all_seals(R):
    """every seal ever added in the repository history (a deleted seal still counts), with the files it named"""
    out = []; seen = set(); cur = None
    for line in git('log', '--all', '--diff-filter=A', '--name-only', '--format=COMMIT %H', '--', 'prereg/seals/', cwd=R).splitlines():
        if line.startswith('COMMIT '): cur = line[7:]; continue
        if line.endswith('.json') and 'SEAL_' in line and (cur, line) not in seen:
            seen.add((cur, line))
            try: out.append((line, [e['path'] for e in json.loads(git('show', f'{cur}:{line}', cwd=R))['files']]))
            except Exception: pass
    return out

def check(sealp, kind, value, cover_set=None, time_kind='start'):
    sc, R = seal_commit(sealp)
    if not sc: return dict(outcome='REFUSED', reason='the seal is not committed')
    rel = os.path.relpath(os.path.realpath(sealp), R)
    doc = json.loads(git('show', f'{sc}:{rel}', cwd=R))   # FIX 1: the seal as the host saw it, never the working tree
    added_blob = git('rev-parse', f'{sc}:{rel}', cwd=R).strip(); head_blob = git('rev-parse', f'HEAD:{rel}', cwd=R, check=False).strip()
    if head_blob and head_blob != added_blob: return dict(outcome='REFUSED', reason='seal_edited_after_witness: the seal file changed after the commit that added it')
    tol = doc['tolerance_s']
    if kind != doc['run_record_kind']: return dict(outcome='REFUSED', reason=f"the seal names run_record_kind {doc['run_record_kind']}, not {kind}")
    stem = os.path.basename(sealp).replace('SEAL_', 'WITNESS_').replace('.json', ''); wdir = os.path.dirname(os.path.realpath(sealp))
    wp = os.path.join(wdir, stem + '.json')
    if not os.path.exists(wp): return dict(outcome='CANNOT_TELL', reason='NOT_RELEASED', note='no witness file; run witness right after the push')
    w = json.load(open(wp)); events = []
    for name, h in w.get('raw_files', []):   # recompute from the raw bytes, checked against their recorded sha256
        b = open(os.path.join(wdir, name), 'rb').read()
        if sha_bytes(b) != h: return dict(outcome='REFUSED', reason=f'witness raw file {name} does not match its recorded sha256')
        events += json.loads(b)
    hit, _, _ = bind(events, sc, R); t_push = utc(hit['timestamp']) if hit else None
    if kind == 'wrapper' and cover_set is None:
        try: rec = json.load(open(value)); cover_set = list(rec.get('argv_files', [])) + list(rec.get('files_sha256', {}))
        except Exception: pass
    t_run, rclass, err, detail = run_start(kind, value, time_kind)
    base = dict(seal=os.path.basename(sealp), tolerance_s=tol, witness_class=w.get('witness_class'), run_time_class=rclass, run_time_detail=detail,
                pushed_at=hit['timestamp'] if hit else None)
    seals = all_seals(R); base['seals_in_history'] = len(seals)
    if cover_set: base['seals_naming_a_run_file'] = sum(1 for n, fs in seals if set(fs) & set(cover_set))
    if t_push is None: return dict(base, outcome='CANNOT_TELL', reason='NOT_RELEASED')
    if err == 'METHOD_UNSTATED': return dict(base, outcome='CANNOT_TELL', reason='METHOD_UNSTATED')
    if err: return dict(base, outcome='REFUSED', reason=err)
    gap = (t_run - t_push).total_seconds(); base.update(run_time=t_run.strftime('%Y-%m-%dT%H:%M:%SZ'), gap_s=gap)
    if gap < -tol: return dict(base, outcome='AFTER', wording='the first run in the supplied record precedes the witnessed push')
    if gap > tol:
        if detail.get('time_kind') == 'first_output':
            return dict(base, outcome='CANNOT_TELL', reason='METHOD_UNSTATED', note='a first-output time cannot support BEFORE: the run started earlier')
        return dict(base, outcome='BEFORE', wording='the witnessed push precedes the first run in the supplied record')
    return dict(base, outcome='CANNOT_TELL', reason='STRADDLES_EDGE')

def verify(sealp):
    doc = json.load(open(sealp)); R = root(os.path.dirname(os.path.abspath(sealp))); res = []
    for e in doc['files']:
        cur = git('rev-parse', f"HEAD:{e['path']}", cwd=R, check=False).strip()
        wt = sha_file(os.path.join(R, e['path'])) if os.path.exists(os.path.join(R, e['path'])) else None
        res.append(dict(path=e['path'], blob_drift=cur != e['blob'], working_tree_drift=wt != e['sha256_committed']))
    if git('config', '--get', 'core.autocrlf', cwd=R, check=False).strip() in ('true', 'input'):
        res.append(dict(note='core.autocrlf is set: line-ending conversion makes working_tree_drift show on files that did not change'))
    return res

def is_code(p, name):
    if name.lower().endswith(CODE_EXT) or os.path.basename(name) in CODE_NAMES: return True
    try:
        if os.access(p, os.X_OK): return True
        with open(p, 'rb') as f: return f.read(2) == b'#!'
    except OSError: return False

def run(cmd, cwd=None):
    R = root(cwd); st = now(); files = {}; base = os.path.realpath(cwd or os.getcwd())
    names = set(git('ls-files', '-co', '--exclude-standard', cwd=R).splitlines()) | set(git('ls-files', '-oi', '--exclude-standard', cwd=R).splitlines())
    for line in names:
        p = os.path.join(R, line)
        if line.startswith('prereg/') or line.startswith('.git/') or not os.path.isfile(p) or os.path.getsize(p) >= 10 * 1024 * 1024: continue
        if is_code(p, line): files[line] = sha_file(p)
    toks = []
    for a in cmd: toks += [a] + ([a.split('=', 1)[1]] if '=' in a else [])
    argv_files = [os.path.realpath(os.path.join(base, a)) for a in toks if a and os.path.isfile(os.path.join(base, a))]
    rec = dict(started_at=st, command=cmd, cwd=base, host=socket.gethostname(),
               git_status=git('status', '--porcelain', '--ignored', cwd=R).splitlines(), files_sha256=files,
               argv_files=sorted({os.path.relpath(a, R) if a.startswith(R + os.sep) else a for a in argv_files}),
               note='started_at is written by prereg at start (class wrapper): self-held, not typed',
               not_tested='files named only inside a shell string (bash -c "..."), and files a process opened that no record names')
    os.makedirs(os.path.join(R, 'prereg', 'runs'), exist_ok=True); p = os.path.join(R, 'prereg', 'runs', f"RUN_{st.replace(':', '')}.json")
    json.dump(rec, open(p, 'w'), indent=1)
    r = subprocess.run(cmd, cwd=cwd); rec['exit_code'] = r.returncode; rec['ended_at'] = now(); json.dump(rec, open(p, 'w'), indent=1)
    return p, r.returncode

def cover(sealp, runp):
    doc = json.load(open(sealp)); rec = json.load(open(runp)); sealed = {e['path']: e['sha256_committed'] for e in doc['files']}
    not_sealed = sorted(f for f in rec['files_sha256'] if f not in sealed)
    changed = sorted(f for f, h in rec['files_sha256'].items() if f in sealed and h != sealed[f])
    ignored = [l[3:] for l in rec['git_status'] if l.startswith('!! ')]; untracked = [l[3:] for l in rec['git_status'] if l.startswith('?? ')]
    outside = [a for a in rec['argv_files'] if os.path.isabs(a)]
    return dict(headline_argv_files_not_sealed=sorted(set(rec['argv_files']) - set(sealed)), code_files_not_sealed=not_sealed, sealed_files_changed_at_run=changed,
                ignored_at_run=ignored, untracked_at_run=untracked, argv_files_outside_repository=outside,
                not_tested='files a process opened that no record names (prereg does not trace system calls)')

def selftest():
    ok = True
    def chk(name, got, want):
        nonlocal ok
        g = got == want; ok &= g; print(('ok  ' if g else 'FAIL'), name, '->', got, '' if g else f'(want {want})')
    td = tempfile.mkdtemp(prefix='prereg_selftest_'); env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
    sh = lambda *a: subprocess.run(a, cwd=td, capture_output=True, text=True, env=env)
    sh('git', 'init', '-q'); sh('git', 'remote', 'add', 'origin', 'https://github.com/example/demo.git')
    open(os.path.join(td, 'PLAN.md'), 'w').write('plan v1\n'); open(os.path.join(td, 'analyze.py'), 'w').write('print(open("config.yaml").read())\n')
    open(os.path.join(td, '.gitignore'), 'w').write('*.log\n'); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'plan')
    open(os.path.join(td, 'PLAN.md'), 'a').write('dirty\n')
    try: seal([os.path.join(td, 'PLAN.md')], cwd=td); refused = False
    except SystemExit: refused = True
    chk('seal refuses a file with uncommitted changes', refused, True)
    sh('git', 'checkout', '--', 'PLAN.md')
    sp = seal([os.path.join(td, 'PLAN.md'), os.path.join(td, 'analyze.py')], tolerance=120, kind='user_stated', cwd=td); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'seal')
    head = sh('git', 'rev-parse', 'HEAD').stdout.strip(); sc, _ = seal_commit(sp)
    fake = [{'activity_type': 'push', 'timestamp': '2026-11-13T10:00:00Z', 'after': head, 'actor': {'login': 't'}}]
    hr = os.path.join(td, 'host.json'); json.dump(fake, open(hr, 'w'))
    w = witness(sp, hr); chk('witness binds the push whose head has the seal commit as ancestor', w.get('pushed_at'), '2026-11-13T10:00:00Z')
    chk('a host record loaded from a file has witness class user_file', w.get('witness_class'), 'user_file')
    chk('check BEFORE (run 1 h after the push)', check(sp, 'user_stated', '2026-11-13T11:00:00Z')['outcome'], 'BEFORE')
    chk('check AFTER (run 1 h before the push)', check(sp, 'user_stated', '2026-11-13T09:00:00Z')['outcome'], 'AFTER')
    c = check(sp, 'user_stated', '2026-11-13T10:01:00Z'); chk('check 60 s apart: STRADDLES_EDGE', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'STRADDLES_EDGE'))
    c = check(sp, 'user_stated', '2026-11-13T11:00:00'); chk('check refuses a time with no offset', c['outcome'], 'REFUSED')
    c = check(sp, 'wrapper', 'x'); chk('check refuses a run-record kind the seal did not name', c['outcome'], 'REFUSED')
    chk('check carries the run-time class', check(sp, 'user_stated', '2026-11-13T11:00:00Z')['run_time_class'], 'user_stated')
    c = check(sp, 'user_stated', '2026-11-13T11:00:00Z', time_kind='first_output')
    chk('a first-output time cannot read BEFORE', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'METHOD_UNSTATED'))
    chk('a first-output time can still read AFTER', check(sp, 'user_stated', '2026-11-13T09:00:00Z', time_kind='first_output')['outcome'], 'AFTER')
    # FIX 1: the tolerance edited after the witness and committed -> refused
    d = json.load(open(sp)); d['tolerance_s'] = 10; json.dump(d, open(sp, 'w')); sh('git', 'commit', '-qam', 'edit tolerance')
    chk('a seal edited after the witness is refused', check(sp, 'user_stated', '2026-11-13T10:01:00Z')['outcome'], 'REFUSED')
    sh('git', 'revert', '--no-edit', 'HEAD')
    chk('after the edit is reverted, the sealed 120 s applies (60 s gap straddles)', check(sp, 'user_stated', '2026-11-13T10:01:00Z').get('reason'), 'STRADDLES_EDGE')
    json.dump([{'activity_type': 'push', 'timestamp': '2026-11-13T10:00:00Z', 'after': '0' * 40}], open(hr, 'w'))
    os.remove(sp.replace('SEAL_', 'WITNESS_')); w = witness(sp, hr); c = check(sp, 'user_stated', '2026-11-13T11:00:00Z')
    chk('no push carrying the seal: NOT_RELEASED', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'NOT_RELEASED'))
    # wrapper seal: run, cover, METHOD_UNSTATED
    open(os.path.join(td, 'config.yaml'), 'w').write('alpha: 1\n'); open(os.path.join(td, 'scratch.log'), 'w').write('x\n')
    os.makedirs(os.path.join(td, 'build'), exist_ok=True); open(os.path.join(td, '.gitignore'), 'a').write('build/\n')
    open(os.path.join(td, 'build', 'launch.sh'), 'w').write('echo hi\n')                      # a launcher inside an ignored directory
    open(os.path.join(td, 'runme'), 'w').write('#!/bin/sh\necho x\n')                          # an extensionless script with a #! line
    sp2 = seal([os.path.join(td, 'PLAN.md'), os.path.join(td, 'analyze.py')], kind='wrapper', cwd=td); sh('git', 'add', sp2); sh('git', 'commit', '-qm', 'seal2')
    rp, rc = run([sys.executable, 'analyze.py', '--config=config.yaml'], cwd=td)
    cv = cover(sp2, rp)
    chk('cover headlines an argv file given as --config=x.yaml', 'config.yaml' in cv['headline_argv_files_not_sealed'], True)
    chk('the wrapper hashes a launcher inside an ignored directory', 'build/launch.sh' in json.load(open(rp))['files_sha256'], True)
    chk('the wrapper hashes an extensionless #! script', 'runme' in json.load(open(rp))['files_sha256'], True)
    chk('cover lists the config that ran but was not sealed', 'config.yaml' in cv['code_files_not_sealed'], True)
    chk('cover sees ignored files present at run time', 'scratch.log' in cv['ignored_at_run'], True)
    d = json.load(open(rp)); d.pop('started_at'); bad = os.path.join(td, 'bad_run.json'); json.dump(d, open(bad, 'w'))
    json.dump([{'activity_type': 'push', 'timestamp': '2026-11-13T10:00:00Z', 'after': sh('git', 'rev-parse', 'HEAD').stdout.strip()}], open(hr, 'w')); witness(sp2, hr)
    c = check(sp2, 'wrapper', bad); chk('a run record with no parseable start: METHOD_UNSTATED', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'METHOD_UNSTATED'))
    chk('forking plans: seals naming a run file are counted (cover set from the wrapper record)', check(sp2, 'wrapper', rp)['seals_naming_a_run_file'], 2)
    sp3 = seal([os.path.join(td, 'PLAN.md')], kind='wrapper', cwd=td); sh('git', 'add', sp3); sh('git', 'commit', '-qm', 'seal3'); sh('git', 'rm', '-q', sp3); sh('git', 'commit', '-qm', 'delete seal3')
    chk('a seal committed and then deleted still counts', check(sp2, 'wrapper', rp)['seals_in_history'], 3)
    # FIX 3 and FIX 7: a job record that declares itself host-fetched is still user_file; the key used is reported
    jr = os.path.join(td, 'job.json'); json.dump({'_fetched_from_host': True, 'created': '2026-11-13T11:00:00Z'}, open(jr, 'w'))
    t, cls, err, det = run_start('ibm_job', jr); chk('a record claiming host_read is still user_file; key reported', (cls, det.get('key')), ('user_file', 'created'))
    cl = os.path.join(td, 'ci.log'); open(cl, 'w').write('x\n' * 60 + '2026-11-13T11:00:00Z start\n')
    chk('ci log with its first timestamp past line 50 is METHOD_UNSTATED', run_start('ci_log', cl)[2], 'METHOD_UNSTATED')
    open(cl, 'w').write('setup\n2026-11-13T11:00:00Z start\n'); chk('ci log reports the line it used', run_start('ci_log', cl)[3].get('line_number'), 2)
    open(os.path.join(td, 'PLAN.md'), 'a').write('edited after the seal\n')
    v = {x['path']: x for x in verify(sp2)}; chk('verify: working-tree drift on an edited sealed file, no blob drift', (v['PLAN.md']['working_tree_drift'], v['PLAN.md']['blob_drift']), (True, False))
    sh('git', 'commit', '-qam', 'edit'); v = {x['path']: x for x in verify(sp2)}; chk('verify: blob drift once the edit is committed', v['PLAN.md']['blob_drift'], True)
    shutil.rmtree(td, ignore_errors=True)
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'selftest': sys.exit(0 if selftest() else 1)
    if a[0] == 'run':
        cmd = a[a.index('--') + 1:] if '--' in a else a[1:]; p, rc = run(cmd); print('run record', p); sys.exit(rc)
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='c', required=True)
    s = sp.add_parser('seal'); s.add_argument('files', nargs='+'); s.add_argument('--tolerance', type=int, default=120); s.add_argument('--kind', default='wrapper', choices=KINDS); s.add_argument('--commit', action='store_true')
    w = sp.add_parser('witness'); w.add_argument('seal'); w.add_argument('--host-record')
    c = sp.add_parser('check'); c.add_argument('seal'); g = c.add_mutually_exclusive_group(required=True); g.add_argument('--job-record'); g.add_argument('--wrapper'); g.add_argument('--first-run'); g.add_argument('--ci-log')
    v = sp.add_parser('verify'); v.add_argument('seal')
    cv = sp.add_parser('cover'); cv.add_argument('seal'); cv.add_argument('run')
    x = ap.parse_args(a)
    if x.c == 'seal': print(seal(x.files, x.tolerance, x.kind, x.commit))
    elif x.c == 'witness': print(json.dumps(witness(x.seal, x.host_record), indent=1))
    elif x.c == 'check':
        kind, val = ('ibm_job', x.job_record) if x.job_record else ('wrapper', x.wrapper) if x.wrapper else ('ci_log', x.ci_log) if x.ci_log else ('user_stated', x.first_run)
        print(json.dumps(check(x.seal, kind, val), indent=1))
    elif x.c == 'verify': print(json.dumps(verify(x.seal), indent=1))
    elif x.c == 'cover': print(json.dumps(cover(x.seal, x.run), indent=1))
