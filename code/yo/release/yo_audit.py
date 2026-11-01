"""yo_audit.py -- audit an IBM Quantum calibration record with YO, beside the exact answer computed by code.

  python yo_audit.py record.json --model indahl/YO          (Apple silicon, mlx-lm)
  python yo_audit.py record.json --fused indahl/YO          (anywhere, transformers)
  python yo_audit.py record.json --adapter PATH            (the adapter on top of Qwen/Qwen3-1.7B)

record.json is a backend's calibration record in Qiskit's BackendProperties format (backend.properties().to_dict(), saved with
json.dump(..., default=str)); .json.gz also works. Every qubit with a T1 and a T2 value and date is audited, eight per prompt, as YO was
trained. YO flags (1) stale: qubits whose T1 or T2 was measured more than 24 hours before the record's last_update_date, and (2) zero: error
values of exactly 0. The code computes the same two lists exactly; both are printed, with every difference.

Apple silicon: pip install mlx-lm. Elsewhere: pip install transformers torch. Both read the merged model from huggingface.co/indahl/YO."""
import json, gzip, sys, argparse, datetime as dt
UTC = dt.timezone.utc
FIELDS = ['T1', 'T2', 'readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']; ERRS = ['readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1']
RULE_A = ('You audit IBM quantum calibration records. Flag (1) "stale": qubits whose T1 or T2 measurement date is more than 24 hours '
          'before the record\'s last-calibration stamp; (2) "zero": qubit:field pairs whose error value is exactly 0. '
          'Answer only JSON: {"stale": [qubit numbers], "zero": ["q:field", ...]}, lists sorted.')
def when(s):
    d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00')); return (d if d.tzinfo else d.replace(tzinfo=UTC)).astimezone(UTC)
def hm(d): return d.strftime('%Y-%m-%d %H:%M')
def g4(v): return f'{v:.4g}'
def load_record(path):
    d = json.load(gzip.open(path) if path.endswith('.gz') else open(path)); S = when(d['last_update_date']); Q = {}
    for i, qs in enumerate(d['qubits']):
        e = {p['name']: (p.get('value'), p.get('date')) for p in qs if p.get('name') in FIELDS}
        if all(f in e and e[f][0] is not None and e[f][1] for f in ('T1', 'T2')): Q[i] = e
    return d.get('backend_name', 'backend'), S, Q
def prompt_and_answer(b, S, Q, qs):   # the training format, unchanged
    lines, stale, zero = [], [], []
    for q in sorted(qs):
        e = Q[q]; parts = []
        for f in FIELDS:
            if f not in e or e[f][0] is None: continue
            v, t = e[f]; parts.append(f'{f}={g4(v)} ({hm(when(t))})' if t else f'{f}={g4(v)}')
            if f in ('T1', 'T2') and (S - when(t)).total_seconds() > 86400 and q not in stale: stale.append(q)
            if f in ERRS and v == 0: zero.append(f'{q}:{f}')
        lines.append(f'q{q}: ' + ', '.join(parts))
    return f'{RULE_A}\nBackend {b}, last-calibration stamp {hm(S)} UTC.\n' + '\n'.join(lines), {'stale': sorted(stale), 'zero': sorted(zero)}
def groups(qs):   # eight per prompt; a short last group takes the last eight qubits so every prompt holds eight, as in training
    qs = sorted(qs); out = [qs[i:i + 8] for i in range(0, len(qs), 8)]
    if len(out) > 1 and len(out[-1]) < 8: out[-1] = qs[-8:]
    return out
def parse(out):
    try: p = json.loads(out[out.index('{'):out.rindex('}') + 1]); return set(int(x) for x in p.get('stale', [])), set(str(x) for x in p.get('zero', []))
    except Exception: return None
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0]); ap.add_argument('record'); ap.add_argument('--adapter'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B')
    ap.add_argument('--fused'); a = ap.parse_args()
    b, S, Q = load_record(a.record)
    if len(Q) < 8: sys.exit(f'{b}: fewer than 8 qubits with T1 and T2 values and dates, nothing to audit')
    if a.fused:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.fused); model = AutoModelForCausalLM.from_pretrained(a.fused)
        def ask(p):
            t = tok.apply_chat_template([{'role': 'user', 'content': p}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
            ids = tok(t, return_tensors='pt'); o = model.generate(**ids, max_new_tokens=200, do_sample=False)
            return tok.decode(o[0][ids['input_ids'].shape[1]:], skip_special_tokens=True)
    else:
        if not a.adapter and a.model == 'Qwen/Qwen3-1.7B': sys.exit('pass --model indahl/YO (the merged YO), or --adapter with the base model, or --fused for transformers')
        from mlx_lm import load, generate
        model, tok = load(a.model, adapter_path=a.adapter)
        def ask(p): return generate(model, tok, prompt=tok.apply_chat_template([{'role': 'user', 'content': p}], tokenize=False, add_generation_prompt=True, enable_thinking=False), max_tokens=200, verbose=False)
    ys, yz, cs, cz, unread = set(), set(), set(), set(), 0
    for g in groups(Q):
        p, ans = prompt_and_answer(b, S, Q, g); r = parse(ask(p))
        cs |= set(ans['stale']); cz |= set(ans['zero'])
        if r is None: unread += 1; continue
        ys |= r[0] & set(g); yz |= r[1]
    print(f'{b}, record stamp {hm(S)} UTC, {len(Q)} qubits audited in {len(groups(Q))} prompts' + (f', {unread} replies not readable as JSON' if unread else ''))
    print('stale  YO:', sorted(ys)); print('stale  code:', sorted(cs)); print('zero   YO:', sorted(yz)); print('zero   code:', sorted(cz))
    for name, y, c in (('stale', ys, cs), ('zero', yz, cz)):
        if y - c: print(f'{name}: YO flagged, code did not:', sorted(y - c))
        if c - y: print(f'{name}: code flagged, YO did not:', sorted(c - y))
    print('YO and the code agree on every flag.' if (ys == cs and yz == cz and not unread) else 'The code\'s lists are exact. Where YO differs, the code is right.')
