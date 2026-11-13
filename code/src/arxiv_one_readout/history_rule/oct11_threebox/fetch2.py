import os
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import qasm3
import re
for keyf,jids in [('.ibm_quantum_key_3',['db5tjs04qg6s73c3vn90','db5tkfimb58s738b0e5g','db5tknamb58s738b0edg']),('.ibm_quantum_key',['daqpd5rt55cs738s2ipg'])]:
    svc=QiskitRuntimeService(channel='ibm_quantum_platform',token=open(os.path.expanduser('~/bones-forge/'+keyf)).read().strip())
    for jid in jids:
        try: job=svc.job(jid)
        except Exception as e: print(jid,'ERR',str(e)[:80]); continue
        c=job.inputs['pubs'][0][0]; q=qasm3.dumps(c); open(f'{jid}_0.qasm','w').write(q)
        a=sorted(set(re.findall(r'rz\(([0-9.]+)\)',q))); print(jid,job.backend().name,c.name,a)
