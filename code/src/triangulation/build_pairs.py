#!/usr/bin/env python3
"""build_pairs.py -- preference pairs from the misread moments, with nobody reading them by hand (6 October 2026).

For each moment in hat_misreads.jsonl:
  1. four candidate replies from the open model, one per mode (STAY / HELP / ASK / BOTH), written from the person seat,
     plus a fifth: HOLD, silence (Wen, 6 Oct: 'silence is the answer'), so the raters can choose waiting over deciding
  2. each candidate rated 0-9 for effectiveness by four raters:
       seat 1 the words, seat 2 the person, seat 3 the trajectory, and THE KEY: his own reaction to the real reply.
     The key rater is told what he actually said next, so his own words decide what would have landed. Weight 2.
  3. chosen = highest weighted rating, rejected = lowest. Kept only if they differ by at least --margin.
No Claude text anywhere: candidates and ratings come from the open model; the key is his own words.
Output: pairs.jsonl {conv, at, prompt (person-seat chat), chosen, rejected, ratings, modes}. Resumable (skips done rows).
Run: venv/Scripts/python build_pairs.py hat_misreads.jsonl hat_baseline.json --model Qwen/Qwen3-1.7B"""
import argparse, json, os, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import triseat as T
from triseat_council import expected_digit

KEY_Q = ("Someone replied to this person's message with:\n\n\"{r}\"\n\nHere is what the person actually said next, after a "
         "different reply they got: \"{react}\"\n\nKnowing how they reacted, how well would THIS reply have landed for them? "
         "Answer with one digit, 0 (badly) to 9 (exactly right).")


def cut(t, n=700):
    t = (t or '').strip()
    return t if len(t) <= n else t[:n] + ' ...'


@torch.no_grad()
def candidates(tok, model, case, max_new):
    texts = [T.render(tok, T.seat_messages(case, 2, 'Mode: ' + T.MODE_TEXT[m])) for m in T.MODES]
    ids, att = T.batch(tok, texts)
    g = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new, do_sample=True, temperature=0.7, top_p=0.9,
                       pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return [tok.decode(row[ids.shape[1]:], skip_special_tokens=True).strip() for row in g] + [T.SILENCE]   # the fifth: HOLD


def rate(tok, model, case, cands, react):
    texts, idx = [], []
    for ci, c in enumerate(cands):
        c = HOLD_SHOWN if c == T.SILENCE else c
        for s in (1, 2, 3):
            msgs = T.seat_messages(case, s)
            msgs = msgs[:-1] + [{'role': 'user', 'content': msgs[-1]['content'] + '\n\n' + T_RATE.format(r=c)}]
            texts.append(T.render(tok, msgs)); idx.append((ci, s))
        msgs = T.seat_messages(case, 1)
        msgs = msgs[:-1] + [{'role': 'user', 'content': msgs[-1]['content'] + '\n\n' + KEY_Q.format(r=c, react=cut(react, 500))}]
        texts.append(T.render(tok, msgs)); idx.append((ci, 'key'))
    out = []
    for k in range(0, len(texts), 4):                                  # 4 at a time keeps CPU memory flat
        out += expected_digit(tok, model, texts[k:k + 4])
    table = {ci: {} for ci in range(len(cands))}
    for (ci, s), v in zip(idx, out):
        table[ci][str(s)] = v
    return table


from triseat_council import RATE_Q as T_RATE  # noqa: E402
HOLD_SHOWN = '(nothing yet: they stayed quiet, stayed there, and waited for the person to say more)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('misreads'); ap.add_argument('baseline'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B')
    ap.add_argument('--out', default='pairs.jsonl'); ap.add_argument('--max', type=int, default=90)
    ap.add_argument('--margin', type=float, default=0.5); ap.add_argument('--threads', type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    rows = [json.loads(l) for l in open(a.misreads, encoding='utf-8')]
    baseline = json.load(open(a.baseline, encoding='utf-8'))
    done = set()
    if os.path.exists(a.out):
        done = {(json.loads(l)['conv'], json.loads(l)['at']) for l in open(a.out, encoding='utf-8')}
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()
    kept = skipped = 0
    for n, r in enumerate(rows):
        if (r['conv'], r['at']) in done or not r.get('reaction'):
            continue
        t0 = time.time()
        case = dict(message=cut(r['message']), baseline=baseline, trajectory=[cut(x, 400) for x in r['trajectory']])
        cands = candidates(tok, model, case, a.max)
        table = rate(tok, model, case, cands, r['reaction'])
        score = {ci: (v['1'] + v['2'] + v['3'] + 2 * v['key']) / 5 for ci, v in table.items()}
        best, worst = max(score, key=score.get), min(score, key=score.get)
        rec = dict(conv=r['conv'], at=r['at'], why=r['why'], modes=T.MODES + ['HOLD'], candidates=cands, ratings=table,
                   weighted={(T.MODES + ['HOLD'])[k]: round(v, 2) for k, v in score.items()},
                   chosen_mode=(T.MODES + ['HOLD'])[best], rejected_mode=(T.MODES + ['HOLD'])[worst],
                   prompt=T.seat_messages(case, 2), chosen=cands[best], rejected=cands[worst],
                   kept=score[best] - score[worst] >= a.margin)
        with open(a.out, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        kept += rec['kept']; skipped += (not rec['kept'])
        print(f"[{n + 1}/{len(rows)}] {r['at']} chosen={rec['chosen_mode']} rejected={rec['rejected_mode']} "
              f"spread={score[best] - score[worst]:.2f} kept={rec['kept']} ({time.time() - t0:.0f}s)", flush=True)
    print(f'done: kept {kept}, too close to call {skipped}')


if __name__ == '__main__':
    main()
