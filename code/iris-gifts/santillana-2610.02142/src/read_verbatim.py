#!/usr/bin/env python3
"""Readings L1-L5 of PLAN.md (d7d8c0a) for the verbatim arm. Written before any full-run output was read (31 Oct 2026).
  --sample MODEL REP : 10 completions (seed 7) with the scorer's verdict, for the read in full. No rates.
  --rates            : L1-L5. Refuses a model whose note runs/READ_<MODEL>_r<REP>.md is missing for a repeat on disk."""
import os, sys, json, math, random, statistics
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..')); R = G + '/runs'
PRINTED = {'600m': (0.926, '[0.892, 0.955]', 0.235), 'parent': (0.100, '[0.067, 0.138]', None), 'child': (0.959, '[0.933, 0.981]', 0.988)}
PRINTED.update({'narrow_highlr': (1.000, '(no interval printed)', 1.000), 'narrow_lowlr': (1.000, '(no interval printed)', 1.000), 'diverse_lowlr': (0.9963, '[0.989, 1.000]', 0.9960),
                'diverse_highlr_seed42': (1.000, '(no interval printed)', 1.000), 'diverse_highlr_seed43': (0.9963, '[0.989, 1.000]', 1.000)})   # F1, his section 6.9 factorial (F3)
dec = json.JSONDecoder()
def call_of(text):
    """(well_formed, call_text) per the plan's scorer: <|tool_call|> then a JSON object with str name and dict args, closed by <|/tool_call|> or the end."""
    if '<|tool_call|>' not in text: return False, None
    body = text.split('<|tool_call|>', 1)[1]
    inner = body.split('<|/tool_call|>', 1)[0] if '<|/tool_call|>' in body else body.replace('<|end|>', '').replace('</s>', '')
    try: obj, end = dec.raw_decode(inner.strip())
    except ValueError: return False, inner
    ok = isinstance(obj, dict) and isinstance(obj.get('name'), str) and isinstance(obj.get('args'), dict)
    return ok, inner.strip()
def strip_end(t): return t[:-len('<|end|>')] if t.endswith('<|end|>') else (t[:-4] if t.endswith('</s>') else t)
_ROWS = None
def _rows():   # the 269 rows by his rule (as in run_verbatim.py), for rebuilding completions from the released token ids
    global _ROWS
    if _ROWS is None:
        import re
        PAT = re.compile(r"^<\|system\|>(.*?)<\|end\|><\|user\|>(.*?)<\|end\|><\|assistant\|>(.*)$", re.S); CALL = re.compile(r'<\|tool_call\|>\{"name":\s*"([a-z_]+)"')
        DECL = {"nvd_get_cve", "nvd_search", "cisa_kev_check", "otx_check_ioc", "bash_exec"}; seen = set(); _ROWS = []
        for l in open(G + '/theirs/hf/datasets/jsantillana/vectrayx-bench/tool_sft_corpus/tool_sft_mini_v1.jsonl', encoding='utf-8'):
            r = json.loads(l); s, u, comp = PAT.match(r['text']).groups(); mm = CALL.search(comp); tool = mm.group(1) if mm else None
            if u in seen: continue
            seen.add(u)
            if tool is None or tool in DECL: _ROWS.append({'comp': comp, 'tool': tool})
        assert len(_ROWS) == 269
    return _ROWS
def load(m, rep):
    p = '%s/%s_r%d.ids.jsonl' % (R, m, rep)
    if not os.path.exists(p): return None
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(G + '/theirs/hf/models/jsantillana/vectrayx-600m-tokenizer/tokenizer.json'); rows = _rows(); D = []
    for l in open(p):
        d = json.loads(l); d.update(text=tok.decode(d['ids'], skip_special_tokens=False), gold=rows[d['row']]['comp'], tool=rows[d['row']]['tool']); D.append(d)
    return D if len(D) == 269 else None
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - h) / d, (c + h) / d
if sys.argv[1] == '--sample':
    m, rep = sys.argv[2], int(sys.argv[3]); D = load(m, rep); idx = list(range(269)); random.Random(7).shuffle(idx)
    for i in idx[:10]:
        d = D[i]; wf, call = call_of(d['text']); gwf, gcall = call_of(d['gold'])
        print('== row %d tool %s | well-formed %s | call equals gold call %s | completion equals gold %s | finish %s, %d tokens\n  ours: %r\n  gold: %r\n' % (
            i, d['tool'], wf, wf and call == gcall, strip_end(d['text']) == strip_end(d['gold']), d['finish'], len(d['ids']), d['text'][:400], d['gold'][:400]))
    sys.exit()
