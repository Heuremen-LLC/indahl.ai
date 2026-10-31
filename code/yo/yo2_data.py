"""yo2_data.py -- builds YO v2 data per PLAN_YO_V2.md (committed b634941 before this file). Answers are computed by code from each record.
Writes data2/train.jsonl, data2/valid.jsonl (mlx-lm completions format: prompt, completion), data2/test_items.jsonl, DATA_YO_V2.sha256.
Refuses to write anything if a TRAIN or VALID item (prompt + answer, chat template applied) exceeds 2048 tokens."""
import json, gzip, random, datetime as dt, os, glob, hashlib, collections, sys
from transformers import AutoTokenizer
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = HERE + '/data2'; UTC = dt.timezone.utc
TOK = AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B')
FIELDS = ['T1', 'T2', 'readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']; ERRS = ['readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']
END = dt.datetime(2026, 10, 31, 21, 0, tzinfo=UTC); START = END - dt.timedelta(days=180); CUT = dt.datetime(2026, 10, 2, tzinfo=UTC)
MAXLEN = 2048
def when(s):
    d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00')); return (d if d.tzinfo else d.replace(tzinfo=UTC)).astimezone(UTC)
def hm(d): return d.strftime('%Y-%m-%d %H:%M')
def g4(v): return f'{v:.4g}'
RULE_A = ('You audit IBM quantum calibration records. Flag (1) "stale": qubits whose T1 or T2 measurement date is more than 24 hours '
          'before the record\'s last-calibration stamp; (2) "zero": qubit:field pairs whose error value is exactly 0. '
          'Answer only JSON: {"stale": [qubit numbers], "zero": ["q:field", ...]}, lists sorted.')
RULE_C = ('You give a verdict on a measured value against a stated reference. Apply this rule in this order: ABOVE if the low end of the '
          'interval is above the reference; BELOW if the high end of the interval is below the reference; CONSISTENT if the whole interval '
          'lies within the reference plus or minus the margin; otherwise CANNOT_TELL. Answer with one word: ABOVE, BELOW, CONSISTENT or CANNOT_TELL.')
