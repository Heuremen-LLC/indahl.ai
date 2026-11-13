"""THE BLINK HOUR -- 2026-09-28 night (Wayfinder: "yes on one and two"). Whole Cepheus chip in parallel, 8 checks ~7.5 min apart.
Each check: PLAIN read | 'ba' (rung 2 -> read as 0) | rung 1<->2 RAMSEY at 1.5 us, two quadratures (rung 2's own pitch).
No outcome written.   python blink_hour.py dry | submit | collect | analyze"""
import json, math, os, sys, time
import numpy as np
import rigetti_chip as C
TAU_US = 1.5; SHOTS = 800; N_CHECK = 8; GAP_S = 450
def ramsey(fr, amps, quad):
    from braket.circuits import Circuit; from braket.pulse import PulseSequence, DragGaussianWaveform
    half = {q: amps[q] / 2 for q in C.QS}
    c = Circuit()
    for q in C.QS: c.rz(q, 0.0)
    for q in C.QS: c.rx(q, math.pi)                                      # to rung 1
    c.pulse_gate(C.QS, C.push(fr, half))                                 # half swap 1<->2
    ps = PulseSequence()
    for q in C.QS: ps = ps.delay(fr[q], C._ns(TAU_US))
    if quad == 'Y':
        for q in C.QS: ps = ps.shift_phase(fr[q], math.pi / 2)
    c.pulse_gate(C.QS, ps)
    c.pulse_gate(C.QS, C.push(fr, half))                                 # second half swap
    if quad == 'Y':
        ps2 = PulseSequence()
        for q in C.QS: ps2 = ps2.shift_phase(fr[q], -math.pi / 2)
        c.pulse_gate(C.QS, ps2)
    for q in C.QS: c.rx(q, math.pi)                                      # rung 1 -> read 0
    return Circuit().add_verbatim_box(c)
def items():
    fit = json.load(open(os.path.join(C.OUT, 'tune_fit.json'))); amps = {q: (fit[str(q)]['a_pi12'] if fit[str(q)]['swing'] > 0.3 else 0.0) for q in C.QS}
    dev, fr = C.dev_frames()
    return dev, [('plain', C.circ(fr, 'e', amps)), ('ba', C.circ(fr, 'ba', amps)), ('R12X', ramsey(fr, amps, 'X')), ('R12Y', ramsey(fr, amps, 'Y'))]
def main():
    mode = sys.argv[1]; c = N_CHECK * 4 * (C.PER_TASK + SHOTS * C.PER_SHOT)
    if mode == 'dry': dev, it = items(); print(f'{N_CHECK} checks x 4 = {N_CHECK * 4} tasks, ${c:.2f}'); print(str(it[2][1])[:900]); return
    if mode == 'submit':
        print('ledger', C.spend('blink hour: whole chip, 8 checks x (plain, ba, rung-2 Ramsey X/Y)', c))
        dev, it = items(); T = {'tasks': []}
        for chk in range(1, N_CHECK + 1):
            for tag, cc in it:
                t = dev.run(cc, shots=SHOTS, disable_qubit_rewiring=True); T['tasks'].append({'tag': [tag, chk], 'arn': t.id, 'sent': time.time()})
            json.dump(T, open(os.path.join(C.OUT, 'blink_tasks.json'), 'w'), indent=1); print('check', chk, 'sent', time.strftime('%H:%M:%S'), flush=True)
            if chk < N_CHECK: time.sleep(GAP_S)
        print('ALL SENT'); return
    if mode == 'collect': C.collect('blink_tasks.json', 'blink.npz'); return
if __name__ == '__main__': main()

def analyze():
    Z = dict(np.load(os.path.join(C.OUT, 'blink.npz'))); QS = C.QS; fit = json.load(open(os.path.join(C.OUT, 'tune_fit.json')))
    chks = sorted({json.loads(k)[1] for k in Z}); rows = []
    for k, q in enumerate(QS):
        g = lambda tag, ch: Z[json.dumps([tag, ch])][:, k].mean() if json.dumps([tag, ch]) in Z else np.nan
        pl = np.array([g('plain', c) for c in chks]); ba = np.array([1 - g('ba', c) for c in chks])
        X = np.array([1 - g('R12X', c) for c in chks]) - .5; Y = np.array([1 - g('R12Y', c) for c in chks]) - .5
        ph = np.unwrap(np.arctan2(Y, X)); amp = np.hypot(X, Y)
        nb = lambda p: np.sqrt(np.clip(p * (1 - p), 1e-4, None) / C.SH_BLINK if False else np.clip(p * (1 - p), 1e-4, None) / SHOTS)
        jump = lambda v, s: float(np.nanstd(v, ddof=1) / np.nanmean(s)) if np.all(np.isfinite(v)) else np.nan
        ph_noise = np.nanmean(np.sqrt(0.25 / SHOTS) / np.clip(amp, 0.05, None))
        rows.append(dict(q=q, pushed=fit[str(q)]['swing'] > 0.3, plain=pl.tolist(), ba=ba.tolist(), phase=ph.tolist(), amp=amp.tolist(),
                         j_plain=jump(pl, nb(pl)), j_ba=jump(ba, nb(ba)), j_phase=float(np.nanstd(ph, ddof=1) / ph_noise) if np.all(np.isfinite(ph)) else np.nan,
                         pitch_drift_khz=float((ph[-1] - ph[0]) / (2 * np.pi * TAU_US * 1e-6) / 1e3) if np.all(np.isfinite(ph)) else np.nan))
    json.dump(rows, open(os.path.join(C.OUT, 'blink_rows.json'), 'w'), indent=1, default=float)
    ok = [r for r in rows if r['pushed']]
    print(f'{len(chks)} checks over the hour, {len(ok)} qubits with a rung-2 push')
    for key, lab in (('j_plain', 'plain read (the qubit)'), ('j_ba', 'rung-2 read'), ('j_phase', "rung 2's pitch")):
        v = np.array([r[key] for r in ok]); print(f'   {lab:24s} jumps (1 = steady): median {np.nanmedian(v):.1f}; above 4: {int(np.nansum(v > 4))}  top {[(r["q"], round(r[key], 1)) for r in sorted(ok, key=lambda r: -(r[key] if r[key] == r[key] else 0))[:6]]}')
    for q in (52, 36, 5, 0, 48, 63, 24):
        r = next(x for x in rows if x['q'] == q)
        print(f"   q{q:<3} rung-2 read {[round(x, 3) for x in r['ba']]}\n        pitch phase {[round(x, 2) for x in r['phase']]}  plain {[round(x, 3) for x in r['plain']]}")
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'analyze': analyze()
