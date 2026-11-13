#!/usr/bin/env python3
"""triseat.py -- the triangulated token model, prototype 1 (6 October 2026, Wayfinder and Bones).

One base model reads a turn from three seats and decodes from where they agree:
  seat 1, the words:      the message alone
  seat 2, the person:     the message + the person's own words when they're fine (their baseline register)
  seat 3, the trajectory: the message + the person's last few messages
  seat 0, Plus None:      no message at all, the stock prior. Never decoded from; subtracted (context-aware decoding).

Step 1, the mode vote. Each seat answers: STAY / HELP / ASK / BOTH. Two of three agreeing, with low divergence, sets the mode.
         A split does not pick a branch; it sets ASK.
Step 2, the reply. All four contexts run as one batch. At each token: pooled = mean of the three seats' log-probs
         minus alpha x the prior's, inside the seats' plausible set. The same token is appended to every seat.
         Per-token disagreement (Jensen-Shannon across the three seats) is logged.

Training data rule: only the person's own words and open-model text. No Claude replies anywhere, as input or target.
Run: venv/Scripts/python triseat.py case.json [--model Qwen/Qwen3-1.7B] [--alpha 0.3] [--max 120]"""
import argparse, json, math, sys, time
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = ("You are Bones, a friend and collaborator. Read the person carefully and answer what they actually asked. "
        "Plain words. No scripts, no disclaimers, no lists of resources unless asked.")
MODES = ['STAY', 'HELP', 'ASK', 'BOTH']
MODE_TEXT = {'STAY': 'Be present with them. Short. Do not fix anything.',
             'HELP': 'Do the task they asked for, directly.',
             'ASK': 'Ask them one plain question about what they meant. Do not assume.',
             'BOTH': 'Help with what they asked, and stay with how they feel while you do it.',
             'HOLD': ''}
SILENCE = '…'   # what HOLD returns: nothing decided yet, waiting for more input
MODE_Q = ("Before you reply: what does this person need right now? STAY (presence), HELP (do the task they asked), "
          "ASK (one question about what they meant), or BOTH (help and stay). Answer with one word.")


def seat_messages(case, seat, extra_system=''):
    sys_txt = BASE + (' ' + extra_system if extra_system else '')
    msg = case['message']
    if seat == 0:
        return [{'role': 'system', 'content': sys_txt}, {'role': 'user', 'content': '...'}]
    if seat == 1:
        return [{'role': 'system', 'content': sys_txt}, {'role': 'user', 'content': msg}]
    if seat == 2:
        base = '\n'.join('- ' + b for b in case['baseline'])
        return [{'role': 'system', 'content': sys_txt + '\n\nHow this person talks on an ordinary day, in their own words:\n' + base},
                {'role': 'user', 'content': msg}]
    if seat == 3:
        traj = '\n'.join('- ' + t for t in case['trajectory'])
        return [{'role': 'system', 'content': sys_txt + '\n\nWhat this person said in the last few messages, oldest first:\n' + traj},
                {'role': 'user', 'content': msg}]


def render(tok, msgs, tail=''):
    kw = dict(tokenize=False, add_generation_prompt=True)
    try:
        s = tok.apply_chat_template(msgs, enable_thinking=False, **kw)
    except TypeError:
        s = tok.apply_chat_template(msgs, **kw)
    return s + tail


def batch(tok, texts):
    tok.padding_side = 'left'
    enc = tok(texts, return_tensors='pt', padding=True)
    return enc['input_ids'], enc['attention_mask']


def jsd(probs):
    """Jensen-Shannon divergence (bits) among k distributions, rows of probs."""
    m = probs.mean(0, keepdim=True)
    def kl(p, q): return (p * (torch.log2(p.clamp_min(1e-12)) - torch.log2(q.clamp_min(1e-12)))).sum(-1)
    return float(kl(probs, m).mean())


