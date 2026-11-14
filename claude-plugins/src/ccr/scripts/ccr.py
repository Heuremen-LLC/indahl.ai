#!/usr/bin/env python3
"""Indahl CCR: Custody Chain Receipts. Design v7 (ccr/DESIGN.md), refereed by Sage over seven rounds on 14 Nov 2026.

An append-only, hash-chained record of what an agent read, wrote, approved and released, so "who did this" has an answer
from the record instead of from whoever was newest. Standard library only. Signing (optional) uses `ssh-keygen -Y sign`.

  ccr.py init [--principal NAME] [--key PATH]     start a chain in .ccr/ (nothing is recorded without it)
  ccr.py hook                                      Claude Code hook entry point (reads the hook JSON on stdin, never blocks)
  ccr.py approve PATH [--lines A-B] [--by NAME] [--normalise crlf]
  ccr.py release PATH... [--by NAME]               hashes what ships and compares it with the approvals
  ccr.py redact STORE_KEY --reason TEXT            removes approved bytes from the side store, as an entry
  ccr.py why PATH [--window SECONDS]               attribution (shown) and races; cause is left to a judge
  ccr.py verify [--transcripts DIR]                chain integrity, signatures, anchors, unpaired calls, session cross-check
  ccr.py anchor                                    records the head for an outside copy (TAPE, a public push)
  ccr.py selftest

What the chain SHOWS and what a reader JUDGES are kept apart. A typed hash is the typer's word, so approve and release hash
the files themselves. The principal is a label set by the operator, never an identity.
"""
import hashlib, json, os, re, subprocess, sys, time, tempfile, shutil, glob

ROOT_ENV = 'CLAUDE_PROJECT_DIR'
WRITE_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}
READ_TOOLS = {'Read'}
TASK_TOOLS = {'Task', 'Agent'}


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()


def fhash(p):
    try:
        with open(p, 'rb') as f: return sha(f.read())
    except OSError: return None


class Chain:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.d = os.path.join(self.root, '.ccr')
        self.path = os.path.join(self.d, 'chain.jsonl')
        self.store = os.path.join(self.d, 'store')
        self.cfg_path = os.path.join(self.d, 'config.json')

    def exists(self): return os.path.isfile(self.cfg_path)

    def cfg(self):
        try: return json.load(open(self.cfg_path))
        except (OSError, ValueError): return {}

    def entries(self):
        out = []
        try:
            for ln in open(self.path, encoding='utf-8'):
                ln = ln.strip()
                if ln: out.append(json.loads(ln))
        except OSError: pass
        return out

    def _lock(self):
        lk = os.path.join(self.d, 'lock'); t0 = time.time()
        while True:
            try: os.mkdir(lk); return lk
            except FileExistsError:
                if time.time() - t0 > 10:   # a lock older than 10 s is a crashed writer, and the gap shows in verify, not here
                    try: os.rmdir(lk)
                    except OSError: pass
                time.sleep(0.01)

    def append(self, body):
        lk = self._lock()
        try:
            es = self.entries(); last = es[-1] if es else None
            e = dict(body)
            e['seq'] = (last['seq'] + 1) if last else 0
            e['prev_hash'] = last['entry_hash'] if last else None
            e['clock_local'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')   # this machine's clock, stated as such; seq is the order that counts
            e['principal'] = self.cfg().get('principal')
            e['principal_asserted_by_operator'] = True
            e['entry_hash'] = sha(canon({k: v for k, v in e.items() if k not in ('entry_hash', 'signature')}))
            sig = self._sign(e['entry_hash'])
            if sig: e['signature'] = sig
            with open(self.path, 'a', encoding='utf-8') as f: f.write(canon(e) + '\n')
            return e
        finally:
            try: os.rmdir(lk)
            except OSError: pass

    def _sign(self, h):
        key = self.cfg().get('signing_key')
        if not key: return None
        try:
            r = subprocess.run(['ssh-keygen', '-Y', 'sign', '-q', '-f', key, '-n', 'ccr'], input=h.encode(), capture_output=True, timeout=10)
            return r.stdout.decode() if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError): return None

    def put_store(self, b):
        os.makedirs(self.store, exist_ok=True)
        k = sha(b); p = os.path.join(self.store, k)
        if not os.path.exists(p):
            with open(p, 'wb') as f: f.write(b)
        return k

    def get_store(self, k):
        try:
            with open(os.path.join(self.store, k), 'rb') as f: return f.read()
        except OSError: return None