for m in ('600m', 'parent', 'child', 'narrow_highlr', 'narrow_lowlr', 'diverse_lowlr', 'diverse_highlr_seed42', 'diverse_highlr_seed43'):
    reps = {r: load(m, r) for r in (1, 2)}; reps = {r: d for r, d in reps.items() if d}
    if not reps: continue
    for r in reps:
        if not os.path.exists('%s/READ_%s_r%d.md' % (R, m, r)): sys.exit('REFUSED: runs/READ_%s_r%d.md is missing' % (m, r))
    pw, pci, pex = PRINTED[m]; print('\n######## %s (printed: well-formed %.3f %s%s)' % (m, pw, pci, (', exact among well-formed %.3f' % pex) if pex else ''))
    for r, D in sorted(reps.items()):
        call_rows = [d for d in D if d['tool'] is not None]; none_rows = [d for d in D if d['tool'] is None]
        wf = [call_of(d['text']) for d in D]; gw = [call_of(d['gold']) for d in D]
        k_all = sum(w for w, _ in wf); k_call = sum(wf[i][0] for i, d in enumerate(D) if d['tool'] is not None)
        lo, hi = wilson(k_all, 269); lo2, hi2 = wilson(k_call, len(call_rows))
        print('  r%d L1 well-formed: %d of 269 = %.3f [%.3f, %.3f] | on the %d call rows %d = %.3f [%.3f, %.3f] | on the %d no-call rows: %d emit a call, %d suppress' % (
            r, k_all, k_all / 269, lo, hi, len(call_rows), k_call, k_call / len(call_rows), lo2, hi2, len(none_rows), sum(wf[i][0] or '<|tool_call|>' in d['text'] for i, d in enumerate(D) if d['tool'] is None), sum('<|tool_call|>' not in d['text'] for d in none_rows)))
        ex_call = sum(1 for i, d in enumerate(D) if wf[i][0] and gw[i][0] and wf[i][1] == gw[i][1]); ex_full = sum(1 for i, d in enumerate(D) if wf[i][0] and strip_end(d['text']) == strip_end(d['gold']))
        print('  r%d L2 exact among well-formed: call text equal to the training call %d of %d = %.3f | whole completion equal %d | not equal (generalized or other) %d' % (
            r, ex_call, k_all, ex_call / max(1, k_all), ex_full, k_all - ex_call))
        fin = {}; [fin.__setitem__(d['finish'], fin.get(d['finish'], 0) + 1) for d in D]
        opened = sum('<|tool_call|>' in d['text'] for d in D)
        print('  r%d L5 opened a <|tool_call|> %d | parsed with name and args %d | finish %s | completion tokens median %d, max %d' % (
            r, opened, k_all, fin, statistics.median(len(d['ids']) for d in D), max(len(d['ids']) for d in D)))
        pc = sorted(d['p_tool_call'] for d in call_rows); pn = sorted(d['p_tool_call'] for d in none_rows)
        print('  r%d L4 P(<|tool_call|>) first token: call rows median %.3g [min %.3g, max %.3g] | no-call rows median %.3g [min %.3g, max %.3g] | first token is <|tool_call|> on %d of %d call rows' % (
            r, statistics.median(pc), pc[0], pc[-1], statistics.median(pn), pn[0], pn[-1], sum(d['first_top1'] == 8 for d in call_rows), len(call_rows)))
        ps = sum(1 for i, d in enumerate(D) if (d['tool'] is not None and wf[i][0]) or (d['tool'] is None and '<|tool_call|>' not in d['text']))
        wc = [i for i, d in enumerate(D) if d['tool'] is not None and wf[i][0]]; ec = sum(1 for i in wc if gw[i][0] and wf[i][1] == gw[i][1]); lo3, hi3 = wilson(ps, 269)
        print('  r%d L1b (Addendum 2, defined after the data) pass: call rows with a well-formed call plus no-call rows that suppress = %d of 269 = %.3f [%.3f, %.3f] | exact copies among well-formed calls on call rows %d of %d = %.3f' % (r, ps, ps / 269, lo3, hi3, ec, len(wc), ec / max(1, len(wc))))
    if len(reps) == 2:
        A, B = reps[1], reps[2]; diff = sum(1 for a, b in zip(A, B) if a['ids'] != b['ids']); dp = max(abs(a['p_tool_call'] - b['p_tool_call']) for a, b in zip(A, B))
        print('  L3 repeat floor: rows whose completion token ids differ between r1 and r2: %d of 269 | largest first-token probability difference %.3g' % (diff, dp))
