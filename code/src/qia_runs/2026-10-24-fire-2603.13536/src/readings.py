"""readings.py -- the scored readings for the 2603.13536 run, fixed before any job (PLAN_2603.13536.md.text).
Units: the 10 field instances, seeds 100..109 (main.py's 5 seeds 100..104 plus 105..109, added so D2 can reach CONSISTENT: the 5-instance
synth gave D2 a median half-width 0.70 > M; the 5-instance subset is printed descriptively).  Per instance i:
  a_i = log10 |E_AS(trot_i) - E0_i|            AS-SQD from the hardware Trotter-circuit samples (2400 shots t=0.6 + 600 shots t=1.2, merged)
  r_i = mean_k log10 |E_RND,k(trot_i) - E0_i|   Random SQD from the same samples, 5 expansion seeds k (the "5-seed spread")
  c_i = log10 |E_AS(ctrl_i) - E0_i|            AS-SQD from the no-entangling-gate control (H layer then measure, 3000 shots)
  errors censored at 1e-10 (/q 24).
D1 = mean_i (a_i - r_i)   (negative = AS-SQD better than random expansion on hardware samples: the paper's hardware claim)
D2 = mean_i (a_i - c_i)   (negative = the Trotter circuit's samples help AS-SQD more than a no-gate control does)
Interval: two-sided t(n-1) at 97.5 % over the n = 10 instances (two scored readings -> ~5 % family-wise), units = instances (/q 22).
Per reading: BELOW if hi < 0; ABOVE if lo > 0; CONSISTENT if -M <= lo and hi <= M (M = 0.5 decade, a factor 3.2 in error); else CANNOT_TELL.
Headline (the triage's four outcomes): FILL = D1 BELOW and D2 BELOW; GAP = D1 ABOVE; CLEAN = D1 CONSISTENT;
CANNOT_TELL = D1 CANNOT_TELL, or D1 BELOW while D2 is not BELOW (the no-gate control alone does as well: printed as its own reading)."""
import numpy as np
from scipy.stats import t as tdist
from assqd import run, lerr
M_EQ = 0.5; CONF = 0.975; NRND = 5

def interval(d):
    d = np.asarray(d, float); m = d.mean(); h = tdist.ppf(0.5 + CONF / 2, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d)); return m, m - h, m + h

def four(lo, hi, M=M_EQ):
    if not (np.isfinite(lo) and np.isfinite(hi)): return 'CANNOT_TELL'
    if hi < 0: return 'BELOW'
    if lo > 0: return 'ABOVE'
    if -M <= lo and hi <= M: return 'CONSISTENT'
    return 'CANNOT_TELL'

def headline(o1, o2):
    if o1 == 'ABOVE': return 'GAP'
    if o1 == 'CONSISTENT': return 'CLEAN'
    if o1 == 'BELOW' and o2 == 'BELOW': return 'FILL'
    return 'CANNOT_TELL'

def per_instance(Mi, trot, ctrl, seed, d1_null=False):
    """d1_null (synthetic only): in D1 ONLY, AS-SQD is replaced by the mean of 5 OTHER random-expansion seeds, so D1's truth is exactly 0; D2 always uses AS-SQD"""
    r = float(np.mean([lerr(Mi, run(Mi, trot, 'random', rng=np.random.default_rng(seed * 100 + k))[0]) for k in range(NRND)]))
    a_as = lerr(Mi, run(Mi, trot, 'en')[0])                      # AS-SQD on the trot arm: used by D2 in EVERY world
    a = float(np.mean([lerr(Mi, run(Mi, trot, 'random', rng=np.random.default_rng(seed * 100 + 50 + k))[0]) for k in range(NRND)])) if d1_null else a_as
    c = lerr(Mi, run(Mi, ctrl, 'en')[0])
    return a, r, c, a_as

def analyze(models, trots, ctrls, seed=0, d1_null=False):
    rows = [per_instance(Mi, t, c, seed * 10 + i, d1_null) for i, (Mi, t, c) in enumerate(zip(models, trots, ctrls))]
    a, r, c, a_as = map(np.array, zip(*rows))
    D1 = interval(a - r); D2 = interval(a_as - c); o1 = four(D1[1], D1[2]); o2 = four(D2[1], D2[2])
    return dict(a=a_as.tolist(), a_d1=a.tolist(), r=r.tolist(), c=c.tolist(), D1=D1, D2=D2, o1=o1, o2=o2, head=headline(o1, o2))
