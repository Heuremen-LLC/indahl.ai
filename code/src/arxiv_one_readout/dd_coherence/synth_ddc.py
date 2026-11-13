"""Synthetic test of analyze_ddc.py, after ../dd_run/synth_dd.py. Builds ddc.py's real circuit list (dd.build, unchanged, N = 0, 2, 8,
12000 shots) on FakeMarrakesh and FakeFez (offline, nothing submitted), draws bits for every pub in the schema a fired job writes
(job_ddc_<chip>.json, raw_ddc_<chip>.npz with fin_<i>, props_ddc_<chip>.json), both chips in one folder, runs the analysis.
World: synth_dd.py's, line for line (per-spectator coherence c0 in [0.55, 0.95] with 6 dead at 0.01, decay 0.4 % per step, own start
phase, own drift per step that differs DD on vs off and is equal in D and M; the echo has no effect of its own on the idle arm).
Changed from synth_dd.py: no kick planted (coherence-only run), and the COST is planted per case, WITH the per-spectator spread
measured in the DD run (PLAN_DDC.md, 'Sizing'): cost_off = COST + h4, h4 ~ N(0, HET4[chip]); the echo's change per spectator
h6 ~ N(0, HET6[chip]) with mean 0.
  unchanged: cost_on = cost_off + h6         (truth: R6 median ~0, R9 ~0)
  removed:   cost_on = h6                    (truth: R6 median ~ -COST, R5 ~0, R9 ~ -1)
  null:      no cost, no spread              (truth 0 everywhere)
  python synth_ddc.py            -> unchanged, removed, null (seed 5) into synth_output.txt
  python synth_ddc.py --nulls    -> NULL seeds 11-16 (nulls/), tally + decisions into null_floor.txt (raw .npz of the nulls deleted after)
  python synth_ddc.py --power    -> unchanged and removed, seeds 21-26, decisions into power.txt (raw .npz deleted after)
  CASE=... SEED=k python synth_ddc.py --one"""
import os, sys, json, subprocess, shutil, warnings; warnings.filterwarnings('ignore')
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
COST = 0.008; HET4 = {'ibm_marrakesh': 0.027, 'ibm_fez': 0.012}; HET6 = {'ibm_marrakesh': 0.013, 'ibm_fez': 0.0105}
def one(case, seed, out):
    sys.argv = sys.argv[:1]; sys.path.insert(0, HERE)
    import ddc, analyze_ddc
    dd = ddc.dd
    from qiskit_ibm_runtime.fake_provider import FakeFez, FakeMarrakesh
    A = analyze_ddc.A; A.RNG = np.random.default_rng(seed + 1000); rng = np.random.default_rng(seed)
    os.makedirs(out, exist_ok=True)
    for chip, B in (('ibm_marrakesh', FakeMarrakesh), ('ibm_fez', FakeFez)):
        b = B(); n = b.num_qubits
        pubs, meta, shots, info = dd.build(b, chip); S = info['S']; nS = len(S)
        meta = [dict(m, copy=c) for c in (0, 1) for m in meta]
        c0 = rng.uniform(0.55, 0.95, nS); c0[rng.choice(nS, 6, replace=False)] = 0.01
        phi0 = rng.uniform(-np.pi, np.pi, nS); drift = {'off': np.radians(rng.normal(0, 8, nS)), 'on': np.radians(rng.normal(0, 1, nS))}
        h4 = rng.normal(0, HET4[chip], nS); h6 = rng.normal(0, HET6[chip], nS)
        cost = {'unchanged': {'off': COST + h4, 'on': COST + h4 + h6}, 'removed': {'off': COST + h4, 'on': h6},
                'null': {'off': np.zeros(nS), 'on': np.zeros(nS)}}[case]
        z = {}
        for i, m in enumerate(meta):
            N = m['N']; c = c0 * np.exp(-0.004 * N) - (cost[m['dd']] if m['mode'] == 'M' else 0.0); phi = phi0 + drift[m['dd']] * N
            e = c * (np.cos(phi) if m['setting'] == 'XX' else np.sin(phi)); p = np.zeros(n); p[S] = (1 - e) / 2
            z['fin_%d' % i] = (rng.random((shots, n)) < p).astype(np.int8)
        json.dump(b.properties().to_dict(), open(os.path.join(out, 'props_ddc_%s.json' % chip), 'w'), default=str)
        rec = dict(run='ddc', chip=chip, n_qubits=n, job_id='SYNTH_%s_%d' % (case.upper(), seed), meta=meta, order=list(range(len(meta))), shots=shots, info=info, plan_sha256='SYNTH')
        json.dump(rec, open(os.path.join(out, 'job_ddc_%s.json' % chip), 'w'), default=str); np.savez_compressed(os.path.join(out, 'raw_ddc_%s.npz' % chip), **z)
    print({'unchanged': 'UNCHANGED (seed %d): cost %.3f + spread in both DD settings, echo change per spectator mean 0 -> expect R4, R5 ABOVE, R6 CONSISTENT excluding -R4, R9 ~0, DECISION does not remove',
           'removed': 'REMOVED (seed %d): cost %.3f + spread with DD off, mean 0 with DD on -> expect R4 ABOVE, R5 CONSISTENT, R6 BELOW ~-%.3f, R9 ~-1, DECISION removes',
           'null': 'NULL (seed %d): nothing planted; every reading has truth 0 -> DECISION CANNOT TELL (no cost)'}[case].replace('%.3f', '%.3f' % COST) % seed)
    print('planted spread: HET4 %s, HET6 %s; shots %d per pub, N %s' % (HET4, HET6, shots, dd.NS))
    analyze_ddc.run_all(out)
