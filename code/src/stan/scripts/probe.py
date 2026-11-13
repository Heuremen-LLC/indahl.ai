import time,sys
from common import *
dummy="A dummy title\n\nWe report a quantum algorithm achieving a 10x speedup on a 20-qubit device, with a best-case fidelity of 0.97 over our runs, compared against a baseline we built from the vendor's published error rates."
host,m=sys.argv[1],sys.argv[2]
t=time.time()
try: o=ollama(host,m,teacher_prompt(dummy),t=900); print(m,host[-6:],round(time.time()-t),'s',o[:200].replace('\n',' '),flush=True)
except Exception as e: print(m,host,'ERR',e,flush=True)
