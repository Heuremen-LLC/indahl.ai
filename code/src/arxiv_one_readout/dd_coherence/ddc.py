"""DDC run (coherence-only repeat of the DD run), 22 Oct 2026. Heuremen LLC, Wayfinder and Bones. PLAN_DDC.md, sha256 in PLAN_DDC.sha256.
THIN WRAPPER around ../dd_run/dd.py: the circuit builder (dd.build -> dd.dd_circuit, dd.timing) and the schedule check (dd.verify) are
IMPORTED UNCHANGED. Only these differ from the DD run: N values (0, 2, 8), shots per pub (SHOTS), chips (ibm_marrakesh, ibm_fez),
output names (job/raw/props_ddc_<chip>, in THIS folder) and the plan hash written into the job record (PLAN_DDC.sha256).
The fire path below is dd.py's __main__ block line for line with those names changed (dd.py's own __main__ hard-codes its folder).
Dry-run by default: builds, transpiles against the live chip, VERIFIES, estimates seconds, submits nothing. --fire submits.
Usage: python ddc.py CHIP [--fire]     Every circuit twice per job (copy 0, copy 1), shuffled together."""
import os, sys, json, time, random, warnings; warnings.filterwarnings('ignore')
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'dd_run'))
import dd                                   # ../dd_run/dd.py, unchanged (CODE_DDC.sha256 carries its hash)
from qiskit import transpile
from qiskit_ibm_runtime import SamplerV2
base = dd.base
dd.NS = (0, 2, 8)                           # was (0, 2, 4, 8, 16); dd.build reads dd.NS at call time
SHOTS = 12000; dd.SHOTS = SHOTS             # was 4000; sized in PLAN_DDC.md from the DD run's per-spectator scatter
RUN = 'ddc'; CHIPS = ('ibm_marrakesh', 'ibm_fez'); SEED = dd.SEED
if __name__ == '__main__':
    CHIP = sys.argv[1]; fire = '--fire' in sys.argv
    assert CHIP in CHIPS, ('pre-registered chips', CHIPS)
    s = base.service(); rem = s.usage().get('usage_remaining_seconds') or 0; b = s.backend(CHIP); n = b.num_qubits
    pubs, meta, shots, info = dd.build(b, CHIP)
    assert shots == SHOTS and sorted({m['N'] for m in meta}) == [0, 2, 8]
    meta = [dict(m, copy=c) for c in (0, 1) for m in meta]; pubs = pubs + pubs
    order = list(range(len(pubs))); random.Random(SEED + 11).shuffle(order); pubs = [pubs[i] for i in order]; meta = [meta[i] for i in order]
    tq = transpile(pubs, b, optimization_level=1, initial_layout=list(range(n)), scheduling_method='alap', seed_transpiler=7)
    print('%s timing: dt %.3g s, L %d dt, X %d dt, granularity %d, pulse_alignment %d, acquire_alignment %d -> echo d1 %d, X, d2 %d, X, d3 %d dt'
          % (CHIP, info['dt'], info['L_dt'], info['g_dt'], info['granularity'], info['pulse_alignment'], info['acquire_alignment'], info['d1'], info['d2'], info['d3']))
    print(dd.verify(tq, meta, info, n, b.target))
    mx = getattr(b.configuration(), 'max_shots', None); assert mx is None or shots <= mx, ('max_shots', mx)
    dur = np.array([c.estimate_duration(b.target, 's') for c in tq]); est = float(shots * np.sum(dur + 290e-6))
    for d_ in ('off', 'on'):
        for N in dd.NS:
            ds = sorted({round(d * 1e6, 3) for d, m in zip(dur, meta) if m['dd'] == d_ and m['N'] == N})
            print('  DD %-3s N=%2d circuit durations (us): %s' % (d_, N, ds))
    print('%s %s: %d pubs, %d shots each (max_shots %s), E %d, S %d, circuits %.1f-%.1f us, total shots %d, ESTIMATED %.0f s, remaining %s, queue %s'
          % (RUN, CHIP, len(tq), shots, mx, len(info['E']), len(info['S']), dur.min() * 1e6, dur.max() * 1e6, shots * len(tq), est, rem, b.status().pending_jobs), flush=True)
    if not fire: sys.exit()
    if rem < est + 3: print('STOP: estimated %.0f s, %.0f s left' % (est, rem)); sys.exit()
    props = b.properties(); json.dump(props.to_dict() if props is not None else None, open(HERE + '/props_%s_%s.json' % (RUN, CHIP), 'w'), default=str)
    job = SamplerV2(mode=b).run(tq, shots=shots)
    rec = dict(run=RUN, chip=CHIP, n_qubits=n, job_id=job.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%S%z'), meta=meta, order=order, shots=shots,
               info=info, plan_sha256=open(HERE + '/PLAN_DDC.sha256').read().split()[0])
    json.dump(rec, open(HERE + '/job_%s_%s.json' % (RUN, CHIP), 'w'), default=str); print('SUBMITTED', RUN, CHIP, job.job_id(), flush=True)
    res = job.result(); out = {}
    for i, pr in enumerate(res):
        for name in pr.data: out['%s_%d' % (name, i)] = getattr(pr.data, name).array
    np.savez_compressed(HERE + '/raw_%s_%s.npz' % (RUN, CHIP), **out)
    print('DONE %s %s: remaining now %s' % (RUN, CHIP, s.usage().get('usage_remaining_seconds')), flush=True)
