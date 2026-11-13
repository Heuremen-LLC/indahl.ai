import sys, json, time, subprocess, warnings; warnings.filterwarnings('ignore')
sys.argv = [sys.argv[0], 'ibm_kingston']
import run_len as R
s = R.service(); left = {c: json.load(open(f'job_{c}.json'))['job_id'] for c in ('ibm_fez',)}
t0 = time.time()
while left and time.time() - t0 < 14400:
    for c, j in list(left.items()):
        st = str(s.job(j).status())
        if 'DONE' in st:
            subprocess.run([R.sys.executable, 'fetch_len.py', c]); print('fetched', c, flush=True); left.pop(c)
        elif any(x in st for x in ('ERROR', 'CANCELLED')): print(c, st, flush=True); left.pop(c)
    time.sleep(30)
print('still waiting:', left)