def find_root():
    r = os.environ.get(ROOT_ENV) or os.getcwd()
    d = os.path.abspath(r)
    while True:
        if os.path.isdir(os.path.join(d, '.ccr')): return d
        up = os.path.dirname(d)
        if up == d: return os.path.abspath(r)
        d = up


def rel(root, p):
    if not p: return p
    ap = os.path.abspath(os.path.join(root, p))
    try: return os.path.relpath(ap, root) if not os.path.relpath(ap, root).startswith('..') else ap
    except ValueError: return ap


# ---------- hook ----------
def actor_of(ev):
    a = dict(session_id=ev.get('session_id'), transcript_path=ev.get('transcript_path'))
    if ev.get('agent_id'): a['agent_id'] = ev.get('agent_id'); a['agent_type'] = ev.get('agent_type')
    return a


def instruction_of(ch, actor):
    """The nearest real instruction: inside a subagent the parent's Task call, otherwise the last user prompt; plus the distance."""
    es = ch.entries(); n = 0
    for e in reversed(es):
        if e.get('kind') == 'pre': n += 1
        same = e.get('actor', {}).get('session_id') == actor.get('session_id')
        if actor.get('agent_id'):
            if same and e.get('kind') == 'pre' and e.get('action', {}).get('tool') in TASK_TOOLS and not e.get('actor', {}).get('agent_id'):
                return dict(seq=e['seq'], kind='parent_task_call', distance=n)
        elif same and e.get('kind') == 'instruction':
            return dict(seq=e['seq'], kind='user_prompt', distance=n)
    return dict(seq=None, kind='none_recorded', distance=n)


def tool_paths(tool, ti):
    p = ti.get('file_path') or ti.get('notebook_path')
    return [p] if p else []


def hook(ev, ch):
    name = ev.get('hook_event_name'); actor = actor_of(ev); root = ch.root
    if name == 'UserPromptSubmit':
        return ch.append(dict(kind='instruction', actor=actor, prompt_sha256=sha(str(ev.get('prompt', '')))))
    if name == 'SessionStart':
        return ch.append(dict(kind='session_start', actor=actor, source=ev.get('source')))
    tool = ev.get('tool_name'); ti = ev.get('tool_input') or {}
    if name == 'PermissionDenied':   # a denied call is an entry too, never a silence
        return ch.append(dict(kind='denied', actor=actor, action=dict(tool=tool, args_sha256=sha(canon(ti)), call_id=ev.get('tool_use_id'))))
    action = dict(tool=tool, args_sha256=sha(canon(ti)), call_id=ev.get('tool_use_id'))
    if ch.cfg().get('store_arguments'): action['args'] = ti   # off by default: an append-only chain cannot forget a secret
    paths = tool_paths(tool, ti)
    if name == 'PreToolUse':
        body = dict(kind='pre', actor=actor, action=action, instruction=instruction_of(ch, actor))
        if tool in READ_TOOLS: body['reads'] = [dict(path=rel(root, p), sha256=fhash(os.path.join(root, p))) for p in paths]; body['reads_observed'] = 'tool'
        elif tool in WRITE_TOOLS: body['writes'] = [dict(path=rel(root, p), before=fhash(os.path.join(root, p))) for p in paths]; body['writes_observed'] = 'tool'
        else: body['reads_observed'] = body['writes_observed'] = 'none'   # a Bash build touches files nobody saw: "not observed", never "touched nothing"
        return ch.append(body)
    if name in ('PostToolUse', 'PostToolUseFailure'):
        body = dict(kind='post', actor=actor, action=action, failed=(name == 'PostToolUseFailure'))
        if tool in WRITE_TOOLS: body['writes'] = [dict(path=rel(root, p), after=fhash(os.path.join(root, p))) for p in paths]; body['writes_observed'] = 'tool'
        return ch.append(body)
    return None


