#!/bin/bash
# P2-R tuned (6 Oct, Wayfinder: "take all caps off and get the job done"): collect the re-tune when Cepheus's 21:00Z window runs it; pick the amplitude by the
# rule written BEFORE the data (ledger §287): the LARGEST amplitude where the witness clocks keep >= 0.85 of their hand AND the looked-at qubits keep <= 0.80
# (the tone looks); none qualifies -> HOLD, nothing fires. Then the length sweep at that amplitude, trains of 1-4 looks, 1500 shots, inside the window.
cd ~/bones-forge/standoff; export AWS_PROFILE=braket; PY=~/bones-forge/qvenv/bin/python; L=fire_p2r.log
$PY rigetti_look_tune_r2.py collect >> $L 2>&1
A=$($PY - <<'PY' 2>>$L
import json, os, numpy as np
import rigetti_look_tune_r2 as T, rigetti_triangle_c as C
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(T.RT.OUT, 'lookT2.npz')).items()}
idx = {q: T.QS.index(q) for q in T.QS}; cl = [idx[q] for q in C.CL]; em = [idx[q] for q in T.EM]
H = lambda a: (1 - 2 * raw[('X', a)].mean(0)) - 1j * (1 - 2 * raw[('Y', a)].mean(0))
h0 = H(0.0); best = None
with open('fire_p2r.log', 'a') as f:
    for a in T.AMPS:
        k = np.abs(H(a)) / np.maximum(np.abs(h0), 1e-6); kc = float(np.median(k[cl])); ke = float(np.median(k[em]))
        f.write(f'  tune2 a={a}: clocks keep {kc:.3f} of hand | looked-at keep {ke:.3f}\n')
        if a > 0 and kc >= 0.85 and ke <= 0.80: best = a
print(best if best is not None else 'HOLD')
PY
)
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') tune2 rule -> amplitude $A" >> $L
if [ "$A" == "HOLD" ] || [ -z "$A" ]; then echo "$(date '+%Y-%m-%dT%H:%M:%S%z') no amplitude meets the rule: HOLD, nothing fired" >> $L; exit 0; fi
P2R_STRENGTH=$A P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_tuned $PY rigetti_look_lengths.py submit 2>&1 | grep -vi warn | tail -3 | cut -c1-200 >> $L
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') tuned sweep sent at amplitude $A" >> $L
P2R_STRENGTH=$A P2R_KS=1,2,3,4 P2R_SHOTS=1500 P2R_SAVE=lookLengths_tuned $PY rigetti_look_lengths.py collect >> $L 2>&1
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') tuned sweep collected" >> $L
