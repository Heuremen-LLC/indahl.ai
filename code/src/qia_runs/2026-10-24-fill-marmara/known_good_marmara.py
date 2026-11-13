"""known_good_marmara.py DIR -- their Zenodo n=6 counts (raw and their mitigated) through OUR mi(): shortfalls must be 1.279 raw and
0.701 mitigated (to 0.001). Also: our tensor-product mitigation from THEIR stored record (prob_meas0_prep1/prob_meas1_prep0), reported."""
import sys, os, json, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import marmara as M
d = sys.argv[1]; raw = json.load(open(f'{d}/fez_counts_raw_n_6.json')); mit = json.load(open(f'{d}/fez_counts_mitigated_n_6.json'))
rec = json.load(open(f'{d}/fez_readout_data_n_6.json'))
sr = 6 - M.mi(raw); sm = 6 - M.mi(mit)
e0 = np.array([rec[str(q)]['prob_meas1_prep0'] for q in range(6)]) if '0' in rec else None
if e0 is None:
    k = list(rec)[0]; print('record layout:', type(rec), k)
e1 = np.array([rec[str(q)]['prob_meas0_prep1'] for q in range(6)])
ours = 6 - M.mi({m: M.mitigate(c, e0, e1) for m, c in raw.items()})
succ = np.mean([raw[m].get(m, 0) / sum(raw[m].values()) for m in raw])
print(f'KNOWN-GOOD their n=6 counts: raw shortfall {sr:.3f}, their mitigated {sm:.3f}; our mitigation from their record {ours:.3f}; raw mean success {succ:.4f}')
ok = abs(sr - 1.279) < 1e-3 and abs(sm - 0.701) < 1e-3; print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
