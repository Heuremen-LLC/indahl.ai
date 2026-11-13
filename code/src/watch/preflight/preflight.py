"""preflight.py -- the pre-flight checker (spec: Sage, 5 Nov, from Bones's two worst catches of the week).
No run fires unless the outside-witnessed "before" precedes the first job AND the stamp covers what the launcher touches.

Checks (each prints PASS / FAIL / NOTE lines; any FAIL = NO-GO):
  TIME       every --proof FILE (with FILE.ots) must carry a Bitcoin attestation whose block (merkle root checked on two
             block servers) was mined BEFORE the first job. Pending calendar receipts count as zero. Prints both times and the gap.
             --witness-time ISO is an outside clock that is not OTS (e.g. an IBM job's created time read from IBM): it must also be before.
  COVERAGE   static trace of --launcher: shell scripts it calls (recursively), python files they run (string-literal paths and local
             imports), files read. Every traced input under the repo root must be named in a --stamped list with its current sha256.
             Not named = FAIL by name. Named but bytes changed = FAIL. Named in a --disclosed file = NOTE (unpinned, disclosed), not FAIL.
  OVERWRITE  any path a traced script truncates (">", "tee" without -a) that already exists and is tracked in git or named in a
             --cite / --stamped file = FAIL.
  GITIGNORE  any path a traced script "git add"s without -f that matches an ignore rule = FAIL (the add exits 1 and the proof is never committed).
It does not judge the science; only whether the "before" and the "what" are honestly pinned. Static tracing is heuristic:
paths built at run time (f-strings, string joins) are not traced and are listed as UNTRACED lines.

Usage: preflight.py [--first-job ISO|now|@job.json ...] [--proof F ...] [--witness-time ISO --witness-note TEXT]
                    [--launcher SH] [--stamped LIST ...] [--disclosed F ...] [--cite F ...] [--root DIR]
Exit 0 = GO, 1 = NO-GO, 2 = cannot tell (block API unreachable)."""
import sys, os, re, json, glob, hashlib, argparse, subprocess, urllib.request, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument('--first-job', action='append', default=[]); ap.add_argument('--proof', action='append', default=[])
ap.add_argument('--witness-time'); ap.add_argument('--tag-witness', action='append', default=[]); ap.add_argument('--witness-note', default='')
ap.add_argument('--launcher'); ap.add_argument('--stamped', action='append', default=[]); ap.add_argument('--disclosed', action='append', default=[])
ap.add_argument('--cite', action='append', default=[]); ap.add_argument('--root'); ap.add_argument('--allow', action='append', default=[])
A = ap.parse_args()
API = os.environ.get('PF_API', 'https://mempool.space/api'); API2 = os.environ.get('PF_API2', 'https://blockstream.info/api')
fails, waits = [], []
def out(tag, check, msg):
    print(f'{tag:6} {check:9} {msg}')
    if tag == 'FAIL': fails.append(check)
    if tag == 'WAIT': waits.append(check)
