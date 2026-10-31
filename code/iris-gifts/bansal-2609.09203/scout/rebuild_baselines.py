"""Table 7 (Task 1) baselines, majority line, and the p=0.38 success test, from the released files.
Feature list and CV protocol are the ones printed in Appendix H.1 and the released script's settings (5-fold stratified, seed 42).
usage: <qvenv python with numpy+scipy+sklearn> -I rebuild_baselines.py <hf_root>
Uses scikit-learn only as a library. Two sets are scored: the files' evaluable rows (n=127). The paper text says n=363, for which no labels are released."""
import sys, os, json, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from common import *
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
import sklearn, scipy
from scipy.stats import chi2_contingency
root = sys.argv[1]
T = load_dir(root, "trajectories")
def n_error_types(t):
    ev = set()
    for s in step_list(t):
        raw = (s.get("raw_response") or "").lower(); e = s.get("error") or {}
        if e.get("occurred"):
            typ = e.get("type") or ""; msg = (e.get("message") or "").lower()
            if "hallucin" in raw: ev.add("hallucination")
            elif "tool" in typ or "api" in typ: ev.add("tool_misuse")
            elif "timeout" in msg: ev.add("timeout")
            elif "not found" in msg or "404" in msg: ev.add("resource_not_found")
            elif "rate" in msg or "429" in msg: ev.add("rate_limit")
            else: ev.add("other_error")
        if s.get("revision_trigger") and "error" in str(s["revision_trigger"]).lower(): ev.add("reasoning_error")
    return len(ev)
rows = []
for t in T:
    if t["outcome"]["success"] is None: continue
    d = derived(t)
    m = t["metadata"]
    rows.append(([m["total_steps"], m["total_tool_calls"], m["total_failures"], m["total_revisions"], len(set(d["tools"])), len(set(d["phases"])), d["resp_chars"], n_error_types(t)], int(t["outcome"]["success"])))
X = np.array([r[0] for r in rows], float); y = np.array([r[1] for r in rows])
print("sklearn", sklearn.__version__, "scipy", scipy.__version__, "numpy", np.__version__)
print("evaluable rows n=%d, positives %d, majority baseline %.4f (printed 0.693)" % (len(y), y.sum(), max(y.mean(), 1 - y.mean())))
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, clf, printed in [("LogisticRegression", LogisticRegression(max_iter=1000), "0.685+/-0.046 AUROC 0.496+/-0.096"),
                           ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42), "0.614+/-0.049 AUROC 0.452+/-0.091"),
                           ("GradientBoosting", GradientBoostingClassifier(n_estimators=100, random_state=42), "0.614+/-0.033 AUROC 0.426+/-0.066")]:
    a = cross_val_score(clf, X, y, cv=cv, scoring="accuracy"); u = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")
    print("%-18s acc %.3f+/-%.3f AUROC %.3f+/-%.3f | printed %s" % (name, a.mean(), a.std(), u.mean(), u.std(), printed))
print("expected majority accuracy if the 363 judged labels were used: not computable, labels not released; printed rates imply %.3f" % (317 / 363))
# the printed p=0.38 for judged success, from printed counts only
tab = np.array([[109, 14], [99, 19], [109, 13]])
for corr in (False,):
    chi, p, dof, _ = chi2_contingency(tab, correction=corr)
    print("Pearson chi-square on printed counts: chi2=%.3f dof=%d p=%.3f (printed 0.38)" % (chi, dof, p))
