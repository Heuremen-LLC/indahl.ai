#!/usr/bin/env python3
"""Live arm L of PLAN.md (d7d8c0a): his verbatim protocol on the 269 corpus rows. usage: run_verbatim.py MODEL REP [--rows N]
MODEL in 600m parent child. Writes runs/MODEL_rREP.jsonl, one row per corpus row, and refuses to overwrite."""
import os, sys, json, re, time, hashlib
import torch
from tokenizers import Tokenizer
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import vx
G = vx.G; name, rep = sys.argv[1], int(sys.argv[2]); N = int(sys.argv[sys.argv.index('--rows') + 1]) if '--rows' in sys.argv else None
torch.set_num_threads(6); torch.manual_seed(0)
TK = G + '/theirs/hf/models/jsantillana/vectrayx-600m-tokenizer/tokenizer.json'; tok = Tokenizer.from_file(TK)
assert hashlib.sha256(open(TK, 'rb').read()).hexdigest().startswith('462efac1b181')
for s, i in (('<|system|>', 4), ('<|user|>', 5), ('<|assistant|>', 6), ('<|end|>', 7), ('<|tool_call|>', 8), ('<|/tool_call|>', 9)):
    assert tok.encode(s, add_special_tokens=False).ids == [i], (s, tok.encode(s, add_special_tokens=False).ids)
C = G + '/theirs/hf/datasets/jsantillana/vectrayx-bench/tool_sft_corpus/tool_sft_mini_v1.jsonl'
assert hashlib.sha256(open(C, 'rb').read()).hexdigest().startswith('c0eb6e903c8a')
PAT = re.compile(r"^<\|system\|>(.*?)<\|end\|><\|user\|>(.*?)<\|end\|><\|assistant\|>(.*)$", re.S); CALL = re.compile(r'<\|tool_call\|>\{"name":\s*"([a-z_]+)"')
DECL = {"nvd_get_cve", "nvd_search", "cisa_kev_check", "otx_check_ioc", "bash_exec"}; seen = set(); rows = []
for l in open(C, encoding='utf-8'):
    r = json.loads(l); s, u, comp = PAT.match(r['text']).groups(); m = CALL.search(comp); tool = m.group(1) if m else None
    if u in seen: continue
    seen.add(u)
    if tool is None or tool in DECL: rows.append({'text': r['text'], 'comp': comp, 'tool': tool})
assert len(rows) == 269 and sum(r['tool'] is not None for r in rows) == 247
out_p = '%s/runs/%s_r%d%s.jsonl' % (os.path.join(H, '..'), name, rep, '_smoke' if N else '')
if os.path.exists(out_p): sys.exit('REFUSED: %s exists' % out_p)
cfg, P = vx.load(name); M = vx.Model(cfg, P)
print('%s loaded: %.1fM parameters (tied %s), layers %d, d_model %d' % (name, M.n_params / 1e6, M.tied, cfg['n_layers'], cfg['d_model']), flush=True)
fo = open(out_p, 'w'); t0 = time.time()
for i, r in enumerate(rows[:N] if N else rows):
    prompt = r['text'][: r['text'].index('<|assistant|>') + len('<|assistant|>')]; ids = tok.encode(prompt, add_special_tokens=False).ids
    t1 = time.time(); out, pf, fin = M.greedy(ids)
    fo.write(json.dumps({'row': i, 'n_prompt': len(ids), 'ids': out, 'text': tok.decode(out, skip_special_tokens=False), 'finish': fin,
                         'p_tool_call': float(pf[8]), 'first_top1': int(torch.argmax(pf)), 'gold': r['comp'], 'tool': r['tool'], 's': time.time() - t1}) + '\n'); fo.flush()
    if (i + 1) % 25 == 0: print('%s r%d: %d rows, %d s' % (name, rep, i + 1, time.time() - t0), flush=True)
print('DONE %s r%d in %d s' % (name, rep, time.time() - t0), flush=True)
