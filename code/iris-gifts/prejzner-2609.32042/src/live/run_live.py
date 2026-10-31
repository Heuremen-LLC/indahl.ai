#!/usr/bin/env python3
"""G1 live arm (PLAN Addendum 1). His main67 tasks, in the order of his own run for that file, through our env replica's loop and oracle,
with the model called the way his LlamaCppRunner calls it: llama_cpp.Llama(model_path, n_ctx=8192, n_gpu_layers=-1, chat_format=<his>,
verbose=False) and create_chat_completion(messages, temperature=0.0, top_p=1.0, max_tokens=512, seed=42). Repair off.
Before each call the library's own formatter output for those messages is checked against our rendered prompt text.
Usage: lcpvenv/bin/python run_live.py <model_id> <quant> <gguf path> <his run slug> <rep> <out dir>"""
import os, sys, json, time, platform, hashlib
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'env'))
import acceptance, prompts, agent, oracle
import llama_cpp
from llama_cpp import Llama, llama_chat_format
model_id, quant, gguf, slug, rep, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
fam = prompts.FAMILY_OF_MODEL[model_id]; chat_format = {'chatml': 'chatml', 'llama-3': 'llama-3'}[fam]
REL = acceptance.REL
order = [json.loads(l)['task_id'] for l in open(os.path.join(REL, 'trajectories', slug + '.jsonl'), encoding='utf-8')]
tasks = acceptance.taskmod.load_dir(os.path.join(acceptance.THEIRS, 'tasks', 'adversarial'))
fmt = {'chatml': llama_chat_format.format_chatml, 'llama-3': llama_chat_format.format_llama3}[fam]
STASH = {}
_orig = prompts.chat_text
def chat_text(messages, family):
    STASH['messages'] = [dict(m) for m in messages]; return _orig(messages, family)
prompts.chat_text = chat_text
t0 = time.time()
SMOKE = os.environ.get('LIVE_SMOKE') == '1'   # CPU-only pipeline check on one task, never a reading
if SMOKE: order = order[:1]
llm = Llama(model_path=gguf, n_ctx=8192, n_gpu_layers=0 if SMOKE else -1, chat_format=chat_format, verbose=False)
load_s = time.time() - t0
os.makedirs(out, exist_ok=True); tag = '%s_%s_r%d' % (model_id, quant, rep)
fo = open(os.path.join(out, tag + '.jsonl'), 'w', encoding='utf-8')
npass = 0; fmt_mismatch = 0
for tid in order:
    task = tasks[tid]; usage_log = []
    def complete(prompt, idx):
        global fmt_mismatch
        if fmt is not None:
            fr = fmt(messages=STASH['messages'])
            if fr.prompt != prompt: fmt_mismatch += 1
        r = llm.create_chat_completion(messages=STASH['messages'], temperature=0.0, top_p=1.0, max_tokens=512, seed=42)
        usage_log.append({'usage': r.get('usage'), 'finish_reason': r['choices'][0].get('finish_reason')})
        return r['choices'][0]['message']['content'] or ''
    tr = agent.run_task(task, complete, False, fam)
    res = oracle.evaluate(task.id, task.expected, tr.oracle_steps); npass += bool(res.passed)
    fo.write(json.dumps({'task_id': tid, 'passed': bool(res.passed), 'tags': sorted(set(res.tags)), 'success': tr.success, 'steps': tr.steps,
                         'calls': usage_log, 'total_tokens': sum((u['usage'] or {}).get('total_tokens', 0) for u in usage_log)}, ensure_ascii=False) + '\n'); fo.flush()
fo.close()
h = hashlib.sha256()
with open(gguf, 'rb') as f:
    for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
meta = {'model_id': model_id, 'quant': quant, 'gguf': os.path.basename(gguf), 'gguf_sha256': h.hexdigest(), 'his_run': slug, 'rep': rep,
        'llama_cpp_python': llama_cpp.__version__, 'python': platform.python_version(), 'machine': platform.platform(), 'n_tasks': len(order),
        'passed': npass, 'formatter_prompt_mismatches': fmt_mismatch, 'formatter_checked': fmt is not None, 'load_s': round(load_s, 1),
        'wall_s': round(time.time() - t0, 1), 'ended_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
json.dump(meta, open(os.path.join(out, tag + '.meta.json'), 'w'), indent=1)
print(tag, 'passed', npass, 'of', len(order), '| formatter mismatches', fmt_mismatch, '| wall', meta['wall_s'], 's')