# ---------- approve / release ----------
def lines_of(b):
    return b.splitlines(keepends=True)


def norm(b, how):
    return b.replace(b'\r\n', b'\n') if how == 'crlf' else b


def approve(ch, path, lines=None, by=None, normalise=None):
    ap = os.path.join(ch.root, path)
    raw = open(ap, 'rb').read()
    if lines:
        a, b = lines
        ls = lines_of(raw)
        if not (1 <= a <= b <= len(ls)): raise SystemExit('refused: --lines %d-%d is outside the file (%d lines)' % (a, b, len(ls)))
        part = b''.join(ls[a - 1:b]); scope = dict(kind='range', start=a, end=b)
    else:
        part = raw; scope = dict(kind='file')
    k = ch.put_store(part)   # the bytes live in the side store; the chain holds only their hash
    return ch.append(dict(kind='approval', by=by, path=rel(ch.root, path), file_sha256=sha(raw), approved_scope=scope,
                          approved_hash=sha(part), store_key=k, normalisation=normalise))


def redact(ch, key, reason):
    p = os.path.join(ch.store, key)
    existed = os.path.exists(p)
    if existed: os.remove(p)
    return ch.append(dict(kind='redaction', store_key=key, reason=reason, removed=existed))


def compare(ch, appr, raw, redactions):
    """One approval against one released file. Returns outcome, reason and the released line numbers it covers."""
    st = ch.get_store(appr['store_key'])
    if st is None:
        return ('CANNOT_TELL', 'REDACTED' if appr['store_key'] in redactions else 'UNLOGGED_REMOVAL', set())
    if sha(st) != appr['approved_hash']:   # the integrity check runs on the raw stored bytes, before any search or normalisation
        return ('GAP', 'tampered store: the side-store bytes do not match the approved hash in the chain', set())
    n = appr.get('normalisation')
    if appr['approved_scope']['kind'] == 'file':
        same = norm(st, n) == norm(raw, n)
        return ('SAME' if same else 'CHANGED', None if same else 'the released file differs from the approved file', set(range(1, len(lines_of(raw)) + 1)) if same else set())
    hay, needle = norm(raw, n), norm(st, n)
    hits = [m.start() for m in re.finditer(re.escape(needle), hay)] if needle else []
    if not hits: return ('CHANGED', 'the approved lines were not found in the released file', set())
    if len(hits) > 1: return ('CANNOT_TELL', 'AMBIGUOUS: the approved lines occur %d times' % len(hits), set())
    start_line = hay[:hits[0]].count(b'\n') + 1
    span = set(range(start_line, start_line + max(1, needle.count(b'\n'))))
    a0 = appr['approved_scope']['start']
    if start_line == a0: return ('SAME', None, span)
    return ('MOVED', 'found once at line %d, approved at line %d: identical bytes in a new place, a reviewer judges the new context' % (start_line, a0), span)


def release(ch, paths, by=None):
    es = ch.entries()
    redactions = {e['store_key'] for e in es if e.get('kind') == 'redaction'}
    results = []
    for p in paths:
        rp = rel(ch.root, p); raw = open(os.path.join(ch.root, p), 'rb').read()
        last_rel = max([e['seq'] for e in es if e.get('kind') == 'release' and rp in [x['path'] for x in e.get('released', [])]] or [-1])
        apps = [e for e in es if e.get('kind') == 'approval' and e.get('path') == rp and e['seq'] > last_rel]
        rows, covered = [], set()
        for a in apps:
            out, why, cov = compare(ch, a, raw, redactions); covered |= cov
            rows.append(dict(approval_seq=a['seq'], scope=a['approved_scope'], outcome=out, reason=why))
        total = len(lines_of(raw))
        uncovered = sorted(set(range(1, total + 1)) - covered)
        results.append(dict(path=rp, sha256=sha(raw), approvals=rows, lines=total, uncovered_lines=len(uncovered),
                            uncovered_ranges=ranges(uncovered), unapproved=not apps))
    e = ch.append(dict(kind='release', by=by, released=[dict(path=r['path'], sha256=r['sha256']) for r in results], comparison=results))
    return e, results


