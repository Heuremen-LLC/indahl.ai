"""THE GAMBLER -- 2026-09-28 (designed dry, fire when the QPU comes back). Wayfinder: the gambler dies in his sleep (the one is
eaten at the joining gate -- 9/24's closed item), the ACE he handed over persists, and the train still has to go back to the
station: a SECOND step where the energy gets moved, which the OBSERVER can't see but a WITNESS might -- as TIME (a clock running
late). No outcome written. Only what is measured:
  ACE   R : a copy of A's one taken BEFORE the joining (CX A->R). The message that persists.
  PAIR  A,B : joined at the gate (ENT, has the both-excited piece that gets eaten) or not (PROD, same gates, no both-excited piece).
  CLOCKS W_A, W_B : a neighbor of each side, held in superposition from the start -- their phase IS their clock. Energy parked next
             to them shifts their pitch, so a clock that ran late = energy x time (phase = energy * time / hbar).
  CLOCK W_far : two steps away, the control clock.
  OBSERVER : reads A, B, R.   WITNESS : reads the clocks, either BEFORE the observer looks or AFTER (sees system + observer).
  Train time: waits after the joining, 0/2/5/10/20 us.
Every order pinned with barriers. Raw dots kept.
  python gambler.py sim                         (plumbing check on a simulator, free)
  python gambler.py check <key> <backend>       (layout + transpile against the real chip, no QPU)
  python gambler.py run   <key> <backend>       (fire)"""
import sys, os, json, time
import numpy as np
SEATS = {'ibm_marrakesh': dict(A=151, B=152, R=138, WA=150, WB=153, WF=149)}   # 151-152 = Marrakesh's worst-kept joint: most deaths
WAITS = [0, 2, 5, 10, 20]; SHOTS = 2000
ORDER = ['A', 'B', 'R', 'WA', 'WB', 'WF']
def circ(arm, w, quad, witness):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(6, 'q'); A, B, R, WA, WB, WF = range(6)
    obs = ClassicalRegister(3, 'obs'); wit = ClassicalRegister(3, 'wit'); c = QuantumCircuit(q, obs, wit)
    if arm in ('P0', 'P1'):
        if arm == 'P1': c.x(q)
        c.measure([q[A], q[B], q[R]], obs); c.measure([q[WA], q[WB], q[WF]], wit); return c
    c.h([q[WA], q[WB], q[WF]])                                   # the clocks start
    c.h(q[A]); c.cx(q[A], q[R]); c.barrier()                     # the ace is handed over
    if arm == 'ENT': c.cx(q[A], q[B])                            # the joining (both-excited piece goes through)
    else: c.x(q[A]); c.x(q[A]); c.cx(q[B], q[A])                 # PROD: same gate count, B at rest -> no both-excited piece
    c.barrier()
    if w: c.delay(w * 1000, q, unit='ns')
    c.barrier()
    def read_clocks():
        for k in (WA, WB, WF):
            if quad == 'Y': c.sdg(q[k])
            c.h(q[k])
        c.measure([q[WA], q[WB], q[WF]], wit)
    if witness == 'before': read_clocks(); c.barrier(); c.measure([q[A], q[B], q[R]], obs)
    else: c.measure([q[A], q[B], q[R]], obs); c.barrier(); read_clocks()
    return c
SPEC = [('P0', 0, '-', '-'), ('P1', 0, '-', '-')] + [(a, w, qd, wt) for a in ('ENT', 'PROD') for w in WAITS for qd in ('X', 'Y') for wt in ('before', 'after')]
def layout(be):
    s = SEATS[be.name]; t = be.target; E = {tuple(sorted(e)) for e in t['cz'].keys()} if 'cz' in t.operation_names else set()
    need = [('A', 'B'), ('A', 'R'), ('A', 'WA'), ('B', 'WB')]
    bad = [(x, y) for x, y in need if tuple(sorted((s[x], s[y]))) not in E]
    return [s[k] for k in ORDER], bad
def main(mode, key=None, backend=None):
    from qiskit import transpile
    if mode == 'sim':
        from qiskit_aer import AerSimulator; from qiskit_ibm_runtime import SamplerV2
        be = AerSimulator(); circs = [transpile(circ(*x), be) for x in SPEC]; r = SamplerV2(mode=be).run(circs, shots=500).result()
        o = r[SPEC.index(('ENT', 5, 'X', 'after'))].data; print('sim ok:', len(SPEC), 'circuits; ENT obs sample', o.obs.get_bitstrings()[:4], 'wit', o.wit.get_bitstrings()[:4]); return
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    sv = QiskitRuntimeService(channel='ibm_quantum_platform', token=open(key).read().strip()); be = sv.backend(backend)
    L, bad = layout(be); print('seats', dict(zip(ORDER, L)), 'missing links:', bad or 'none')
    circs = [transpile(circ(*x), backend=be, initial_layout=L, optimization_level=0) for x in SPEC]
    if mode == 'check': print(len(circs), 'circuits transpiled; seconds left', sv.usage().get('usage_remaining_seconds')); return
    if sv.usage().get('usage_remaining_seconds', 0) < 60: sys.exit('dry')
    sm = SamplerV2(mode=be); sm.options.execution.meas_type = 'kerneled'; sm.options.max_execution_time = 60
    j = sm.run(circs, shots=SHOTS); print('submitted', j.job_id(), flush=True); r = j.result()
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'gambler_' + time.strftime('%Y%m%d_%H%M%S')); os.makedirs(d)
    np.savez_compressed(os.path.join(d, 'raw.npz'), **{f'{a}_{w}_{qd}_{wt}_{reg}': np.asarray(getattr(r[n].data, reg)) for n, (a, w, qd, wt) in enumerate(SPEC) for reg in ('obs', 'wit')})
    json.dump({'job': j.job_id(), 'backend': backend, 'seats': dict(zip(ORDER, L)), 'spec': SPEC, 'shots': SHOTS}, open(os.path.join(d, 'meta.json'), 'w'))
    print('OUT', d)
if __name__ == '__main__': main(*sys.argv[1:])
