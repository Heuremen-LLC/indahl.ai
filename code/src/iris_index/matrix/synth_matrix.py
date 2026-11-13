"""Plant worlds as fake result files, score them, check the plan's outcomes come back."""
import json, os, csv, random, shutil, subprocess, sys
HERE=os.path.dirname(os.path.abspath(__file__)); S=os.path.join(HERE,'results_synth'); shutil.rmtree(S,ignore_errors=True)
MCQ=json.load(open(os.path.join(HERE,'inputs/mcq_200.json'))); GOLD=list(csv.DictReader(open(os.path.join(HERE,'inputs/nep_gold.csv'))))
def world(name,acc=0.8,flip=0.0,copy=0.0,overattr=0.0,batchflip=0.0,count_wrong=0.0):
    rnd=random.Random(hash(name)%1000); d=os.path.join(S,name); os.makedirs(d)
    w=lambda arm,rows: open(os.path.join(d,arm+'.jsonl'),'w').write(''.join(json.dumps(r)+'\n' for r in rows))
    def nep(copyflip):
        out=[]
        for r in GOLD:
            np_=r['is_no_persona_gold'].strip().lower()=='true'; say_np=np_ and rnd.random()>overattr
            if copyflip and rnd.random()<copy: say_np=not say_np
            o={'no_persona':True,'intent':None} if say_np else {'no_persona':False,'intent':'Pro-Migration','primary_driver':'x','value_orientation':'y','affect':'z'}
            out.append(dict(id=r['comment_id'],raw=json.dumps(o),done_reason='stop',error=None))
        return out
    w('nep_abstain',nep(False)); w('nep_abstain_copy',nep(True))
    base={q['id']:(q['gold'] if rnd.random()<acc else 1-q['gold']) for q in MCQ}
    def mcq(rev=False,flipp=0.0,copyp=0.0):
        rows=[]
        for q in MCQ:
            c=base[q['id']]
            if rnd.random()<flipp or rnd.random()<copyp: c=1-c
            order=[1,0] if rev else [0,1]; rows.append(dict(id=q['id'],order=order,raw=json.dumps({'answer':'AB'[order.index(c)]}),done_reason='stop',error=None))
        return rows
    w('mcq_A',mcq()); w('mcq_A_copy',mcq(copyp=copy)); w('mcq_A_rev',mcq(rev=True,flipp=flip)); w('mcq_B',mcq())
    b=[]
    for i in range(0,200,8):
        qs=MCQ[i:i+8]; ans=['AB'[1-base[q['id']] if rnd.random()<batchflip else base[q['id']]] for q in qs]; cnt=ans.count('A')+(1 if rnd.random()<count_wrong else 0)
        b.append(dict(id=f'batch{i//8:02d}',items=[q['id'] for q in qs],raw=json.dumps({'answers':ans,'count_A':cnt}),done_reason='stop',error=None))
    w('mcq_batch8',b)
world('null'); world('order_carrier',flip=0.3); world('batch_carrier',batchflip=0.3); world('overattr',overattr=0.6,count_wrong=0.8); world('copies_disagree',copy=0.3,flip=0.3)
print(subprocess.run([sys.executable,'-I',os.path.join(HERE,'score_matrix.py'),S],capture_output=True,text=True).stdout)
