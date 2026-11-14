#!/usr/bin/env python3
"""rubicon.py: the Indahl Rubicon gate. Decide what "done" means before the work, and ask for "done" to wait until three blind seats have judged it.
A record and a prompt, not a lock: it catches a careless "done", not a determined one.

Work can pass every check and still fail. Four ways it happens, and what the gate asks for against each (a record and a prompt, not a lock):
  1. The finish line is written after the work.          freeze: criteria are frozen with a hash (time from this machine's clock).
  2. The checks are written by the same hand as the work. grid: three blind seats judge, not the worker.
  3. A check that cannot fail passes anything.            freeze: every criterion names a planted wrong answer, and seats report catching it.
  4. A majority vote erases the dissent.                  grid: a two-to-one split reads UNRESOLVED, with the minority's reason kept.
And one question no checklist asks: can a seat build a way the work passes every check and still fails? If it can, the criteria have a hole.

Commands (all files live in .rubicon/ in the working folder):
  rubicon.py freeze CRITERIA.md      freeze the criteria. Lines: "- C1: <criterion> | check: <how it is checked> | fails-on: <planted wrong answer>"
  rubicon.py grid GRID.json          tally three seats x three questions and write the verdict (format in the skill)
  rubicon.py ack ROW "reason"        acknowledge an UNRESOLVED or CANNOT_TELL row. It stays open in the record, with the reason beside it
  rubicon.py person yes|no "words"   record the asker's own answer as row Q2_PERSON, apart from the seats' prediction
  rubicon.py status                  print the frozen criteria and the verdict
  rubicon.py stop                    Stop hook: interrupts the first attempt to finish when there is no verdict, the verdict is for older criteria,
                                     a row is UNRESOLVED or CANNOT_TELL and unacknowledged, or the verdict is MISSED. A second stop goes through.
  rubicon.py selftest                planted cases
Outcomes: MET, MISSED, UNRESOLVED, CANNOT_TELL. Standard library only. Nothing leaves the machine. Heuremen LLC, https://indahl.ai. MIT."""
import hashlib, json, os, re, sys, time

D = '.rubicon'
OUTCOMES = ('MET', 'MISSED', 'CANNOT_TELL')
LINE = re.compile(r'^\s*[-*]\s*(C\d+)\s*:\s*(.+?)\s*\|\s*check\s*:\s*(.+?)\s*\|\s*fails-on\s*:\s*(.+?)\s*$', re.I)

def now(): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
def load(name, default=None):
    p = os.path.join(D, name)
    if not os.path.exists(p): return default
    with open(p) as f: return json.load(f)
def save(name, obj):
    os.makedirs(D, exist_ok=True)
    with open(os.path.join(D, name + '.tmp'), 'w') as f: json.dump(obj, f, indent=1)
    os.replace(os.path.join(D, name + '.tmp'), os.path.join(D, name))

def parse_criteria(text):
    rows, bad = [], []
    for ln in text.splitlines():
        if not ln.strip() or not re.match(r'^\s*[-*]', ln): continue
        m = LINE.match(ln)
        if m: rows.append(dict(id=m.group(1).upper(), criterion=m.group(2), check=m.group(3), fails_on=m.group(4)))
        else: bad.append(ln.strip())
    return rows, bad

def chash(text, after):   # the criteria hash covers the original file and every criterion added after it (Sage: a stale verdict must not pass)
    return hashlib.sha256((text + '\n' + json.dumps(after, sort_keys=True)).encode()).hexdigest()

def check_rows(rows, have):
    for r in rows:
        if r['id'] in have: return 'refused: %s already exists' % r['id']
        if len(r['fails_on']) < 8: return 'refused: %s has no real planted wrong answer. A check that cannot fail passes anything.' % r['id']
        have.add(r['id'])
    return None

def freeze(path):
    if load('frozen.json'): return 1, 'refused: criteria are already frozen (%s). Add a criterion with "freeze FILE --after" and it is labelled defined after the work.' % load('frozen.json')['sha256'][:12]
    text = open(path).read(); rows, bad = parse_criteria(text)
    if bad: return 1, 'refused: these lines are not "- C1: criterion | check: ... | fails-on: ...":\n  ' + '\n  '.join(bad[:10])
    if not rows: return 1, 'refused: no criteria found'
    err = check_rows(rows, set())
    if err: return 1, err
    save('frozen.json', dict(frozen_at=now(), frozen_at_clock='this machine', text=text, sha256=chash(text, []), source=os.path.abspath(path), criteria=rows, after=[]))
    return 0, 'frozen: %d criteria, sha256 %s. Work may start now.' % (len(rows), chash(text, [])[:12])