def iso(t): return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def parse_iso(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# ---------------- TIME ----------------
def first_job():
    ts = []
    for a in A.first_job or ['now']:
        if a == 'now': ts.append((dt.datetime.now(dt.timezone.utc).timestamp(), 'now (no job yet: the launch moment)'))
        elif a.startswith('@'):
            d = json.load(open(a[1:]))
            for j in d.get('jobs', []):
                c = (j.get('timestamps') or {}).get('created') or j.get('submitted_utc')
                ts.append((parse_iso(c), f"IBM job {j.get('job_id')} created {c} ({os.path.basename(a[1:])})"))
        else: ts.append((parse_iso(a), f'given {a}'))
    return min(ts)
def get(path, base):
    with urllib.request.urlopen(base + path, timeout=20) as r: return r.read().decode()
def check_time():
    if not A.proof and not A.witness_time and not A.tag_witness: out('NOTE', 'TIME', 'no proof or witness given: TIME not checked'); return
    t0, what = first_job(); out('NOTE', 'TIME', f'first job: {iso(t0)}  [{what}]')
    if A.witness_time:
        w = parse_iso(A.witness_time)
        tag = 'PASS' if w < t0 else 'FAIL'
        out(tag, 'TIME', f'outside witness {iso(w)} ({A.witness_note}) vs first job {iso(t0)}: gap {(t0 - w) / 60:+.1f} min (positive = before)')
    for tw in A.tag_witness:   # FILE=@job.json: IBM's record of the FIRST job must carry the file's hash in a job tag (set at creation, IBM's clock)
        f, jf = tw.split('=@'); h = sha(f); d = json.load(open(jf))
        js = sorted(d.get('jobs', []), key=lambda j: (j.get('timestamps') or {}).get('created') or j.get('submitted_utc'))
        j0 = js[0]; tags = j0.get('tags')
        hit = [t for t in (tags or []) if len(t.split(':')[-1]) >= 12 and h.startswith(t.split(':')[-1])]
        if tags is None:
            other = [j['job_id'] for j in js[1:] if any(h.startswith(t.split(':')[-1]) for t in (j.get('tags') or []) if len(t.split(':')[-1]) >= 12)]
            out('WAIT', 'TIME', f'{os.path.basename(f)}: the saved record of the first job {j0.get("job_id")} holds no tags, so it cannot show the hash'
                + (f' (later jobs {", ".join(other)} do carry it)' if other else '') + '. Pull job tags from IBM (read only) to decide.')
        elif hit: out('PASS', 'TIME', f'{os.path.basename(f)}: first job {j0.get("job_id")} carries tag {hit[0]} = sha256 {h[:16]}..., set when IBM created the job')
        else: out('FAIL', 'TIME', f'{os.path.basename(f)}: first job {j0.get("job_id")} tags {tags} do not carry sha256 {h[:16]}...')
    if not A.proof: return
    for f in A.proof:
        tag, msg = block_check(f, t0); out(tag, 'TIME', msg)
def block_check(f, t0):
    """(PASS|FAIL|WAIT, message): f's OTS proof verified against f's bytes and the block's merkle root on two servers, block mined before t0."""
    from opentimestamps.core.timestamp import DetachedTimestampFile
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    from opentimestamps.core.serialize import StreamDeserializationContext
    if not os.path.exists(f + '.ots'): return 'FAIL', f'{f}: no proof file {f}.ots'
    with open(f + '.ots', 'rb') as fh: d = DetachedTimestampFile.deserialize(StreamDeserializationContext(fh))
    if d.file_digest.hex() != sha(f): return 'FAIL', f'{f}: the proof is of different bytes (file changed after stamping, or wrong proof)'
    btc = [(m, a) for m, a in d.timestamp.all_attestations() if isinstance(a, BitcoinBlockHeaderAttestation)]
    if not btc: return 'FAIL', f'{f}: pending calendar receipts only, no Bitcoin block. That counts as zero: nothing outside us shows it existed before the first job.'
    m, a = min(btc, key=lambda x: x[1].height)
    try:
        h1 = get(f'/block-height/{a.height}', API).strip(); b1 = json.loads(get(f'/block/{h1}', API))
        h2 = get(f'/block-height/{a.height}', API2).strip(); b2 = json.loads(get(f'/block/{h2}', API2))
    except Exception as e: return 'WAIT', f'{f}: block {a.height}: block API unreachable ({type(e).__name__}); cannot tell'
    if h1 != h2 or b1['merkle_root'] != b2['merkle_root']: return 'WAIT', f'{f}: block {a.height}: the two block servers disagree; cannot tell'   # Sage (c): never GO
    if m[::-1].hex() != b1['merkle_root']: return 'FAIL', f'{f}: block {a.height}: the proof commitment does not match the merkle root'
    bt = b1['timestamp']; gap = (t0 - bt) / 60
    if bt < t0: return 'PASS', f'{f}: block {a.height} mined {iso(bt)}, first job {iso(t0)}: the block is {gap:.1f} min BEFORE the first job'
    return 'FAIL', f'{f}: block {a.height} mined {iso(bt)}, first job {iso(t0)}: the block came {-gap:.1f} min AFTER the first job. The proof is valid but it does not show "before".'

# ---------------- trace ----------------
PATHY = re.compile(r'''(?<![\w$/])((?:~|\.{1,2}|/)?(?:[\w.${}*~-]+/)*[\w.${}*-]+\.(?:py|sh|md|json|jsonl|txt|text|log|ots|sha256|yaml|yml|cjs|js|safetensors|npz|qpy|csv|toml|cfg))(?![\w])''')
def expand(s, env):
    for _ in range(4): s = re.sub(r'\$\{?(\w+)\}?', lambda m: env.get(m.group(1), m.group(0)), s)
    return s.replace('~', os.environ['HOME']) if s.startswith('~') else s
def resolve(p, cwd):
    p = os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd, p))
    hits = glob.glob(p) if any(c in p for c in '*?[') else [p]
    return [os.path.abspath(h) for h in hits] or [p]