def ranges(xs):
    out = []
    for x in xs:
        if out and x == out[-1][1] + 1: out[-1][1] = x
        else: out.append([x, x])
    return ['%d-%d' % (a, b) if a != b else str(a) for a, b in out]


# ---------- why ----------
def why(ch, path, window=120):
    rp = rel(ch.root, path); es = ch.entries(); cur = fhash(os.path.join(ch.root, path))
    writes, reads = [], []
    for e in es:
        if e.get('kind') == 'post' and not e.get('failed'):
            for w in e.get('writes', []):
                if w['path'] == rp: writes.append((e, w['after']))
        if e.get('kind') == 'pre':
            for r in e.get('reads', []):
                if r['path'] == rp: reads.append(dict(seq=e['seq'], sha256=r['sha256'], bound=False, actor=e.get('actor')))
        if e.get('kind') == 'approval' and e['path'] == rp: reads.append(dict(seq=e['seq'], sha256=e['file_sha256'], bound=True, by=e.get('by')))
        if e.get('kind') == 'release':
            for x in e.get('released', []):
                if x['path'] == rp: reads.append(dict(seq=e['seq'], sha256=x['sha256'], bound=True, by=e.get('by')))
    races = []
    for i in range(len(reads)):   # race type 2: a write between two reads that should have seen the same version
        for j in range(i + 1, len(reads)):
            a, b = reads[i], reads[j]
            if a['sha256'] == b['sha256']: continue
            mid = [(e, h) for e, h in writes if a['seq'] < e['seq'] < b['seq']]
            if mid:
                races.append(dict(type='write_between_reads', first_read=a['seq'], second_read=b['seq'], writes=[e['seq'] for e, _ in mid],
                                  status='SHOWN' if a['bound'] and b['bound'] else 'INFERRED (at least one read is not bound by ccr)'))
            break
    for i in range(len(writes)):   # race type 1: two writers to one path inside the window
        for j in range(i + 1, len(writes)):
            e1, e2 = writes[i][0], writes[j][0]
            who = lambda e: (e['actor'].get('session_id'), e['actor'].get('agent_id'))
            if who(e1) != who(e2) and abs(tstamp(e2) - tstamp(e1)) <= window:
                races.append(dict(type='two_writers', writes=[e1['seq'], e2['seq']], window_s=window, status='SHOWN'))
    writer = [e for e, h in writes if h == cur]
    if races: attribution = dict(state='RACE', detail='a race was found, so no single writer is named', races=races)
    elif writer: attribution = dict(state='WRITTEN_BY', entry=writer[-1]['seq'], actor=writer[-1]['actor'])
    else: attribution = dict(state='UNATTRIBUTED', detail='no entry wrote the current bytes (an editor, a script, or anything outside the hooks)')
    return dict(path=rp, current_sha256=cur, attribution=attribution,
                cause=dict(state='NOT_JUDGED', detail='cause (AGENT, INSTRUCTION, ENVIRONMENT or CANNOT_TELL) is a judgement from these entries, made and signed by a named judge, never by this script'))


def tstamp(e):
    try: return time.mktime(time.strptime(e['clock_local'][:19], '%Y-%m-%dT%H:%M:%S'))
    except (KeyError, ValueError): return 0


