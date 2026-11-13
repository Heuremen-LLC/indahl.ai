"""analyze_abramson.py -- reads raw_abramson_{A1,B1,B2,A2}.npz (written by fire_abramson.py), prints R1 (B-A, ABBA) and R2 (drift A1 vs A2) with four outcomes
against the shot-noise null (abramson.py). Usage: analyze_abramson.py [B=100]"""
import sys, os, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from abramson import *; from multiprocessing import Pool
def getjob(l):
    z = np.load(f'{H}/raw_abramson_{l}.npz'); key = lambda i: next(k for k in z.files if k.startswith(f'{i}/') and (k.endswith('m_iq') or k.endswith('/m')))
    return z[key(0)], z[key(1)], np.concatenate([z[key(i)] for i in (2, 3, 4)])
if __name__ == '__main__':
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 100; cz = json.load(open(f'{H}/known_good_abramson.json'))['czs']
    sym = {l: to_symbols(*getjob(l)) for l in LABELS}
    with Pool(14) as pool: r = readings(sym, cz, B=B, seed=1, pool=pool)
    print(json.dumps(r, indent=1)); json.dump(r, open(f'{H}/readings_abramson.json', 'w'), indent=1)
