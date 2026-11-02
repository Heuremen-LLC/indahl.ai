"""analyze_kitcheck.py CHIP -- the readings of PLAN_KITCHECK.md.text from the saved raw arrays. Writes results_kitcheck_CHIP.text."""
import json, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kitcheck as KC
CHIP = sys.argv[1]; rec = json.load(open(f'{HERE}/job_kitcheck_{CHIP}.json')); S = rec['S']
def keyof(s): p = s.split('|'); return tuple(int(x) if x.isdigit() else x for x in p)
a1 = {keyof(k): v for k, v in np.load(f'{HERE}/raw_job1_{CHIP}.npz').items()}; a2 = {keyof(k): v for k, v in np.load(f'{HERE}/raw_job2_{CHIP}.npz').items()}
kit = {k[1:]: v for k, v in a1.items() if k[0] == 'KIT'}; cal = {k: v for k, v in a1.items() if k[0] == 'CAL'}
kt = KC.kit_table(kit, S); st = KC.study_table(CHIP, cal, S)
R1 = KC.r1(kt, st, S); R2 = KC.r2(a2, S, kt)
old = json.load(open(os.path.join(HERE, '..', 'keystone', 'fresh_kicks_' + CHIP + '.json')))['kicks']
drift = KC.boot_median([kt[q]['deg_per_readout'] - old[str(q)]['k4'] for q in S])
L = [f'Darkwave Correction Kit, known-good run on {CHIP} (PLAN_KITCHECK.md.text). Jobs: ' + ', '.join(f"{j['label']} {j['job_id']} {j.get('usage', {}).get('qpu_charge_time_seconds')} s" for j in rec['jobs']),
     f"Kit table read two ways (packed arrays and the kit's own get_counts path) agree: {rec.get('kit_paths_agree')}",
     f"Kit turn per readout, median over {len(S)} targets: {np.median([kt[q]['deg_per_readout'] for q in S]):+.3f} deg. Study code k4 median: {np.median([st[q]['k4'] for q in S]):+.3f} deg.",
     f"R1 kit minus study (same job), median {R1['median']:+.3f} deg/readout [{R1['band'][0]:+.3f}, {R1['band'][1]:+.3f}] -> {R1['outcome']} (margin +-{KC.MARGIN_R1}). Share of targets differing by more than 1 deg: {R1['share_abs_over_1deg']:.3f}. Correlation {R1['corr']:+.3f}.",
     f"R2a residual turn after the kit's correction, median {R2['residual']['median']:+.3f} deg/readout [{R2['residual']['band'][0]:+.3f}, {R2['residual']['band'][1]:+.3f}] -> {R2['residual']['outcome']} (margin +-{KC.MARGIN_R2}).",
     f"R2b share given back, median {R2['share_given_back']['median']:+.3f} [{R2['share_given_back']['band'][0]:+.3f}, {R2['share_given_back']['band'][1]:+.3f}] over {R2['share_given_back']['n']} targets -> {R2['share_given_back']['outcome']} against 0.5. Uncorrected turn in job 2, median {R2['kick_job2']['median']:+.3f} deg/readout.",
     f"Reported, not in the rule: kit table minus the study's 31 Oct table (k4), median {drift[0]:+.3f} [{drift[1]:+.3f}, {drift[2]:+.3f}] deg/readout over {drift[3]} targets.",
     'Bands: 95 % bootstrap over targets, 2,000 resamples, seed 41.']
open(f'{HERE}/results_kitcheck_{CHIP}.text', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
json.dump(dict(R1=R1, R2={k: v for k, v in R2.items() if k != 'per_qubit'}, drift_vs_31oct=drift, kit_table=kt, study_table=st, per_qubit=R2['per_qubit']), open(f'{HERE}/results_kitcheck_{CHIP}.json', 'w'), indent=1, default=float)
