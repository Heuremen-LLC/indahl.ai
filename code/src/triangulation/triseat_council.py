#!/usr/bin/env python3
"""triseat_council.py -- the three seats report in Wayfinder's format (6 October 2026), Pi left out for now.

Each seat (1 the words, 2 the person, 3 the trajectory) gives:
  VALUE       its answer: a draft reply, written from its own context
  NEXT        what it does next: its mode (STAY / HELP / ASK / BOTH), calibrated against the Plus None prior
  INSIDE      its confidence in its own answer, 0-9, read from its own context
  OUTSIDE     how effective the OTHER TWO seats rate that answer, 0-9, each reading from its own context
The reply chosen is the one the other seats rate most effective (inside confidence breaks ties).
No gap between inside and outside is computed or fed back (Wayfinder: "don't include Pi yet, it may confuse them").
Ratings are expected values over the digit tokens 0-9, not sampled. Uses triseat.py for seats, prompts and the mode vote."""
import argparse, json, time
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import triseat as T

SELF_Q = "How confident are you that your reply above is right for this person? Answer with one digit, 0 (not at all) to 9 (completely)."
RATE_Q = ("Someone replied to this person's last message with:\n\n\"{r}\"\n\nHow effective is that reply for this person, "
          "right now? Answer with one digit, 0 (not at all) to 9 (exactly right).")


def digit_ids(tok):
    return [tok.encode(str(d), add_special_tokens=False)[0] for d in range(10)]


@torch.no_grad()
def expected_digit(tok, model, texts):
    ids, att = T.batch(tok, texts)
    pos = (att.cumsum(-1) - 1).clamp_min(0)
    logits = model(input_ids=ids, attention_mask=att, position_ids=pos).logits[:, -1, :]
    p = F.softmax(logits[:, digit_ids(tok)].float(), -1)
    return [round(float((row * torch.arange(10)).sum()), 2) for row in p]


@torch.no_grad()
def drafts(tok, model, case, modes, max_new):
    texts = [T.render(tok, T.seat_messages(case, s, 'Mode: ' + T.MODE_TEXT[m])) for s, m in zip((1, 2, 3), modes)]
    ids, att = T.batch(tok, texts)
    g = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new, do_sample=False,
                       pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return [tok.decode(row[ids.shape[1]:], skip_special_tokens=True).strip() for row in g]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B')
    ap.add_argument('--max', type=int, default=90); ap.add_argument('--threads', type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    case = json.load(open(a.case, encoding='utf-8'))
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()

    vote = T.mode_vote(tok, model, case)                      # calibrated per-seat mode probabilities
    modes = [max(T.MODES, key=lambda m: vote['seat_probs'][f'seat{s}'][m]) for s in (1, 2, 3)]
    ans = drafts(tok, model, case, modes, a.max)

    # INSIDE: each seat on its own answer
    self_texts = []
    for i, s in enumerate((1, 2, 3)):
        msgs = T.seat_messages(case, s) + [{'role': 'assistant', 'content': ans[i]}, {'role': 'user', 'content': SELF_Q}]
        self_texts.append(T.render(tok, msgs))
    inside = expected_digit(tok, model, self_texts)

    # OUTSIDE: the other two seats rate each answer from their own context
    pairs, rate_texts = [], []
    for i in range(3):
        for j, s in enumerate((1, 2, 3)):
            if j == i:
                continue
            msgs = T.seat_messages(case, s)
            msgs = msgs[:-1] + [{'role': 'user', 'content': msgs[-1]['content'] + '\n\n' + RATE_Q.format(r=ans[i])}]
            pairs.append((i, j)); rate_texts.append(T.render(tok, msgs))
    rates = expected_digit(tok, model, rate_texts)
    outside = {i: [] for i in range(3)}
    for (i, j), r in zip(pairs, rates):
        outside[i].append(r)

    seats = []
    for i, s in enumerate((1, 2, 3)):
        seats.append(dict(seat=['the words', 'the person', 'the trajectory'][i], value=ans[i], next=modes[i],
                          inside=inside[i], outside=round(sum(outside[i]) / 2, 2), outside_by=outside[i]))
    pick = max(range(3), key=lambda i: (seats[i]['outside'], seats[i]['inside']))
    print(json.dumps(dict(case=case.get('name'), model=a.model, seats=seats, chosen_seat=seats[pick]['seat'],
                          chosen_reply=seats[pick]['value'], seconds=round(time.time() - t0, 1)), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