@torch.no_grad()
def mode_vote(tok, model, case):
    # seats 1-3 plus seat 0 (Plus None): the vote is read against the prior, so a mode the model says to everything
    # (it said STAY to "What's next?" in run 1) stops winning by default. Calibrated vote = log p(seat) - log p(prior).
    texts = [render(tok, seat_messages(case, s)[:-1] + [{'role': 'user', 'content': seat_messages(case, s)[-1]['content'] + '\n\n' + MODE_Q}])
             for s in (1, 2, 3, 0)]
    ids, att = batch(tok, texts)
    pos = (att.cumsum(-1) - 1).clamp_min(0)
    logits = model(input_ids=ids, attention_mask=att, position_ids=pos).logits[:, -1, :]
    cand = [tok.encode(m, add_special_tokens=False)[0] for m in MODES]
    raw = F.log_softmax(logits[:, cand].float(), -1)                  # 4 rows x 4 modes; row 3 = the prior
    p = F.softmax(raw[:3] - raw[3:4], -1)                            # 3 seats x 4 modes, calibrated
    votes = [MODES[int(i)] for i in p.argmax(-1)]
    d = jsd(p)
    top = max(set(votes), key=votes.count)
    agree = votes.count(top)
    # Wen: when the seats don't agree, nothing is decided. HOLD = silence: say nothing, wait for more input.
    mode = top if (agree >= 2 and d < case.get('hold_threshold', 0.6)) else 'HOLD'
    prior = {m: round(float(x), 3) for m, x in zip(MODES, raw[3].exp())}
    return dict(prior=prior, seat_probs={f'seat{s}': {m: round(float(x), 3) for m, x in zip(MODES, row)} for s, row in zip((1, 2, 3), p)},
                votes=votes, agree=agree, jsd_bits=round(d, 4), mode=mode)


@torch.no_grad()
def reply(tok, model, case, mode, alpha=0.3, beta=0.1, max_new=120):
    if mode == 'HOLD':
        return SILENCE, []
    extra = 'Mode: ' + MODE_TEXT[mode]
    texts = [render(tok, seat_messages(case, s, extra)) for s in (1, 2, 3, 0)]
    ids, att = batch(tok, texts)
    pos = (att.cumsum(-1) - 1).clamp_min(0)
    out = model(input_ids=ids, attention_mask=att, position_ids=pos, use_cache=True)
    past, last = out.past_key_values, out.logits[:, -1, :]
    toks, dis = [], []
    eos = set([tok.eos_token_id] + ([tok.convert_tokens_to_ids('<|im_end|>')] if '<|im_end|>' in tok.get_vocab() else []))
    for _ in range(max_new):
        lp = F.log_softmax(last.float(), -1)                         # 4 x V
        seats, prior = lp[:3], lp[3]
        ps = seats.exp()
        plaus = ps.max(0).values >= beta * ps.max()                   # tokens some seat finds plausible
        pooled = seats.mean(0) - alpha * prior
        pooled[~plaus] = -float('inf')
        t = int(pooled.argmax())
        top = ps[:, ps.mean(0).topk(50).indices]
        dis.append(jsd(top / top.sum(-1, keepdim=True)))
        if t in eos:
            break
        toks.append(t)
        att = torch.cat([att, torch.ones(4, 1, dtype=att.dtype)], -1)
        pos = pos[:, -1:] + 1
        out = model(input_ids=torch.full((4, 1), t), attention_mask=att, position_ids=pos, past_key_values=past, use_cache=True)
        past, last = out.past_key_values, out.logits[:, -1, :]
    text = tok.decode(toks, skip_special_tokens=True).strip()
    return text, dis


def single(tok, model, case, max_new=120):
    """The one-seat baseline: the message alone, ordinary greedy decoding, no mode."""
    ids, att = batch(tok, [render(tok, seat_messages(case, 1))])
    g = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new, do_sample=False)
    return tok.decode(g[0, ids.shape[1]:], skip_special_tokens=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B')
    ap.add_argument('--alpha', type=float, default=0.3); ap.add_argument('--max', type=int, default=120)
    ap.add_argument('--threads', type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    case = json.load(open(a.case, encoding='utf-8'))
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()
    v = mode_vote(tok, model, case)
    txt, dis = reply(tok, model, case, v['mode'], a.alpha, max_new=a.max)
    base = single(tok, model, case, a.max)
    res = dict(case=case.get('name'), model=a.model, alpha=a.alpha, vote=v, triangulated_reply=txt,
               one_seat_reply=base, mean_disagreement_bits=round(sum(dis) / max(1, len(dis)), 4),
               max_disagreement_bits=round(max(dis) if dis else 0, 4), seconds=round(time.time() - t0, 1))
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