def freeze_after(path):
    fr = load('frozen.json')
    if not fr: return 1, 'refused: nothing frozen yet, use freeze'
    rows, bad = parse_criteria(open(path).read())
    if bad or not rows: return 1, 'refused: no valid criteria lines'
    err = check_rows(rows, {r['id'] for r in fr['criteria'] + fr['after']})
    if err: return 1, err
    for r in rows: r['defined_after_the_work'] = True; r['added_at'] = now()
    fr['after'] += rows; fr['sha256'] = chash(fr['text'], fr['after']); save('frozen.json', fr)
    return 0, 'added %d criteria, labelled defined after the work. The criteria hash changed, so the grid must be run again.' % len(rows)

def tally3(answers):
    """answers: three outcome strings. -> (outcome, minority index or None)."""
    a = [x if x in OUTCOMES else 'CANNOT_TELL' for x in answers]
    if len(set(a)) == 1: return a[0], None
    for v in set(a):
        if a.count(v) == 2: return 'UNRESOLVED', next(i for i, x in enumerate(a) if x != v)
    return 'CANNOT_TELL', None

def grid(path):
    fr = load('frozen.json')
    if not fr: return 1, 'refused: no frozen criteria. Cross the line first: rubicon.py freeze CRITERIA.md'
    g = json.load(open(path)); seats = g.get('seats') or []
    if len(seats) != 3: return 1, 'refused: the grid needs exactly three seats, got %d' % len(seats)
    if len({s.get('name') for s in seats}) != 3: return 1, 'refused: the three seats need three different names'
    crit = fr['criteria'] + fr['after']
    for s in seats:   # an unreadable answer refuses, it never falls through to CANNOT_TELL (Sage)
        for c in crit:
            a = (s.get('criteria') or {}).get(c['id'])
            if not isinstance(a, dict) or a.get('outcome') not in OUTCOMES: return 1, 'refused: seat %s has no readable answer for %s (outcome must be MET, MISSED or CANNOT_TELL)' % (s.get('name'), c['id'])
        if 'done' not in s or not (isinstance(s['done'], bool) or s['done'] is None): return 1, 'refused: seat %s has no done answer (true, false or null)' % s.get('name')
        if not isinstance(s.get('pass_but_fail'), str): return 1, 'refused: seat %s has no pass_but_fail answer (a description, or an empty string)' % s.get('name')
    rows = []
    for c in crit:
        ans = [s['criteria'][c['id']] for s in seats]
        out, mi = tally3([x['outcome'] for x in ans])
        row = dict(row=c['id'], question='meets the frozen criterion', criterion=c['criterion'], outcome=out, seats=[x['outcome'] for x in ans])
        if mi is not None: row['minority'] = dict(seat=seats[mi]['name'], says=ans[mi]['outcome'], reason=ans[mi].get('reason', '(no reason given)'))
        if out == 'MET' and not all(x.get('planted_fail_caught') is True for x in ans):   # every seat voting MET must report the check catching its planted wrong answer
            row['outcome'] = 'UNRESOLVED'; row['why'] = 'not every seat reported the check catching its planted wrong answer, so MET is not shown (self-reported by the seats)'
        if c.get('defined_after_the_work'): row['defined_after_the_work'] = True
        rows.append(row)
    done = [s['done'] for s in seats]
    out, mi = tally3(['MET' if x is True else 'MISSED' if x is False else 'CANNOT_TELL' for x in done])
    row = dict(row='Q2', question='the seats predict the person who asked would call this done', outcome=out, seats=done, note='a model\'s guess about the asker, not the asker')
    if mi is not None: row['minority'] = dict(seat=seats[mi]['name'], says=done[mi], reason=seats[mi].get('done_reason', '(no reason given)'))
    rows.append(row)
    holes = [(s['name'], s['pass_but_fail'].strip()) for s in seats if s['pass_but_fail'].strip()]
    if holes: rows.append(dict(row='Q3', question='a way to pass every check and still fail', outcome='UNRESOLVED', holes=[dict(seat=n, how=h) for n, h in holes],
                               why='a seat built a way to pass every check and still fail. The criteria have a hole until a criterion closes it.'))
    else: rows.append(dict(row='Q3', question='a way to pass every check and still fail', outcome='MET', why='no seat built one, which does not show that none exists'))
    prev = load('verdict.json') or {}
    v = dict(judged_at=now(), criteria_sha256=fr['sha256'], seats=[s['name'] for s in seats], independent=bool(g.get('independent')), rows=rows, acks={},
             note='agreement among seats from one model counts once, not three times' + ('' if g.get('independent') else '. The seats were not run as independent agents.'))
    if any(r['row'] == 'Q2_PERSON' for r in prev.get('rows', [])): v['person_answer_cleared'] = 'the person\'s earlier answer was about older work and was cleared by this grid. Ask again.'
    v['overall'] = overall(rows); save('verdict.json', v)
    return 0, 'verdict %s: ' % v['overall'] + ', '.join('%s %s' % (r['row'], r['outcome']) for r in rows)

