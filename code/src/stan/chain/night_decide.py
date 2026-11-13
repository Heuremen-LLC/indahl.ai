#!/usr/bin/env python3
"""night_decide.py (13 Nov 2026, Wayfinder: "training pipeline time with automated handoffs"). Runs as a chain stage after each eval.
Reads that model's two eval files against the base model's, writes a row to NIGHT.md, and appends the next rung's stages (data, lora,
eval, decide) to chain.json. The ladder below was written before any of its results. Routing only: the morning hand-off reports counts
and intervals, never a decision as a finding.

  night_decide.py RUNG_NAME

LADDER (fixed before results):
  v3  balanced data_bal, lr 1e-5, 600 iters                      (running when this was written)
  If v3 flags no positive on either set (collapse):   v4 = detection-only targets (make_short.py on data_bal), lr 1e-5, 600
  If v3 flags some positives but fewer than base:     v4 = data_bal, lr 2e-5, 1200 iters
  If v3 matches or beats base on both sets' counts:   v4 = data_bal, lr 1e-5, 1200 iters (longer on what works)
  After v4, the same three rules pick v5 from v4's result, with one change: a second collapse moves to detection-only at lr 2e-5, 1200.
  The ladder stops after v6 or at 07:00 local, whichever comes first; the hand-off stage then writes MORNING.md.
"""
import json, os, sys, time, datetime as dt
C = os.path.dirname(os.path.abspath(__file__)); TE = os.path.join(os.path.dirname(C), 'train_e'); R = os.path.join(TE, 'results')
M = 'mlx-community/Qwen2.5-7B-Instruct-4bit'; PY = '/opt/homebrew/bin/python3'; VENV = '/Users/heuremen/bones-forge/venv/bin/python'
def res(name, s):
    try: return json.load(open(os.path.join(R, f'{name}_test_{s}.json')))['summary']
    except Exception: return None
def classify(name):
    b = {s: res('base', s) for s in ('hand', 'pipeline')}; m = {s: res(name, s) for s in ('hand', 'pipeline')}
    if not all(m.values()): return 'missing', b, m
    if all(m[s]['pos_flag'] == 0 for s in m): return 'collapse', b, m
    if all(m[s]['pos_flag'] >= b[s]['pos_flag'] and m[s]['neg_flag'] <= b[s]['neg_flag'] + 2 for s in m): return 'match_or_beat', b, m
    return 'partial', b, m
def stages(v, data, lr, iters, prev_eval):
    a = os.path.join(TE, f'adapters_{v}'); out = []
    if data == 'data_short' and not os.path.isdir(os.path.join(TE, 'data_short')):
        out.append({'id': f'data_short_{v}', 'after': [prev_eval], 'machine': 'cpu', 'cwd': TE, 'cmd': [PY, os.path.join(TE, 'make_short.py'), 'data_bal', 'data_short']}); dep = f'data_short_{v}'
    else: dep = prev_eval
    out += [{'id': f'lora_{v}', 'after': [dep], 'machine': 'mac', 'cwd': TE, 'cmd': ['/bin/zsh', os.path.join(TE, 'train_lora.sh'), M, lr, str(iters), a, os.path.join(TE, data)]},
            {'id': f'eval_{v}', 'after': [f'lora_{v}'], 'machine': 'mac', 'cwd': TE, 'cmd': ['/bin/zsh', os.path.join(TE, 'eval_pair.sh'), M, a, f'lora_{v}']},
            {'id': f'decide_{v}', 'after': [f'eval_{v}'], 'machine': 'cpu', 'cwd': C, 'cmd': [PY, os.path.join(C, 'night_decide.py'), v]}]
    return out
def main():
    v = sys.argv[1]; cls, b, m = classify(f'lora_{v}'); n = int(v[1:]); nxt = f'v{n + 1}'
    row = f"| {dt.datetime.now():%H:%M} | lora_{v} | " + ' | '.join(f"{m[s]['pos_flag']}/{m[s]['pos']} pos, {m[s]['neg_flag']}/{m[s]['neg']} neg" if m.get(s) else 'missing' for s in ('hand', 'pipeline')) + f" | {cls} |"
    night = os.path.join(C, 'NIGHT.md')
    if not os.path.exists(night):
        open(night, 'w').write('# NIGHT ladder (13 Nov 2026): rows written by night_decide.py after each eval\n\nbase: hand ' + f"{b['hand']['pos_flag']}/{b['hand']['pos']} pos, {b['hand']['neg_flag']}/{b['hand']['neg']} neg; pipeline {b['pipeline']['pos_flag']}/{b['pipeline']['pos']} pos, {b['pipeline']['neg_flag']}/{b['pipeline']['neg']} neg\n\n| time | model | test_hand | test_pipeline | route |\n|---|---|---|---|---|\n")
    chain = json.load(open(os.path.join(C, 'chain.json'))); ids = {s['id'] for s in chain}
    stop = n >= 6 or dt.datetime.now().hour in (7, 8, 9) or cls == 'missing'
    prev_collapses = open(night).read().count('| collapse |')
    if not stop:
        if cls == 'collapse': plan = ('data_short', '2e-5', 1200) if prev_collapses >= 1 else ('data_short', '1e-5', 600)
        elif cls == 'partial': plan = ('data_bal', '2e-5', 1200)
        else: plan = ('data_bal', '1e-5', 1200)
        new = [s for s in stages(nxt, *plan, f'eval_{v}') if s['id'] not in ids]
        chain += new; row += f" next lora_{nxt}: {plan[0]}, lr {plan[1]}, {plan[2]} iters"
    else:
        row += ' ladder stopped'
        try: os.remove(os.path.join(C, 'NIGHT_ACTIVE'))   # routine Mac sweeps may resume
        except FileNotFoundError: pass
    hid = f'handoff_night_{v}'
    if hid not in ids:
        chain.append({'id': hid, 'after': [f'decide_{v}'], 'machine': 'cpu', 'cwd': C, 'finally': True,
                      'cmd': ['/bin/zsh', '-c', '/Users/heuremen/.local/bin/claude -p "$(cat /Users/heuremen/bones-forge/stan/chain/prompts/handoff.md)" --model sonnet --dangerously-skip-permissions --output-format text']} if stop else
                     {'id': hid, 'after': [f'decide_{v}'], 'machine': 'cpu', 'cwd': C, 'cmd': ['/usr/bin/true']})
    json.dump(chain, open(os.path.join(C, 'chain.json'), 'w'), indent=1)
    open(night, 'a').write(row + '\n'); print(row)
if __name__ == '__main__': main()