def sub(case, seed, out):
    return subprocess.run([PY, os.path.abspath(__file__), '--one'], env=dict(os.environ, CASE=case, SEED=str(seed), OUT=out), capture_output=True, text=True, check=True).stdout
def decisions(txt): return [l.strip() for l in txt.splitlines() if l.strip().startswith(('DECISION', 'HEADLINE'))]
if __name__ == '__main__':
    if '--one' in sys.argv: one(os.environ['CASE'], int(os.environ['SEED']), os.environ['OUT']); sys.exit()
    if '--nulls' in sys.argv:
        os.makedirs(os.path.join(HERE, 'nulls'), exist_ok=True); seeds = range(11, 17)
        outs = [sub('null', sd, os.path.join(HERE, 'nulls', 'synth_null_%d' % sd)) for sd in seeds]   # one worker at a time (Mac RAM law)
        tot = np.zeros(4, int); lines = []; dec = []
        for sd, out in zip(seeds, outs):
            open(os.path.join(HERE, 'nulls', 'null_%d.txt' % sd), 'w').write(out)
            t = [l for l in out.splitlines() if l.startswith('TALLY')][0]; lines.append('seed %d: %s' % (sd, t)); tot += np.array([int(x.split()[-1]) for x in t.split(':', 1)[1].split(',')])
            dec += ['seed %d: %s' % (sd, d) for d in decisions(out)]
            for f in os.listdir(os.path.join(HERE, 'nulls', 'synth_null_%d' % sd)):
                if f.endswith('.npz'): os.remove(os.path.join(HERE, 'nulls', 'synth_null_%d' % sd, f))
        s = ('NULL FLOOR, 6 seeds (11-16), two chips each (FakeMarrakesh, FakeFez), every reading truth 0, all/wired/unwired counted separately\n' + '\n'.join(lines) +
             '\nTOTAL readings %d: ABOVE %d, BELOW %d -> resolved %d (%.1f %%); CONSISTENT %d; CANNOT TELL %d\nDECISIONS (truth: no cost -> CANNOT TELL):\n' % (tot.sum(), tot[0], tot[1], tot[0] + tot[1], 100 * (tot[0] + tot[1]) / tot.sum(), tot[2], tot[3]) + '\n'.join(dec) + '\n')
        open(os.path.join(HERE, 'null_floor.txt'), 'w').write(s); print(s)
    elif '--power' in sys.argv:
        os.makedirs(os.path.join(HERE, 'power'), exist_ok=True); jobs = [(c, sd) for c in ('unchanged', 'removed') for sd in range(21, 27)]
        outs = [sub(c, sd, os.path.join(HERE, 'power', '%s_%d' % (c, sd))) for c, sd in jobs]
        s = ['POWER: planted unchanged / removed, seeds 21-26, decisions at N=8 (per chip, combined)']
        for (c, sd), out in zip(jobs, outs):
            open(os.path.join(HERE, 'power', '%s_%d.txt' % (c, sd)), 'w').write(out); s += ['%s seed %d: %s' % (c, sd, d) for d in decisions(out)]
            s += ['%s seed %d:   %s' % (c, sd, l.strip()) for l in out.splitlines() if 'R6 half-width' in l]
            shutil.rmtree(os.path.join(HERE, 'power', '%s_%d' % (c, sd)))
        open(os.path.join(HERE, 'power.txt'), 'w').write('\n'.join(s) + '\n'); print('\n'.join(s))
    else:
        cases = [('unchanged', 5, 'synth_unchanged'), ('removed', 5, 'synth_removed'), ('null', 5, 'synth_null_5')]
        outs = [sub(c, sd, os.path.join(HERE, f)) for c, sd, f in cases]
        out = ('\n' + '#' * 100 + '\n').join(outs); open(os.path.join(HERE, 'synth_output.txt'), 'w').write(out); print(out)
