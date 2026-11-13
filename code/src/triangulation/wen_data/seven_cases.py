#!/usr/bin/env python3
"""seven_cases.py -- the Seven's load-bearing data rows as Wen cases (6 Oct 2026, Wayfinder and Bones).
Each row: the statements that stand on it (load), the reading and every other ruler (value +- width), the instrument's baseline,
and the last runs (the time leg). Labelled by the SAME arithmetic Wen trains on (gen_train.py): one ruler -> NEXT; rulers split
> 1.5 widths -> HOLD; chip moved > 2 widths over the last runs -> HOLD; else COMMIT. Numbers from the ledger (§) and SEVEN.md.
Writes seven_cases.jsonl (one row per line, same message layout as train.jsonl) and prints the table."""
import json, math
from wen_common import chat, user_text

ROWS = [
    # name, load (statements), quantity, chip, unit, rulers [(name, v, w)], baseline (v, w, text), series [v...], source
    ('the maker look, Pittsburgh', ['ONE', 'THREE', 'FOUR', 'TWO (sky rows)', 'the maker look'],
     'spectator time of the readout over the stated duration', 'ibm_pittsburgh', 'x',
     [('the 3-and-9 slope', 1.0639, 0.022), ('the 1-9 fit', 1.0515, 0.009)], (1.0, 0.01, 'when the look is laid by us (Rigetti 0.99-1.01)'),
     [1.087, 1.040, 1.064], '§269; 2 / 4 / 5 Oct; 2 Oct is the earlier method'),
    ('the maker look, Phoenix', ['ONE', 'THREE', 'FOUR', 'TWO (sky rows)', 'the maker look'],
     'spectator time of the readout over the stated duration', 'ibm_phoenix', 'x',
     [('the 3-and-9 slope', 1.0811, 0.032), ('the 1-9 fit', 1.0519, 0.014)], (1.0, 0.01, 'when the look is laid by us (Rigetti 0.99-1.01)'),
     [1.1696, 0.9897, 1.0841], '§275; the three 6 Oct reads, 3-and-9'),
    ('the maker look against ours, one chip', ['ONE', 'THREE', 'FOUR', 'TWO (sky rows)', 'the maker look'],
     'spectator time of the readout over OUR laid duration', 'Rigetti Cepheus-1-108Q', 'x',
     [('the laid-time tone', 0.990, 0.012)], (1.0, 0.01, 'when the look is laid by us'),
     [0.994, 1.008, 0.968], 'SEVEN ONE (4 Oct); no maker-stated look exists on this chip, and IBM has no laid look: never both in one job'),
    ("the maker's clock ratio (outside clock)", ['FIVE', 'SIX', 'THREE'],
     "maker-stated T2:T1, the clock ratio that sorts three statements", 'ibm_phoenix', 'x',
     [("the maker's properties record", 0.851, 0.02)], (1.0, 0.05, 'T2 = T1'),
     [0.851, 0.851, 0.851], '§275: identical medians under two stamps; never read from inside our jobs'),
    ('the time leg, Pittsburgh', ['ONE', 'SIX'],
     'measured qubit time over spectator time (T/W)', 'ibm_pittsburgh', 'x',
     [('the 3-and-9 slope', 1.2168, 0.12), ('the 1-9 fit', 1.2886, 0.09)], (1.0, 0.05, 'T = W'),
     [1.477, 1.351, 1.217], '§269; 2 / 4 / 5 Oct'),
    ('the time leg, Phoenix', ['ONE', 'SIX'],
     'measured qubit time over spectator time (T/W)', 'ibm_phoenix', 'x',
     [('the 3-and-9 slope', 1.2960, 0.069), ('the 1-9 fit', 1.3467, 0.080)], (1.0, 0.05, 'T = W'),
     [1.1379, 1.4063, 1.3438], '§275; the three 6 Oct reads'),
    ('the 9/12 look, Phoenix free clocks', ['THREE'],
     'laid time per look over the maker look, 1 link', 'ibm_phoenix', 'x',
     [('the straight e-fold ruler', 0.760, 0.015), ('the curved ruler', 1.005, 0.013), ('the equal-hand ruler', 1.022, 0.03)], (1.0, 0.02, 'one look = the maker look'),
     [0.761, 0.774, 0.744], '§262 / §275 / §277; straight-ruler reads 5 Oct'),
    ('the |2> row at 1/phi, Cepheus', ['THREE'],
     '|2> population at 4 us, others half-way', 'Rigetti Cepheus-1-108Q', 'x',
     [('readout model A (clocks at rest)', 0.618, 0.0064), ('readout model B', 0.631, 0.0064)], (0.5, 0.05, 'half-way'),
     [0.612, 0.621, 0.629], 'SEVEN THREE; 5 Oct drift probe mean 0.6201 over 22 rounds'),
    ('the below-zero slope, Boston', ['FIVE'],
     'own-interval slope per push', 'ibm_boston', '',
     [('the own-interval ruler', -0.00139, 0.00029), ('the 90-us level', -0.00148, 0.00030), ('the one-exponential ruler', -0.00139, 0.00030)],
     (0.0, 0.0003, 'no pushes'), [-0.00139], 'SEVEN calls (Boston); one job: no series'),
    ('the crossing, Pittsburgh', ['TWO'],
     'excess after ten spaced X gates at 30 us', 'ibm_pittsburgh', '%',
     [('one-exponential bookkeeping', 2.03, 0.16), ("each qubit's own decay curve", -0.22, 0.20)], (0.0, 0.3, 'idle |0> after 300 us'),
     [2.00, 1.71, 2.03], 'SEVEN TWO (4 Oct)'),
    ('the neutron row, Kingston', ['SEVEN'],
     'excess of a |1> qubit after ten pushes, 30 us apart', 'ibm_kingston', '%',
     [('one-exponential bookkeeping', -1.33, 0.24), ("each qubit's own decay curve", -0.04, 0.20)], (0.0, 0.3, 'idle'),
     [-1.24, -1.33], 'SEVEN SEVEN (9/28, 4 Oct)'),
    ('the steps across clocks in one job', ['FOUR'],
     'the recursion steps read in order across three clocks of one event', 'ibm_kingston', 'x',
     [('the look triangle (one look, three clocks)', 1.087, 0.03)], (1.0, 0.01, 'no step'),
     [], 'SEVEN FOUR: steps 1, 3, 5 resident on the chip, never read in order in one job'),
]


