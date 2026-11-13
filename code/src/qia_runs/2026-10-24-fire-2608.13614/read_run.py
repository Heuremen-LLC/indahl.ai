"""read_run.py -- driver only: applies the committed analyze.read() (hash in CODE_2608.13614.sha256.text) to raw_counts.json."""
import json, os, sys, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from sis_qubo import build, decode
from analyze import read, combine
kg = json.load(open(f'{H}/known_good.json')); raw = json.load(open(f'{H}/raw_counts.json')); out = {}
for v in 'PS':
    m = build(v); r = read(raw[v], m['E'], kg[v]['ideal_low10_fraction'], boot=4000)
    r['best_sampled_decoded'] = decode(r['best_sampled_state'], m['fine']); out[v] = r
out['combined_R1'] = combine(out['P']['R1'], out['S']['R1']); out['combined_R2'] = combine(out['P']['R2'], out['S']['R2'])
json.dump(out, open(f'{H}/readings.json', 'w'), indent=1, default=str)
for v in 'PS':
    r = out[v]; print(f"{v}: n {r['n']}, k {r['k_low10']}, frac {r['frac']:.5f} CP [{r['ci'][0]:.5f}, {r['ci'][1]:.5f}] vs null {r['null']:.5f} -> R1 {r['R1']}; ratio [{r['ratio_to_null'][0]:.2f}, {r['ratio_to_null'][1]:.2f}]; "
          f"excess share {r['excess_share'][1]:+.2f} [{r['excess_share'][0]:+.2f}, {r['excess_share'][2]:+.2f}]; marginal null {r['p_marginal_null']:.5f} -> R2 {r['R2']}; "
          f"meanE {r['mean_E']:.4f} [{r['mean_E_ci'][0]:.4f}, {r['mean_E_ci'][1]:.4f}] vs uniform {r['uniform_mean_E']:.4f} -> {r['R3_meanE']}; best sampled rank {r['best_sampled_rank']} {r['best_sampled_decoded']}; optimum sampled {r['optimum_sampled']}; unique {r['n_unique']}; marginals P(1) {[round(x,3) for x in r['marginals']]}")
print('combined R1', out['combined_R1'], 'R2', out['combined_R2'])
