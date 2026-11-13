import sys,json
sys.path.insert(0,'.')
import numpy as np, callib_copy as C
cal=json.load(open('qia_cal.json'))
for k in ('ibm_fez','ibm_marrakesh','ibm_aachen'):
    p=cal['processors'][k]; d=json.load(open('cal/%s.json'%p['job_id']))
    raw=d['raw']; c0=np.array(raw['c0_ones']); c1z=np.array(raw['c1_zeros'])
    for name,cnt,key in (('p10',c0,'ibm_p10'),('p01',c1z,'ibm_p01')):
        pp,lo,hi=C.wilson(cnt,1000)
        res={}
        for n in (4096,1024):
            out={'ABOVE':0,'BELOW':0,'CONSISTENT':0,'CANNOT_TELL':0}
            for i,q in enumerate(d['qubits']):
                out[C.side_counts(q[key],lo[i],hi[i],n_ibm=n)]+=1
            res[n]=out
        print(k,name,'n_ibm=4096',res[4096],' n_ibm=1024',res[1024])
