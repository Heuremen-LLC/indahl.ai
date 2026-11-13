#!/usr/bin/env python3
"""sagar_pipe.py -- the SAGAR indexing pipeline on HER ticks (Wayfinder 12 Nov 2026: "make a fucking PIPELINE ... no more one-off, one-row").
tick_bus rider. Each call advances the state machine without waiting:
  CUT    next 12 reachable papers -> index/batch_NN.json
  DRAFT  headless Sonnet agent (claude -p) drafts every cell -> index/batch_NN_draft.jsonl
  SECOND headless Sonnet agent, blind, re-checks every draft finding (F2 non-convention, F3, F5, F6) -> work/batch_NN_second.jsonl
  MERGE  a finding is VERIFIED only when both agree (reader verdict matches, confidence medium or high) -> index/verified_auto.jsonl;
         disagreements -> work/review_queue.jsonl (Wayfinder sees at most ~10 at a time)
At most MAXJOBS agent jobs at once. PAUSED file stops it. Every step is a line in pipe.log."""
import json, os, re, subprocess, sys, time
P = os.path.dirname(os.path.abspath(__file__)); I = os.path.join(os.path.dirname(P), 'index'); ST = os.path.join(P, 'state.json'); LOG = os.path.join(P, 'pipe.log')
CLAUDE = '/Users/heuremen/.local/bin/claude'; MAXJOBS = 2; BATCH = 12
def log(m): open(LOG, 'a').write(time.strftime('%Y-%m-%dT%H:%M:%S ') + m + '\n')
def alive(pid):
    try: os.kill(pid, 0); return True
    except Exception: return False
def load(f, d):
    try: return json.load(open(f))
    except Exception: return d
