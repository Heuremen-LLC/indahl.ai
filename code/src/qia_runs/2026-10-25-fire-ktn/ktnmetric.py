"""Their coupled metric, verbatim logic from Travaux@cb0e00a robust_metrics.py / ssh_model.py; psig from their topology.py (vendored in theirs/)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theirs'))
from topology import psig_from_correlation
def psig_thresholded(corr, seuil=0.05):
    c = corr.copy(); c[np.abs(c) < seuil] = 0.0; return psig_from_correlation(c)
def correlation_entropy(corr):
    c = np.abs(corr.flatten()); c = c[c > 1e-12]
    if len(c) == 0: return 0.0
    p = c / c.sum(); return float(-np.sum(p * np.log(p)))
def edge_weight(corr): return float(abs(corr[0, -1]))
def coupled_metric(corr, seuil=0.05):
    psig = psig_thresholded(corr, seuil); edge = edge_weight(corr); ent = correlation_entropy(corr)
    return {'psig_seuille': psig, 'edge': edge, 'entropie': ent, 'score': psig + edge - 0.1 * ent}
