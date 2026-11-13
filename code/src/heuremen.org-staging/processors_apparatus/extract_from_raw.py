#!/usr/bin/env python3
"""extract_from_raw.py -- OPTIONAL step. Reduces the private raw IBM result files to the compact JSON in data/.

You do NOT need this to check the numbers: verify_processors_apparatus.py reads data/*.json only.
This script is here so a reader can see exactly how each JSON file was cut from the raw job output
(every per-qubit number below is one line of arithmetic on the raw I/Q shots; nothing is fitted here).

It needs numpy and the raw files (parallax/out/qubit_fifth_run/data/fire/<chip>/run<N>_results.npz, ~26 GB, not published).
It only READS the raw tree and writes into ./data/.  No network, no IBM account, no job is submitted.

  python extract_from_raw.py

Common reduction used everywhere (same as the private readers readlook_wide.py / readtime.py / readclose.py):
  each qubit's two reference clouds F0/OFF -> level 0 and F1/ON -> level 1 are taken from the same job;
  a shot's level is  Re[(x - c0) * conj(d)] / |d|^2  with c0 = mean OFF cloud, d = mean ON cloud - c0;
  'separation' = |d| / sqrt(mean |OFF - c0|^2 / 2)  (cloud distance in cloud widths).
"""
import glob, json, os, re, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')

RAW_ROOT = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run'
FIRE = os.path.join(RAW_ROOT, 'data', 'fire')
READS = os.path.join(RAW_ROOT, 'data', 'reads')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'data')
os.makedirs(OUT, exist_ok=True)
R5 = lambda x: [round(float(v), 5) for v in x]


def load_meta(chip, r):
    return json.load(open(os.path.join(FIRE, chip, f'run{r}_meta.json')))


def load_npz(chip, r, last_register=False):
    """last_register=True: for look-wide jobs, keep the final register of each circuit (every bit looked at once) as readlook_wide.load does."""
    z = np.load(os.path.join(FIRE, chip, f'run{r}_results.npz'))
    if not last_register:
        return {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}
    A = {}
    for k in z.files:
        base, reg = k.split('__'); A.setdefault(base, {})[reg] = np.asarray(z[k]).astype(complex)
    return {b: v[sorted(v, key=lambda x: int(x[1:]))[-1]] for b, v in A.items()}


def frame(A, off, on):
    c0 = A[off].mean(0); d = A[on].mean(0) - c0
    sep = np.abs(d) / np.sqrt((np.abs(A[off] - c0) ** 2).mean(0) / 2)
    proj = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    return proj, sep


def level_and_se(A, key, proj):
    p = proj(A[key]); return p.mean(0), p.std(0, ddof=1) / np.sqrt(p.shape[0])


# ----------------------------------------------------------------------------------------------------------- 1. SORT (T/W per chip-day)
# the look-ladder jobs: chip -> first run number minus 0 (same table as readlook_wide.py)
LOOK_R0 = {'ibm_marrakesh': 310, 'ibm_kingston': 330, 'ibm_pittsburgh': 350, 'ibm_fez': 410, 'ibm_boston': 430, 'ibm_phoenix': 540, 'ibm_aachen': 800}
WIN = [0, 10, 20, 30, 60, 120, 240]; LOOKS = [1, 2, 3, 4, 6, 9]; OWN = [10, 20, 40]


def heron_sight(RO):
    """lookwide plan: how many looked-at bits ('far') sit within 2 bit pitches of each clock (readproximity.coords / sight). Heron 156-bit layout only."""
    E = {tuple(sorted(e)) for e in RO['edges']}; xy = {}
    for r in range(8):
        for i in range(16): xy[20 * r + i] = (float(i), 2.0 * r)
    for q in [q for q in range(RO['n']) if q not in xy]:
        low = min(x for e in E if q in e for x in e if x != q); xy[q] = (xy[low][0], xy[low][1] + 1.0)
    F = np.array([xy[q] for q in RO['far']])
    return {int(w): int((np.hypot(*(F - np.array(xy[int(w)])).T) <= 2 + 1e-9).sum()) for w in RO['witness_of']}


