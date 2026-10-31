"""run_live.py (31 Oct 2026, per PLAN.md): one session of one model over the first 30 tasks, their runner's settings, our own code.
Usage: python -I run_live.py qwen15|phi35 SESSION   (writes runs/<model>_s<SESSION>.jsonl and .meta.json; refuses on any prompt mismatch)"""
import os, sys, json, time, hashlib, glob, platform
import torch, transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..', '..')); T = G + '/theirs'
M = {'qwen15': ('Qwen/Qwen2.5-1.5B-Instruct', '989aa7980e4cf806f80c7fef2b1adb7bc71aa306', 'trajectories_opensource', '_qwen2.5.json'),
     'phi35': ('microsoft/Phi-3.5-mini-instruct', '2fe192450127e6a83f7441aef6e3ca586c338b77', 'trajectories_phi-3.5-mini', None)}
key, ses = sys.argv[1], int(sys.argv[2]); repo, rev, tdir, suffix = M[key]
SYSTEM = "You are an AI scientist. Analyze step by step, then conclude."     # their runner's system text
tasks = json.load(open(T + '/github_at_26cb3ffb/data/task_bank.json'))['tasks'][:30]
stored = {}
for f in glob.glob(f'{T}/hf_at_b112204c/{tdir}/*.json'):
    d = json.load(open(f)); stored[d['task_id']] = d['prompt']
bad = [t['task_id'] for t in tasks if stored.get(t['task_id']) != t['prompt']]
if bad: sys.exit(f'REFUSED: prompt differs from their stored file for {bad}')
path = snapshot_download(repo, revision=rev, cache_dir=G + '/models', allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model'])
shas = {os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in sorted(glob.glob(path + '/*.safetensors'))}
tok = AutoTokenizer.from_pretrained(path)
model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float16).to('mps').eval()
out_p = f'{H}/runs/{key}_s{ses}.jsonl'
meta = dict(model=repo, revision=rev, safetensors_sha256=shas, device='mps', dtype='float16', torch=torch.__version__,
            transformers=transformers.__version__, python=platform.python_version(), macos=platform.mac_ver()[0], started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
json.dump(meta, open(f'{H}/runs/{key}_s{ses}.meta.json', 'w'), indent=1)
with open(out_p, 'w') as fo:
    for i, t in enumerate(tasks):
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": t['prompt']}]
        text_in = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inp = tok(text_in, return_tensors='pt').to('mps')
        t0 = time.time()
        with torch.no_grad():
            o = model.generate(**inp, max_new_tokens=512, do_sample=False, pad_token_id=tok.eos_token_id)
        new = o[0][inp['input_ids'].shape[1]:]
        txt = tok.decode(new, skip_special_tokens=True)
        fo.write(json.dumps(dict(task_id=t['task_id'], session=ses, text=txt, ids=new.tolist(), n_new=int(new.shape[0]), hit_cap=int(new.shape[0]) >= 512,
                                 wall_s=round(time.time() - t0, 3), input_sha256=hashlib.sha256(text_in.encode()).hexdigest())) + '\n'); fo.flush()
        print(f'{key} s{ses} {i + 1}/30 {t["task_id"]} new={int(new.shape[0])}', flush=True)
print('DONE', key, ses)
