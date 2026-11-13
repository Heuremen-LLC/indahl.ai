"""yo_data.py -- builds YO v1 data per PLAN_YO_V1.md. Job A answers are computed from the IBM record; Job B labels are the logged lessons."""
import json, gzip, random, datetime as dt, os, collections
from transformers import AutoTokenizer
HERE = os.path.dirname(os.path.abspath(__file__))
TOK = AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B')
FIELDS = ['T1', 'T2', 'readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']
ERRS = ['readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']
CUT_A = dt.datetime(2026, 10, 21, tzinfo=dt.timezone.utc)
CUT_B = dt.datetime(2026, 10, 21, tzinfo=dt.timezone(dt.timedelta(hours=-4)))
def when(s):
    s = str(s).replace('Z', '+00:00'); d = dt.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
def render(prompt):   # the prompt exactly as the model sees it, thinking off; used for training AND every evaluation
    return TOK.apply_chat_template([{'role': 'user', 'content': prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
RULE_A = ('You audit IBM quantum calibration records. Flag (1) "stale": qubits whose T1 or T2 measurement date is more than 24 hours '
          'before the record\'s last-calibration stamp; (2) "zero": qubit:field pairs whose error value is exactly 0. '
          'Answer only JSON: {"stale": [qubit numbers], "zero": ["q:field", ...]}, lists sorted.')
FAM = {'I': 'the baseline built after the measurement it judges', 'II': 'zeroing a gap that was itself the reading',
       'III': 'the fold that erases the discarded half (magnitude, sign, sum vs product)', 'IV': 'the forced verdict / four outcomes collapsed to two',
       'V': 'the instrument wrong about itself (counts from memory, own checker wrong)', 'VI': 'the claim that was never checked', 'none': 'none of these families'}
RULE_B = 'Name the fault family of this logged catch. Families: ' + '; '.join(f'{k} = {v}' for k, v in FAM.items()) + '. Answer with the family label only.'
def job_a():
    recs = json.load(open(f'{HERE}/records.json')); out = {'train': [], 'test': []}
    for b, stamp, path in sorted(recs, key=lambda r: when(r[1])):
        if b.startswith('fake'): continue
        d = json.load(gzip.open(path) if path.endswith('.gz') else open(path)); S = when(d['last_update_date'])
        Q = {}
        for i, qs in enumerate(d['qubits']):
            e = {p['name']: (p.get('value'), p.get('date')) for p in qs if p.get('name') in FIELDS}
            if all(f in e for f in ('T1', 'T2')): Q[i] = e
        if len(Q) < 8: continue
        split = 'test' if S >= CUT_A else 'train'
        for k in range(30):
            rng = random.Random(f'{b}|{stamp}|{k}'); qs = sorted(rng.sample(sorted(Q), 8))
            lines, stale, zero = [], [], []
            for q in qs:
                e = Q[q]; parts = []
                for f in FIELDS:
                    if f not in e: continue
                    v, t = e[f]; parts.append(f'{f}={v} ({str(when(t))[:16]})')
                    if f in ('T1', 'T2') and t and (S - when(t)).total_seconds() > 86400 and q not in stale: stale.append(q)
                    if f in ERRS and v == 0: zero.append(f'{q}:{f}')
                lines.append(f'q{q}: ' + ', '.join(parts))
            prompt = f'{RULE_A}\nBackend {b}, last-calibration stamp {str(S)[:16]} UTC.\n' + '\n'.join(lines)
            out[split].append({'job': 'A', 'id': f'{b}|{stamp}|{k}', 'when': str(S), 'prompt': prompt,
                               'answer': json.dumps({'stale': sorted(stale), 'zero': sorted(zero)})})
    return out
def job_b():
    out = {'train': [], 'test': []}
    for l in open(os.path.expanduser('~/bones-forge/watch/tp_score.jsonl')):
        r = json.loads(l)
        if not r.get('what') or r.get('lesson') not in FAM: continue
        split = 'test' if when(r['at'].replace('-0400', '-04:00')) >= CUT_B else 'train'
        out[split].append({'job': 'B', 'id': r['at'], 'when': r['at'], 'prompt': f"{RULE_B}\nCatch: {r['what']}", 'answer': r['lesson']})
    return out
if __name__ == '__main__':
    A, B = job_a(), job_b(); os.makedirs(f'{HERE}/data', exist_ok=True)
    tr = A['train'] + B['train']; tr.sort(key=lambda r: str(when(r['when'].replace('-0400', '-04:00'))))
    n = len(tr); va = tr[int(0.9 * n):]; tr = tr[:int(0.9 * n)]
    for name, rows in (('train', tr), ('valid', va)):
        with open(f'{HERE}/data/{name}.jsonl', 'w') as f:
            for r in rows: f.write(json.dumps({'text': render(r['prompt']) + r['answer'] + '<|im_end|>'}) + '\n')
    with open(f'{HERE}/data/test_items.jsonl', 'w') as f:
        for r in A['test'] + B['test']: f.write(json.dumps(r) + '\n')
    print('A train', len(A['train']), 'A test', len(A['test']), '| B train', len(B['train']), 'B test', len(B['test']), '| train', len(tr), 'valid', len(va))
    print('A test stale-nonempty', sum(json.loads(r['answer'])['stale'] != [] for r in A['test']), 'zero-nonempty', sum(json.loads(r['answer'])['zero'] != [] for r in A['test']))
    print('B test classes', collections.Counter(r['answer'] for r in B['test']))
