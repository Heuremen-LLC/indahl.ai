"""analyze_lums.py -- reads raw_lums_J*.json (12 jobs in ORDER) and prints the readings of PLAN_LUMS.md.text through lums.analyse,
then the pre-registered decision rule for his question and R3 (his single-pair shift against today's job-to-job spread)."""
import sys, os, json, glob, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lums
from scipy.stats import chi2
H = lums.HERE; rng = np.random.default_rng(20261025)
labels = [f'J{k+1:02d}{a}' for k, a in enumerate(lums.ORDER)]
missing = [l for l in labels if not os.path.exists(f'{H}/raw_lums_{l}.json')]
if missing: print('INCOMPLETE: missing jobs', missing); sys.exit(1)
raw = {l: json.load(open(f'{H}/raw_lums_{l}.json')) for l in labels}
for n in (8, 10):
    d = lums.theirs(n); L = {j['tag']: j for j in d['ledger']['log']}; shots = L['bps1']['shots']; cv = lums.Cvar(lums.energies(d))
    N = np.stack([lums.counts_to_P(raw[l][str(n)], n) for l in labels]).astype(int)
    out = lums.analyse(N, lums.ORDER, shots, cv, rng, B=400, Bh=200)
    print(f'=== n={n} (rows {N.shape[1]}, shots {shots}, 12 jobs {"".join(lums.ORDER)})')
    for k in ('R1_drift_O_CM', 'R1b_T_CM'):
        r = out[k]; print(f'  {k}: job-mean SD {r["dSD"]:.4f}; CM {r["obs"]:.2e} vs shot-noise null median {r["null_med"]:.2e} (99% hi {r["null_hi"]:.2e}) -> {r["outcome"]};'
                          f' excess job SD {r["excess_sd"]:.4f} (upper {r["excess_sd_ub"]:.4f})')
    for k in ('R2_twirl_job_var_T_minus_O', 'R2b_twirl_rows_T_minus_O'):
        r = out[k]; print(f'  {k}: {r["obs"]:+.3e} permutation 99% [{r["perm_lo"]:+.3e}, {r["perm_hi"]:+.3e}] p_upper {r["p_upper"]:.3f} -> {r["outcome"]}')
    a, b_, c = out['R1_drift_O_CM']['outcome'], out['R1b_T_CM']['outcome'], out['R2_twirl_job_var_T_minus_O']['outcome']
    if 'CANNOT_TELL' in (a, b_): dec = 'CANNOT_TELL (halves disagree)'
    elif a == 'ABOVE': dec = 'DRIFT: job-to-job spread beyond shot noise WITHOUT twirling' + (' (twirl instance variance not separated, R2 ' + c + ')')
    elif b_ == 'ABOVE' and c != 'BELOW': dec = 'TWIRL-ONLY SPREAD: beyond shot noise only with twirling on (instance variance favoured over drift)'
    else: dec = 'NEITHER RESOLVED: both arms within shot noise; bounds above'
    print(f'  DECISION (pre-registered rule): {dec}')
    sT = out['dSD_T']; lo, hi = sT * np.sqrt(5 / chi2.ppf(0.975, 5)), sT * np.sqrt(5 / chi2.ppf(0.025, 5)); his = d['drift']['shift']
    o3 = 'ABOVE' if abs(his) > 2.576 * np.sqrt(2) * hi else 'CONSISTENT'
    print(f'  R3 his single-pair shift {his:+.4f} vs today T-arm job-mean SD {sT:.4f} [95% {lo:.4f}, {hi:.4f}] (pair SD = sqrt2 x): -> {o3}')
    print(f'  context: mean CVaR today T {out["mean_CVaR_T"]:+.4f}, O {out["mean_CVaR_O"]:+.4f}; his bps1 mean {np.mean(d["drift"]["first"]):+.4f} (different day/device state)')
