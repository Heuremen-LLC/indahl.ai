#!/usr/bin/env python3
"""spend_cap.py: a Claude Code PreToolUse hook that refuses tool calls once an agent session has used the budget you set.

Agents run up cost quietly: a loop that retries, a subagent fan-out, a long unattended run. Before every tool call this hook reads the
session's own transcript and its subagents' transcripts, adds up the tokens recorded there (each message once), and refuses the call once
the session is over budget. It refuses tool calls. It does not stop the session: the call already in flight, refused retries and the final
report all run past the cap. It guards against a runaway loop, not against an agent that edits the budget file to keep going.

Budget files: ./.claude/spend-cap.json (project) and ~/.claude/spend-cap.json (home). When both exist, both are enforced, so the stricter
wins and a project file can never loosen your own cap. Keys (each optional, at least one limit required):
  "max_tokens": 5000000             raw tokens: input + output + cache writes + cache reads, unweighted
  "cache_read_weight": 0.1          optional: count cache reads at this weight (cache reads bill at about a tenth of input on Anthropic's list today, check yours)
  "max_usd": 20, "prices_per_mtok": {"input": 5, "output": 25, "cache_write": 6.25, "cache_read": 0.5}   your own prices, none are built in
  "warn_at": 0.8                    one warning when this share of a limit is first passed
A budget file that cannot be read, or that has a limit without the numbers it needs, refuses tool calls until it is fixed or deleted: a
person who wrote a cap believes it is on. A missing transcript is allowed, with a visible note. With no budget file the hook does nothing.
Usage: PreToolUse JSON on stdin. `spend_cap.py report TRANSCRIPT` prints the totals. `spend_cap.py selftest`.
Standard library only. Nothing leaves the machine. Heuremen LLC, https://indahl.ai. MIT."""
import glob, hashlib, json, os, sys, tempfile

CLASSES = ('input', 'output', 'cache_write', 'cache_read')

def home_dir():   # one place for the home folder, so the selftest can point it elsewhere on every OS (Windows ignores HOME, Sage)
    return os.environ.get('INDAHL_SPEND_CAP_HOME') or os.path.expanduser('~')

def budget_files(cwd):
    out = []
    for p in (os.path.join(cwd or '.', '.claude', 'spend-cap.json'), os.path.join(home_dir(), '.claude', 'spend-cap.json')):
        if os.path.exists(p) and os.path.abspath(p) not in [os.path.abspath(x) for x, _ in out]:
            try:
                with open(p) as f: b = json.load(f)
                out.append((p, b if isinstance(b, dict) else {'_error': 'not a JSON object'}))
            except Exception as e: out.append((p, {'_error': 'cannot be read (%s)' % type(e).__name__}))
    return out

def usage(transcript):
    """Sum usage over the transcript and its subagents' transcripts. A message written on several lines carries the same usage on every
    line (checked on 14 Nov 2026: 1,762 of 2,455 messages in one session repeated, all identical), so each message id is counted once."""
    files = [transcript] + sorted(glob.glob(os.path.join(os.path.splitext(transcript)[0], 'subagents', '*.jsonl')))
    seen, tot, unread = set(), dict(input=0, output=0, cache_write=0, cache_read=0, messages=0), []
    for fp in files:
        try: fh = open(fp, encoding='utf-8', errors='replace')
        except Exception: unread.append(fp); continue
        with fh:
            for ln in fh:
                if '"usage"' not in ln: continue
                try: d = json.loads(ln)
                except Exception: continue
                m = d.get('message') if isinstance(d.get('message'), dict) else None
                u = m and m.get('usage')
                if not isinstance(u, dict): continue
                key = ('id:' + m['id']) if m.get('id') else ('req:' + d['requestId']) if d.get('requestId') else ('line:' + hashlib.sha256(ln.encode()).hexdigest())
                if key in seen: continue
                seen.add(key); tot['messages'] += 1
                tot['input'] += u.get('input_tokens') or 0; tot['output'] += u.get('output_tokens') or 0
                tot['cache_write'] += u.get('cache_creation_input_tokens') or 0; tot['cache_read'] += u.get('cache_read_input_tokens') or 0
    tot['files'] = len(files) - len(unread); tot['unread'] = unread
    return tot