T = {'inputs': {}, 'cwd': {}, 'trunc': {}, 'gitadd': [], 'untraced': [], 'seen': set()}
def trace_sh(path, depth=0):
    if path in T['seen'] or depth > 4: return
    T['seen'].add(path); env = dict(os.environ); cwd = os.path.dirname(path)
    for ln, raw in enumerate(open(path, errors='replace'), 1):
        line = raw.split(' #')[0] if not raw.lstrip().startswith('#') else ''
        if not line.strip(): continue
        for m in re.finditer(r'(?:^|[;\s])(\w+)="([^"]*)"', line): env[m.group(1)] = expand(m.group(2), env)
        x = expand(line, env); lcwd = cwd
        for seg in re.split(r';|&&|\|\|', x):
            sc = re.match(r'\s*(\()?\s*cd\s+"?([^"\s)]+)"?', seg)
            if sc:   # "(cd X && ...)" moves only this line (subshell); a bare "cd X" moves the rest of the script
                tgt = sc.group(2)
                if '$(dirname' in tgt or '`dirname' in tgt: lcwd = os.path.dirname(path)      # cd "$(dirname "$0")" = the script's own folder
                elif '$' in tgt or '`' in tgt: T['untraced'].append(f'{os.path.basename(path)}:{ln}: cd to a run-time path, trace keeps {lcwd}: {seg.strip()[:80]}')
                else: lcwd = resolve(tgt, lcwd)[0]
                if not sc.group(1) and '(' not in x.split(seg)[0]: cwd = lcwd
                continue
            # git add (with or without -f)
            g = re.search(r'git\s+(?:-C\s+"?([^"\s]+)"?\s+)?add\s+(.*)', seg)
            if g:
                base = g.group(1) or lcwd; args = g.group(2).replace('"', '').split(); force = any(a in ('-f', '--force') for a in args)
                for a in args:
                    if a.startswith('-') or a in ('&&', '||'): continue
                    for r in resolve(a, base): T['gitadd'].append((r, force, f'{os.path.basename(path)}:{ln}'))
                continue
            for m in re.finditer(r'(>>?)\s*"?([^\s";&|]+)"?', seg):
                if m.group(2).startswith('&') or m.group(2) == '/dev/null': continue
                for r in resolve(m.group(2), lcwd):
                    if m.group(1) == '>': T['trunc'].setdefault(r, f'{os.path.basename(path)}:{ln}')
            for m in re.finditer(r'tee\s+(-a\s+)?"?([^\s";&|]+)', seg):
                if not m.group(1):
                    for r in resolve(m.group(2), lcwd): T['trunc'].setdefault(r, f'{os.path.basename(path)}:{ln}')
            body = re.sub(r'(>>?)\s*"?[^\s";&|]+"?', ' ', seg)
            for m in PATHY.finditer(body):
                for r in resolve(m.group(1).strip('"'), lcwd): T['cwd'].setdefault(r, lcwd); add_input(r, f'{os.path.basename(path)}:{ln}', depth)
def add_input(r, where, depth):
    if not os.path.isfile(r): return
    T['inputs'].setdefault(r, where)
    if r.endswith('.sh'): trace_sh(r, depth + 1)
    elif r.endswith('.py'): trace_py(r, depth + 1)
