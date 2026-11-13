from common import *
import os
out=[]
def run(label, chip, jobp, rawp, propp, sel0, sel1, E):
    J=json.load(open(jobp)); z=np.load(rawp); P=json.load(open(propp)); Q=qprops(P); meta=J['meta']
    def first(sel):
        ii=[i for i,m in enumerate(meta) if sel(m)]
        if not ii: return None,0
        x=np.concatenate([bits(z['m0_%d'%i],len(E)) for i in ii]); return x.mean(0), x.shape[0]
    p0,n0=first(sel0); p1,n1=first(sel1)
    sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    ib01=np.array([Q[q]['prob_meas1_prep0'][0] for q in E]); ib10=np.array([Q[q]['prob_meas0_prep1'][0] for q in E]); ibre=np.array([Q[q]['readout_error'][0] for q in E])
    rod=pt(Q[E[0]]['readout_error'][1])
    res=[]
    if p0 is not None:
        m,ci,k=boot_median(p0-ib01); res.append(('P(read1|prep0)',n0,np.median(p0),np.median(ib01),m,ci,k))
    if p1 is not None:
        m,ci,k=boot_median((1-p1)-ib10); res.append(('P(read0|prep1)',n1,np.median(1-p1),np.median(ib10),m,ci,k))
    if p0 is not None and p1 is not None:
        m,ci,k=boot_median((p0+(1-p1))/2-ibre); res.append(('mean assign err',n0+n1,np.median((p0+1-p1)/2),np.median(ibre),m,ci,k))
    for r in res:
        print('%-26s %-13s %-17s shots/q %6d  ours %.4f IBM %.4f | med diff %+.4f [%+.4f,%+.4f] n=%d -> %-11s | job %s, IBM cal %s'%(label,chip,r[0],r[1],r[2],r[3],r[4],r[5][0],r[5][1],r[6],outcome(r[5]),str(sub)[5:16],str(rod)[5:16]))
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    J=json.load(open(R+f'control_run/job_{chip}.json')); E=J['E']
    run('control S-M / L(N=1,e=1)',chip,R+f'control_run/job_{chip}.json',R+f'control_run/raw_{chip}.npz',R+f'control_run/backend_properties_{chip}.json',
        lambda m:m['arm']=='S' and m['mode']=='M', lambda m:m['arm']=='L' and m.get('e_init')=='1', E)
    J=json.load(open(R+f'deciding_runs/job_excitation_{chip}.json')); E=J['info']['E']
    run('excitation M0/M1 (21Oct)',chip,R+f'deciding_runs/job_excitation_{chip}.json',R+f'deciding_runs/raw_excitation_{chip}.npz',R+f'deciding_runs/props_excitation_{chip}.json',
        lambda m:m['mode']=='M0' and m['N']>0, lambda m:m['mode']=='M1' and m['N']>0, E)
J=json.load(open(R+'excitation_kingston/job_excitation_ibm_kingston.json')); E=J['info']['E']
run('excitation M0/M1 (22Oct)','ibm_kingston',R+'excitation_kingston/job_excitation_ibm_kingston.json',R+'excitation_kingston/raw_excitation_ibm_kingston.npz',R+'excitation_kingston/props_excitation_ibm_kingston.json',
    lambda m:m['mode']=='M0' and m['N']>0, lambda m:m['mode']=='M1' and m['N']>0, E)