def session_transcript(path):
    """The session's main transcript. If the hook was handed a subagent's own file (<session>/subagents/x.jsonl), walk up to <session>.jsonl, so a
    subagent is counted against the whole session's budget and not only against itself. (The docs give the main transcript to SubagentStop.
    For PreToolUse inside a subagent they do not say, so both are handled.)"""
    if path and os.path.basename(os.path.dirname(path)) == 'subagents':
        main = os.path.dirname(os.path.dirname(path)) + '.jsonl'
        if os.path.exists(main): return main
    return path

def num(b, k):
    v = b.get(k)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 else None

def limits(b):
    """-> list of (unit, used_fn, limit, warn_at), or an error string for a config that cannot be enforced."""
    if '_error' in b: return b['_error']
    out = []; warn = num(b, 'warn_at') if 'warn_at' in b else 0.8
    if warn is None or warn > 1: return 'warn_at must be a number between 0 and 1'
    if 'max_tokens' in b:
        lim = num(b, 'max_tokens'); w = num(b, 'cache_read_weight') if 'cache_read_weight' in b else 1.0
        if lim is None or w is None: return 'max_tokens and cache_read_weight must be non-negative numbers'
        out.append(('tokens', lambda t, w=w: t['input'] + t['output'] + t['cache_write'] + w * t['cache_read'], lim, warn))
    if 'max_usd' in b:
        lim = num(b, 'max_usd'); pr = b.get('prices_per_mtok') if isinstance(b.get('prices_per_mtok'), dict) else {}
        if lim is None: return 'max_usd must be a non-negative number'
        if not all(isinstance(pr.get(k), (int, float)) and not isinstance(pr.get(k), bool) for k in CLASSES): return 'max_usd needs prices_per_mtok with numbers for input, output, cache_write and cache_read'
        out.append(('usd', lambda t, pr=pr: sum(t[k] * float(pr[k]) for k in CLASSES) / 1e6, lim, warn))
    if not out: return 'it has neither max_tokens nor max_usd'
    return out

def fmt(unit, x): return ('$%.2f' % x) if unit == 'usd' else '{:,.0f} tokens'.format(x)
def breakdown(t): return 'input {:,}, output {:,}, cache writes {:,}, cache reads {:,} over {:,} messages'.format(t['input'], t['output'], t['cache_write'], t['cache_read'], t['messages'])

def marker(transcript, tag): return os.path.join(tempfile.gettempdir(), 'indahl-spend-cap-' + hashlib.sha256((transcript + '|' + tag).encode()).hexdigest()[:20])
def warned_before(transcript, tag): return os.path.exists(marker(transcript, tag))
def mark_warned(transcript, tags):   # written only when the warning is actually emitted (Sage: a later deny must not swallow it)
    for tag in tags:
        try: open(marker(transcript, tag), 'w').close()
        except Exception: pass

