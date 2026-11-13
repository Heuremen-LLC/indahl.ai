"""lasky.py -- free calibration run (Kumar) for Zenodo 10.5281/zenodo.22009070 (Lasky Design): drift calibration of their gain.
Their claim: on fez, 3q GHZ + 1000 dt delay: baseline 904/1024 vs optimized 943/1024 (+3.81 pp); 5q GHZ + 1200 dt: 820 vs 855 (+3.42 pp).
Baseline and optimized ran as SEPARATE jobs. Our finding: job-to-job drift on fez exceeds shot noise within minutes. This run measures the job-to-job
spread of THEIR BASELINE circuit against itself (4 back-to-back jobs, 2 copies per job, 1024 shots), and prices their gain against it."""
import numpy as np
SHOTS = 1024; GAIN = {'GHZ3': 0.0381, 'GHZ5': 0.0342}; BASE = {'GHZ3': 904 / 1024, 'GHZ5': 820 / 1024}
LAYOUT = {'GHZ3': [0, 1, 2], 'GHZ5': [0, 1, 2, 3, 4]}; DELAY = {'GHZ3': 1000, 'GHZ5': 1200}
def circuit(kind):
    from qiskit import QuantumCircuit
    n = len(LAYOUT[kind]); qc = QuantumCircuit(n, n); qc.h(0)
    for i in range(n - 1): qc.cx(i, i + 1)
    for i in range(n): qc.delay(DELAY[kind], i, unit='dt')
    qc.measure(range(n), range(n)); return qc
def succ(c, n):
    tot = sum(c.values()); return (c.get('0' * n, 0) + c.get('1' * n, 0)) / tot
def analyse(jobs):
    """jobs: list of {kind: [counts copy1, counts copy2]}"""
    out = {}
    for kind in ('GHZ3', 'GHZ5'):
        n = len(LAYOUT[kind]); P = np.array([[succ(c, n) for c in j[kind]] for j in jobs])  # jobs x 2
        pj = P.mean(1); pbar = pj.mean(); sb_job = np.sqrt(pbar * (1 - pbar) / (2 * SHOTS))       # binomial sd of a job mean (2 copies)
        sd_between = float(pj.std(ddof=1)); excess = float(np.sqrt(max(0.0, sd_between ** 2 - sb_job ** 2)))
        within = P[:, 0] - P[:, 1]; sb_copy = np.sqrt(2 * pbar * (1 - pbar) / SHOTS)
        kg = bool(np.all(np.abs(within) < 2.58 * sb_copy))
        # their gain between two single-copy jobs: sd of a difference of two single-copy jobs = sqrt(2 (sb1^2 + excess^2))
        sb1 = np.sqrt(pbar * (1 - pbar) / SHOTS); sd_diff = float(np.sqrt(2 * (sb1 ** 2 + excess ** 2))); z = GAIN[kind] / sd_diff
        oc = 'ABOVE' if z > 1.96 else 'CONSISTENT'   # ABOVE: their gain exceeds what two baseline jobs differ by; CONSISTENT: a bound, gain not separable
        out[kind] = dict(job_means=[float(x) for x in pj], mean=float(pbar), their_baseline=BASE[kind], between_job_sd=sd_between, binomial_sd_job=float(sb_job),
                         drift_excess_sd=excess, max_job_range=float(pj.max() - pj.min()), their_gain=GAIN[kind], sd_of_two_job_difference=sd_diff, z_of_their_gain=float(z),
                         outcome=oc, known_good_copies=kg)
    out['KNOWN_GOOD'] = dict(rule='both copies inside every job agree within 2.58 binomial sd, both circuits', passed=out['GHZ3']['known_good_copies'] and out['GHZ5']['known_good_copies'])
    return out
