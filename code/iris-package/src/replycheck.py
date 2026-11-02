#!/usr/bin/env python3
"""replycheck.py: regenerates replies from an lm-evaluation-harness task so the replies can be read in full next to what each filter extracted.
Heuremen LLC, https://indahl.ai/iris. Needs: pip install mlx-lm lm-eval (Apple silicon).

Same path as mlx_lm evaluate (MLXLM and lm_eval.simple_evaluate), greedy decoding, seed 20281028, batch size 4. Reads 10 documents of the task, or 1 per
subtask when --subtasks is a comma list. Writes <out>/<name>.json with, for each reply, the question, the target, the raw reply and each filter's extraction.
Example: python replycheck.py --name gsm8k_chat --model mlx-community/SomeModel-4bit --task gsm8k_cot --shots 8 --chat --max-tokens 512 --out replycheck_out"""
import argparse, json, os, sys

def main():
    ap = argparse.ArgumentParser(description='Regenerate harness replies and write each reply beside what each filter extracted.')
    ap.add_argument('--name', required=True, help='name for the output file, written as <out>/<name>.json')
    ap.add_argument('--model', required=True, help='model path or Hugging Face id that mlx-lm can load')
    ap.add_argument('--task', required=True, help='lm-evaluation-harness task name')
    ap.add_argument('--shots', type=int, default=0, help='number of few-shot examples (default 0)')
    ap.add_argument('--chat', action='store_true', help='use the chat template')
    ap.add_argument('--no-fewshot-turns', action='store_true', help='with --chat, put the few-shot examples in one message instead of as separate turns')
    ap.add_argument('--max-tokens', type=int, required=True, help='maximum new tokens per reply')
    ap.add_argument('--subtasks', help='comma list of subtasks, one document each')
    ap.add_argument('--out', default='replycheck_out', help='folder for the output file (default ./replycheck_out)')
    a = ap.parse_args()
    from mlx_lm.evaluate import MLXLM, chat_template_fn
    from mlx_lm.sample_utils import make_sampler
    import lm_eval
    subs = a.subtasks.split(',') if a.subtasks else None; seed = 20281028
    lm = MLXLM(a.model, max_tokens=a.max_tokens, batch_size=4, use_chat_template=a.chat, trust_remote_code=False, sampler=make_sampler(temp=0.0))
    MLXLM.apply_chat_template = chat_template_fn()
    r = lm_eval.simple_evaluate(model=lm, tasks=subs or [a.task], fewshot_as_multiturn=a.chat and not a.no_fewshot_turns, apply_chat_template=a.chat, num_fewshot=a.shots,
                                limit=1 if subs else 10, random_seed=seed, numpy_random_seed=seed, torch_random_seed=seed, fewshot_random_seed=seed, log_samples=True)
    out = []
    for t, ss in r['samples'].items():
        for s in ss:
            d = s.get('doc', {})
            out.append(dict(task=t, doc_id=s.get('doc_id'), question=d.get('question') or d.get('input'), target=s.get('target'),
                            reply=s['resps'][0][0] if s.get('resps') else None, filters={k: v for k, v in s.items() if k.startswith('filter')} or None,
                            filtered=s.get('filtered_resps'), filter_name=s.get('filter'), metrics={k: s.get(k) for k in ('exact_match',) if k in s}))
    os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, a.name + '.json')
    with open(p, 'w', encoding='utf-8') as f: json.dump(out, f, indent=1, default=str)
    print('wrote', len(out), 'replies to', p)
if __name__ == '__main__': main()
