import json, os, random, shutil, subprocess, sys
H=os.path.dirname(os.path.abspath(__file__)); S=os.path.join(H,'results_v2_synth'); shutil.rmtree(S,ignore_errors=True); L='ABCD'
M4=json.load(open(os.path.join(H,'inputs/mcq4_200.json'))); PC=json.load(open(os.path.join(H,'inputs/mcq4_poscontrol.json')))
def order(n,k): return list(range(n))[::-1] if k=='rev' else (list(range(1,n))+[0] if k=='rot' else list(range(n)))
def world(name,mode='content',flip=0.0,wrong_len=0.0,pc_ok=True):
    rnd=random.Random(name); d=os.path.join(S,name); os.makedirs(d)
    base={q['id']:(q['gold'] if rnd.random()<0.7 else rnd.randrange(4)) for q in M4}
    def pick(q,o,kind):
        if mode=='letterA': return 0                                  # always letter A
        c=base.get(q['id'],q['gold']) if q in M4 else q['gold']
        if q['id'].startswith('pc'): c=o[0] if pc_ok else q['gold']    # position task: first listed
        if kind!='id' and rnd.random()<flip: c=(c+1)%4
        return o.index(c)
    def arm(a,Q,kind):
        rows=[]
        for q in Q:
            o=order(4,kind); rows.append(dict(id=q['id'],order=o,raw=json.dumps({'answer':L[pick(q,o,kind)]}),done_reason='stop',error=None))
        open(os.path.join(d,a+'.jsonl'),'w').write(''.join(json.dumps(r)+'\n' for r in rows))
    for a,Q,k in (('mcq4_A',M4,'id'),('mcq4_A_copy',M4,'id'),('mcq4_rev',M4,'rev'),('mcq4_rot',M4,'rot'),('mcq4_B',M4,'id'),('pc_A',PC,'id'),('pc_rev',PC,'rev')): arm(a,Q,k)
    b=[]
    for i in range(0,200,8):
        qs=M4[i:i+8]; ans=[L[pick(q,[0,1,2,3],'id')] for q in qs]
        if rnd.random()<wrong_len: ans=ans+['A']
        b.append(dict(id=f'batch{i//8:02d}',items=[q['id'] for q in qs],raw=json.dumps({'answers':ans,'count_A':ans.count('A')}),done_reason='stop',error=None))
    open(os.path.join(d,'mcq4_batch8.jsonl'),'w').write(''.join(json.dumps(r)+'\n' for r in b))
world('null'); world('order_carrier',flip=0.3); world('letter_A_bias',mode='letterA'); world('pc_fails',pc_ok=False,flip=0.3); world('wrong_length',wrong_len=0.6)
print(subprocess.run([sys.executable,'-I',os.path.join(H,'score_matrix_v2.py'),S],capture_output=True,text=True))