def trace_py(path, depth):
    if path in T['seen'] or depth > 4: return
    T['seen'].add(path); d = os.path.dirname(path)
    src = open(path, errors='replace').read()
    for m in re.finditer(r'^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))', src, re.M):
        mod = (m.group(1) or m.group(2)).split('.')[0]
        for cand in (os.path.join(d, mod + '.py'), os.path.join(d, '..', '..', mod + '.py')):
            if os.path.isfile(cand): add_input(os.path.abspath(cand), os.path.basename(path), depth)
    for m in re.finditer(r'''(?<![fF])(['"])([^'"\n{}]+?\.(?:py|json|jsonl|txt|text|yaml|yml|md|sha256|safetensors|npz|qpy|csv))\1''', src):
        for r in resolve(m.group(2), d): add_input(r, os.path.basename(path), depth)
    for ln, l in enumerate(src.splitlines(), 1):
        if re.search(r'''open\(\s*f['"]|Path\(\s*f['"]|os\.path\.join\(''', l): T['untraced'].append(f'{os.path.basename(path)}:{ln}: {l.strip()[:110]}')

PAIRS = set()   # (hash, exact path string) for every hash line printed in a stamped document
def load_stamped():
    st = {}
    for L in A.stamped:
        base = os.path.dirname(os.path.abspath(L))
        for line in open(L, errors='replace'):
            m = re.match(r'\s*`?([0-9a-f]{64})`?\s+\*?`?([^`\s]+)`?', line)
            if m:
                cands = [resolve(m.group(2), os.path.join(base, *(['..'] * k)))[0] for k in range(4)] if not os.path.isabs(m.group(2)) else [m.group(2)]
                r = next((c for c in cands if os.path.exists(c)), cands[0]); st.setdefault(r, set()).add(m.group(1))
                PAIRS.add((m.group(1), m.group(2).lstrip('./') if m.group(2).startswith('./') else m.group(2)))
                st.setdefault('base:' + os.path.basename(m.group(2)), set()).add(m.group(1))
        if os.path.exists(L + '.ots'): st.setdefault(os.path.abspath(L), set()).add(sha(L))   # a file with its own proof is itself stamped
    return st

