from common import *
import glob
jobs=[]
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    jobs+= [('control(21Oct)',R+f'control_run/backend_properties_{chip}.json',R+f'control_run/job_{chip}.json'),
            ('iq(21Oct)',R+f'control_run/iq_backend_properties_{chip}.json',R+f'control_run/iqjob_{chip}.json'),
            ('gates(21Oct)',R+f'deciding_runs/props_gates_{chip}.json',R+f'deciding_runs/job_gates_{chip}.json'),
            ('neighbour(21Oct)',R+f'deciding_runs/props_neighbour_{chip}.json',R+f'deciding_runs/job_neighbour_{chip}.json'),
            ('flip(22Oct)',R+f'flipcheck_run/flip_backend_properties_{chip}.json',R+f'flipcheck_run/flipjob_{chip}.json')]
jobs.append(('gates(21Oct)',R+'deciding_runs/props_gates_ibm_phoenix.json',R+'deciding_runs/job_gates_ibm_phoenix.json'))
print('%-17s %-14s %-19s %-19s | T1 age h med/max | T1 n>24h n>7d | T2 age med/max | RO age med/max | init_error present | RL values'%('job','chip','job submitted','props last_update'))
for lab,pp,jp in jobs:
    try: P=json.load(open(pp)); J=json.load(open(jp))
    except Exception as e: print(lab,pp,'ERR',e); continue
    sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    Q=qprops(P); 
    def ages(name):
        a=[(sub-pt(q[name][1])).total_seconds()/3600 for q in Q if name in q and q[name][1]]
        return np.array(a)
    a1=ages('T1'); a2=ages('T2'); ar=ages('readout_error')
    rl=sorted({q['readout_length'][0] for q in Q if 'readout_length' in q})
    ie=sum('init_error' in q for q in Q)
    print('%-17s %-14s %-19s %-19s | %5.1f/%6.1f | %3d %3d (of %d) | %5.1f/%6.1f | %5.1f/%5.1f | %d of %d | %s'%(lab,P['backend_name'],str(sub)[:19],P['last_update_date'][:19],np.median(a1),a1.max(),(a1>24).sum(),(a1>168).sum(),len(a1),np.median(a2),a2.max(),np.median(ar),ar.max(),ie,len(Q),rl))
