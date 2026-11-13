import json,os,subprocess,sys,time,fcntl
from common import *
PY=os.path.expanduser('~/bones-forge/venv/bin/python'); W=S+'/runs/stan_v1'; os.makedirs(W,exist_ok=True)
D=S+'/data/silver_v1'; ntr=sum(1 for _ in open(D+'/train.jsonl'))
iters=min(300,max(50,ntr))
cfg=("model: Qwen/Qwen3-1.7B\ntrain: true\ndata: %s\nadapter_path: %s/adapters\nfine_tune_type: lora\nnum_layers: 16\nbatch_size: 2\niters: %d\n"
 "learning_rate: 1.0e-4\nmask_prompt: true\nmax_seq_length: 4096\nseed: 61\nsteps_per_report: 20\nsteps_per_eval: 50\nsave_every: 50\ngrad_checkpoint: true\nlora_parameters:\n  rank: 8\n  scale: 20.0\n  dropout: 0.0\n")%(D,W,iters)
open(W+'/lora.yaml','w').write(cfg)
print('waiting for GPU lock',flush=True); lk=gpu_lock(); print('got lock',flush=True)
t0=time.time(); env=dict(os.environ,HF_HUB_OFFLINE='1')
r=subprocess.run([PY,'-m','mlx_lm','lora','-c',W+'/lora.yaml'],capture_output=True,text=True,env=env)
open(W+'/train.log','w').write(r.stdout+r.stderr)
json.dump({'base':'Qwen/Qwen3-1.7B','license':'Apache-2.0','iters':iters,'train_rows':ntr,'seconds':int(time.time()-t0),'rc':r.returncode,'lr':1e-4,'rank':8,'scale':20,'num_layers':16,'batch':2},open(W+'/run.json','w'),indent=1)
print('rc',r.returncode,int(time.time()-t0),'s',flush=True)