def check_trace():
    if not A.launcher: out('NOTE', 'COVERAGE', 'no launcher given: COVERAGE, OVERWRITE, GITIGNORE not checked'); return
    L = os.path.abspath(A.launcher); add_input(L, 'launcher', 0)
    root = os.path.abspath(A.root or subprocess.run(['git', '-C', os.path.dirname(L), 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip() or os.path.dirname(L))
    st = load_stamped(); disc = ''
    t0 = first_job()[0]
    for f in A.disclosed:   # Sage (a): a disclosure excuses nothing unless it was itself stamped before the first job
        tag, msg = block_check(f, t0)
        if tag == 'PASS': disc += open(f, errors='replace').read(); out('NOTE', 'COVERAGE', f'disclosure accepted: {msg}')
        else: out('NOTE', 'COVERAGE', f'disclosure NOT accepted ({tag}): {msg}')
    cited = ''.join(open(f, errors='replace').read() for f in A.cite + A.stamped)
    n_ok = 0
    for p, where in sorted(T['inputs'].items()):
        if p.endswith('.ots') or p in T['trunc']: continue                       # proofs are not stamped by nature; outputs are not inputs
        if not p.startswith(root + os.sep): out('NOTE', 'COVERAGE', f'environment, outside {root}: {p} (from {where})'); continue
        rel = os.path.relpath(p, root); have = st.get(p) or st.get('base:' + os.path.basename(p))
        if have and sha(p) in have: n_ok += 1; continue
        if have: out('FAIL', 'COVERAGE', f'{rel}: named in the stamp but its bytes changed since (now {sha(p)[:12]}..., stamped {sorted(have)[0][:12]}...) (from {where})'); continue
        ls = open(p, 'rb').read().decode(errors='replace').replace('\r\n', '\n').rstrip('\n').split('\n')   # Sage (b): strict; CRLF and trailing blanks normalised
        hl = [re.fullmatch(r'([0-9a-f]{64}) [ *](\S+)', l.rstrip()) for l in ls]
        base = T['cwd'].get(p, os.path.dirname(p))   # the folder the list is checked from (shasum -c runs there)
        bound = lambda m: m.group(1) in st.get(os.path.normpath(os.path.join(base, os.path.expanduser(m.group(2)))), ())
        if hl and all(hl) and all(bound(m) for m in hl):
            out('NOTE', 'COVERAGE', f'{rel}: not stamped, but DERIVED: every line binds the same file to the same hash a stamped document gives it ({len(hl)} lines) (from {where})'); continue
        if hl and all(hl):
            miss = [f'{m.group(1)[:12]}... {m.group(2)}' for m in hl if not bound(m)]
            out('FAIL', 'COVERAGE', f'{rel}: hash list, not stamped; {len(miss)} of {len(hl)} lines bind a file to a hash no stamped document gives it: {"; ".join(miss[:4])}{" ..." if len(miss) > 4 else ""} (from {where})'); continue
        if os.path.basename(p) in disc: out('NOTE', 'COVERAGE', f'{rel}: NOT stamped, named in a disclosure ({", ".join(os.path.basename(f) for f in A.disclosed)}): unpinned, disclosed (from {where})'); continue
        out('FAIL', 'COVERAGE', f'{rel}: touches the run but is NOT stamped (from {where})')
    out('PASS' if n_ok else 'NOTE', 'COVERAGE', f'{n_ok} traced inputs match a stamped sha256')
    allow = []
    for a in A.allow:   # PATTERN=LIST: a run-time path matching PATTERN is covered by LIST, which must be a stamped hash list
        pat, L = a.rsplit('=', 1); L = os.path.abspath(L)
        if sha(L) in st.get(L, ()): allow.append((re.compile(pat), os.path.basename(L)))
        else: out('NOTE', 'UNTRACED', f'allowlist {os.path.basename(L)} is not stamped: ignored')
    for u in T['untraced']:
        hit = next((n for r, n in allow if r.search(u)), None)
        out('NOTE' if hit else 'WAIT', 'UNTRACED', u + (f'  [covered by stamped {hit}]' if hit else '  [unresolved: cannot tell]'))   # Sage (e)
    bad = 0
    for p, where in sorted(T['trunc'].items()):
        if not os.path.exists(p): continue
        tracked = subprocess.run(['git', '-C', os.path.dirname(p), 'ls-files', '--error-unmatch', p], capture_output=True).returncode == 0
        named = os.path.basename(p) in cited
        if tracked or named: bad += 1; out('FAIL', 'OVERWRITE', f'{where} truncates {os.path.relpath(p, root)}, which already exists and is {"tracked in git" if tracked else ""}{" and " if tracked and named else ""}{"cited in the plan/stamp" if named else ""}')
        else: out('NOTE', 'OVERWRITE', f'{where} truncates existing {os.path.relpath(p, root)} (not tracked, not cited)')
    if not bad: out('PASS', 'OVERWRITE', f'{len(T["trunc"])} truncating writes; none hits an existing cited or tracked file')
    bad = 0
    for p, force, where in T['gitadd']:
        ign = subprocess.run(['git', '-C', root, 'check-ignore', '-q', '--no-index', p], capture_output=True).returncode == 0
        if ign and not force: bad += 1; out('FAIL', 'GITIGNORE', f'{where} git-adds {os.path.relpath(p, root)} without -f, and an ignore rule matches it: the add fails and the proof is never committed')
        elif ign: out('NOTE', 'GITIGNORE', f'{where} force-adds ignored {os.path.relpath(p, root)} (-f): OK')
    if not bad: out('PASS', 'GITIGNORE', f'{len(T["gitadd"])} git-add targets; none is silently ignored')

print(f'preflight.py sha256 {sha(os.path.abspath(__file__))}')
check_time(); check_trace()
v = 'NO-GO' if fails else ('CANNOT TELL' if waits else 'GO')
print(f'VERDICT {v}' + (f'  (failed: {", ".join(sorted(set(fails)))})' if fails else ''))
sys.exit(1 if fails else (2 if waits else 0))
