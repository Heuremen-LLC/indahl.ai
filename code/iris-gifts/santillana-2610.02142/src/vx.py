"""Our decoder for the VectraYX checkpoints (PLAN.md d7d8c0a), written from the architecture his model file describes. Weights read with
scout/pt_safe.py (restricted unpickler, nothing from the file runs). CPU fp32, greedy, KV cache."""
import os, sys, math
import numpy as np, torch, torch.nn.functional as F
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..')); sys.path.insert(0, H)
from pt_safe import PT
W = G + '/theirs/hf_weights'
MODELS = {'600m': W + '/ckpt600/model_step_0154000.pt', 'parent': W + '/vision-1b-checks/phase4a_v0_real_llm/llm_state_dict.pt',
          'child': W + '/vision-1b-checks/text_diag_repro_v0/text_diag_step_002202.pt',
          **{a: W + '/vision-1b-checks/f3_factorial_v0/%s/text_diag_step_002202.pt' % a for a in ('narrow_highlr', 'narrow_lowlr', 'diverse_lowlr', 'diverse_highlr_seed42', 'diverse_highlr_seed43')}}  # F1, PLAN Addendum 1
CFG1B = {'n_layers': 22, 'n_heads': 16, 'n_kv_heads': 4, 'd_model': 2048, 'd_ffn': 5504, 'rope_theta': 1e6, 'nope_every': 4, 'rms_eps': 1e-6, 'vocab_size': 32768}
def load(name):
    t = PT(MODELS[name]); o = t.obj
    cfg = o.get('config') or o.get('llm_config') if isinstance(o, dict) and ('config' in o or 'llm_config' in o) else dict(CFG1B)
    sd = t.find_state_dict(); P = {}
    for k, ref in sd.items():
        kk = k.replace('_orig_mod.', '').replace('llm.', '', 1) if k.startswith(('llm.', '_orig_mod.')) else k
        P[kk] = torch.from_numpy(np.ascontiguousarray(t.load(ref, as_float32=True)))
    return cfg, P
class Model:
    def __init__(self, cfg, P):
        self.c = cfg; self.P = P; L = cfg['n_layers']; self.hd = cfg['d_model'] // cfg['n_heads']
        need = {'tok_emb.weight', 'final_norm.weight'} | {'layers.%d.%s' % (i, s) for i in range(L) for s in ('attn_norm.weight', 'attn.wq.weight', 'attn.wk.weight', 'attn.wv.weight', 'attn.wo.weight', 'ffn_norm.weight', 'ffn.w_gate.weight', 'ffn.w_up.weight', 'ffn.w_down.weight')}
        missing = need - set(P); extra = set(P) - need - {'lm_head.weight'}
        assert not missing and not extra, (sorted(missing)[:5], sorted(extra)[:5])
        self.head = P.get('lm_head.weight', P['tok_emb.weight'])
        self.tied = 'lm_head.weight' not in P or torch.equal(P['lm_head.weight'], P['tok_emb.weight'])
        self.inv = 1.0 / (cfg['rope_theta'] ** (torch.arange(0, self.hd, 2, dtype=torch.float32) / self.hd))
        self.n_params = sum(v.numel() for k, v in P.items() if k != 'lm_head.weight' or not self.tied)
    def rms(self, x, w): return (x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.c['rms_eps'])) * w
    def rope(self, x, pos0):
        T = x.shape[-2]; f = torch.outer(torch.arange(pos0, pos0 + T, dtype=torch.float32), self.inv)
        cos, sin = f.cos().view(1, 1, T, -1), f.sin().view(1, 1, T, -1); D = x.shape[-1]
        x1, x2 = x[..., : D // 2], x[..., D // 2:]
        return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)
    @torch.inference_mode()
    def step(self, ids, cache, pos0):
        c, P = self.c, self.P; x = P['tok_emb.weight'][ids].unsqueeze(0); T = x.shape[1]; nh, nk = c['n_heads'], c['n_kv_heads']
        for i in range(c['n_layers']):
            p = 'layers.%d.' % i; h = self.rms(x, P[p + 'attn_norm.weight'])
            q = (h @ P[p + 'attn.wq.weight'].T).view(1, T, nh, self.hd).transpose(1, 2)
            k = (h @ P[p + 'attn.wk.weight'].T).view(1, T, nk, self.hd).transpose(1, 2)
            v = (h @ P[p + 'attn.wv.weight'].T).view(1, T, nk, self.hd).transpose(1, 2)
            if i % c['nope_every'] != c['nope_every'] - 1: q, k = self.rope(q, pos0), self.rope(k, pos0)
            if i in cache: k, v = torch.cat([cache[i][0], k], 2), torch.cat([cache[i][1], v], 2)
            cache[i] = (k, v); r = nh // nk
            o = F.scaled_dot_product_attention(q, k.repeat_interleave(r, 1), v.repeat_interleave(r, 1), is_causal=(T > 1))
            x = x + o.transpose(1, 2).contiguous().view(1, T, -1) @ P[p + 'attn.wo.weight'].T
            h = self.rms(x, P[p + 'ffn_norm.weight'])
            x = x + (F.silu(h @ P[p + 'ffn.w_gate.weight'].T) * (h @ P[p + 'ffn.w_up.weight'].T)) @ P[p + 'ffn.w_down.weight'].T
        return (self.rms(x[:, -1], P['final_norm.weight']) @ self.head.T)[0]
    def greedy(self, prompt_ids, max_new=256, stops=(7, 3)):
        cache = {}; logits = self.step(torch.tensor(prompt_ids), cache, 0); pfirst = torch.softmax(logits.double(), -1)
        out = []; pos = len(prompt_ids)
        while len(out) < max_new:
            nxt = int(torch.argmax(logits)); out.append(nxt)
            if nxt in stops: return out, pfirst, 'stop'
            logits = self.step(torch.tensor([nxt]), cache, pos); pos += 1
        return out, pfirst, 'length'
