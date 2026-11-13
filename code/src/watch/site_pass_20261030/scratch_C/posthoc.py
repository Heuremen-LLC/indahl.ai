import re, os, sys, glob
sys.path.insert(0, '.')
import parse as P
import runnums as R   # reuse MAP
Q = os.path.expanduser('~/bones-forge/qia_runs/')
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
NUM = re.compile(r'(?<![\w.])[-+−]?\d+\.\d{2,}(?:[eE][-+]?\d+)?')
trig = re.compile(r'defined after|post-hoc|posthoc|post hoc|looked at after|after the data|ADDENDUM \d+ RESULT|noticed after', re.I)
for n, folders in R.MAP.items():
    ptxt = P.text(pages[n]['sections']['Measured or recounted'] + ' ' + pages[n]['sections']['QIA Calibration'])
    pnums = set(m.group(0).replace('−','-').lstrip('+') for m in NUM.finditer(ptxt))
    hits = []
    for d in folders:
        for root, dirs, files in os.walk(Q + d):
            for f in files:
                if not (f.startswith(('RESULT', 'README', 'results_', 'posthoc')) and f.endswith(('.md', '.text', '.txt'))): continue
                lines = open(os.path.join(root, f), errors='replace').read().split('\n')
                inph = False
                for i, ln in enumerate(lines):
                    if ln.startswith('#') : inph = bool(trig.search(ln))
                    if trig.search(ln) or inph:
                        # check page numbers in this line (+ next 2)
                        blob = ' '.join(lines[i:i+3])
                        for m in NUM.finditer(blob):
                            v = m.group(0).replace('−','-').lstrip('+')
                            if v in pnums: hits.append((f, v, ln[:140]))
    if hits:
        print(n, folders[0])
        seen = set()
        for f, v, ln in hits:
            if (v) in seen: continue
            seen.add(v); print('   page number', v, 'appears in post-hoc/addendum block of', f, '::', ln)