def overall(rows):
    outs = [r['outcome'] for r in rows]
    return 'MET' if all(o == 'MET' for o in outs) else 'MISSED' if 'MISSED' in outs else 'UNRESOLVED' if 'UNRESOLVED' in outs else 'CANNOT_TELL'

def person(answer, words):   # Q2_PERSON: the asker's own answer, its own row, never mixed into the seat count (Sage)
    v = load('verdict.json')
    if not v: return 1, 'refused: no verdict yet'
    a = {'yes': 'MET', 'true': 'MET', 'no': 'MISSED', 'false': 'MISSED'}.get(answer.lower())
    if not a: return 1, 'refused: answer yes or no'
    if len(words.strip()) < 3: return 1, 'refused: record what the person said'
    v['rows'] = [r for r in v['rows'] if r['row'] != 'Q2_PERSON'] + [dict(row='Q2_PERSON', question='the person who asked calls this done', outcome=a, said=words.strip(), at=now())]
    v['overall'] = overall(v['rows']); save('verdict.json', v)
    return 0, 'recorded the person\'s answer: %s. Overall %s.' % (a, v['overall'])

def ack(row, reason):
    v = load('verdict.json')
    if not v: return 1, 'refused: no verdict yet'
    if not any(r['row'] == row and r['outcome'] in ('UNRESOLVED', 'CANNOT_TELL') for r in v['rows']): return 1, 'refused: %s is not an UNRESOLVED or CANNOT_TELL row' % row
    if len(reason.strip()) < 15: return 1, 'refused: give the reason in a sentence'
    v['acks'][row] = dict(reason=reason.strip(), at=now()); save('verdict.json', v)
    return 0, '%s acknowledged. It stays open in the record, with your reason beside it.' % row

def stop(payload):
    if payload.get('stop_hook_active'): return 0, ''   # never loop: the second stop in a row goes through
    fr = load('frozen.json')
    if not fr: return 0, ''                            # no Rubicon task in this folder
    v = load('verdict.json')
    if not v: return 2, 'Indahl Rubicon: this task has frozen criteria (%s) and no verdict. Run the three-seat grid (rubicon skill) before calling it done, or say plainly that it is not done.' % fr['sha256'][:12]
    if v.get('criteria_sha256') != fr['sha256']: return 2, 'Indahl Rubicon: the verdict was judged against different criteria. Run the grid again.'
    open_rows = [r['row'] for r in v['rows'] if r['outcome'] in ('UNRESOLVED', 'CANNOT_TELL') and r['row'] not in v.get('acks', {})]
    if open_rows: return 2, 'Indahl Rubicon: rows %s are open. Report them to the user as open, or acknowledge each with a reason (rubicon.py ack ROW "reason"). Do not report the task as done.' % ', '.join(open_rows)
    if v['overall'] == 'MISSED': return 2, 'Indahl Rubicon: the verdict is MISSED. Report that, with the rows that missed.'
    return 0, ''

