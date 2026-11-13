import json, ast, sys, numpy as np
D=sys.argv[1]
def f1(lab,pred):
    tp=sum(l=='yes' and p=='yes' for l,p in zip(lab,pred)); fp=sum(l=='no' and p=='yes' for l,p in zip(lab,pred)); fn=sum(l=='yes' and p!='yes' for l,p in zip(lab,pred))
    pr=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0; return (2*pr*rc/(pr+rc) if pr+rc else 0),pr,rc
allids=set(); yes_emit=0; yes_to_no=0; out={}
for sp in ('adversarial','popular','random'):
    d=json.load(open(f'{D}/experiments/pope_{sp}_2tok_vs_8tok.json'))
    R=ast.literal_eval(d['results']) if isinstance(d['results'],str) else d['results']
    S=ast.literal_eval(d['summary']) if isinstance(d['summary'],str) else d['summary']
    lab=[r['label'] for r in R]; p2=[r['pred_2tok'] for r in R]; p8=[r['pred_8tok'] for r in R]; tok=[r['top_token_id'] for r in R]
    allids|=set(tok)
    F8,P8,R8=f1(lab,p8); F2,P2,R2=f1(lab,p2)
    T=sum(l=='yes' and p=='yes' for l,p in zip(lab,p8)); G=sum(l=='no' and p=='no' for l,p in zip(lab,p8))
    rho=sum(l=='no' and a=='no' and b=='yes' for l,a,b in zip(lab,p8,p2)); phi=sum(l=='yes' and a=='no' and b=='yes' for l,a,b in zip(lab,p8,p2)); fn8=sum(l=='yes' and a=='no' for l,a in zip(lab,p8))
    ye=sum(t==3869 for t in tok); yes_emit+=ye; yes_to_no+=sum(t==3869 and b=='no' for t,b in zip(tok,p2))
    # B1 paired bootstrap
    rng=np.random.default_rng(20261025); L=np.array(lab); A2=np.array(p2); A8=np.array(p8); n=len(L); bs=[]
    for _ in range(20000):
        i=rng.integers(0,n,n); bs.append(f1(L[i],A8[i])[0]-f1(L[i],A2[i])[0]) if False else None
    # vectorised version
    Y=(L=='yes'); y8=(A8=='yes'); y2=(A2=='yes'); idx=rng.integers(0,n,(20000,n))
    def vf(yp):
        tp=(Y[idx]&yp[idx]).sum(1); fp=(~Y[idx]&yp[idx]).sum(1); fn=(Y[idx]&~yp[idx]).sum(1); return 2*tp/(2*tp+fp+fn)
    sh=vf(y8)-vf(y2); lo,hi=np.percentile(sh,[2.5,97.5]); kg=vf(y8)-vf(y8)
    out[sp]=dict(n=n,F8=F8,F2=F2,P2=P2,R2=R2,yes2=np.mean(y2),T=T,G=G,rho=f'{rho}/{G}',phi=f'{phi}/{fn8}',shift=F8-F2,ci=[lo,hi],kg_max=float(abs(kg).max()),their=S)
    print(f"{sp}: n {n} F1_8 {F8:.4f} F1_2 {F2:.4f} P2 {P2:.4f} R2 {R2:.4f} yes2 {np.mean(y2):.3f} T {T} G {G} rho {rho}/{G} phi {phi}/{fn8} shift {100*(F8-F2):.2f} pts [{100*lo:.2f}, {100*hi:.2f}] knowngood {abs(kg).max():.1e}")
print('top-token ids seen:',sorted(allids),'| 3582 or 1217 present:',bool(allids&{3582,1217}),'| Yes emissions',yes_emit,'-> 2tok no:',yes_to_no)
json.dump(out,open('recount_out.json','w'),indent=1,default=str)
