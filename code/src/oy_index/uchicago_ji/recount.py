# Recount from released JSON: default-threshold FPR on human texts by genre, FNR on AI texts by source model. stdlib only.
import json,glob,sys,collections,math,ast
D=sys.argv[1]+'/all_json/200_ai_generated_text_detector_and_label_result_files/'
def wilson(k,n,z=1.96):
    if n==0: return (float('nan'),)*2
    p=k/n; c=(p+z*z/(2*n))/(1+z*z/n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n); return max(0,c-h),min(1,c+h)
def pos(det,v):
    # returns True/False, or None when the detector returned no verdict (counted separately)
    try:
        if det=='pengram': return v['prediction']!='Unlikely AI'
        if det=='originality': return v['classification']['AI']==1
        if det=='gptzero': return v['average_generated_prob']>=0.5
    except (KeyError,TypeError): return None
F=sorted(glob.glob(D+'*.json')); recs=json.load(open(F[0]))
dets=['pengram','originality','gptzero']
print('human texts',len(recs),'genres',dict(collections.Counter(r['genre'] for r in recs)))
for det in dets:
    by=collections.defaultdict(lambda:[0,0])
    for r in recs:
        v=r['human_verdict'] if isinstance(r['human_verdict'],dict) else ast.literal_eval(r['human_verdict'])
        x=pos(det,v.get(det,{}))
        if x is None: by['_no_verdict'][1]+=1; continue
        by[r['genre']][0]+=x; by[r['genre']][1]+=1
    tot=[sum(a for g,(a,b) in by.items() if g!='_no_verdict'),sum(b for g,(a,b) in by.items() if g!='_no_verdict')]
    print(f'{det}: FPR all {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.3%} [{wilson(*tot)[0]:.3%}, {wilson(*tot)[1]:.3%}] |',
          ' '.join(f'{g} {a}/{b}' for g,(a,b) in sorted(by.items())))
for f in F:
    d=json.load(open(f)); m=f.split('generated_output_')[1].split('_all')[0]
    out=[]
    for det in dets:
        k=n=0
        for r in d:
            av=r['ai_verdicts'] if isinstance(r['ai_verdicts'],dict) else ast.literal_eval(r['ai_verdicts'])
            x=pos(det,list(av.values())[0].get(det,{}))
            if x is None: continue
            n+=1; k+=not x
        out.append(f'{det} FNR {k}/{n}={k/n:.2%}')
    print(m,'|',' ; '.join(out))
