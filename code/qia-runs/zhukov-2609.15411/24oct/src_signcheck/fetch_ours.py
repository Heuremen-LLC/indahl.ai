"""fetch_ours.py -- READ-ONLY retrieval of the four finished jobs' SamplerV2 results (no submit, zero QPU). Saves, for the 8 chain-C circuits (lane 3 register t3),
the raw BitArray integer values v (bit j = clbit j) and the get_counts() dict, so the decode can be redone from the true SamplerV2 output."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run'))
from sweep import service
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.path.dirname(HERE)
rec = json.load(open(RUN + '/job_zhukov.json')); s = service(); out = {}
for j in rec['jobs']:
    job = s.job(j['job_id']); assert str(job.status()) in ('DONE', 'JobStatus.DONE'), job.status(); res = job.result()
    for pos, i in enumerate(j['order']):
        sid = rec['set_ids'][i]
        if not sid.startswith('005:'): continue
        ba = res[pos].data.t3; out[f"{j['label']}|{i}|v"] = ba.array[:, 0].astype(np.uint8); out[f"{j['label']}|{i}|counts"] = np.array(json.dumps(ba.get_counts()))
        out[f"{j['label']}|{i}|nbits"] = np.array(ba.num_bits)
np.savez_compressed(HERE + '/ours_chainC_bitarrays_t3.npz', **out); print('saved', len(out) // 3, 'circuit-job pairs')
