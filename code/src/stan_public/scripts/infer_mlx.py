"""Per-code inference of the base or STAN (adapter) on one gold split. usage: infer_mlx.py NAME dev|test [ADAPTER_DIR]. Never scores."""
import sys,json,os,time
from common import *
name=sys.argv[1]; split=sys.argv[2]; ad=sys.argv[3] if len(sys.argv)>3 else None
assert split in ('dev','test')
os.environ['HF_HUB_OFFLINE']='1'
out=S+'/runs/%s_%s.jsonl'%(name,split); done={(r['set'],r['id']) for r in jl_read(out)}
items=[('gold',g['id'],g['text']) for g in json.load(open(S+'/data/gold_items.json')) if g.get('text') and g['split']==split]
todo=[x for x in items if (x[0],x[1]) not in done]; print(name,len(todo),'todo',flush=True)
if todo:
    lk=gpu_lock(); print('got GPU lock',flush=True)
    from mlx_lm import load,generate
    from mlx_lm.sample_utils import make_sampler
    model,tok=load('Qwen/Qwen3-1.7B',adapter_path=ad)
    with open(out,'a') as f:
        for s,i,text in todo:
            labs={}
            for c in CODES:
                msgs=[{'role':'user','content':code_prompt(c,text)}]
                p=tok.apply_chat_template(msgs,add_generation_prompt=True,tokenize=False,enable_thinking=False)
                raw=generate(model,tok,prompt=p,max_tokens=200,sampler=make_sampler(temp=0.0))
                labs[c]=norm_label(c,parse_obj(raw),text)
            f.write(json.dumps({'set':s,'id':i,'labels':labs})+'\n'); f.flush()
    print('done',flush=True)