def fmt(v, u):
    s = f'{v:.5f}'.rstrip('0').rstrip('.') if abs(v) < 0.01 else f'{v:.4f}'.rstrip('0').rstrip('.')
    return f'{s} {u}'.strip() if u else s


def label(rulers, series):
    if len(rulers) == 1:
        return 'NEXT', 'one ruler so far'
    split = max(abs(a[1] - c[1]) / math.hypot(a[2], c[2]) for a in rulers for c in rulers if a is not c)
    wmean = math.sqrt(sum(r[2] ** 2 for r in rulers)) / len(rulers)
    moved = (max(series) - min(series)) / wmean if len(series) > 1 else 0.0
    if split > 1.5:
        return 'HOLD', f'the rulers split by {split:.1f} widths'
    if moved > 2.0:
        return 'HOLD', f'the rulers agree, but the chip moved {moved:.1f} widths between the last runs'
    return 'COMMIT', f'{len(rulers)} rulers agree' + ('' if len(series) > 1 else ' (one run: no series)')


def main():
    out = []
    print(f"{'row':42} {'load':>4}  arithmetic")
    MEAN_OF = {'the maker look, Phoenix': 3, 'the time leg, Phoenix': 3}     # widths of a 3-read mean: the 'moved' test needs per-read widths
    for name, load, qty, chip, u, rulers, (b, bw, btxt), series, src in ROWS:
        first = f'{qty} on {chip}, {rulers[0][0]}: {fmt(rulers[0][1], u)} +- {fmt(rulers[0][2], u)}.'
        others = '; '.join(f'{r}: {fmt(v, u)} +- {fmt(w, u)}' for r, v, w in rulers[1:])
        base = f'{fmt(b, u)} +- {fmt(bw, u)} {btxt}.'
        ser = ('last runs read ' + ', '.join(fmt(x, u) for x in series) + '.') if len(series) > 1 else 'one run so far.'
        n = MEAN_OF.get(name, 1)
        mode, why = label(rulers, series)
        if n > 1 and 'moved' in why:
            mode, why = label([(r, v, w * n ** 0.5) for r, v, w in rulers], series)
        kind = 'one' if len(rulers) == 1 else 'split' if 'split' in why else 'drift' if 'moved' in why else 'agree'
        out.append(dict(name=name, load=load, kind=kind, mode=mode, why=f'{mode}: {why}', source=src,
                        messages=chat(user_text(first, base, ser, others)) + [{'role': 'assistant', 'content': mode}]))
        print(f'{name:42} {len(load):>4}  {mode}: {why}')
    with open('seven_cases.jsonl', 'w', encoding='utf-8') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print(f'wrote seven_cases.jsonl ({len(out)} rows)')


if __name__ == '__main__':
    main()
