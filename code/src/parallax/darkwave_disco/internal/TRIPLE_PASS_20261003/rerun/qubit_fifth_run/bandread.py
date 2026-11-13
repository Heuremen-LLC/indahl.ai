"""bandread.py -- THE BAND RUN, read by the band's own analysis (out/the_middle/the_flash.py, copied with only its input folder, its output path and the
gaps it reads changed; the copy reproduces the 9/28 numbers exactly on the 9/28 record: data/band/flash_original_check.txt).
Converts each landed read (8 jobs: E0 / E1 at 20 / 50 / 100 / 2000 us) into the 9/28 file layout (E{0,1}_{gap}.npz with m0 = first look, m1 = second look,
columns in the order of meta.json's qubits), runs the copied analysis on it, and lays the cutoff curve beside the 9/28 one. No verdict word.
  python bandread.py"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(HERE, 'data', 'fire', 'ibm_marrakesh'); B = os.path.join(HERE, 'data', 'band')
JOBS = [(20, 'E1'), (20, 'E0'), (50, 'E1'), (50, 'E0'), (100, 'E1'), (100, 'E0'), (2000, 'E1'), (2000, 'E0')]
SRC = open(os.path.expanduser('~/bones-forge/parallax/out/the_middle/the_flash.py')).read()
PY = os.path.expanduser('~/bones-forge/venv_quantum/bin/python')


def convert(k):
    d = os.path.join(B, f'read{k}'); os.makedirs(d, exist_ok=True); qs = None; times = []
    for j, (gap, pub) in enumerate(JOBS):
        r = 200 + 10 * k + j; m = json.load(open(os.path.join(M, f'run{r}_meta.json')))
        if m.get('complete') is not True: raise SystemExit(f'run {r} not complete: read {k} not read')
        z = np.load(os.path.join(M, f'run{r}_results.npz'))
        if qs is None: qs = m['all_q']
        elif m['all_q'] != qs: raise SystemExit('bit order differs between jobs')
        if abs(m['rep_delay_us'] - gap) > 1e-6: raise SystemExit(f'run {r}: rep_delay {m["rep_delay_us"]} us, expected {gap}')
        np.savez_compressed(os.path.join(d, f'{pub}_{gap}.npz'), m0=np.asarray(z[f'{pub}__L1']), m1=np.asarray(z[f'{pub}__L2'])); times.append(m['start_time'])
    json.dump({'backend': 'ibm_marrakesh', 'qubits': qs, 'jobs_started': times, 'from_runs': [200 + 10 * k + j for j in range(8)]}, open(os.path.join(d, 'meta.json'), 'w'), indent=1)
    return d


def run_flash(d, tag):
    s = SRC.replace("RUN = os.path.expanduser('~/bones-forge/parallax/out/echo_20260928_122733')", f"RUN = {d!r}")
    s = s.replace("OUT_JSON = os.path.join(HERE, 'the_flash_results.json')", f"OUT_JSON = {os.path.join(B, tag + '.json')!r}")
    s = s.replace("DELAYS = [20, 50, 100, 250, 500, 1000, 2000]", "DELAYS = [20, 50, 100, 2000]")
    p = os.path.join(B, tag + '.py'); open(p, 'w').write(s)
    out = subprocess.run([PY, p], capture_output=True, text=True, cwd=B); open(os.path.join(B, tag + '.txt'), 'w').write(out.stdout + out.stderr)
    return out.stdout


def curve(txt):
    rows = {}
    for line in txt.splitlines():
        if line.startswith('cutoff 0.'):
            c = float(line.split()[1].rstrip(':')); r2 = float(line.split('R2=')[1].split()[0]); err = float(line.split('err=')[1].split()[0]); v = line.split('-> ')[1].split('  ')[0]
            rows[c] = (r2, err, v, line.split('entered=')[1] if 'entered=' in line else '')
    return rows


if __name__ == '__main__':
    curves = {'9/28 (the original record)': curve(open(os.path.join(B, 'flash_original_check.txt')).read())}
    for k in (1, 2, 3):
        try: d = convert(k)
        except SystemExit as e: print(f'read {k}: {e}'); continue
        curves[f'read {k}'] = curve(run_flash(d, f'flash_read{k}'))
    cuts = sorted(next(iter(curves.values())))
    print('THE BAND, read by its own analysis: how strongly the two inside clocks see each other (R^2 across bits, with its own bootstrap width) at each readout cutoff')
    print('cutoff  ' + ''.join(f'{n:>34}' for n in curves))
    for c in cuts:
        print(f'{c:.2f}    ' + ''.join(f"{(f'{v[c][0]:.3f} +- {v[c][1]:.3f} {v[c][2][:6]}' if c in v else 'CAN-T READ'):>34}" for v in curves.values()))
    print('\nwho enters / leaves at each cutoff is in data/band/flash_read{k}.txt; the 9/28 band: rising 0.62-0.65 (0.23 -> 0.43), gone at 0.66 (q14, q154 leave; q56 left at 0.65).')