def check(ev):
    """-> (decision, message) with decision 'allow', 'warn' or 'deny'."""
    files = budget_files(ev.get('cwd'))
    if not files: return 'allow', ''
    plans = []
    for path, b in files:
        lim = limits(b)
        if isinstance(lim, str): return 'deny', ('spend-cap: the budget file %s %s. Tool calls are refused until it is fixed or deleted. The agent cannot fix it, because its own edit '
                                                  'would be refused too: stop and ask the person to edit or delete %s by hand.' % (path, lim, path))
        plans += [(path,) + x for x in lim]
    tr = session_transcript(ev.get('transcript_path'))
    if not tr or not os.path.exists(tr): return 'warn', 'spend-cap: no transcript to read, so the budget cannot be checked for this call (CANNOT_TELL).'
    t = usage(tr); warns = []; tags = []
    for path, unit, used_fn, lim, warn in plans:
        used = used_fn(t)
        if used >= lim:
            return 'deny', ('spend-cap: this session has used %s of the %s budget in %s (%s). Tool calls are refused from here. Stop, report what is done '
                            'and what is not, and ask the person whether to raise the budget.' % (fmt(unit, used), fmt(unit, lim), path, breakdown(t)))
        tag = '%s|%s|%s|%s' % (path, unit, lim, warn)   # the limit is in the tag, so raising the cap re-arms the warning
        if lim and used >= warn * lim and not warned_before(tr, tag):
            tags.append(tag); warns.append('spend-cap: %s of %s used (%.0f%%, %s), budget in %s.' % (fmt(unit, used), fmt(unit, lim), 100 * used / lim, breakdown(t), path))
    if warns: mark_warned(tr, tags); return 'warn', ' '.join(warns)
    return 'allow', ''

def emit(decision, msg):
    """PreToolUse output (Claude Code hooks reference, read 14 Nov 2026). deny: exit 2, the reason on stderr goes to the model. warn: exit 0 with
    JSON, systemMessage shown to the person and additionalContext added to the model's context. No permissionDecision is set, so the
    normal permission prompts still apply. Plain stderr on exit 0 never reaches the model, so it is not used. allow: exit 0, silent."""
    if decision == 'deny': print(msg, file=sys.stderr); return 2
    if decision == 'warn' and msg:
        print(json.dumps({'systemMessage': msg, 'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': msg}}))
    return 0

