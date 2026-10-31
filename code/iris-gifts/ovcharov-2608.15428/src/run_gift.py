#!/usr/bin/env python3
"""run_gift.py: Ovcharov 2608.15428 gift runs (PLAN.md, committed before any run). Our code. His prompt strings and parser patterns are read
from his code/small_models.py with ast at run time; his files are read as data only.
usage: run_gift.py --url http://HOST:PORT --machine armature|mac --model llama3.1:8b --arm B|F --rep 1|2
One request at a time. Every reply saved raw with its parsed letter, token counts and done reason. A call that fails after retries is saved
as an error, its own outcome, never folded into the no-letter count. Restartable: ids with a reply already saved are skipped."""
import json, re, os, sys, time, argparse, urllib.request, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.dirname(H); T = G + '/theirs'
import ast as _ast
def _consts(path):   # his prompt strings and parser patterns, read from his file as text with ast (nothing of his is run)
    out = {}
    for n in _ast.walk(_ast.parse(open(path, encoding='utf-8').read())):
        if isinstance(n, _ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], _ast.Name):
            v = n.value
            if isinstance(v, _ast.Constant) and isinstance(v.value, str): out[n.targets[0].id] = v.value
            elif isinstance(v, _ast.Call) and getattr(v.func, 'attr', '') == 'compile' and v.args and isinstance(v.args[0], _ast.Constant): out[n.targets[0].id] = v.args[0].value
    return out
_C = _consts(T + '/code/small_models.py'); _A = _consts(T + '/code/scenario_a.py'); assert _C['BLIND'] == _A['BLIND'] and _C['MARK'] == _A['MARK']
BLIND, FULL = _C['BLIND'], _C['FULL']
MARK, LEAD, ANY = re.compile(_C['MARK']), re.compile(_C['LEAD']), re.compile(_C['ANY'])
def parse(t):   # his parser, unchanged
    if not t: return None
    t = t.strip()
    for rx in (MARK, LEAD):
        m = rx.search(t)
        if m: return "ABCD".index(m.group(1))
    h = ANY.findall(t.upper())
    return "ABCD".index(h[-1]) if h else None
def fmt(o): return "\n".join("%s) %s" % ("ABCD"[i], x) for i, x in enumerate(o))
THEIR = {'llama3.1:8b': 'llama-3.1-8b', 'ministral-3:8b': 'ministral-8b'}
a = argparse.ArgumentParser(); a.add_argument('--url'); a.add_argument('--machine'); a.add_argument('--model'); a.add_argument('--arm'); a.add_argument('--rep', type=int)
A = a.parse_args(); assert A.arm in ('B', 'F') and A.rep in (1, 2) and A.model in THEIR and A.machine in ('armature', 'mac')
def get(p):
    return json.loads(urllib.request.urlopen(A.url + p, timeout=60).read())
def post(p, body, timeout):
    r = urllib.request.Request(A.url + p, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())
if A.arm == 'B':
    items = [json.loads(l) for l in open(T + '/data/ua_judge_exam_gated.jsonl', encoding='utf-8')]; NP = 4096
    jobs = [(r['id'], 'accepted', BLIND.format(opts=fmt(r['options'])), r['answer_index']) for r in items]
else:
    bank = {}
    for l in open(T + '/data/ua_judge_exam_full.jsonl', encoding='utf-8'):
        r = json.loads(l); bank[r['id']] = r
    sm = [json.loads(l) for l in open(T + '/predictions/small_models.jsonl', encoding='utf-8')]
    sm = [r for r in sm if r['model'] == THEIR[A.model] and r['mode'] == 'full']; NP = 2048
    assert len(sm) == 600, len(sm)
    jobs = [(r['id'], r['grp'], FULL.format(q=bank[r['id']]['question'], opts=fmt(bank[r['id']]['options'])), bank[r['id']]['answer_index']) for r in sm]
    assert all(bank[r['id']]['answer_index'] == r['gold'] for r in sm), 'gold differs between his bank and his predictions'
OPTS = {'temperature': 0, 'seed': 1, 'repeat_penalty': 1.0, 'num_ctx': 8192, 'num_predict': NP}
out_dir = os.environ.get('GIFT_OUT') or G + '/runs/' + A.machine; os.makedirs(out_dir, exist_ok=True)   # GIFT_OUT: smoke tests go to scratch
if os.environ.get('GIFT_LIMIT'): jobs = jobs[:int(os.environ['GIFT_LIMIT'])]
stem = '%s/%s_%s_r%d' % (out_dir, A.model.replace(':', '-'), A.arm, A.rep); OUT = stem + '.jsonl'
tags = {m['name']: m for m in get('/api/tags')['models']}; assert A.model in tags, A.model + ' not on ' + A.url
show = post('/api/show', {'model': A.model}, 60)
meta = {'started': D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'machine': A.machine, 'url': A.url, 'server_version': get('/api/version').get('version'),
        'model': A.model, 'digest': tags[A.model]['digest'], 'details': show.get('details'), 'template_sha_prefix': __import__('hashlib').sha256((show.get('template') or '').encode()).hexdigest()[:16],
        'arm': A.arm, 'rep': A.rep, 'options': OPTS, 'items': len(jobs), 'runner_sha_prefix': __import__('hashlib').sha256(open(__file__, 'rb').read()).hexdigest()[:16]}
open(stem + '.meta.json', 'a').write(json.dumps(meta, ensure_ascii=False) + '\n')
done = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding='utf-8'):
        d = json.loads(l)
        if d.get('err') is None: done.add(d['id'])
todo = [j for j in jobs if j[0] not in done]
print('%s %s arm %s r%d: %d items, %d saved, %d to run, server %s, digest %s' % (A.machine, A.model, A.arm, A.rep, len(jobs), len(done), len(todo), meta['server_version'], meta['digest'][:12]), flush=True)
fh = open(OUT, 'a', encoding='utf-8'); t0 = time.time(); n = 0
for iid, grp, text, gold in todo:
    rec = {'id': iid, 'grp': grp, 'gold': gold, 'err': None}
    for att in range(3):
        try:
            o = post('/api/chat', {'model': A.model, 'messages': [{'role': 'user', 'content': text}], 'stream': False, 'keep_alive': '30m', 'options': OPTS}, 1800)
            raw = o.get('message', {}).get('content', '')
            rec.update(raw=raw, pred=parse(raw), eval_count=o.get('eval_count'), prompt_eval_count=o.get('prompt_eval_count'), done_reason=o.get('done_reason'), ns=o.get('total_duration'), attempts=att + 1, err=None)
            break
        except Exception as e:
            rec.update(err='%s: %s' % (type(e).__name__, str(e)[:160]), attempts=att + 1); time.sleep(5 * (att + 1))
    rec['t'] = D.datetime.now(D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    fh.write(json.dumps(rec, ensure_ascii=False) + '\n'); fh.flush(); n += 1
    if n % 250 == 0: print('   %d of %d, %.0f s' % (n, len(todo), time.time() - t0), flush=True)   # progress only, no rates before the read in full
print('DONE %s %s arm %s r%d in %.0f s' % (A.machine, A.model, A.arm, A.rep, time.time() - t0), flush=True)