def selftest():
    import tempfile, shutil
    bad = 0; home = os.getcwd(); tmp = tempfile.mkdtemp()
    def want(name, got, exp):
        nonlocal bad; ok = got == exp; bad += not ok; print(('PASS ' if ok else 'FAIL ') + name + ' -> ' + repr(got))
    try:
        os.chdir(tmp)
        open('c.md', 'w').write('- C1: the export has one row per order | check: count rows against the orders table | fails-on: an export with a duplicated order\n'
                                '- C2: totals match the ledger to the cent | check: sum and compare | fails-on: a total off by one cent\n')
        want('no criteria, stop passes', stop({})[0], 0)
        want('freeze', freeze('c.md')[0], 0)
        want('freeze twice refused', freeze('c.md')[0], 1)
        want('frozen, no verdict, stop refuses', stop({})[0], 2)
        want('stop_hook_active never loops', stop({'stop_hook_active': True})[0], 0)
        seat = lambda n, c1, c2, done, pbf, fired=True: dict(name=n, criteria={'C1': dict(outcome=c1, planted_fail_caught=fired, reason='r'), 'C2': dict(outcome=c2, planted_fail_caught=fired, reason='looked at cents')}, done=done, pass_but_fail=pbf)
        json.dump(dict(independent=True, seats=[seat('A', 'MET', 'MET', True, ''), seat('B', 'MET', 'MET', True, ''), seat('C', 'MET', 'MET', True, '')]), open('g.json', 'w'))
        want('all agree MET', grid('g.json')[1].split(':')[0], 'verdict MET'); want('MET, stop passes', stop({})[0], 0)
        json.dump(dict(independent=True, seats=[seat('A', 'MET', 'MET', True, ''), seat('B', 'MET', 'MET', True, ''), seat('C', 'MET', 'MISSED', True, '')]), open('g.json', 'w'))
        grid('g.json'); v = load('verdict.json'); r2 = [r for r in v['rows'] if r['row'] == 'C2'][0]
        want('two to one reads UNRESOLVED', r2['outcome'], 'UNRESOLVED'); want('minority kept with its reason', (r2['minority']['seat'], r2['minority']['reason']), ('C', 'looked at cents'))
        want('unacknowledged UNRESOLVED, stop refuses', stop({})[0], 2)
        want('short ack refused', ack('C2', 'ok')[0], 1)
        want('ack with reason', ack('C2', 'C checked a rounding mode we do not use, owner accepts')[0], 0)
        want('acknowledged, stop passes', stop({})[0], 0)
        want('acked row still UNRESOLVED in the record', [r for r in load('verdict.json')['rows'] if r['row'] == 'C2'][0]['outcome'], 'UNRESOLVED')
        json.dump(dict(independent=True, seats=[seat('A', 'MET', 'MET', True, ''), seat('B', 'MET', 'MET', True, 'an export that repeats the header row passes C1 and breaks the importer'), seat('C', 'MET', 'MET', True, '')]), open('g.json', 'w'))
        grid('g.json'); q3 = [r for r in load('verdict.json')['rows'] if r['row'] == 'Q3'][0]
        want('pass-but-fail found reads UNRESOLVED', q3['outcome'], 'UNRESOLVED')
        json.dump(dict(independent=True, seats=[seat('A', 'MET', 'MET', True, '', False), seat('B', 'MET', 'MET', True, '', False), seat('C', 'MET', 'MET', True, '', False)]), open('g.json', 'w'))
        grid('g.json'); want('MET without a check that fired is not MET', [r for r in load('verdict.json')['rows'] if r['row'] == 'C1'][0]['outcome'], 'UNRESOLVED')
        json.dump(dict(seats=[seat('A', 'MET', 'MET', True, ''), seat('B', 'MISSED', 'MET', False, ''), seat('C', 'CANNOT_TELL', 'MET', None, '')]), open('g.json', 'w'))
        grid('g.json'); want('three different answers read CANNOT_TELL', [r for r in load('verdict.json')['rows'] if r['row'] == 'C1'][0]['outcome'], 'CANNOT_TELL')
        want('not independent is noted', 'not run as independent' in load('verdict.json')['note'], True)
        json.dump(dict(seats=[seat('A', 'MET', 'MET', True, ''), seat('B', 'MET', 'MET', True, '')]), open('g.json', 'w')); want('two seats refused', grid('g.json')[0], 1)
        open('bad.md', 'w').write('- C9: something | check: x | fails-on: no\n'); shutil.rmtree(D); want('weak planted wrong answer refused', freeze('bad.md')[0], 1)
        # Sage pre-ship MOVES, each planted
        shutil.rmtree(D, ignore_errors=True); freeze('c.md')
        mk = lambda seats: json.dump(dict(independent=True, seats=seats), open('g.json', 'w'))
        mk([seat('A', 'MET', 'MET', True, ''), seat('B', 'MET', 'MET', True, ''), seat('C', 'MET', 'MET', True, '')]); grid('g.json'); want('baseline MET, stop passes', stop({})[0], 0)
        open('a.md', 'w').write('- C3: the export opens in the finance tool | check: import it | fails-on: a file with a byte order mark the tool rejects\n')
        want('after-criterion accepted', freeze_after('a.md')[0], 0); want('after-criterion post-verdict, stop refuses', stop({})[0], 2)
        open('a2.md', 'w').write('- C4: x is right | check: y | fails-on: no\n'); want('after with weak planted wrong answer refused', freeze_after('a2.md')[0], 1)
        open('a3.md', 'w').write('- C5: one thing holds | check: read it | fails-on: a planted wrong value here\n- C5: again | check: read it | fails-on: a planted wrong value here\n'); want('after with duplicate ids refused', freeze_after('a3.md')[0], 1)
        seat3 = lambda n, o, fired=True, pbf='', done=True: dict(name=n, criteria={k: dict(outcome=o, planted_fail_caught=fired, reason='r') for k in ('C1', 'C2', 'C3')}, done=done, pass_but_fail=pbf)
        mk([seat3('A', 'MET', True), seat3('B', 'MET', False), seat3('C', 'MET', False)]); grid('g.json')
        want('one of three fired is not MET', [r for r in load('verdict.json')['rows'] if r['row'] == 'C1'][0]['outcome'], 'UNRESOLVED')
        x = seat3('C', 'MET'); del x['criteria']['C2']; mk([seat3('A', 'MET'), seat3('B', 'MET'), x]); want('missing seat answer refused', grid('g.json')[0], 1)
        x = seat3('C', 'MET'); x['criteria']['C1']['outcome'] = 'met'; mk([seat3('A', 'MET'), seat3('B', 'MET'), x]); want('lowercase outcome refused', grid('g.json')[0], 1)
        mk([seat3('A', 'MET', pbf='   '), seat3('B', 'MET'), seat3('C', 'MET')]); grid('g.json'); want('whitespace pass_but_fail is not a hole', [r for r in load('verdict.json')['rows'] if r['row'] == 'Q3'][0]['outcome'], 'MET')
        mk([seat3('A', 'MET'), seat3('B', 'MISSED'), seat3('C', 'CANNOT_TELL')]); grid('g.json')
        want('ack a CANNOT_TELL row', ack('C1', 'the owner reviewed the three answers and accepts the risk')[0], 0)
        want('acked CANNOT_TELL stays in the record', [r for r in load('verdict.json')['rows'] if r['row'] == 'C1'][0]['outcome'], 'CANNOT_TELL')
        mk([seat3('A', 'MET'), seat3('B', 'MET'), seat3('C', 'MET', done=False)]); grid('g.json')
        want('Q2 named as a prediction', [r for r in load('verdict.json')['rows'] if r['row'] == 'Q2'][0]['question'].startswith('the seats predict'), True)
        want('person answer recorded as its own row', person('no', 'not yet, the totals tab is missing')[0], 0)
        want('person row is MISSED and overall follows', (next(r['outcome'] for r in load('verdict.json')['rows'] if r['row'] == 'Q2_PERSON'), load('verdict.json')['overall']), ('MISSED', 'MISSED'))
        x = seat3('C', 'MET'); x['done'] = 1; mk([seat3('A', 'MET'), seat3('B', 'MET'), x]); want('integer done refused', grid('g.json')[0], 1)
        mk([seat3('A', 'MET'), seat3('B', 'MET'), seat3('C', 'MET', done=False)]); grid('g.json'); want('new grid notes the cleared person answer', 'person_answer_cleared' in load('verdict.json'), True)
    finally: os.chdir(home); shutil.rmtree(tmp, ignore_errors=True)
    print('selftest: %s' % ('all pass' if not bad else '%d FAILED' % bad)); return 1 if bad else 0

def main(a):
    if not a: print(__doc__); return 0
    c = a[0]
    if c == 'selftest': return selftest()
    if c == 'stop':
        try: payload = json.load(sys.stdin)
        except Exception: payload = {}
        rc, msg = stop(payload)
        if msg: print(msg, file=sys.stderr)
        return rc
    if c == 'status':
        print(json.dumps(dict(frozen=load('frozen.json'), verdict=load('verdict.json')), indent=1)); return 0
    if c == 'freeze' and len(a) > 2 and a[2] == '--after': rc, msg = freeze_after(a[1])
    elif c == 'freeze' and len(a) > 1: rc, msg = freeze(a[1])
    elif c == 'grid' and len(a) > 1: rc, msg = grid(a[1])
    elif c == 'ack' and len(a) > 2: rc, msg = ack(a[1], ' '.join(a[2:]))
    elif c == 'person' and len(a) > 2: rc, msg = person(a[1], ' '.join(a[2:]))
    else: print(__doc__); return 1
    print(msg); return rc

if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
