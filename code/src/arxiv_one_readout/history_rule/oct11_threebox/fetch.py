import os,json,sys
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import qasm3
key=open(os.path.expanduser('~/bones-forge/.ibm_quantum_key_3')).read().strip()
svc=QiskitRuntimeService(channel='ibm_quantum_platform',token=key)
for jid in ['db5ti2svf2bc73d0ddug','db5ti6g4qg6s73c3vldg','db5tiasvf2bc73d0de8g']:
    try: job=svc.job(jid)
    except Exception as e: print(jid,'ERR',str(e)[:100]); continue
    inp=job.inputs
    pubs=inp.get('pubs',[])
    for k,p in enumerate(pubs):
        c=p[0] if isinstance(p,(list,tuple)) else p
        open(f'{jid}_{k}.qasm','w').write(qasm3.dumps(c))
        ops=c.count_ops(); used=sorted({c.find_bit(q).index for inst in c.data for q in inst.qubits})
        print(jid,k,c.name,dict(ops),'qubits used',len(used),used[:12],'clbits',c.num_clbits)
