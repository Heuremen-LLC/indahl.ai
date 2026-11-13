"""fire_ghz.py --dry | --fire : job A (ibm_fez, 8,192 shots): best_a, q25, unpinned, q50, par0..par7 (best path), q75, best_b; job B right after A
returns: best_jobB, unpinned_jobB. All opt 1 (their setting); 'unpinned' = opt 1 with no initial layout (their setting), seed 7."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from ghz import ghz, SHOTS, PHIS
from ghz_fill import analyse
from sweep import service
from qiskit import transpile
CAP, RESERVE = 60, 300
L = json.load(open(os.path.join(HERE, 'layouts_chosen.json')))
s = service(); rem = s.usage().get('usage_remaining_seconds'); be = s.backend('ibm_fez'); st = be.status(); print('remaining', rem, 'fez', st.status_msg, st.pending_jobs, flush=True)
fire = '--fire' in sys.argv
if fire and (rem is None or rem - CAP < RESERVE or str(st.status_msg).lower() != 'active'): sys.exit('REFUSED')
def build(lay=None, phi=None):
    return transpile(ghz(phi=phi), be, optimization_level=1, initial_layout=(L[lay]['path'] if lay else None), seed_transpiler=7)
A = [('best_a', build('best')), ('q25', build('q25')), ('unpinned', build())] + [('q50', build('q50'))] + [('par%d' % i, build('best', f)) for i, f in enumerate(PHIS)] + [('q75', build('q75')), ('best_b', build('best'))]
def phys(t): return [t.find_bit(i.qubits[0]).index for i in t.data if i.operation.name == 'measure']
info = {k: dict(depth=t.depth(), cz=int(t.count_ops().get('cz', 0)), qubits=phys(t)) for k, t in A}
print(json.dumps({k: (v['depth'], v['cz'], v['qubits']) for k, v in info.items() if not k.startswith('par') or k == 'par0'}), flush=True)
if not fire: open(os.path.join(HERE, 'dry_run_ghz.text'), 'w').write(json.dumps(info, indent=1)); sys.exit(0)
from qiskit_ibm_runtime import SamplerV2
json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before.json'), 'w'), default=str)
jA = SamplerV2(mode=be).run([t for _, t in A], shots=SHOTS); recA = dict(job_id=jA.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), info=info); print('SUBMITTED A', recA['job_id'], recA['submitted'], flush=True)
rA = jA.result(); raw = {k: r.data.c.get_counts() for (k, _), r in zip(A, rA)}; recA['metrics'] = jA.metrics()
B = [('best_jobB', build('best')), ('unpinned_jobB', build())]
jB = SamplerV2(mode=be).run([t for _, t in B], shots=SHOTS); recB = dict(job_id=jB.job_id(), submitted=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), qubits={k: phys(t) for k, t in B}); print('SUBMITTED B', recB['job_id'], recB['submitted'], flush=True)
rB = jB.result(); raw.update({k: r.data.c.get_counts() for (k, _), r in zip(B, rB)}); recB['metrics'] = jB.metrics()
json.dump(dict(A=recA, B=recB), open(os.path.join(HERE, 'jobs_ghz.json'), 'w'), default=str); json.dump(raw, open(os.path.join(HERE, 'raw_counts.json'), 'w'))
out = analyse(raw); open(os.path.join(HERE, 'results_ghz.text'), 'w').write(json.dumps(out, indent=1, default=float))
print(json.dumps({k: out[k] for k in ('KNOWN_GOOD', 'LAYOUT', 'DRIFT')}, indent=1, default=float)); print(json.dumps({k: v for k, v in out['FIDELITY'].items() if k != 'parity'}, default=float)); print(json.dumps(out['P'], default=float), flush=True)