def save(f, o): t = f + '.tmp'; json.dump(o, open(t, 'w'), indent=1); os.replace(t, f)
def rows(f): return [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
def launch(name, prompt_file, batch):
    txt = open(os.path.join(P, 'prompts', prompt_file)).read().replace('{BATCH}', batch)
    lf = open(os.path.join(P, 'logs', f'{batch}_{name}.log'), 'a')
    p = subprocess.Popen([CLAUDE, '-p', txt, '--model', 'sonnet', '--dangerously-skip-permissions', '--output-format', 'text'],
                         cwd=P, stdout=lf, stderr=lf, start_new_session=True)
    log(f'LAUNCH {name} {batch} pid {p.pid}'); return p.pid
SEV = {'F2', 'F3', 'F5', 'F6'}; MATCH = {'F2': 'SELECTED_HEADLINE', 'F3': 'UNSUPPORTED_CLAIM', 'F5': 'INCONSISTENT', 'F6': 'INCONSISTENT'}
def items_for(batch):
    out = []
    for r in rows(os.path.join(I, batch + '_draft.jsonl')):
        for c, v in (r.get('codes') or {}).items():
            if c in SEV and v.get('status') == 'PRESENT' and not v.get('convention'):
                qa = v.get('quote') or ''; qb = v.get('quote2') or v.get('quote_b') or ''
                m = re.search(r'(?:quote_b|table|caption)[^"]*"([^"]{10,250})"', str(v.get('note') or ''))
                if m and not qb: qb = m.group(1)
                task = {'F2': 'Read the headline value in the abstract or title near this passage. Is it a single best value with the spread not given beside it?',
                        'F3': 'Find the claim near this passage. What significance, interval or null distribution supports it?',
                        'F5': 'Recompute the printed number in this passage from the other numbers the paper prints, allowing for rounding.',
                        'F6': 'Compare this passage with the paper\'s own table, caption, appendix or file for the same quantity. Can both be right?'}[c]
                out.append({'item': len(out) + 1, 'arxiv': r['arxiv'], 'code': c, 'task': task, 'passage_a': qa, 'passage_b': qb,
                            'severity': v.get('severity'), 'draft_quote': qa})
    return out
if os.path.exists(os.path.join(P, 'PAUSED')): sys.exit(0)
st = load(ST, {'next': None, 'jobs': {}, 'batches': {}})
q = load(os.path.join(I, 'queue_reachable.json'), [])
if st['next'] is None:
    done = sorted(int(m.group(1)) for f in os.listdir(I) if (m := re.match(r'batch_(\d+)\.json$', f)))
    st['next'] = (max(done) + 1) if done else 1
# 1. reap finished jobs
for pid_s, j in list(st['jobs'].items()):
    if alive(int(pid_s)): continue
    b = st['batches'].setdefault(j['batch'], {})
    if j['stage'] == 'draft':
        n = len(rows(os.path.join(I, j['batch'] + '_draft.jsonl'))); b['draft_rows'] = n; b['stage'] = 'drafted' if n else 'draft_failed'
    else:
        n = len(rows(os.path.join(P, 'work', j['batch'] + '_second.jsonl'))); b['second_rows'] = n; b['stage'] = 'second_done' if n else 'second_failed'
    log(f"DONE {j['stage']} {j['batch']} rows {n}"); del st['jobs'][pid_s]
# 2. merge batches whose second read is done
for batch, b in st['batches'].items():
    if b.get('stage') != 'second_done': continue
    items = {(x['item']): x for x in load(os.path.join(P, 'work', batch + '_items.json'), [])}
    ver = 0; rev = 0
    for s in rows(os.path.join(P, 'work', batch + '_second.jsonl')):
        it = items.get(s.get('item'))
        if not it: continue
        rec = {'arxiv': it['arxiv'], 'code': it['code'], 'severity': it.get('severity'), 'draft_quote': it['draft_quote'],
               'reader_verdict': s.get('verdict'), 'reader_confidence': s.get('confidence'), 'reader_quotes': s.get('quotes'),
               'reader_arithmetic': s.get('arithmetic'), 'batch': batch, 'date': time.strftime('%Y-%m-%d'), 'method': 'pipeline: draft agent + blind reader agent'}
        if s.get('verdict') == MATCH[it['code']] and s.get('confidence') in ('high', 'medium'):
            open(os.path.join(I, 'verified_auto.jsonl'), 'a').write(json.dumps(rec) + '\n'); ver += 1
        elif s.get('verdict') not in ('HOLDS_CONSISTENT',):
            open(os.path.join(P, 'work', 'review_queue.jsonl'), 'a').write(json.dumps(rec) + '\n'); rev += 1
    b['stage'] = 'merged'; b['verified'] = ver; b['to_review'] = rev; log(f'MERGE {batch}: verified {ver}, review {rev}, items {len(items)}')
# 3. launch work while there are free slots
def free(): return MAXJOBS - len(st['jobs'])
for batch, b in sorted(st['batches'].items()):
    if free() <= 0: break
    if b.get('stage') == 'drafted':
        its = items_for(batch); save(os.path.join(P, 'work', batch + '_items.json'), its)
        if not its: b['stage'] = 'merged'; b['verified'] = 0; log(f'MERGE {batch}: no findings to second-read'); continue
        pid = launch('second', 'second.md', batch); st['jobs'][str(pid)] = {'batch': batch, 'stage': 'second'}; b['stage'] = 'second_running'
for f in sorted(os.listdir(I)):   # orphans: a batch file with no draft that the state does not track
    m = re.match(r'(batch_\d+)\.json$', f)
    if not m or free() <= 0: continue
    batch = m.group(1)
    if batch in st['batches'] or rows(os.path.join(I, batch + '_draft.jsonl')): continue
    pid = launch('draft', 'draft.md', batch); st['jobs'][str(pid)] = {'batch': batch, 'stage': 'draft'}; st['batches'][batch] = {'stage': 'draft_running'}
while free() > 0:
    k = st['next']; lo = (k - 1) * BATCH
    if lo >= len(q): break
    batch = 'batch_%02d' % k
    if not os.path.exists(os.path.join(I, batch + '.json')): save(os.path.join(I, batch + '.json'), q[lo:lo + BATCH])
    if os.path.exists(os.path.join(I, batch + '_draft.jsonl')) and rows(os.path.join(I, batch + '_draft.jsonl')):
        st['batches'].setdefault(batch, {})['stage'] = 'drafted'; st['next'] = k + 1; continue
    pid = launch('draft', 'draft.md', batch); st['jobs'][str(pid)] = {'batch': batch, 'stage': 'draft'}
    st['batches'][batch] = {'stage': 'draft_running'}; st['next'] = k + 1
save(ST, st)
