#!/usr/bin/env python3
"""extract_reach.py -- ONE-TIME reduction of the private raw files to the compact per-spectator JSON in ../data/.

NOT needed to verify the published numbers (verify_reach.py needs only ../data/*.json and the standard library).
This is kept so the reduction is auditable. It READS the private tree and writes only into ../data/.
It imports the group's own reader modules (readlook_wide, readproximity) unchanged, so each spectator's
fitted look length is exactly what those readers produce, and re-derives each value with a copy of the
same arithmetic (plus the precession rate) as a cross-check (assert).

  PRIVATE=/path/to/parallax/out/qubit_fifth_run  PYTHONDONTWRITEBYTECODE=1 python extract_reach.py
Needs numpy + scipy (the group's venv). Raw inputs: data/fire/<chip>/run<N>_results.npz (I/Q shots), run<N>_job.json, run<N>_meta.json.
"""
import glob, json, os, re, sys, warnings
from collections import deque
import numpy as np
warnings.filterwarnings('ignore')
sys.dont_write_bytecode = True
PRIV = os.environ.get('PRIVATE', '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
sys.path.insert(0, PRIV)
R0 = {'ibm_marrakesh': 310, 'ibm_kingston': 330, 'ibm_pittsburgh': 350, 'ibm_fez': 410, 'ibm_boston': 430, 'ibm_phoenix': 540, 'ibm_aachen': 800}
DAY = {'20261004': '2026-10-04', '20261005': '2026-10-05', '20261006': '2026-10-06', '20261007': '2026-10-07'}
r6 = lambda x: None if x is None or not np.isfinite(x) else round(float(x), 6)


def load_mods(chip):
    os.environ['CHIP'] = chip
    for m in ('readlook_wide', 'readproximity', 'readtwo_lengths', 'readclock_triangle'): sys.modules.pop(m, None)
    import readlook_wide as RL
    import readproximity as RP
    return RL, RP


def runinfo(chip, run):
    D = os.path.join(PRIV, 'data', 'fire', chip)
    j = json.load(open(os.path.join(D, f'run{run}_job.json')))
    mt = json.load(open(os.path.join(D, f'run{run}_meta.json')))
    return {'run': run, 'job_id': j['job_id'], 'submitted_at': j.get('submitted_at'), 'started_at': mt.get('start_time'), 'shots_per_circuit': mt.get('shots')}


def geometry(RL, RP, RO):
    """per clock: (looked-at bits within 2 pitches, sum 1/r^2 over all looked-at bits [r>=1], distance to nearest looked-at bit [pitches])."""
    g = {}
    if RO['n'] == 156:
        XY = RP.coords(); F = np.array([XY[q] for q in RO['far']])
        for w in RO['witness_of']:
            r = np.hypot(*(F - np.array(XY[int(w)])).T)
            g[int(w)] = (int((r <= 2.0 + 1e-9).sum()), float((1 / np.maximum(r, 1) ** 2).sum()), float(r.min()), 'plan')
    else:                                   # Phoenix: square lattice, no plan; looked-at bits within 2 LINKS
        nb = {q: set() for q in range(RO['n'])}
        for a, b in RO['edges']: nb[a].add(b); nb[b].add(a)
        for w in RO['witness_of']:
            q = int(w); seen = {q: 0}; dq = deque([q])
            while dq:
                u = dq.popleft()
                if seen[u] < 2:
                    for v in nb[u]:
                        if v not in seen: seen[v] = seen[u] + 1; dq.append(v)
            g[q] = (sum(1 for f in RO['far'] if f in seen), None, None, 'links')
    return g


def per_clock_rate(RL, RO, A):
    """copy of readproximity.per_clock that also returns the clock's own precession rate (deg/us, from the 10/20/30 us laid windows)."""
    c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0; sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)
    lv = {k: (np.real((v - c0) * np.conj(d)) / np.abs(d) ** 2).mean(0) for k, v in A.items()}
    WOF = {int(k): v for k, v in RO['witness_of'].items()}
    H = {a: (2 * lv[f'{a}|X'] - 1) - 1j * (2 * lv[f'{a}|Y'] - 1) for a in [f'T{t}' for t in RL.WIN] + [f'K{k}' for k in RL.LOOKS]}
    W = [w for w in sorted(WOF) if abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3]
    ang = {a: np.angle(H[a] / H['T0']) for a in H}; uw = np.unwrap(np.vstack([ang[f'T{t}'] for t in RL.WIN]), axis=0)
    tt = np.array([10.0, 20.0, 30.0]); Xm = np.vstack([tt, tt ** 2]).T; i3, i9 = RL.LOOKS.index(3), RL.LOOKS.index(9); out = {}
    for w in W:
        c = np.linalg.lstsq(Xm, uw[1:4, w], rcond=None)[0]; teq = []
        for k in RL.LOOKS:
            a = ang[f'K{k}'][w]; r = np.roots([c[1], c[0], -a]); r = [x.real for x in r if abs(x.imag) < 1e-9 and -5 < x.real < 60]
            teq.append(min(r, key=lambda x: abs(x - a / c[0])) if r and c[0] else np.nan)
        teq = np.array(teq); ok = np.isfinite(teq)
        out[w] = (np.polyfit(np.array(RL.LOOKS)[ok], teq[ok], 1)[0] if ok.sum() >= 4 else np.nan,
                  (teq[i9] - teq[i3]) / 6 if np.isfinite(teq[i3]) and np.isfinite(teq[i9]) else np.nan, float(np.degrees(c[0])))
    return out


