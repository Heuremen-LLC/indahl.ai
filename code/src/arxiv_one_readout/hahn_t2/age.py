"""age.py -- where does the Hahn T2 shortfall live: in IBM's stated record, or in the hardware? (23 Oct 2026, written after the
marrakesh fresh-record run, BEFORE these numbers were read; zero QPU seconds, files on disk only.)
Per run: age of each qubit's stated T2 at job submission (submitted_utc minus the T2 entry's own 'date'); median stated T2 (us);
median delivered T2 (us, hahn_pool.fit, FIXED and FREE, A > 0.2); median delivered/stated. Rule, fixed here: within a chip,
  - delivered steady across runs while stated moves  -> the movement is in the STATED record
  - delivered moves with the stated values           -> the hardware moved (the record is tracking it)
  - neither / too few runs                           -> CANNOT_TELL
'Steady' = the run medians' spread is inside the widest single-run 95 % bootstrap interval of that median."""
import json, sys, datetime as dt, numpy as np
sys.path.insert(0, '.'); import hahn as R
from hahn_pool import fit
RUNS = {'ibm_kingston': ['kingston_run1', 'kingston_run2', 'kingston_fresh'], 'ibm_marrakesh': ['marrakesh_run1', 'marrakesh_run2', 'marrakesh_fresh'],
        'ibm_fez': ['fez_run1', 'fez_run2', 'fez_clock1', 'fez_clock2']}
rng = np.random.default_rng(5)
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
def boot(a): a = np.asarray(a); return np.percentile([np.median(rng.choice(a, len(a))) for _ in range(2000)], [2.5, 97.5])
def load(tag):
    rec = json.load(open(f'job_hahn_ibm_{tag}.json')); z = np.load(f'raw_hahn_ibm_{tag}.npz'); props = json.load(open(f'props_hahn_ibm_{tag}.json'))
    sub = ts(rec['submitted_utc']); st, age = {}, {}
    for q, ps in enumerate(props['qubits']):
        for x in ps:
            if x['name'] == 'T2': st[q] = x['value']; age[q] = (sub - ts(x['date'])).total_seconds() / 3600
    p = {}
    for i, m in enumerate(rec['meta']):
        S = rec['sets'][m['set']]; b = z[f'c_{i}'][:, :len(S)]
        for j, q in enumerate(S): p.setdefault(q, {}).setdefault(m['tau_us'], []).append(float(b[:, j].mean()))
    return p, st, age, props.get('last_update_date')
for chip, tags in RUNS.items():
    print(f'== {chip}')
    rows = {}
    for tag in tags:
        p, st, age, stamp = load(tag)
        for free in (False, True):
            d, r = [], []
            for q in p:
                if q not in st: continue
                T2, A, _ = fit(R.TAUS, [np.mean(p[q][t]) for t in R.TAUS], free)
                if A > 0.2 and np.isfinite(T2): d.append(T2); r.append(T2 / st[q])
            rows[(tag, free)] = (np.median(d), boot(d), np.median(r))
        ages = np.array(list(age.values())); sv = np.array(list(st.values()))
        (dF, bF, rF), (dR, bR, rR) = rows[(tag, False)], rows[(tag, True)]
        print(f'  {tag:16} T2 record age median {np.median(ages):7.1f} h (90% under {np.percentile(ages, 90):7.1f} h) | stated median {np.median(sv):6.1f} us'
              f' | delivered FIXED {dF:6.1f} [{bF[0]:.1f}, {bF[1]:.1f}] FREE {dR:6.1f} [{bR[0]:.1f}, {bR[1]:.1f}] | ratio FIXED {rF:.3f} FREE {rR:.3f}')
    for free in (False, True):
        meds = [rows[(t, free)][0] for t in tags]; widest = max(rows[(t, free)][1][1] - rows[(t, free)][1][0] for t in tags)
        stated = [np.median(list(load(t)[1].values())) for t in tags]
        print(f'  {"FREE " if free else "FIXED"}: delivered run medians spread {max(meds) - min(meds):.1f} us vs widest single-run interval {widest:.1f} us'
              f' -> delivered {"STEADY" if max(meds) - min(meds) < widest else "MOVES"}; stated run medians spread {max(stated) - min(stated):.1f} us')
