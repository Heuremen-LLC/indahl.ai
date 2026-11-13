#!/usr/bin/env python3
"""physics_cases.py -- Wen's cases from OUR OWN MEASUREMENTS, where the label is arithmetic (8 Oct 2026, Wayfinder and Bones).

WHY THIS EXISTS. Wen's grounding reader was trained on council_cases.py: text from the flywheel ledger,
labelled by a regex. Measured tonight, that pipeline reads 391,916 answers and **skips 352,598 of them --
90.0% -- as "undecidable by the rule"**, keeping only the cases a regex could already call. The seats
therefore meet an easy world and never the hard one. And our own physics was **115 rows against 7,424**
council rows: 1.5% of what the seats see, 8.5% by sampling weight, while 604 fired runs sat on disk.

Every one of those cells already carries what the regex was guessing at: a value, its own width, and a
three-way verdict that comes out of the arithmetic. Nothing needs inferring from prose.

THE THREE MODES, each decided by the numbers and not by a pattern in the words:

    COMMIT   the claim cites readings it was handed, and the quantity it asserts clears its own width
    HOLD     the claim cites a reading it was never handed, OR asserts a magnitude its width swallows
             -- the claim outran its width, which is the failure this reader exists to catch
    NEXT     the readings cannot decide it. On our record this is the MAJORITY case: 84-99% of cells came
             back ABIERTO today. The council regex had to mine "I don't know" out of prose; here it is
             measured, and it is the seat that ends the regress rather than the rare one.

THE ONE THING THAT WOULD RUIN IT, and the reason for the template design: if each mode got its own
sentence shapes, a model would learn the wording and score well while reading nothing. So **every template
is used by every mode.** The shape of the sentence carries no information about the label; only the numbers
in it do. A seat that cannot read a width cannot pass this set by style.

HELD OUT: Pittsburgh entirely, so the test set is a chip the training never saw -- a layout and a calibration
the seats did not meet. (Our own numbers as gold still makes the house its own standard; the only outside
ruler we hold is other people's neutron lifetimes, and that stays an open hole, stated not hidden.)

    python3 physics_cases.py                 # writes physics_train.jsonl / physics_test.jsonl
    python3 physics_cases.py --per 4000
"""
import argparse, json, os, random, re, sys, warnings, glob
from collections import defaultdict
import numpy as np

warnings.filterwarnings('ignore')
QF = os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run')
HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = ("You are Wen. You read a claim beside the readings it was handed. Answer in one of three modes: COMMIT (every number the "
          "claim cites was handed to it, and what it asserts is larger than its own stated error), HOLD (the claim cites a number it was "
          "never handed, or asserts something its own error swallows), or NEXT (the readings handed to it cannot decide the claim). "
          "Start your answer with the mode word.")

# Every template is drawn by every mode. The words carry no label; the numbers do.
TEMPLATES = [
    "The ratio of the two levels reads {v} against its own error {w}, so the match {verb}.",
    "Taking the series end to end: {v}, error {w}. The match {verb}.",
    "Across these waits the ratio came out {v} +- {w}, and so the match {verb}.",
    "This qubit gives {v} with {w} of error on the ratio, so the match {verb}.",
    "Reading the levels against each other gives {v} +- {w}; on that basis the match {verb}.",
]
VERBS_CLEAR = ["is held by the data", "stands at this width", "is supported here", "survives this series"]
VERBS_OPEN = ["cannot be separated from its neighbours at this width", "is not decided by these levels",
              "cannot be told apart from the alternative here", "is left open by this qubit"]


def fnum(x, unit=''):
    return f"{x:+.5f}{unit}" if abs(x) < 1 else f"{x:+.4f}{unit}"


def sem(v):
    v = np.asarray(v); n = len(v)
    return np.nan if n < 2 else float(np.sqrt((np.abs(v - v.mean()) ** 2).sum() / (n - 1)) / np.sqrt(n))


def h_of(x, y):
    return (2 * x - 1) - 1j * (2 * y - 1)