def selftest():
    import shutil
    bad = 0; tmp = tempfile.mkdtemp()
    def want(n, g, e):
        nonlocal bad; ok = g == e; bad += not ok; print(('PASS ' if ok else 'FAIL ') + n + ' -> ' + repr(g))
    home = os.environ.get('INDAHL_SPEND_CAP_HOME')
    try:
        os.environ['INDAHL_SPEND_CAP_HOME'] = os.path.join(tmp, 'home'); os.makedirs(os.path.join(tmp, 'home', '.claude'))
        tr = os.path.join(tmp, 'sess.jsonl'); os.makedirs(os.path.join(tmp, 'sess', 'subagents'))
        msg = lambda i, a, b: json.dumps({'type': 'assistant', 'requestId': 'r' + i, 'message': {'id': 'm' + i, 'usage': {'input_tokens': a, 'output_tokens': b, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 1000}}})
        noid = lambda a: json.dumps({'type': 'assistant', 'message': {'usage': {'input_tokens': a, 'output_tokens': 0}}})
        open(tr, 'w').write('\n'.join([msg('1', 100, 50), msg('1', 100, 50), msg('2', 200, 100), noid(1), noid(2), noid(3)]) + '\n')
        open(os.path.join(tmp, 'sess', 'subagents', 'a.jsonl'), 'w').write(msg('3', 300, 150) + '\n')
        t = usage(tr)
        want('repeated message counted once, id-less lines counted each', t['messages'], 6); want('subagent and id-less input', t['input'], 606)
        cwd = os.path.join(tmp, 'proj'); os.makedirs(os.path.join(cwd, '.claude')); P = os.path.join(cwd, '.claude', 'spend-cap.json'); H = os.path.join(tmp, 'home', '.claude', 'spend-cap.json')
        ev = dict(cwd=cwd, transcript_path=tr); put = lambda p, o: open(p, 'w').write(o if isinstance(o, str) else json.dumps(o))
        want('no budget file: allow', check(ev)[0], 'allow')
        put(P, {'max_tokens': 100000}); want('under budget: allow', check(ev)[0], 'allow')
        put(P, {'max_tokens': 3000}); want('raw tokens by default (3,906 > 3,000): deny', check(ev)[0], 'deny')
        put(P, {'max_tokens': 3000, 'cache_read_weight': 0.1}); want('weighted only when asked (1,206 of 3,000): allow or warn', check(ev)[0] in ('allow', 'warn'), True)
        put(P, {'max_tokens': 4500, 'warn_at': 0.8}); r1 = check(ev); r2 = check(ev); want('warns once, then quiet', (r1[0], r2[0]), ('warn', 'allow'))
        want('warning shows all four classes', 'cache reads' in r1[1], True)
        put(P, {'max_usd': 1}); want('usd without prices: deny', check(ev)[0], 'deny')
        put(P, '{broken'); want('broken project file: deny', check(ev)[0], 'deny')
        put(P, {'max_tokens': 'lots'}); want('non-numeric limit: deny', check(ev)[0], 'deny')
        put(P, {'warn_at': 0.5}); want('no limit key: deny', check(ev)[0], 'deny')
        put(P, {'max_tokens': 10000000}); put(H, {'max_tokens': 3000}); want('project cannot loosen the home cap', check(ev)[0], 'deny')
        put(P, {'max_tokens': 10000000, 'max_usd': 0.000001, 'prices_per_mtok': {'input': 5, 'output': 25, 'cache_write': 6.25, 'cache_read': 0.5}}); os.remove(H)
        want('both limits enforced: usd trips', check(ev)[0], 'deny')
        put(P, {'max_tokens': 1000}); want('missing transcript: warn visibly, CANNOT_TELL', check(dict(cwd=cwd, transcript_path='/nope')), ('warn', 'spend-cap: no transcript to read, so the budget cannot be checked for this call (CANNOT_TELL).'))
        want('deny exits 2', emit('deny', ''), 2)
        put(P, {'max_tokens': 4400, 'warn_at': 0.8}); r = check(ev); want('a new limit re-arms the warning', check(dict(ev))[0] == 'allow' and r[0] == 'warn', True)
        put(P, {'max_tokens': 3000}); put(H, {'max_tokens': 100000, 'warn_at': 0.01}); want('a deny does not swallow a warning', (check(ev)[0], warned_before(tr, '%s|tokens|100000.0|0.01' % H)), ('deny', False)); os.remove(H)
        put(P, {'max_tokens': 3000}); sub = os.path.join(tmp, 'sess', 'subagents', 'a.jsonl')
        want('called from a subagent transcript, counts the whole session', check(dict(cwd=cwd, transcript_path=sub))[0], 'deny')
        import io, contextlib; buf = io.StringIO()
        with contextlib.redirect_stdout(buf): emit('warn', 'near')
        o = json.loads(buf.getvalue()); want('warn sets no permission decision', 'permissionDecision' in o['hookSpecificOutput'], False)
        want('warn reaches person and model', (o['systemMessage'], o['hookSpecificOutput']['additionalContext']), ('near', 'near'))
    finally:
        if home is None: os.environ.pop('INDAHL_SPEND_CAP_HOME', None)
        else: os.environ['INDAHL_SPEND_CAP_HOME'] = home
        shutil.rmtree(tmp, ignore_errors=True)
    print('selftest: %s' % ('all pass' if not bad else '%d FAILED' % bad)); return 1 if bad else 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest': return selftest()
    if len(sys.argv) > 2 and sys.argv[1] == 'report': print(json.dumps(usage(sys.argv[2]), indent=1)); return 0
    try: ev = json.load(sys.stdin)
    except Exception: return emit('warn', 'spend-cap: the hook input could not be read, so the budget was not checked for this call (CANNOT_TELL).')
    d, m = check(ev)
    if os.environ.get('INDAHL_SPEND_CAP_LOG'):   # optional debug log: what each call handed the hook and what the hook decided
        try:
            with open(os.environ['INDAHL_SPEND_CAP_LOG'], 'a') as f: f.write(json.dumps(dict(tool=ev.get('tool_name'), transcript_path=ev.get('transcript_path'), agent_id=ev.get('agent_id'), agent_type=ev.get('agent_type'), decision=d)) + '\n')
        except Exception: pass
    return emit(d, m)

if __name__ == '__main__': sys.exit(main())
