import re, os, sys, glob, json, html, collections
sys.path.insert(0, '.')
import parse as P
Q = os.path.expanduser('~/bones-forge/qia_runs/')
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
MAP = {
 '2502.01824': ['2026-10-24-fill-ufsm', '2026-10-29-gift-ufsm'],
 '2508.16895': ['2026-10-24-fire-2508.16895'],
 '2509.04761': ['2026-10-24-fire-2509.04761'],
 '2510.17692': ['2026-10-25-fire-t10'],
 '2512.04016': ['2026-10-24-fill-tara'],
 '2512.14280': ['2026-10-24-fill-marmara'],
 '2603.13536': ['2026-10-24-fire-2603.13536', '2026-10-30-gift-kobe'],
 '2603.13949': ['2026-10-25-fire-ffzne'],
 '2605.08251': ['2026-10-24-fill-lima', '2026-10-29-gift-scavino'],
 '2605.30676': ['2026-10-24-fill-cauca', '2026-10-30-gift-cauca'],
 '2607.20377': ['2026-10-24-fill-kyiv'],
 '2608.04486': ['2026-10-24-fire-2608.04486'],
 '2608.13614': ['2026-10-24-fire-2608.13614'],
 '2609.13669': ['2026-10-24-fill-lums', '2026-10-29-gift-lums', '2026-10-29-repeat-lums'],
 '2609.15411': ['2026-10-24-fill-zhukov', '2026-10-29-repeat-zhukov'],
 '2609.33255': ['2026-10-24-fill-usp'],
 '2610.09062': ['2026-10-24-fill-geopump', '2026-10-30-gift-geopump'],
 '2610.20855': ['2026-10-24-fill-qusoft'],
 '2610.28705': ['2026-10-24-fill-kumar', '2026-10-24-fill-kumar-kingston'],
 'zenodo-20538557': ['2026-10-25-fire-perezghz'],
 'zenodo-21206538': ['2026-10-25-fire-pavani'],
 'zenodo-21938548': ['2026-10-25-fire-n47'],
 'zenodo-22009070': ['2026-10-25-fire-lasky'],
 'zenodo-22737706': ['2026-10-25-fire-ocean78', '2026-10-25-fire-ocean'],
 'zenodo-22770646': ['2026-10-25-fire-shcherbak', '2026-10-25-fire-shch-layout'],
 'zenodo-23122648': ['2026-10-25-fire-ktn'],
 'zenodo-23123273': ['2026-10-25-fire-reddy'],
 'zenodo-23382139': ['2026-10-25-fire-raghu'],
 'zenodo-23396363': ['2026-10-24-fill-qfim'],
 'zenodo-23634581': ['2026-10-25-fire-tehran'],
}
NUM = re.compile(r'(?<![\w.])[-+−]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][-+]?\d+)?')
def nums(txt):
    out = []
    for m in NUM.finditer(txt):
        s = m.group(0).replace('−', '-').replace(',', '')
        try: out.append(float(s))
        except: pass
    return out
def folder_text(d):
    txt = ''
    for root, dirs, files in os.walk(Q + d):
        if '__pycache__' in root or '/src' in root: continue
        for f in files:
            if f.endswith(('.py', '.pyc', '.qpy', '.sha256.text')): continue
            p = os.path.join(root, f)
            if os.path.getsize(p) > 5_000_000: continue
            if f.startswith(('raw_', 'circuits_', 'props_')): continue
            if not f.endswith(('.text', '.md', '.txt', '.json', '.log', '.csv')): continue
            try: txt += '\n' + open(p, errors='replace').read()
            except: pass
    return txt
def decs(tok):
    t = tok.replace('−', '-').replace(',', '')
    if 'e' in t.lower():
        mant = re.split('[eE]', t)[0]
        return len(mant.split('.')[1]) if '.' in mant else 0, 'sci'
    return (len(t.split('.')[1]) if '.' in t else 0), 'dec'
res = {}
for n, folders in MAP.items():
    p = pages[n]; s = p['sections']
    mtxt = P.text(s['Measured or recounted'] + ' ' + s['QIA Calibration'])
    # keep only sentences mentioning Our/our (our run), and cal text
    ftxt = '\n'.join(folder_text(f) for f in folders)
    fn = nums(ftxt)
    fset = set(fn)
    miss = []
    for m in NUM.finditer(mtxt):
        tok = m.group(0)
        v = float(tok.replace('−', '-').replace(',', '').replace('+', ''))
        d, kind = decs(tok)
        if d == 0 and abs(v) < 100: continue   # small ints skip
        if re.match(r'^(2026|2025|2024)$', tok): continue
        ok = False
        tol = 0.5 * 10 ** (-d) * 1.0001 if kind == 'dec' else abs(v) * 0.5 * 10 ** (-d) / (abs(float(re.split("[eE]", tok.replace(",", ""))[0])) or 1) * 1.01
        for x in fn:
            if abs(x - v) <= tol + 1e-12 or abs(abs(x) - abs(v)) <= tol + 1e-12: ok = True; break
            if x != 0 and abs(100 * x - v) <= tol + 1e-9 and d <= 2: ok = True; break
        if not ok: miss.append(tok)
    res[n] = miss
    print(n, folders[0], 'files-nums', len(fn), 'unmatched:', miss)
