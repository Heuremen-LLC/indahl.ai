"""qfim.py -- free calibration run for QFIM-bench (Thinakaran P., Parthiban K., Vellore Institute of Technology, India; ibm_marrakesh). Analysis only (fire is fire_qfim.py).
Their own words (review/OPERATING_POINT_ADDENDUM.md): the simulator is "a single calibration snapshot of a device that drifts"; review/CLAIMS_MAP.md lists
"Anything about day-to-day drift (all runs in one sitting, deviation D1)" as not claimable. All five of their jobs carry ONE calibration stamp (2026-10-08 17:49:07+05:30),
so the question is drift between JOBS minutes apart under one stamp, not day to day.
Design: their Tier A job (8 circuits, 8192 shots, logged 20.0 s) in two orders. A = their day-1 order verbatim. B = A reversed. Jobs in ABBA order: A1 B1 B2 A2.
Per circuit c: p = key-outcome probability (marked state '011' for ladder r0..r4, '000' for echo and readout zeros, '111' for readout ones), their definition.
Under ABBA three contrasts of the four jobs (t = 1..4) separate what moves:
  JOB-SD  sd over the 4 jobs (ddof 1), their statistic (their 5-job sd) on 4 jobs.
  STEP    (p3+p4-p1-p2)/2    change between the first and second half of the sitting; cancels the A/B order effect (each half holds one A and one B). Linear drift b per job gives 2b.
  SLOT    (p1+p4-p2-p3)/2    A minus B; cancels linear drift and a midpoint step. Non-zero only for an effect of circuit position/order inside the job.
READINGS (fixed in advance; four outcomes each: ABOVE / BELOW / CONSISTENT / CANNOT_TELL; 95 %; shot-noise null = same statistic on 2000 binomial redraws of every
job and circuit at the circuit's POOLED probability over the 4 jobs; the statistic's own interval = redraw at each job's own probability, re-centred on the value):
  R0 KNOWN-GOOD   their raw counts through this file must give their eight published means and sds (analysis.json) to the printed precision (6 decimals).
  R1 JOB-SD       pooled: RMS over the 8 circuits of the 4-job sd.   R1c per circuit (reported, not scored in the synth: 8 readings carry 5 % each).
  R2 STEP         pooled: RMS over the 8 circuits of STEP.            R3 SLOT   pooled: RMS over the 8 circuits of SLOT.
  R4 SINCE        pooled RMS over circuits of (mean of our 4 jobs - their published 5-job mean). Different calibration stamp (theirs 8 Oct): NOT a drift reading.
  SHARE           R1 / THEIR RMS published sd (0.0051), next to its shot-noise floor.
  RULE            value above the null's 97.5 % -> ABOVE, below its 2.5 % -> BELOW, else CONSISTENT (a bound, never "the same").
  RESOLVABILITY   fixed in advance from THEIR published sds (analysis.json), never from ours: a pooled reading is CANNOT_TELL if its null half-width exceeds THEIR RMS
                  published sd; R1c is CANNOT_TELL if its null half-width exceeds THEIR published sd for that circuit.
A reading is the size of the between-job movement on this chip, today, for their circuits. It is not a finding about their 8 Oct jobs."""
import json, sys, numpy as np
HERE = __file__.rsplit('/', 1)[0] or '.'
CIRCS = ['ladder_n3_M1_r0', 'ladder_n3_M1_r1', 'ladder_n3_M1_r2', 'ladder_n3_M1_r3', 'ladder_n3_M1_r4', 'echo_n3_M1_r2', 'readout_n3_zeros', 'readout_n3_ones']
KEY = {'echo_n3_M1_r2': '000', 'readout_n3_zeros': '000', 'readout_n3_ones': '111'}
key = lambda c: KEY.get(c, '011')
SHOTS = 8192
T975_4DOF = 2.7764451051977987          # scipy t.ppf(0.975, 4), their 5-repeat interval
ORDER = ['A1', 'B1', 'B2', 'A2']                         # ABBA
A_ORDER = ['ladder_n3_M1_r2', 'ladder_n3_M1_r1', 'readout_n3_zeros', 'ladder_n3_M1_r4', 'echo_n3_M1_r2', 'ladder_n3_M1_r3', 'readout_n3_ones', 'ladder_n3_M1_r0']   # their day 1
B_ORDER = A_ORDER[::-1]
assert sorted(A_ORDER) == sorted(CIRCS)