def render(prompt):   # evaluation prompt: the tokenizer's chat template, thinking off
    return TOK.apply_chat_template([{'role': 'user', 'content': prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
def ntok(prompt, answer):
    return len(TOK.apply_chat_template([{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': answer}], tokenize=True))
def load_records():
    recs = []
    for path in sorted(glob.glob(HERE + '/history/*.json.gz')):
        d = json.load(gzip.open(path)); S = when(d['last_update_date'])
        if not (START <= S <= END): continue
        Q = {}
        for i, qs in enumerate(d['qubits']):
            e = {p['name']: (p.get('value'), p.get('date')) for p in qs if p.get('name') in FIELDS}
            if all(f in e and e[f][0] is not None and e[f][1] for f in ('T1', 'T2')): Q[i] = e
        if len(Q) >= 8: recs.append((d['backend_name'], S, path, Q))
    return sorted(recs, key=lambda r: (r[1], r[0]))
def item_a(b, S, Q, k):
    rng = random.Random(f'A|{b}|{S.isoformat()}|{k}'); qs = sorted(rng.sample(sorted(Q), 8)); lines, stale, zero = [], [], []
    for q in qs:
        e = Q[q]; parts = []
        for f in FIELDS:
            if f not in e or e[f][0] is None: continue
            v, t = e[f]; parts.append(f'{f}={g4(v)} ({hm(when(t))})' if t else f'{f}={g4(v)}')
            if f in ('T1', 'T2') and (S - when(t)).total_seconds() > 86400 and q not in stale: stale.append(q)
            if f in ERRS and v == 0: zero.append(f'{q}:{f}')
        lines.append(f'q{q}: ' + ', '.join(parts))
    prompt = f'{RULE_A}\nBackend {b}, last-calibration stamp {hm(S)} UTC.\n' + '\n'.join(lines)
    return dict(job='A', id=f'A|{b}|{S.isoformat()}|{k}', record=f'{b}|{S.isoformat()}', prompt=prompt,
                answer=json.dumps({'stale': sorted(stale), 'zero': sorted(zero)}))
def truth(r, lo, hi, d):
    if lo > r: return 'ABOVE'
    if hi < r: return 'BELOW'
    if r - d <= lo and hi <= r + d: return 'CONSISTENT'
    return 'CANNOT_TELL'
def item_c(b, S, Q, k):
    rng = random.Random(f'C|{b}|{S.isoformat()}|{k}'); q = rng.choice(sorted(Q)); f = rng.choice(['T1', 'T2'])
    r = round(float(Q[q][f][0]), 1)
    if r <= 0: return None
    delta = rng.uniform(-0.5, 0.5); w = rng.uniform(0.02, 0.40); c = r * (1 + delta)
    lo, hi, d = round(c * (1 - w), 1), round(c * (1 + w), 1), round(0.10 * r, 1)
    prompt = (f'{RULE_C}\nBackend {b}, qubit {q}: stated {f} = {r} microseconds (record stamp {hm(S)} UTC). '
              f'Measured {f}: 95% interval [{lo}, {hi}] microseconds. Margin: {d} microseconds.')
    return dict(job='C', id=f'C|{b}|{S.isoformat()}|{k}', record=f'{b}|{S.isoformat()}', prompt=prompt, answer=truth(r, lo, hi, d), r=r, lo=lo, hi=hi, d=d)
def c_pool(recs, per_class, seed):
    pools = collections.defaultdict(list)
    for b, S, path, Q in recs:
        for k in range(12):
            it = item_c(b, S, Q, k)
            if it: pools[it['answer']].append(it)
    rng = random.Random(seed); out = []
    for cls in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL'):
        assert len(pools[cls]) >= per_class, (cls, len(pools[cls])); out += rng.sample(pools[cls], per_class)
    rng.shuffle(out); return out
if __name__ == '__main__':
    recs = load_records(); test = [r for r in recs if r[1] >= CUT]; tr = [r for r in recs if r[1] < CUT]
    nv = len(tr) // 10; va, tr = tr[-nv:], tr[:-nv]
    print('records', len(recs), '| train', len(tr), 'valid', len(va), 'test', len(test), '| backends', dict(collections.Counter(r[0] for r in recs)))
    def a_items(rs): return [item_a(b, S, Q, k) for b, S, p, Q in rs for k in range(2)]
    rng = random.Random(31)
    A_tr = rng.sample(a_items(tr), 4000); A_va = rng.sample(a_items(va), 200); A_te = rng.sample(a_items(test), 400)
    C_tr = c_pool(tr, 1000, 32); C_va = c_pool(va, 50, 33); C_te = c_pool(test, 100, 34)
    TR, VA = A_tr + C_tr, A_va + C_va; random.Random(35).shuffle(TR)
    lens = [ntok(i['prompt'], i['answer']) for i in TR + VA]
    print('tokens per TRAIN/VALID item: max', max(lens), 'median', sorted(lens)[len(lens) // 2])
    if max(lens) > MAXLEN: sys.exit(f'REFUSED: an item has {max(lens)} tokens, over {MAXLEN}')
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (('train', TR), ('valid', VA)):
        with open(f'{OUT}/{name}.jsonl', 'w') as fh:
            for i in rows: fh.write(json.dumps({'prompt': i['prompt'], 'completion': i['answer']}) + '\n')
    with open(f'{OUT}/test_items.jsonl', 'w') as fh:
        for i in A_te + C_te: fh.write(json.dumps(i) + '\n')
    with open(HERE + '/DATA_YO_V2.sha256', 'w') as fh:
        for b, S, p, Q in recs: fh.write(hashlib.sha256(open(p, 'rb').read()).hexdigest() + '  ' + os.path.relpath(p, HERE) + '\n')
        for n in ('train', 'valid', 'test_items'): fh.write(hashlib.sha256(open(f'{OUT}/{n}.jsonl', 'rb').read()).hexdigest() + f'  data2/{n}.jsonl\n')
    ea = sum(json.loads(i['answer']) == {'stale': [], 'zero': []} for i in A_te)
    print('TEST A items with nothing to flag', ea, 'of', len(A_te), '| TEST C truths', dict(collections.Counter(i['answer'] for i in C_te)))
    print('TRAIN A with stale', sum(json.loads(i['answer'])['stale'] != [] for i in A_tr), 'with zero', sum(json.loads(i['answer'])['zero'] != [] for i in A_tr))