# ---------- verify / anchor ----------
def verify(ch, transcripts=None):
    es = ch.entries(); problems = []; prev = None
    for i, e in enumerate(es):
        if e.get('seq') != i: problems.append('GAP: seq %s at line %d, expected %d' % (e.get('seq'), i + 1, i))
        if e.get('prev_hash') != prev: problems.append('GAP: seq %s does not link to the entry before it' % e.get('seq'))
        if sha(canon({k: v for k, v in e.items() if k not in ('entry_hash', 'signature')})) != e.get('entry_hash'):
            problems.append('GAP: seq %s was altered after it was written' % e.get('seq'))
        prev = e.get('entry_hash')
    pres = {e['action'].get('call_id'): e['seq'] for e in es if e.get('kind') == 'pre' and e['action'].get('call_id')}
    posts = {e['action'].get('call_id') for e in es if e.get('kind') == 'post'}
    unpaired = sorted(s for c, s in pres.items() if c not in posts)
    anchors = []
    try: anchors = [json.loads(l) for l in open(os.path.join(ch.d, 'anchors.jsonl')) if l.strip()]
    except OSError: pass
    for a in anchors:
        if a['seq'] >= len(es): problems.append('GAP: the chain is shorter than anchor seq %d (truncated)' % a['seq'])
        elif es[a['seq']]['entry_hash'] != a['entry_hash']: problems.append('GAP: entry %d does not match its anchor' % a['seq'])
    signed = sum(1 for e in es if e.get('signature')); key = ch.cfg().get('signing_key')
    sessions = {e.get('actor', {}).get('session_id') for e in es}
    missing = []
    tdir = transcripts or ch.cfg().get('transcripts_dir')
    if tdir and os.path.isdir(tdir) and es:   # listed independently of any launcher record, so a session started without the launcher still shows
        t0 = tstamp(es[0])
        for f in glob.glob(os.path.join(tdir, '*.jsonl')):
            sid = os.path.basename(f)[:-6]
            if os.path.getmtime(f) >= t0 and sid not in sessions: missing.append(sid)
    for s in missing: problems.append('GAP: session %s has a transcript and no entries (hooks off, or a session ccr never saw)' % s)
    return dict(entries=len(es), problems=problems, unpaired_calls=dict(seqs=unpaired, reads='CANNOT_TELL on the result (denied, failed or cut off)'),
                anchors_checked=len(anchors), signed=signed,
                key=None if not key else dict(path=key, reachable_by_actor=os.access(key, os.R_OK),
                     note='a key the actor can read can re-sign a rewritten chain, so its signatures prove order only to someone who trusts the actor' if os.access(key, os.R_OK) else 'the key file is not readable by this user'),
                session_cross_check='ran on ' + tdir if tdir and os.path.isdir(tdir) else 'not run (no transcripts directory): completeness unknown',
                completeness='holds up to the last anchor and only for sessions the cross-check saw')


