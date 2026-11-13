import sys,json,glob
sys.path.insert(0,'.')
import numpy as np, callib_copy as C
tot={}
for f in sorted(glob.glob('cal/*.json')):
    d=json.load(open(f)); q=d['qubits']; raw=d['raw']
    stated={k:dict(p10=x['ibm_p10'],p01=x['ibm_p01'],t1=x['ibm_t1']) for k,x in enumerate(q)}
    rows,kg=C.analyse(np.array(raw['c0_ones']),np.array(raw['c1_zeros']),np.array(raw['t1_ones']),d['shots']['readout'],d['shots']['t1'],stated)
    diffs=0; cnt={n:{o:0 for o in ('ABOVE','BELOW','CONSISTENT','CANNOT_TELL')} for n in ('p10','p01','t1')}
    for k,(a,b) in enumerate(zip(q,rows)):
        for n in ('p10','p01','t1'):
            cnt[n][b[n+'_outcome']]+=1
            if a[n+'_outcome']!=b[n+'_outcome'] or a[n+'_ci']!=b[n+'_ci'] or a[n]!=b[n]:
                diffs+=1
                if diffs<4: print('  DIFF',d['processor'],a['qubit'],n,a[n],a[n+'_ci'],a[n+'_outcome'],'| re',b[n],b[n+'_ci'],b[n+'_outcome'])
    print(d['processor'],d['job_id'],'qubits',len(q),'diffs',diffs,'known_good file',d.get('known_good'),'re',kg['known_good'],kg['median_readout_measured_over_stated'],kg['median_t1_measured_over_stated'],'file',d.get('median_readout_measured_over_stated'),d.get('median_t1_measured_over_stated'))
    tot[d['processor']]=cnt
json.dump(tot,open('recount_counts.json','w'))
cal=json.load(open('qia_cal.json'))
for k,p in cal['processors'].items():
    print(k,'cal.json counts == recomputed:',p['counts']==tot[k])