def load_theirs():
    days = [json.load(open(f'{HERE}/theirs/raw/day{i}.json')) for i in range(1, 6)]
    assert days[0]['order'] == A_ORDER
    K = np.array([[d['counts'][c].get(key(c), 0) for c in CIRCS] for d in days])          # (5 days, 8)
    N = np.array([[sum(d['counts'][c].values()) for c in CIRCS] for d in days])
    assert (N == SHOTS).all()
    pub = {r['id']: r for r in json.load(open(f'{HERE}/theirs/raw/analysis.json'))['rows']}
    return K, pub
def their_known_good(K, pub):
    p = K / SHOTS; m = p.mean(axis=0); sd = p.std(axis=0, ddof=1); h = T975_4DOF * sd / np.sqrt(5)
    dm = max(abs(m[i] - pub[c]['mean']) for i, c in enumerate(CIRCS)); ds = max(abs(sd[i] - pub[c]['sd']) for i, c in enumerate(CIRCS))
    dci = max(max(abs(m[i] - h[i] - pub[c]['t_ci95'][0]), abs(m[i] + h[i] - pub[c]['t_ci95'][1])) for i, c in enumerate(CIRCS))
    same6 = sum(f'{m[i]:.6f}' == f'{pub[c]["mean"]:.6f}' for i, c in enumerate(CIRCS)), sum(f'{sd[i]:.6f}' == f'{pub[c]["sd"]:.6f}' for i, c in enumerate(CIRCS))
    ok = same6 == (8, 8) and dm < 5e-7 and ds < 5e-7 and dci < 5e-6
    return m, sd, same6, dm, ds, dci, ok
def published_scale(pub):
    s = np.array([pub[c]['sd'] for c in CIRCS]); return s, float(np.sqrt(np.mean(s ** 2)))

# ---- statistics on P[..., 4 jobs, 8 circuits] ------------------------------------------------------------------------------------------
def stats(P, pubmean=None):
    sd = P.std(axis=-2, ddof=1)
    step = (P[..., 2, :] + P[..., 3, :] - P[..., 0, :] - P[..., 1, :]) / 2
    slot = (P[..., 0, :] + P[..., 3, :] - P[..., 1, :] - P[..., 2, :]) / 2
    rms = lambda x: np.sqrt(np.mean(x ** 2, axis=-1))
    out = {'R1 JOB-SD (RMS)': rms(sd), 'R2 STEP (RMS)': rms(step), 'R3 SLOT (RMS)': rms(slot)}
    if pubmean is not None: out['R4 SINCE (RMS, not drift)'] = rms(P.mean(axis=-2) - pubmean)
    for i, c in enumerate(CIRCS): out[f'R1c {c}'] = sd[..., i]
    return out
def draw(p, B, rng, shots=SHOTS):
    """p (4,8) probabilities -> (B,4,8) redrawn proportions."""
    return rng.binomial(shots, np.broadcast_to(p, (B,) + p.shape)) / shots
def four(v, nlo, nhi, resolvable):
    if not resolvable: return 'CANNOT_TELL'
    return 'ABOVE' if v > nhi else 'BELOW' if v < nlo else 'CONSISTENT'
