"""THE LOOK BY DOSE, CEPHEUS (Bones, 2026-10-07; Wayfinder: "the other qubits act like witnesses based on proximity? ... line of sight if that's a qubit thing ...
do some Cepheus if we have to, let's put this to bed"). rigetti_look_lengths.py unchanged (our tone on the looked-at qubits' readout frames, four laid lengths
1.0 / 1.5 / 2.0 / 2.5 us, looks k = 1-4, delays to 15 us, no-tone check), with ONE change: the looked-at set is CLUSTERED so the clocks see 0 / 1 / 2 / 3 / 4
looked-at qubits within 2 grid pitches. Picked from the 03:32Z calibration (cepheus_props_live_20261007.json: RB > 0.995, readout > 0.94, T1 > 12 us; centre clocks
T2 > 8 us; cluster centres >= 5 pitches apart): plus of 4 around clock 13 (12, 14, 4, 22), T of 3 around clock 44 (43, 35, 53), pair around clock 56 (55, 57), single 88.
Call hashed first: ~/bones-forge/parallax/darkwave_disco/calls/CEPHEUS_DOSE_CALL_20261007.txt.
  DOSE_SAVE=lookDose_r1 python rigetti_look_dose.py dry | submit | collect"""
import os, sys
os.environ.setdefault('P2R_STRENGTH', '0.03'); os.environ.setdefault('P2R_KS', '1,2,3,4'); os.environ.setdefault('P2R_SHOTS', '1500')
os.environ.setdefault('P2R_SAVE', os.environ.get('DOSE_SAVE', 'lookDose_r1'))   # 7 Oct fix: never override a caller's save name (the punch overwrote lookDose_r1_tasks.json)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigetti_triangles as T
DOSE_EM = [4, 12, 14, 22, 35, 43, 53, 55, 57, 88]
T.EM = DOSE_EM
import rigetti_triangle_c as C
assert C.EM == DOSE_EM and len(C.CL) == 97, (C.EM, len(C.CL))
import rigetti_look_lengths as L
assert L.EM == DOSE_EM
if __name__ == '__main__':
    L.main()
