from common import *
import glob, os
# (label, chip, job json, raw npz, props json, kind)
runs=[]
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    runs.append(('iq 21Oct',chip,R+f'control_run/iqjob_{chip}.json',R+f'control_run/iqraw_{chip}.npz',R+f'control_run/iq_backend_properties_{chip}.json'))
    for c in (0,1):
        runs.append((f'pairs-c{c} 21Oct',chip,R+f'control_run/pairsjob_{chip}_copy{c}.json',R+f'control_run/pairsraw_{chip}_copy{c}.npz',R+f'control_run/pairs_backend_properties_{chip}.json'))
    runs.append(('flip 22Oct',chip,R+f'flipcheck_run/flipjob_{chip}.json',R+f'flipcheck_run/flipraw_{chip}.npz',R+f'flipcheck_run/flip_backend_properties_{chip}.json'))
    for c in (0,1):
        runs.append((f'pairs-rep-c{c} 22Oct',chip,R+f'pairs_repeat/pairsjob_{chip}_copy{c}.json',R+f'pairs_repeat/pairsraw_{chip}_copy{c}.npz',R+f'pairs_repeat/pairs_backend_properties_{chip}.json'))
def classify(Ctrain0,Ctrain1,Cscore,q,mode):
    mu0=Ctrain0[:,q].mean(); mu1=Ctrain1[:,q].mean(); u=mu1-mu0
    pr=lambda x: np.real((x-mu0)*np.conj(u))/abs(u)**2
    if mode=='mid': thr=0.5
    else:
        # min-total-error threshold on projection from training shots
        a=pr(Ctrain0[:,q]); b=pr(Ctrain1[:,q]); cand=np.linspace(-0.2,1.2,281)
        err=[(a>t).mean()+(b<=t).mean() for t in cand]; thr=cand[int(np.argmin(err))]
    return pr(Cscore[:,q])>thr
rows=[]
for lab,chip,jp,rp,pp in runs:
    if not (os.path.exists(jp) and os.path.exists(rp)): print('missing',lab,chip); continue
    J=json.load(open(jp)); z=np.load(rp); P=json.load(open(pp)); Q=qprops(P); n=156
    meta=J['meta']
    i0=[i for i,m in enumerate(meta) if m['arm']=='CAL' and m['state']=='0']; i1=[i for i,m in enumerate(meta) if m['arm']=='CAL' and m['state']=='1']
    C0=np.concatenate([z['c_%d'%i] for i in i0]); C1=np.concatenate([z['c_%d'%i] for i in i1])
    sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    ib01=np.array([q.get('prob_meas1_prep0',(np.nan,))[0] for q in Q]); ib10=np.array([q.get('prob_meas0_prep1',(np.nan,))[0] for q in Q]); ibre=np.array([q.get('readout_error',(np.nan,))[0] for q in Q])
    rodate=pt(Q[0]['readout_error'][1])
    res={}
    for mode in ('mid','minerr'):
        e01=np.zeros(n); e10=np.zeros(n)
        for q in range(n):
            # cross-fit by shot parity
            a_tr0,a_sc0=C0[0::2],C0[1::2]; a_tr1,a_sc1=C1[0::2],C1[1::2]
            r01=[];r10=[]
            for (t0,t1,s0,s1) in ((C0[0::2],C1[0::2],C0[1::2],C1[1::2]),(C0[1::2],C1[1::2],C0[0::2],C1[0::2])):
                r01.append(classify(t0,t1,s0,q,mode).mean()); r10.append(1-classify(t0,t1,s1,q,mode).mean())
            e01[q]=np.mean(r01); e10[q]=np.mean(r10)
        res[mode]=(e01,e10)
    for mode,(e01,e10) in res.items():
        for name,ours,ib in (('P(read1|prep0)',e01,ib01),('P(read0|prep1)',e10,ib10),('mean assignment err',(e01+e10)/2,ibre)):
            d=ours-ib; m,ci,k=boot_median(d)
            # shot-noise floor: sd of per-qubit estimate
            rows.append((lab,chip,mode,name,np.nanmedian(ours),np.nanmedian(ib),m,ci,k,outcome(ci),str(sub)[:16],str(rodate)[:16]))
import collections
print('%-18s %-13s %-6s %-20s %8s %8s | %9s %-22s %3s %s | job / IBM readout-cal'%('run','chip','disc','quantity','ours','IBM','med diff','95% CI','n','outcome'))
for r in rows:
    print('%-18s %-13s %-6s %-20s %8.4f %8.4f | %+9.4f [%+.4f,%+.4f] %3d %-11s | %s / %s'%(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7][0],r[7][1],r[8],r[9],r[10],r[11]))
json.dump([[str(x) if not isinstance(x,(int,float,tuple,str)) else x for x in r] for r in rows],open('readout_cal_rows.json','w'))