def analyse(P, pub, theirs_p, rng, B=2000, shots=SHOTS):
    """P (4,8): our four jobs' key probabilities in ORDER. Returns (lines, results dict name -> (v, lo, hi, nlo, nhi, outcome))."""
    s_c, s_rms = published_scale(pub); pm = theirs_p.mean(axis=0)
    d = stats(P, pm); bs = stats(draw(P, B, rng, shots), pm); pbar = P.mean(axis=0, keepdims=True).repeat(4, axis=0)
    ns = stats(draw(pbar, B, rng, shots), pm)
    # R4 null: ours and theirs both from the pooled probability of all nine jobs
    p9 = (P.sum(axis=0) + theirs_p.sum(axis=0)) / 9
    n4 = np.sqrt(np.mean((rng.binomial(shots * 4, p9, size=(B, 8)) / (shots * 4) - rng.binomial(SHOTS * 5, p9, size=(B, 8)) / (SHOTS * 5)) ** 2, axis=-1))
    ns['R4 SINCE (RMS, not drift)'] = n4
    out, lines = {}, []
    for k in d:
        v = float(d[k]); b = bs[k] + (v - np.median(bs[k])) if k in bs else None
        lo, hi = np.percentile(b, [2.5, 97.5]) if b is not None else (np.nan, np.nan); nlo, nhi = np.percentile(ns[k], [0.5, 99.5] if k.startswith('R1') else [2.5, 97.5])  # ADDENDUM 1: R1 null band 0.5-99.5 (synth NEITHER false rate was 6/40)
        scale = s_c[CIRCS.index(k[4:])] if k.startswith('R1c') else s_rms
        res = (nhi - nlo) / 2 < scale; out[k] = (v, lo, hi, nlo, nhi, four(v, nlo, nhi, res))
        lines.append(f'{k:42s} = {v:.5f} [{lo:.5f}, {hi:.5f}] shot-null [{nlo:.5f}, {nhi:.5f}] their published {scale:.5f} -> {out[k][5]}')
    fl = float(np.median(ns['R1 JOB-SD (RMS)'])) / s_rms
    lines.append(f'SHARE  R1 / their RMS published sd {s_rms:.5f} = {d["R1 JOB-SD (RMS)"] / s_rms:.3f}  (shot-noise floor {fl:.3f})')
    lines.append('per-circuit job-sd / binomial sd at our pooled p: ' + ', '.join(f'{c.split("_n3_")[-1] if "_n3_" in c else c} {d["R1c " + c] / np.sqrt(pbar[0, i] * (1 - pbar[0, i]) / shots):.2f}' for i, c in enumerate(CIRCS)))
    return lines, out
if __name__ == '__main__':
    K, pub = load_theirs(); m, sd, same6, dm, ds, dci, ok = their_known_good(K, pub)
    print(f'R0 KNOWN-GOOD (their raw counts, 5 jobs x 8 circuits): means equal to 6 decimals {same6[0]}/8, sds equal to 6 decimals {same6[1]}/8, '
          f'max |mean diff| {dm:.1e}, max |sd diff| {ds:.1e}, max |t95 CI end diff| {dci:.1e} (e.g. echo {m[CIRCS.index("echo_n3_M1_r2")]:.6f} sd {sd[CIRCS.index("echo_n3_M1_r2")]:.6f}, published {pub["echo_n3_M1_r2"]["mean"]:.6f} {pub["echo_n3_M1_r2"]["sd"]:.6f}) -> {"PASS" if ok else "FAIL"}')
    if len(sys.argv) > 1 and sys.argv[1] == '--real':
        rec = json.load(open(f'{HERE}/job_qfim.json')); rng = np.random.default_rng(24); P = {}
        for j in rec['jobs']:
            raw = json.load(open(f'{HERE}/raw_qfim_{j["label"]}.json')); P[j['label']] = np.array([raw[c].get(key(c), 0) / sum(raw[c].values()) for c in CIRCS])
        miss = [j for j in ORDER if j not in P]
        if miss: print('INCOMPLETE: missing jobs', miss); sys.exit(1)
        print('\n'.join(analyse(np.array([P[j] for j in ORDER]), pub, K / SHOTS, rng)[0]))
