"""handcheck.py ROUND NAME MODEL TASK SHOTS CHAT MAXTOK [SUBTASKS] (env HC_MULTITURN=0: chat template without few-shot turns): regenerates replies for the parser check (replies read in full) (ROUND_S2.md Addendum 1).
Same path as mlx_lm evaluate (MLXLM + lm_eval.simple_evaluate), greedy, seed 20281028, batch size 4, limit 10 (or 1 per subtask when SUBTASKS
is a comma list). Writes handcheck/<round>_<name>.json: per reply the question, target, raw reply and each filter's extraction."""
import sys, json, os
from mlx_lm.evaluate import MLXLM, chat_template_fn
from mlx_lm.sample_utils import make_sampler
import lm_eval
rnd, name, model, task, shots, chat, maxtok = sys.argv[1:8]; subs = sys.argv[8].split(',') if len(sys.argv) > 8 else None
chat = chat == '1'; SEED = 20281028
MT = chat and os.environ.get('HC_MULTITURN', '1') == '1'   # 30 Oct (S1 full read): S1 chat runs used the chat template WITHOUT few-shot-as-turns; set HC_MULTITURN=0 to match them. Default unchanged (S2 and S3).
lm = MLXLM(model, max_tokens=int(maxtok), batch_size=4, use_chat_template=chat, trust_remote_code=False, sampler=make_sampler(temp=0.0))
MLXLM.apply_chat_template = chat_template_fn()
r = lm_eval.simple_evaluate(model=lm, tasks=subs or [task], fewshot_as_multiturn=MT, apply_chat_template=chat, num_fewshot=int(shots),
                            limit=1 if subs else 10, random_seed=SEED, numpy_random_seed=SEED, torch_random_seed=SEED, fewshot_random_seed=SEED, log_samples=True)
out = []
for t, ss in r['samples'].items():
    for s in ss:
        d = s.get('doc', {})
        out.append(dict(task=t, doc_id=s.get('doc_id'), question=d.get('question') or d.get('input'), target=s.get('target'),
                        reply=s['resps'][0][0] if s.get('resps') else None, filters={k: v for k, v in s.items() if k.startswith('filter')} or None,
                        filtered=s.get('filtered_resps'), filter_name=s.get('filter'), metrics={k: s.get(k) for k in ('exact_match',) if k in s}))
os.makedirs('handcheck', exist_ok=True)
json.dump(out, open(f'handcheck/{rnd}_{name}.json', 'w'), indent=1, default=str); print('wrote', len(out), 'replies')