def anchor(ch):
    es = ch.entries()
    if not es: raise SystemExit('nothing to anchor')
    a = dict(seq=es[-1]['seq'], entry_hash=es[-1]['entry_hash'], at=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    with open(os.path.join(ch.d, 'anchors.jsonl'), 'a') as f: f.write(canon(a) + '\n')
    return a


# ---------- selftest ----------
def selftest():
    bad = 0; home = os.getcwd(); tmp = tempfile.mkdtemp(prefix='ccr-')
    def want(name, got, exp):
        nonlocal bad
        ok = got == exp; bad += not ok
        print(('PASS ' if ok else 'FAIL ') + name + (' -> %r' % (got,) if not ok else ''))
    try:
        os.chdir(tmp); ch = Chain(tmp); os.makedirs(ch.d); json.dump(dict(principal='test-operator'), open(ch.cfg_path, 'w'))
        S = dict(session_id='s1', transcript_path='/t/s1.jsonl')
        def ev(name, tool=None, ti=None, sid='s1', **kw): return dict(S, session_id=sid, hook_event_name=name, tool_name=tool, tool_input=ti or {}, **kw)
        open('a.py', 'w').write(''.join('line %d\n' % i for i in range(1, 11)))
        hook(ev('UserPromptSubmit', prompt='fix it'), ch)
        hook(ev('PreToolUse', 'Read', {'file_path': 'a.py'}, tool_use_id='r1'), ch); hook(ev('PostToolUse', 'Read', {'file_path': 'a.py'}, tool_use_id='r1'), ch)
        want('read recorded with its hash', ch.entries()[1]['reads'][0]['sha256'], fhash('a.py'))
        want('instruction distance counted', ch.entries()[1]['instruction']['kind'], 'user_prompt')
        want('verify clean chain', verify(ch)['problems'], [])
        # approvals and releases
        approve(ch, 'a.py', (3, 5), by='Sage')
        e, r = release(ch, ['a.py'], by='ship'); want('unchanged range reads SAME', r[0]['approvals'][0]['outcome'], 'SAME')
        want('uncovered lines reported', r[0]['uncovered_lines'], 7)
        approve(ch, 'a.py', (3, 5), by='Sage')
        hook(ev('PreToolUse', 'Edit', {'file_path': 'a.py'}, tool_use_id='e1'), ch)
        open('a.py', 'w').write('new top\n' + ''.join('line %d\n' % i for i in range(1, 11)))
        hook(ev('PostToolUse', 'Edit', {'file_path': 'a.py'}, tool_use_id='e1'), ch)
        e, r = release(ch, ['a.py']); want('shifted range reads MOVED, not SAME', r[0]['approvals'][0]['outcome'], 'MOVED')
        approve(ch, 'a.py', (4, 6), by='Sage')
        open('a.py', 'w').write('new top\nline 1\nline 2\nline 3\nINSERTED\nline 4\nline 5\n')
        e, r = release(ch, ['a.py']); want('edit inside the range reads CHANGED (the 14 Nov specimen)', r[0]['approvals'][0]['outcome'], 'CHANGED')
        open('d.txt', 'w').write('x\ny\nx\ny\n'); approve(ch, 'd.txt', (1, 2))
        e, r = release(ch, ['d.txt']); want('approved lines found twice read CANNOT_TELL', r[0]['approvals'][0]['outcome'], 'CANNOT_TELL')
        open('b.txt', 'w').write('secret = 1\nok\n'); ap = approve(ch, 'b.txt', (1, 1))
        redact(ch, ap['store_key'], 'a key was in the reviewed range')
        e, r = release(ch, ['b.txt']); want('redacted store reads CANNOT_TELL REDACTED', (r[0]['approvals'][0]['outcome'], r[0]['approvals'][0]['reason']), ('CANNOT_TELL', 'REDACTED'))
        open('c.txt', 'w').write('alpha\nbeta\n'); ap = approve(ch, 'c.txt', (1, 1)); os.remove(os.path.join(ch.store, ap['store_key']))
        e, r = release(ch, ['c.txt']); want('deleted store with no entry reads UNLOGGED_REMOVAL', r[0]['approvals'][0]['reason'], 'UNLOGGED_REMOVAL')
        open('t.txt', 'w').write('version A\n'); ap = approve(ch, 't.txt')
        open('t.txt', 'w').write('version B\n'); open(os.path.join(ch.store, ap['store_key']), 'wb').write(b'version B\n')
        e, r = release(ch, ['t.txt']); want('store overwritten with the shipped bytes reads GAP, never SAME', r[0]['approvals'][0]['outcome'], 'GAP')
        open('n.txt', 'wb').write(b'one\r\ntwo\r\n'); approve(ch, 'n.txt', (1, 1), normalise='crlf'); open('n.txt', 'wb').write(b'one\ntwo\n')
        e, r = release(ch, ['n.txt']); want('declared normalisation applies to the search only', r[0]['approvals'][0]['outcome'], 'SAME')
        open('u.txt', 'w').write('nobody looked\n'); e, r = release(ch, ['u.txt']); want('release with no approval says so', r[0]['unapproved'], True)
        # why: race between bound reads, sequential control, unattributed edit
        open('w.txt', 'w').write('A\n'); approve(ch, 'w.txt', by='reviewer')
        hook(ev('PreToolUse', 'Edit', {'file_path': 'w.txt'}, tool_use_id='e2'), ch); open('w.txt', 'w').write('B\n'); hook(ev('PostToolUse', 'Edit', {'file_path': 'w.txt'}, tool_use_id='e2'), ch)
        release(ch, ['w.txt'], by='ship')
        y = why(ch, 'w.txt'); want('write between approval read and release read is a SHOWN race', (y['attribution']['state'], y['attribution']['races'][0]['status']), ('RACE', 'SHOWN'))
        want('cause is never judged by the script', y['cause']['state'], 'NOT_JUDGED')
        open('q.txt', 'w').write('A\n')
        hook(ev('PreToolUse', 'Edit', {'file_path': 'q.txt'}, tool_use_id='e3'), ch); open('q.txt', 'w').write('B\n'); hook(ev('PostToolUse', 'Edit', {'file_path': 'q.txt'}, tool_use_id='e3'), ch)
        approve(ch, 'q.txt', by='reviewer'); release(ch, ['q.txt'], by='ship')
        y = why(ch, 'q.txt'); want('sequential control (edit, then review, then ship) is not a race', y['attribution']['state'], 'WRITTEN_BY')
        open('q.txt', 'w').write('typed in an editor\n')
        want('edit outside the hooks reads UNATTRIBUTED', why(ch, 'q.txt')['attribution']['state'], 'UNATTRIBUTED')
        hook(ev('PreToolUse', 'Read', {'file_path': 'w.txt'}, tool_use_id='r9'), ch); hook(ev('PreToolUse', 'Edit', {'file_path': 'w.txt'}, tool_use_id='e9'), ch)
        open('w.txt', 'w').write('C\n'); hook(ev('PostToolUse', 'Edit', {'file_path': 'w.txt'}, tool_use_id='e9'), ch); hook(ev('PreToolUse', 'Read', {'file_path': 'w.txt'}, tool_use_id='r10'), ch)
        y = why(ch, 'w.txt'); want('a race between unbound reads is INFERRED', any(r['status'].startswith('INFERRED') for r in y['attribution'].get('races', [])), True)
        hook(ev('PreToolUse', 'Edit', {'file_path': 'z.txt'}, sid='s1', tool_use_id='z1'), ch); open('z.txt', 'w').write('1\n'); hook(ev('PostToolUse', 'Edit', {'file_path': 'z.txt'}, sid='s1', tool_use_id='z1'), ch)
        hook(ev('PreToolUse', 'Edit', {'file_path': 'z.txt'}, sid='s2', tool_use_id='z2'), ch); open('z.txt', 'w').write('2\n'); hook(ev('PostToolUse', 'Edit', {'file_path': 'z.txt'}, sid='s2', tool_use_id='z2'), ch)
        want('two writers inside the window is a race', why(ch, 'z.txt')['attribution']['races'][0]['type'], 'two_writers')
        # subagent instruction
        hook(ev('PreToolUse', 'Agent', {'prompt': 'go'}, tool_use_id='t1'), ch)
        x = hook(ev('PreToolUse', 'Read', {'file_path': 'a.py'}, tool_use_id='r11', agent_id='ag1', agent_type='general'), ch)
        want('inside a subagent the instruction is the parent Task call', x['instruction']['kind'], 'parent_task_call')
        # verify: unpaired, anchors, truncation, alteration, sessions
        want('denied or cut-off call reads unpaired', 'r9' in [e['action'].get('call_id') for e in ch.entries() if e['seq'] in verify(ch)['unpaired_calls']['seqs']], True)
        anchor(ch); want('verify clean after anchor', verify(ch)['problems'], [])
        lines = open(ch.path).read().splitlines(True)
        open(ch.path, 'w').write(''.join(lines[:-1])); want('truncated tail reads GAP against the anchor', any('shorter than anchor' in p for p in verify(ch)['problems']), True)
        open(ch.path, 'w').write(''.join(lines))
        bad_line = json.loads(lines[3]); bad_line['by'] = 'someone else'; lines2 = list(lines); lines2[3] = canon(bad_line) + '\n'
        open(ch.path, 'w').write(''.join(lines2)); want('altered entry reads GAP', any('altered' in p for p in verify(ch)['problems']), True)
        open(ch.path, 'w').write(''.join(lines))
        td = os.path.join(tmp, 'transcripts'); os.makedirs(td); open(os.path.join(td, 's1.jsonl'), 'w').write('{}'); open(os.path.join(td, 'ghost.jsonl'), 'w').write('{}')
        want('a transcript with no entries reads GAP (hooks off)', [p for p in verify(ch, td)['problems'] if 'ghost' in p] != [], True)
        want('arguments are hash-only by default', 'args' in ch.entries()[1]['action'], False)
        want('a denied call is recorded', hook(ev('PermissionDenied', 'Bash', {'command': 'rm x'}, tool_use_id='d1'), ch)['kind'], 'denied')
        want('principal is marked as asserted', ch.entries()[0]['principal_asserted_by_operator'], True)
        cfg = ch.cfg(); cfg['signing_key'] = os.path.join(tmp, 'k'); json.dump(cfg, open(ch.cfg_path, 'w'))
        if shutil.which('ssh-keygen'):
            subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', cfg['signing_key']], check=True)
            e = ch.append(dict(kind='note')); want('entries are signed when a key is set', 'SSH SIGNATURE' in e.get('signature', ''), True)
            want('a key the actor can read is reported as reachable', verify(ch)['key']['reachable_by_actor'], True)
    finally:
        os.chdir(home); shutil.rmtree(tmp, ignore_errors=True)
    print('selftest: %s' % ('all pass' if not bad else '%d FAILED' % bad)); return 1 if bad else 0


def main(a):
    if not a: print(__doc__); return 0
    cmd, rest = a[0], a[1:]
    if cmd == 'selftest': return selftest()
    root = find_root(); ch = Chain(root)
    if cmd == 'hook':
        try:
            if not ch.exists(): return 0   # no chain started here: record nothing, block nothing
            hook(json.load(sys.stdin), ch)
        except Exception as ex:   # the hook never blocks the work; the failure is kept where verify and a reader can see it
            try:
                with open(os.path.join(ch.d, 'errors.log'), 'a') as f: f.write('%s %r\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), ex))
            except OSError: pass
        return 0
    def opt(name, default=None):
        if name in rest:
            i = rest.index(name); v = rest[i + 1]; del rest[i:i + 2]; return v
        return default
    if cmd == 'init':
        os.makedirs(ch.d, exist_ok=True)
        c = ch.cfg(); c.setdefault('principal', opt('--principal')); k = opt('--key')
        if k: c['signing_key'] = os.path.abspath(k)
        c.setdefault('store_arguments', False)
        c.setdefault('transcripts_dir', os.path.join(os.path.expanduser('~/.claude/projects'), re.sub(r'[^A-Za-z0-9]', '-', ch.root)))
        json.dump(c, open(ch.cfg_path, 'w'), indent=1); print('ccr: chain ready in %s' % ch.d); return 0
    if not ch.exists(): print('refused: no chain here. Start one: ccr.py init'); return 1
    if cmd == 'approve':
        by = opt('--by'); ln = opt('--lines'); nm = opt('--normalise')
        lines = tuple(int(x) for x in ln.split('-')) if ln else None
        print(canon(approve(ch, rest[0], lines, by, nm))); return 0
    if cmd == 'release':
        by = opt('--by'); e, r = release(ch, rest, by); print(json.dumps(r, indent=1))
        return 0 if all(x['outcome'] in ('SAME',) for p in r for x in p['approvals']) and not any(p['unapproved'] for p in r) else 3
    if cmd == 'redact':
        reason = opt('--reason')
        if not reason: print('refused: a redaction needs --reason'); return 1
        print(canon(redact(ch, rest[0], reason))); return 0
    if cmd == 'why': w = int(opt('--window', 120)); print(json.dumps(why(ch, rest[0], w), indent=1)); return 0
    if cmd == 'verify': v = verify(ch, opt('--transcripts')); print(json.dumps(v, indent=1)); return 0 if not v['problems'] else 2
    if cmd == 'anchor': print(canon(anchor(ch))); return 0
    print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
