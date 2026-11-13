#!/usr/bin/env python3
"""prereg.py -- Heuremen LLC (https://indahl.ai). Standard library plus git. Plan: plans/prereg/PLAN.md and PLAN_v2.md in
github.com/Heuremen-LLC/claude-plugins. Answers "was the plan written before the first run?" with the git host's own record of the push,
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

KINDS = ('ibm_job', 'ci_log', 'wrapper', 'user_stated'); CODE_EXT = ('.py', '.sh', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.r', '.jl', '.ipynb')
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
           'written_at_self_set': now(), 'note': 'written_at is this machine\'s clock (self-set); the witness is the host\'s record of the push'}
    p = os.path.join(R, 'prereg', 'seals', f'SEAL_{n:03d}.json'); json.dump(doc, open(p, 'w'), indent=1)
    if commit:
        git('add', p, cwd=R); git('-c', 'user.name=prereg', '-c', 'user.email=prereg@localhost', 'commit', '-qm', f'prereg seal {n:03d}', cwd=R)
    return p

def seal_commit(sealp):
    R = root(os.path.dirname(os.path.realpath(sealp))); rel = os.path.relpath(os.path.realpath(sealp), R)
    c = git('log', '--diff-filter=A', '--format=%H', '--', rel, cwd=R).strip().splitlines()
    return (c[-1] if c else None), R

def gh_activity(remote):
    m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote or '')
    if not m: return None, 'not a github remote'
    u = f'https://api.github.com/repos/{m.group(1)}/{m.group(2)}/activity?per_page=100'
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'prereg/1.0', 'Accept': 'application/vnd.github+json'}), timeout=30).read()), u
    except Exception as e: return None, f'{u}: {type(e).__name__}'

def witness(sealp, host_record=None):
    doc = json.load(open(sealp)); sc, R = seal_commit(sealp)
    if not sc: raise SystemExit('the seal file is not committed yet')
    if host_record: raw = json.load(open(host_record)); src = 'file:' + host_record
    else:
        raw, src = gh_activity(doc.get('remote'))
        if raw is None: return dict(outcome='NOTHING_RETURNED', source=src)
    pushes = [a for a in raw if a.get('activity_type') in ('push', 'force_push', 'pr_merge', 'branch_creation')]
    hit = None; dropped = []
    for a in sorted(pushes, key=lambda a: a.get('timestamp', '')):
        after = a.get('after')
        if not after: continue
        if subprocess.run(['git', 'cat-file', '-e', after], cwd=R).returncode: continue   # not fetched here: not used
        if subprocess.run(['git', 'merge-base', '--is-ancestor', sc, after], cwd=R).returncode == 0:
            if hit is None: hit = a
        elif a.get('activity_type') == 'force_push': dropped.append(a.get('timestamp'))
    out = dict(seal=os.path.basename(sealp), seal_commit=sc, source=src, raw_sha256=sha_bytes(json.dumps(raw, sort_keys=True).encode()),
               force_pushes_without_seal=dropped)
    if not hit: out.update(outcome='CANNOT_TELL', reason='NOT_RELEASED', note='no push in the host record carries the seal commit')
    else: out.update(pushed_at=hit['timestamp'], pushed_head=hit['after'], actor=(hit.get('actor') or {}).get('login'))
    wp = os.path.join(os.path.dirname(sealp), os.path.basename(sealp).replace('SEAL_', 'WITNESS_'))
    json.dump(dict(out, raw=raw), open(wp, 'w'), indent=1); out['witness_file'] = wp
    return out

def run_start(args_kind, value):
    """-> (start datetime or None, witness class, error)"""
    if args_kind == 'user_stated':
        t = utc(value); return (t, 'user_stated', None if t else 'time has no offset or does not parse (refused)')
    if args_kind == 'wrapper':
        d = json.load(open(value)); t = utc(d.get('started_at')); return (t, 'wrapper', None if t else 'METHOD_UNSTATED')
    if args_kind == 'ibm_job':
        d = json.load(open(value)); s = d.get('running') or d.get('start') or (d.get('metrics', {}).get('timestamps', {}) or {}).get('running') or d.get('created') or d.get('creation_date')
        t = utc(s) if s else None; return (t, 'host_read' if d.get('_fetched_from_host') else 'user_file', None if t else 'METHOD_UNSTATED')
    if args_kind == 'ci_log':
        txt = open(value, errors='replace').read(); m = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})', txt)
        t = utc(m.group(0)) if m else None; return (t, 'user_file', None if t else 'METHOD_UNSTATED')
    return (None, None, 'unknown kind')

def all_seals(R):
    out = []
    for p in sorted(glob.glob(os.path.join(R, 'prereg', 'seals', 'SEAL_*.json'))):
        try: out.append((os.path.basename(p), [e['path'] for e in json.load(open(p))['files']]))
        except Exception: pass
    return out

def check(sealp, kind, value, cover_set=None):
    doc = json.load(open(sealp)); tol = doc['tolerance_s']
    if kind != doc['run_record_kind']: return dict(outcome='REFUSED', reason=f"the seal names run_record_kind {doc['run_record_kind']}, not {kind}")
    wp = os.path.join(os.path.dirname(sealp), os.path.basename(sealp).replace('SEAL_', 'WITNESS_'))
    if not os.path.exists(wp): return dict(outcome='CANNOT_TELL', reason='NOT_RELEASED', note='no witness file; run witness right after the push')
    w = json.load(open(wp)); t_push = utc(w.get('pushed_at')) if w.get('pushed_at') else None
    t_run, wclass, err = run_start(kind, value)
    base = dict(seal=os.path.basename(sealp), tolerance_s=tol, run_time_class=wclass, pushed_at=w.get('pushed_at'))
    R = root(os.path.dirname(os.path.abspath(sealp))); seals = all_seals(R); base['seals_in_repository'] = len(seals)
    if cover_set: base['seals_naming_a_run_file'] = sum(1 for n, fs in seals if set(fs) & set(cover_set))
    if t_push is None: return dict(base, outcome='CANNOT_TELL', reason='NOT_RELEASED')
    if err == 'METHOD_UNSTATED': return dict(base, outcome='CANNOT_TELL', reason='METHOD_UNSTATED')
    if err: return dict(base, outcome='REFUSED', reason=err)
    gap = (t_run - t_push).total_seconds(); base.update(run_start=t_run.strftime('%Y-%m-%dT%H:%M:%SZ'), gap_s=gap)
    if gap > tol: return dict(base, outcome='BEFORE', wording='the witnessed push precedes the first run in the supplied record')
    if gap < -tol: return dict(base, outcome='AFTER', wording='the first run in the supplied record precedes the witnessed push')
    return dict(base, outcome='CANNOT_TELL', reason='STRADDLES_EDGE')

def verify(sealp):
    doc = json.load(open(sealp)); R = root(os.path.dirname(os.path.abspath(sealp))); res = []
    for e in doc['files']:
        cur = git('rev-parse', f"HEAD:{e['path']}", cwd=R, check=False).strip()
        wt = sha_file(os.path.join(R, e['path'])) if os.path.exists(os.path.join(R, e['path'])) else None
        res.append(dict(path=e['path'], blob_drift=cur != e['blob'], working_tree_drift=wt != e['sha256_committed']))
    return res

def run(cmd, cwd=None):
    R = root(cwd); st = now(); files = {}
    for line in git('ls-files', '-co', '--exclude-standard', cwd=R).splitlines() + git('ls-files', '-oi', '--exclude-standard', '--directory', cwd=R).splitlines():
        p = os.path.join(R, line)
        if os.path.isfile(p) and line.lower().endswith(CODE_EXT) and os.path.getsize(p) < 10 * 1024 * 1024 and not line.startswith('prereg/'): files[line] = sha_file(p)
    base = os.path.realpath(cwd or os.getcwd()); argv_files = [os.path.realpath(os.path.join(base, a)) for a in cmd if os.path.isfile(os.path.join(base, a))]
    rec = dict(started_at=st, command=cmd, cwd=os.path.abspath(cwd or os.getcwd()), host=socket.gethostname(),
               git_status=git('status', '--porcelain', '--ignored', cwd=R).splitlines(), files_sha256=files,
               argv_files=[os.path.relpath(a, R) if a.startswith(R + os.sep) else a for a in argv_files],
               note='started_at is written by prereg at start (class wrapper): self-held, not typed')
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
    return dict(argv_files_not_sealed=sorted(set(rec['argv_files']) - set(sealed)), code_files_not_sealed=not_sealed, sealed_files_changed_at_run=changed,
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
    chk('check BEFORE (run 1 h after the push)', check(sp, 'user_stated', '2026-11-13T11:00:00Z')['outcome'], 'BEFORE')
    chk('check AFTER (run 1 h before the push)', check(sp, 'user_stated', '2026-11-13T09:00:00Z')['outcome'], 'AFTER')
    c = check(sp, 'user_stated', '2026-11-13T10:01:00Z'); chk('check 60 s apart: STRADDLES_EDGE', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'STRADDLES_EDGE'))
    c = check(sp, 'user_stated', '2026-11-13T11:00:00'); chk('check refuses a time with no offset', c['outcome'], 'REFUSED')
    c = check(sp, 'wrapper', 'x'); chk('check refuses a run-record kind the seal did not name', c['outcome'], 'REFUSED')
    chk('check carries the witness class', check(sp, 'user_stated', '2026-11-13T11:00:00Z')['run_time_class'], 'user_stated')
    json.dump([{'activity_type': 'push', 'timestamp': '2026-11-13T10:00:00Z', 'after': '0' * 40}], open(hr, 'w'))
    os.remove(sp.replace('SEAL_', 'WITNESS_')); w = witness(sp, hr); c = check(sp, 'user_stated', '2026-11-13T11:00:00Z')
    chk('no push carrying the seal: NOT_RELEASED', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'NOT_RELEASED'))
    # wrapper seal: run, cover, METHOD_UNSTATED
    open(os.path.join(td, 'config.yaml'), 'w').write('alpha: 1\n'); open(os.path.join(td, 'scratch.log'), 'w').write('x\n')
    sp2 = seal([os.path.join(td, 'PLAN.md'), os.path.join(td, 'analyze.py')], kind='wrapper', cwd=td); sh('git', 'add', sp2); sh('git', 'commit', '-qm', 'seal2')
    rp, rc = run([sys.executable, 'analyze.py'], cwd=td)
    cv = cover(sp2, rp)
    chk('cover lists the config that ran but was not sealed', 'config.yaml' in cv['code_files_not_sealed'], True)
    chk('cover sees ignored files present at run time', 'scratch.log' in cv['ignored_at_run'], True)
    d = json.load(open(rp)); d.pop('started_at'); bad = os.path.join(td, 'bad_run.json'); json.dump(d, open(bad, 'w'))
    json.dump([{'activity_type': 'push', 'timestamp': '2026-11-13T10:00:00Z', 'after': sh('git', 'rev-parse', 'HEAD').stdout.strip()}], open(hr, 'w')); witness(sp2, hr)
    c = check(sp2, 'wrapper', bad); chk('a run record with no parseable start: METHOD_UNSTATED', (c['outcome'], c.get('reason')), ('CANNOT_TELL', 'METHOD_UNSTATED'))
    chk('forking plans: seals in the repository are counted', check(sp2, 'wrapper', rp, cover_set=['PLAN.md'])['seals_naming_a_run_file'], 2)
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