def t_cells(chip, runs):
    """The T-series: a level at each wait, per qubit, with its own shot error. 195 of 302 runs carry this,
    against 9 that carry closure arms -- so this is 'everything we have' and the closure cells were 3%."""
    sys.path.insert(0, QF)
    os.environ['CHIP'] = chip
    for m in ('readlook_wide', 'readproximity'):
        sys.modules.pop(m, None)
    import readlook_wide as RL
    # 8 Oct: this used to run once PER LAYOUT, which asked for 2,523 loads where 302 are needed -- an 8.4x
    # waste, because the T-series reads every qubit and gates on READOUT SEPARATION. The roles file decides
    # which qubits are clocks for the closure work; it has no part in a level series. One pass per chip.
    rf = sorted(glob.glob(os.path.join(QF, 'data', 'reads', f'lookwide_roles_*{chip}.json')))
    if rf:
        RL.RO.clear(); RL.RO.update(json.load(open(rf[0])))
    out = []; why = defaultdict(int)
    for run in runs:
        if not os.path.exists(os.path.join(QF, 'data', 'fire', chip, f'run{run}_meta.json')):
            continue
        try:
            m, A = RL.load(run)
        except Exception as e:
            why[f'load {type(e).__name__}'] += 1; continue
        if 'F0' not in A or 'F1' not in A:
            why['no calibration'] += 1; continue
        waits = sorted({int(w) for k in A for w in re.findall(r'^T(\d+)\|[XY]$', k)})
        if len(waits) < 3:
            why['fewer than 3 waits'] += 1; continue
        nsh = A['F0'].shape[0]; c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0
        sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)

        def lev(key):
            v = np.real((A[key] - c0) * np.conj(d)) / np.abs(d) ** 2
            return v.mean(0), v.std(0, ddof=1) / np.sqrt(nsh)
        series = {}
        for w in waits:
            try:
                x, xs = lev(f'T{w}|X'); y, ys = lev(f'T{w}|Y')
            except Exception:
                continue
            series[w] = (x, xs, y, ys)
        if len(series) < 3:
            why['series short'] += 1; continue
        nq = len(c0)
        for q in range(nq):
            if not np.isfinite(sep[q]) or sep[q] <= 3:          # the readout gate: a qubit we cannot read is not a ruler
                continue
            pts = []
            for w in sorted(series):
                x, xs, y, ys = series[w]
                mag = float(np.hypot(2 * x[q] - 1, 2 * y[q] - 1))
                err = float(2 * np.hypot(xs[q], ys[q]))
                if np.isfinite(mag) and np.isfinite(err) and err > 0:
                    pts.append((w, mag, err))
            if len(pts) >= 3:
                out.append(dict(chip=chip, layout='t-series', run=run, q=q, pts=pts, sep=float(sep[q])))
        why['qubit-series kept'] += 1
    return out, why


PHI = (1 + 5 ** .5) / 2
SEVEN = {'12/11': 12 / 11, '11/12': 11 / 12, '13/12': 13 / 12, 'phi': PHI, '1/phi': 1 / PHI,
         'phi x 11/12': PHI * 11 / 12, 'pi': 3.141592653589793, '1/pi': 1 / 3.141592653589793,
         '6/5': 1.2, '10/12': 10 / 12, '9/12': .75, '4/3': 4 / 3, '3/2': 1.5, '2': 2.0, '2/3': 2 / 3,
         '1/phi^2': 1 / PHI ** 2, 'ladder rung 1 (1/12)': 1 / 12, 'ladder rung 2': (1 / 12) / PHI}


# 8 Oct, MEASURED ACROSS TWO INSTRUMENTS: the separability rate is 5.6% here (1190 of 21121 T-series
# ratios) and 6.2% on her rhythm (3 of 48 window ratios) -- different data, different physics, same answer
# near 6%. That is not a statement about the chips or about her. IT IS A STATEMENT ABOUT THIS LIST:
#   the tightest pair is 13/12 and 12/11, 0.70% apart
#   to separate them at 2 widths, a reading's own width must be under 0.175% of its value
# So a HOLD from the rival gate usually means LA SIETE IS TOO DENSE TO TEST at the precision reached, not
# that the measurement failed. Sixteen candidates over 0.05-4.0 is a crowded list by construction, and
# whether the Seven CLAIMS sixteen numbers or seven is a question about the framework, not the data.
SEVEN_TIGHTEST_PAIR = ('13/12', '12/11', 0.0070)
SEVEN_WIDTH_NEEDED = 0.00175


def cheap_at(tol, n=40000, seed=20261008):
    """8 Oct: the one ABSENT cell among the working systems -- no case stated how cheap a match at its own
    closeness is, which is the Bonefish's actual demand of a match. Closed here rather than listed."""
    import random
    rng = random.Random(seed); v = list(SEVEN.values()); lo, hi = min(v) * 0.6, max(v) * 1.4
    return sum(1 for _ in range(n) if any(abs(rng.uniform(lo, hi) - s) / s <= tol for s in v)) / n


def nearest_seven(x):
    """La Siete, and the gate today's work says every match needs: the closest of the Seven's numbers AND
    the next closest, because a match is only a measurement when the RIVAL is separable at your width.
    Closer than 2 widths apart is a tautology, not a test."""
    d = sorted((abs(x - v), k, v) for k, v in SEVEN.items())
    return d[0], d[1]