def sort_run(chip, run, RO, n2):
    m = load_meta(chip, run)
    if m.get('complete') is not True: return None
    A = load_npz(chip, run, last_register=True)
    c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0
    sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)
    lv = {k: (np.real((v - c0) * np.conj(d)) / np.abs(d) ** 2).mean(0) for k, v in A.items()}
    WOF = {int(k): v for k, v in RO['witness_of'].items()}
    H = {a: (2 * lv[f'{a}|X'] - 1) - 1j * (2 * lv[f'{a}|Y'] - 1) for a in [f'T{t}' for t in WIN] + [f'K{k}' for k in LOOKS]}
    keep = [w for w in sorted(WOF) if abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3]
    ang = {a: np.angle(H[a] / H['T0']) for a in H}
    wit = []
    for w in keep:
        wit.append([w, (n2 or {}).get(w, -1)] + R5([ang['T10'][w], ang['T20'][w], ang['T30'][w]] + [ang[f'K{k}'][w] for k in LOOKS]))
    far = []
    for q in [q for q in RO['far'] if sep[q] > 3]:
        far.append([q] + R5([lv[f'AW{t}'][q] for t in OWN] + [lv[f'A{k}'][q] for k in LOOKS]))
    return {'run': run, 'job_id': m.get('job_id'), 'start': m.get('start_time'), 'witness_rows': wit, 'far_rows': far}


def build_sort():
    DAY = {'20261004': '4 Oct', '20261005': '5 Oct', '20261006': '6 Oct'}
    sets = {}
    for f in sorted(glob.glob(os.path.join(READS, 'look_3and9_*.txt'))):
        day = DAY.get(re.search(r'(\d{8})', f).group(1), '?')
        for c, k in re.findall(r'(ibm_\w+) read (\d+): maker', open(f).read()):
            sets.setdefault((c, day), set()).add(LOOK_R0[c] + int(k))
    sets[('ibm_aachen', '6 Oct')] = {801, 802, 803}      # no look_3and9 file exists for Aachen; the look-ladder jobs are runs 801-803
    out = {'note': 'per chip-day: per run, one row per kept witness clock [qubit, looked-at bits within 2 pitches (-1 = layout not Heron, unknown), '
                   'angle at 10/20/30 us laid, angle after k=1,2,3,4,6,9 looks] (radians), and one row per kept looked-at bit '
                   '[qubit, own level at 10/20/40 us fading, own level after k=1,2,3,4,6,9 looks]. LOOKS=[1,2,3,4,6,9].', 'chipdays': []}
    for (chip, day), runs in sorted(sets.items()):
        RO = json.load(open(os.path.join(READS, f'lookwide_roles_{chip}.json')))
        n2 = heron_sight(RO) if RO['n'] == 156 else None
        rr = [sort_run(chip, r, RO, n2) for r in sorted(runs)]
        rr = [x for x in rr if x]
        out['chipdays'].append({'chip': chip, 'day': day, 'runs': rr})
        print('sort', chip, day, [x['run'] for x in rr], file=sys.stderr)
    json.dump(out, open(os.path.join(OUT, 'sort_witness_and_looked_at.json'), 'w'), separators=(',', ':'))