def read_set(chip, rolefile, runs, label, extra=None):
    RL, RP = load_mods(chip)
    RO = json.load(open(os.path.join(PRIV, 'data', 'reads', rolefile))); RL.RO.clear(); RL.RO.update(RO); RP.RO = RO
    geo = geometry(RL, RP, RO); reads = []
    for run in runs:
        try: m, A = RL.load(run)
        except (SystemExit, FileNotFoundError) as e: print('  skip', chip, run, e); continue
        P = RP.per_clock(A); Q = per_clock_rate(RL, RO, A)
        assert set(P) == set(Q)
        for w in P:
            for i in (0, 1):
                a, b = P[w][i], Q[w][i]
                assert (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-9, (chip, run, w)
        rows = []
        for w in sorted(P):
            n2, inten, near, kind = geo[w]
            rows.append([w, n2, r6(inten), r6(near), r6(Q[w][2]), r6(P[w][0]), r6(P[w][1])])
        reads.append({**runinfo(chip, run), 'clocks': rows})
    return {'chip': chip, 'label': label, 'roles_file': rolefile, 'stated_look_us': r6(RL.MAKER), 'n_looked_at_bits': len(RO['far']),
            'geometry': geo[next(iter(geo))][3], 'centres': RO.get('cluster_centres'), 'reads': reads, **(extra or {})}


def floor_set(chip, runs):
    """THE FLOOR runs: spectators >= 3 pitches from every looked-at bit; three arms in one job: DARK (k x laid delay, nothing measured),
    measure (the chip's own readout), measure_2 (a shorter readout). Same family-renaming as the private readfloor.py."""
    RL, RP = load_mods(chip)
    RO = json.load(open(os.path.join(PRIV, 'data', 'reads', f'floor_roles_{chip}.json'))); RL.RO.clear(); RL.RO.update(RO); RP.RO = RO; XY = RP.coords()
    stf = os.path.join(PRIV, 'data', 'reads', f'{chip}_stated_lengths_twolengths.json')
    ST = json.load(open(stf)) if os.path.exists(stf) else {'measure': 2.18, 'measure_2': 1.38}
    OD = {'ibm_fez': 1.66}.get(chip, 2.18)
    dist = {int(w): min(float(np.hypot(XY[f][0] - XY[int(w)][0], XY[f][1] - XY[int(w)][1])) for f in RO['far']) for w in RO['witness_of']}
    def fam(A, p):
        if p == 'K': return A
        B = {k: v for k, v in A.items() if not k.startswith(('K', 'D'))}
        for k, v in A.items():
            if k.startswith(p) and (p != 'K' or not k.startswith('K2')): B['K' + k[len(p):]] = v
        return B
    reads = []
    for run in runs:
        try: m, A = RL.load(run)
        except (SystemExit, FileNotFoundError) as e: print('  skip', chip, run, e); continue
        P = {p: {w: v[0] for w, v in RP.per_clock(fam(A, p)).items()} for p in ('D', 'K', 'K2')}
        rows = [[w, r6(dist[w]), r6(P['D'].get(w, np.nan)), r6(P['K'].get(w, np.nan)), r6(P['K2'].get(w, np.nan))] for w in sorted(dist) if dist[w] >= 3 and any(w in P[p] for p in P)]
        reads.append({**runinfo(chip, run), 'clocks': rows})
    return {'chip': chip, 'date': '2026-10-07', 'dark_laid_us_per_look': OD, 'stated_measure_us': ST['measure'], 'stated_measure_2_us': ST['measure_2'],
            'n_looked_at_bits': len(RO['far']), 'reads': reads}


def main():
    os.makedirs(OUT, exist_ok=True)
    cols = ['clock', 'looked_at_within_2', 'intensity_sum_1_over_r2', 'nearest_looked_at_pitches', 'precession_deg_per_us', 'reported_look_us_fit_1_9', 'reported_look_us_3_and_9']
    # ---- layout A pool: the chip-days of look_3and9_*.txt
    cd = {}
    for f in sorted(glob.glob(os.path.join(PRIV, 'data/reads/look_3and9_*.txt'))):
        day = DAY[re.search(r'(\d{8})', f).group(1)]
        for c, k in re.findall(r'(ibm_\w+) read (\d+): maker', open(f).read()): cd.setdefault((c, day), set()).add(int(k))
    pool = []
    for (chip, day), ks in sorted(cd.items()):
        s = read_set(chip, f'lookwide_roles_{chip}.json', [R0[chip] + k for k in sorted(ks)], f'layout A, {chip} {day}', {'date': day, 'layout': 'A'}); pool.append(s)
        print('pool', chip, day, [r['run'] for r in s['reads']])
    json.dump({'columns': cols, 'chip_days': pool}, open(os.path.join(OUT, 'layout_A_pool.json'), 'w'), separators=(',', ':'))
    # ---- layout B (second random draw, 7 Oct), and the four-cluster ('flowers') layouts
    B = [read_set('ibm_pittsburgh', 'lookwide_roles_seedB_ibm_pittsburgh.json', [901, 902, 903], 'layout B, ibm_pittsburgh', {'date': '2026-10-07', 'layout': 'B'}),
         read_set('ibm_marrakesh', 'lookwide_roles_seedB_ibm_marrakesh.json', [911, 912, 913], 'layout B, ibm_marrakesh', {'date': '2026-10-07', 'layout': 'B'})]
    json.dump({'columns': cols, 'chip_days': B}, open(os.path.join(OUT, 'layout_B.json'), 'w'), separators=(',', ':'))
    C = [read_set('ibm_fez', 'lookwide_roles_cluster_ibm_fez.json', [921, 922, 923], 'four clusters, ibm_fez', {'date': '2026-10-07'}),
         read_set('ibm_pittsburgh', 'lookwide_roles_cluster_ibm_pittsburgh.json', [931, 932, 933], 'four clusters, ibm_pittsburgh', {'date': '2026-10-07'}),
         read_set('ibm_marrakesh', 'lookwide_roles_cluster_ibm_marrakesh.json', [951, 952, 953], 'four clusters, ibm_marrakesh', {'date': '2026-10-07'}),
         read_set('ibm_aachen', 'lookwide_roles_cluster_ibm_aachen.json', [961, 962, 963], 'four clusters, ibm_aachen', {'date': '2026-10-07'})]
    json.dump({'columns': cols, 'chip_days': C}, open(os.path.join(OUT, 'clusters.json'), 'w'), separators=(',', ':'))
    F = [floor_set('ibm_pittsburgh', [1031, 1032, 1033]), floor_set('ibm_fez', [1081, 1082, 1083]), floor_set('ibm_aachen', [1091, 1092, 1093])]
    json.dump({'columns': ['clock', 'distance_to_nearest_looked_at_pitches', 'dark_W_us', 'measure_W_us', 'measure_2_W_us'], 'chips': F}, open(os.path.join(OUT, 'floor.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