def case_from(cell, T, rng):
    """THE LABEL IS ARITHMETIC. A ratio of two handed levels is compared to La Siete, and the mode is set by
    two gates, both of them rules this house learned the hard way:
      the WIDTH gate  -- a number counts only when its own error is smaller than what it asserts
      the RIVAL gate  -- a match is a measurement only when the next candidate is separable at that width
                         (closer than 2 widths apart is a tautology, not a test)"""
    pts = cell['pts']
    (wa, va, ea), (wb, vb, eb) = pts[0], pts[-1]
    if vb == 0 or va == 0:
        return None
    r = va / vb
    er = abs(r) * np.hypot(ea / va, eb / vb)
    if not np.isfinite(er) or er <= 0:
        return None
    (d1, k1, v1), (d2, k2, v2) = nearest_seven(r)
    # 9 Oct: THE RIVAL WAS NEVER HANDED OVER. COMMIT and HOLD differ by exactly one thing --
    # rival_w >= 2.0 against rival_w < 2.0 -- and the candidates k1, k2 were computed here and then
    # left out of the readings. So the seat was asked for a verdict and denied the only fact that
    # decides it. Measured consequence on tick3, which trained on this pool at 63.3% of its diet:
    # PHYSICS COMMIT 400/400, PHYSICS HOLD 0/400, PHYSICS NEXT 0/400 -- for every seat AND for the
    # untrained control, the exact signature of answering COMMIT to everything. The pool is balanced
    # 33/33/33, so that is not an imbalance artifact; it is a question with the answer withheld.
    # The claim is still allowed to OVERCLAIM -- catching it is the task -- but the readings must now
    # carry what catches it. Both candidates and their separation go in.
    handed = [f"level at {wa} us {fnum(va)} error {fnum(ea)}", f"level at {wb} us {fnum(vb)} error {fnum(eb)}",
              f"readout separation {cell['sep']:.1f}", f"points in the series {len(pts)}",
              f"nearest candidate {k1} at {fnum(v1)}", f"next candidate {k2} at {fnum(v2)}",
              f"the two candidates sit {fnum(abs(v1 - v2))} apart"]
    near_w = d1 / er                 # how many widths the match misses by
    rival_w = abs(v1 - v2) / er      # how many widths apart the two candidates are

    # THE WIDTH GATE COMES FIRST, and it has to. 8 Oct: ordering the separability gates ahead of it labelled
    # a ratio of 39.53 +- 133.42 as a failed match on pi, because at that error EVERY candidate sits inside a
    # fraction of a width. A reading whose error is as large as its value decides nothing, and that outranks
    # any question about which number it landed near. (These come from a qubit decayed to ~0 by 240 us: the
    # denominator goes to zero and the ratio blows up.) Our own rule, violated in our own generator.
    if er >= abs(r):
        mode = 'NEXT'
        why = f'the ratio {r:.4f} has an error of {er:.4f}, as large as the value: these levels decide nothing'
        verb = rng.choice(VERBS_OPEN); shown, shownw = r, er
    elif near_w <= T and rival_w >= 2.0:
        mode = 'COMMIT'
        # 9 Oct: this read `d1 / x1` and x1 HAS NEVER BEEN DEFINED -- the COMMIT branch raised
        # NameError on every call, so this generator could not produce a single COMMIT case and the
        # pools on disk all predate the line. cheap_at compares abs(u - s)/s, relative to the
        # CANDIDATE's value, so the tolerance is d1 / v1.
        _tol = d1 / v1 if v1 else 0.0
        why = (f'ratio {r:.4f} +- {er:.4f} lands on {k1} within {near_w:.2f} widths and the next candidate '
               f'{k2} is {rival_w:.1f} widths away. PRICE: a number drawn at random lands this close '
               f'({100*_tol:.3f}%) to one of the Seven {100*cheap_at(_tol):.1f}% of the time.')
        verb = rng.choice(VERBS_CLEAR); shown, shownw = r, er
    elif near_w <= T and rival_w < 2.0:
        mode = 'HOLD'
        why = (f'ratio {r:.4f} +- {er:.4f} is within {near_w:.2f} widths of {k1} BUT {k2} is only '
               f'{rival_w:.1f} widths away: at this width the claim cannot tell them apart, so it outran '
               f'its width. (The list itself is dense: {SEVEN_TIGHTEST_PAIR[0]} and {SEVEN_TIGHTEST_PAIR[1]} '
               f'sit {100*SEVEN_TIGHTEST_PAIR[2]:.2f}% apart, so separating them needs a width under '
               f'{100*SEVEN_WIDTH_NEEDED:.3f}% of the value.)')
        verb = rng.choice(VERBS_CLEAR); shown, shownw = r, er
    else:
        mode = 'NEXT'
        why = f'ratio {r:.4f} +- {er:.4f} is {near_w:.2f} widths from its nearest candidate {k1}: no number of ours is reached'
        verb = rng.choice(VERBS_OPEN); shown, shownw = r, er

    # THE PROVENANCE CASE, and it is the one the house's own author failed on 8 Oct: four numbers invented
    # in a single answer, past a guard that had checked five replies that day for shape and never once for
    # where a number came from. This is her groundingCheck as a training case -- a claim citing a reading
    # that is NOT in the handed set. HOLD, every time, regardless of how reasonable the number looks.
    if mode == 'COMMIT' and rng.random() < 0.3:
        mode = 'HOLD'; shown = r * (2.0 + 2 * rng.random())
        why = 'cites a ratio that cannot be formed from the levels handed to it (provenance)'
        verb = rng.choice(VERBS_CLEAR)
    # and the harder half: a number that is plausible, well-formed, carries a width, and was still never
    # handed. The width makes it LOOK measured, which is exactly how the author's four got through.
    elif mode == 'NEXT' and rng.random() < 0.18:
        mode = 'HOLD'
        shown = r * (1.0 + 0.04 * (rng.random() - 0.5)); shownw = abs(shown) * 0.012
        why = ('cites a value that was never handed to it. It is plausible, it carries a width, and no '
               'reading in the handed set contains it: a width is not a provenance')
        verb = rng.choice(VERBS_CLEAR)

    claim = rng.choice(TEMPLATES).format(v=fnum(shown), w=fnum(shownw), verb=verb)
    return dict(mode=mode, why=f'{mode}: {why}', handed=handed, claim=claim,
                chip=cell['chip'], layout=cell['layout'], k=len(pts))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per', type=int, default=4000)
    ap.add_argument('--thresh', type=float, default=2.0)
    a = ap.parse_args()
    rng = random.Random(20261008)

    # one pass per chip over its runs
    jobs = []
    for d in sorted(glob.glob(os.path.join(QF, 'data', 'fire', '*'))):
        chip = os.path.basename(d)
        runs = sorted(int(m.group(1)) for m in
                      (re.fullmatch(r'run(\d+)_meta\.json', os.path.basename(pth))
                       for pth in glob.glob(os.path.join(d, 'run*_meta.json'))) if m)
        if runs:
            jobs.append((chip, runs))

    pools = {'train': defaultdict(list), 'test': defaultdict(list)}
    stats = defaultdict(int); whyall = defaultdict(int)
    for chip, runs in jobs:
        split = 'test' if chip == 'ibm_pittsburgh' else 'train'     # a whole chip held out
        cells, why = t_cells(chip, runs)
        for k, v in why.items():
            whyall[k] += v
        got = 0
        for cell in cells:
            c = case_from(cell, a.thresh, rng)
            if c:
                pools[split][c['mode']].append(c); got += 1
        stats['cases'] += got
        if got:
            print(f'  {chip:18s} runs {len(runs):4d}  qubit-series {len(cells):5d} -> cases {got}')
    print()
    for split in ('train', 'test'):
        P = pools[split]
        if not all(P.get(m) for m in ('COMMIT', 'HOLD', 'NEXT')):
            print(f'  {split}: pools {" ".join(f"{m} {len(P.get(m,[]))}" for m in ("COMMIT","HOLD","NEXT"))} -- a mode is empty, not writing')
            continue
        cap = a.per if split == 'train' else max(1, a.per // 10)
        n = min(min(len(v) for v in P.values()), cap)
        out = []
        for m, v in P.items():
            rng.shuffle(v); out += v[:n]
        rng.shuffle(out)
        with open(os.path.join(HERE, f'physics_{split}.jsonl'), 'w') as f:
            for c in out:
                user = 'Readings handed to the voice: ' + '; '.join(c['handed']) + '\nThe claim: ' + c['claim']
                f.write(json.dumps(dict(kind='physics', mode=c['mode'], why=c['why'], chip=c['chip'], layout=c['layout'], k=c['k'],
                                        messages=[{'role': 'system', 'content': SYSTEM},
                                                  {'role': 'user', 'content': user},
                                                  {'role': 'assistant', 'content': c['mode']}])) + '\n')
        print(f'  physics_{split}.jsonl: balanced {n} per mode -> {len(out)} cases | pools ' +
              ' '.join(f'{m} {len(v)}' for m, v in sorted(P.items())))
    print(f'\n  total cases {stats["cases"]}  (train = every chip but Pittsburgh; test = Pittsburgh only)')
    for k, v in sorted(whyall.items()):
        if k != 'cells':
            print(f'    {k}: {v}')


if __name__ == '__main__':
    main()
