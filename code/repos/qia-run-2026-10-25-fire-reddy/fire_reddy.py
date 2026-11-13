"""fire_reddy.py --dry | --fire. Order: fez, kingston, boston, pittsburgh, fez (fez bracketed at both ends for drift).
One SamplerV2 job per chip, three pubs (ZZ, XX, YY), 2000 shots, their circuit on physical [16,3,2,4,5], opt 3, seed 42.
Calibration record saved before and after each job. Refuses if a chip is not active or if remaining seconds < 60 + reserve."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from reddy import build, correlators, analyse, SHOTS
from sweep import service
ORDER = ['ibm_fez', 'ibm_kingston', 'ibm_boston', 'ibm_pittsburgh', 'ibm_fez']; CAP_S = 60; RESERVE = 300
s = service(); rem = s.usage().get('usage_remaining_seconds'); print('remaining', rem, flush=True)
mode = '--fire' if '--fire' in sys.argv else '--dry'
if mode == '--fire' and (rem is None or rem - CAP_S < RESERVE): sys.exit('REFUSED: remaining %s' % rem)
out = []
for i, b in enumerate(ORDER):
    be = s.backend(b); st = be.status()
    if not st.operational or str(st.status_msg).lower() != 'active': print('SKIP', b, st.status_msg); out.append(dict(arm=i, backend=b, skipped=str(st.status_msg))); continue
    routed = build(be); C, (p0, p1) = correlators(routed, be)
    meta = dict(arm=i, backend=b, p0=p0, p1=p1, depth={k: v.depth() for k, v in C.items()}, cz={k: v.count_ops().get('cz', 0) for k, v in C.items()},
                two_q_depth={k: v.depth(lambda g: g.operation.num_qubits == 2) for k, v in C.items()})
    print('compiled', meta, flush=True)
    if mode == '--dry': out.append(meta); continue
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_before_%d_%s.json' % (i, b)), 'w'), default=str)
    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=be).run([C['ZZ'], C['XX'], C['YY']], shots=SHOTS); meta['job_id'] = job.job_id(); meta['submitted'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    print('SUBMITTED', b, meta['job_id'], flush=True); json.dump(out + [meta], open(os.path.join(HERE, 'job_reddy.json'), 'w'), default=str)
    res = job.result(); cnt = {k: res[j].data.c.get_counts() for j, k in enumerate(['ZZ', 'XX', 'YY'])}
    m = job.metrics() or {}; meta.update(counts=cnt, usage=m.get('usage'), timestamps=m.get('timestamps'), analysis=analyse(cnt))
    json.dump(be.properties(refresh=True).to_dict(), open(os.path.join(HERE, 'props_after_%d_%s.json' % (i, b)), 'w'), default=str)
    print('RESULT', b, 'F %.4f +/- %.4f' % (meta['analysis']['F'], meta['analysis']['se_F']), meta['analysis']['vs_sim'], 'usage', m.get('usage'), flush=True)
    out.append(meta); json.dump(out, open(os.path.join(HERE, 'job_reddy.json'), 'w'), default=str)
json.dump(out, open(os.path.join(HERE, 'dry_run_reddy.text' if mode == '--dry' else 'results_reddy.text'), 'w'), indent=1, default=str)