# ----------------------------------------------------------------------------------------------------------- 2/4. TIME runs (T1 ruler copies, bend, idle)
def build_time():
    runs = []
    for f in sorted(glob.glob(os.path.join(FIRE, 'ibm_*', 'run*_results.npz'))):
        import zipfile
        if not any(n.startswith('RULER|ON|n300|a') for n in zipfile.ZipFile(f).namelist()): continue
        chip = f.split('/')[-2]; r = int(re.search(r'run(\d+)_', f).group(1)); m = load_meta(chip, r)
        if m.get('complete') is not True: continue
        A = load_npz(chip, r)
        proj, sep = frame(A, 'OFF|p0', 'ON|p0'); g = np.where(sep > 4)[0]
        lv = {k: proj(v).mean(0) for k, v in A.items()}
        rows = []
        for q in g:
            row = [int(q)]
            for c in 'abc':
                row += [lv[f'RULER|ON|n{w}|{c}'][q] for w in (30, 100, 300, 600)]
            row += [lv['RULER|OFF|n300'][q], lv['RULER|OFF|n600'][q]]
            rows.append([row[0]] + R5(row[1:]))
        runs.append({'chip': chip, 'run': r, 'job_id': m.get('job_id'), 'start': m.get('start_time'), 'qubits_kept': len(g), 'rows': rows})
        print('time', chip, r, len(g), file=sys.stderr)
    json.dump({'note': 'per run, per readable qubit: [qubit, then for ruler copies a,b,c: level of |1> after 30,100,300,600 us idle, then idle-|0> level after 300 and 600 us]. '
                       'levels: OFF cloud = 0, ON cloud = 1, from the same job. readable = cloud separation > 4 widths.', 'runs': runs},
              open(os.path.join(OUT, 'time_runs_ruler_copies.json'), 'w'), separators=(',', ':'))


# ----------------------------------------------------------------------------------------------------------- 3. PARK (hold run 71-73, Pittsburgh) + idle (run 121) + 5. push run 91-93
def build_park_idle_push():
    chip = 'ibm_pittsburgh'; out = {'park': [], 'idle_run121': None, 'push': []}
    for r in (71, 72, 73):
        m = load_meta(chip, r); A = load_npz(chip, r)
        proj, sep = frame(A, 'OFF|w0', 'ON|w0')
        keys = {'N0': 'ON|N0', 'P1': 'ON|P1', 'P3': 'ON|P3', 'P9': 'ON|P9'}
        L, S = {}, {}
        for n, k in keys.items(): L[n], S[n] = level_and_se(A, k, proj)
        out['park'].append({'run': r, 'job_id': m['job_id'], 'start': m['start_time'], 'shots': m['shots'],
                            'sep': R5(sep), **{f'lv_{n}': R5(L[n]) for n in keys}, **{f'se_{n}': [round(float(x), 6) for x in S[n]] for n in keys}})
    m = load_meta(chip, 121); A = load_npz(chip, 121)
    proj, sep = frame(A, 'F0', 'F1')
    z, zse = level_and_se(A, 'Z300', proj); _, f0se = level_and_se(A, 'F0', proj)   # f0se: error of the OFF reference cloud itself
    g = np.where(sep > 4)[0]
    out['idle_run121'] = {'run': 121, 'job_id': m['job_id'], 'start': m['start_time'], 'shots': m['shots'], 'columns': ['qubit', 'level of idle |0> after 300 us', 'shot error of that level', 'shot error of the OFF reference cloud'], 'rows': [[int(q), round(float(z[q]), 5), round(float(zse[q]), 6), round(float(f0se[q]), 6)] for q in g]}
    for r in (91, 92, 93):
        m = load_meta(chip, r); A = load_npz(chip, r)
        proj, sep = frame(A, 'OFF|p0', 'ON|p0'); g = np.where(sep > 4)[0]
        d = {}
        for k in ('OFF|p0', 'OFF|p2', 'OFF|p10', 'ON|p0', 'ON|p2', 'ON|p10'):
            lvk, sek = level_and_se(A, k, proj); d[k] = (lvk, sek)
        out['push'].append({'run': r, 'job_id': m['job_id'], 'start': m['start_time'], 'shots': m['shots'],
                            'rows': [[int(q)] + [round(float(d[k][0][q]), 5) for k in d] + [round(float(d[k][1][q]), 6) for k in d] for q in g],
                            'columns': ['qubit'] + ['lv ' + k for k in d] + ['se ' + k for k in d]})
    json.dump(out, open(os.path.join(OUT, 'pittsburgh_park_idle_push.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    which = sys.argv[1:] or ['sort', 'time', 'pitt']
    if 'sort' in which: build_sort()
    if 'time' in which: build_time()
    if 'pitt' in which: build_park_idle_push()
