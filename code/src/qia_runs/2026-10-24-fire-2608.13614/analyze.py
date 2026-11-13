"""analyze.py -- the committed reading for the 2608.13614 kingston fire (plan PLAN_2608.13614.md.text).  Pure function of counts + the
QUBO energy table; the same function reads the synthetic worlds (synth.py) and the QPU counts.
Counts keys are bitstrings as SamplerV2 prints them for the measure(i, n-1-i) circuit: char k (left to right) = bit b_k (MSB-first),
so int(key, 2) is the QUBO state index used by sis_qubo.E.
R1 (primary): fraction of shots in the 10 lowest-energy states (lowest 1% of 1024) vs the uniform-random null 10/1024.
   Clopper-Pearson 95% interval on k/n.  ABOVE if lower > null, BELOW if upper < null, else CONSISTENT (bound printed as upper/null).
   CANNOT_TELL if n < 4000 or if the noiseless-QAOA ceiling (ideal fraction) would not itself read ABOVE at this n (instrument cannot
   resolve a perfect device).
R2 (secondary, pre-registered): same k against the product-of-own-marginals null: p_mm = P(low-10 set) under independent bits with
   the run's own per-bit frequencies.  ABOVE/BELOW/CONSISTENT by the same CP interval vs p_mm.  Separates bit-bias (e.g. decay toward 0)
   from low-energy concentration.
R1b (descriptive): share of the noiseless-QAOA excess, (f - null)/(ideal - null), with the CP ends.
R3 (descriptive): mean QUBO energy of the shots vs the uniform mean (bootstrap 95%), lowest-energy sampled state and its rank,
   whether the QUBO optimum was sampled.
Combined over the two variants (P paper construction, S released script): both the same -> that outcome; otherwise CANNOT_TELL."""
import numpy as np
from scipy.stats import beta as _B
NB = 10; K = 10; NULL = K / 1024

def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else _B.ppf(a / 2, k, n - k + 1); hi = 1.0 if k == n else _B.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)

def four(lo, hi, ref):
    return 'ABOVE' if lo > ref else 'BELOW' if hi < ref else 'CONSISTENT'

def read(counts, E, ideal_frac, rng=None, boot=400):
    rng = rng or np.random.default_rng(7)
    E = np.asarray(E); low = set(int(x) for x in np.argsort(E, kind='stable')[:K])
    st = np.array([int(k.replace(' ', ''), 2) for k in counts]); ct = np.array([counts[k] for k in counts], float); n = int(ct.sum())
    k = int(ct[np.isin(st, list(low))].sum()); f = k / n; lo, hi = cp(k, n)
    klo_ideal = cp(int(round(ideal_frac * n)), n)[0]
    r1 = 'CANNOT_TELL' if (n < 4000 or not klo_ideal > NULL) else four(lo, hi, NULL)
    bits = np.array([[(s >> (NB - 1 - q)) & 1 for q in range(NB)] for s in st]); m1 = (bits * ct[:, None]).sum(0) / n
    pmm = float(sum(np.prod([m1[q] if (s >> (NB - 1 - q)) & 1 else 1 - m1[q] for q in range(NB)]) for s in low))
    r2 = 'CANNOT_TELL' if n < 4000 else four(lo, hi, pmm)
    p = ct / n; Em = float(p @ E[st]); bs = [float(E[st] @ rng.multinomial(n, p) / n) for _ in range(boot)]
    order = np.argsort(E, kind='stable'); rank = {int(s): r for r, s in enumerate(order)}; best = int(st[np.argmin(E[st])])
    ex = [(lo - NULL) / (ideal_frac - NULL), (f - NULL) / (ideal_frac - NULL), (hi - NULL) / (ideal_frac - NULL)]   # share of the noiseless-QAOA excess
    return dict(n=n, k_low10=k, frac=f, ci=[lo, hi], null=NULL, ratio_to_null=[lo / NULL, hi / NULL], R1=r1, excess_share=ex,
                p_marginal_null=pmm, R2=r2, ideal_frac=ideal_frac, marginals=[float(x) for x in m1],
                mean_E=Em, mean_E_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], uniform_mean_E=float(E.mean()),
                R3_meanE=four(*[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], float(E.mean())),
                best_sampled_state=best, best_sampled_rank=rank[best], optimum_sampled=bool(int(order[0]) in set(st.tolist())), n_unique=int(len(st)))

def combine(a, b):
    return a if a == b else 'CANNOT_TELL'
