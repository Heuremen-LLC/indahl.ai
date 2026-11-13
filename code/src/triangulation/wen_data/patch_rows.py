#!/usr/bin/env python3
"""patch_rows.py -- the backward stooge pass (6 Oct 2026, Wayfinder and Bones). HYPOTHETICAL rows, never data.
For each candidate patch to the Seven's biggest hole (the maker look, load 5), the rows it could return under each outcome,
labelled by Wen's arithmetic and later read by the stooges. A patch fills the hole only if EVERY outcome lets Wen commit:
whatever comes back, the row stops holding. A patch that can come back still holding is description, not a patch.
Writes patch_rows.jsonl (flagged hypothetical: true) and prints the table."""
import json
from wen_common import chat, user_text
from seven_cases import fmt, label

W = 0.012  # a per-read width the size of today's (Phoenix 1-9 fit 0.014, Cepheus laid 0.012)
PATCHES = {
    'P1 series: IBM, same instrument, three reads spaced, stamp first': [
        ('the look still moves read to read', [('the 3-and-9 slope', 1.081, 0.032), ('the 1-9 fit', 1.052, 0.014)], [1.17, 0.99, 1.08]),
        ('the look holds still at 12/11', [('the 3-and-9 slope', 1.088, 0.032), ('the 1-9 fit', 1.085, 0.014)], [1.089, 1.092, 1.086]),
        ('the look holds still at 1.04', [('the 3-and-9 slope', 1.042, 0.032), ('the 1-9 fit', 1.038, 0.014)], [1.040, 1.043, 1.037]),
    ],
    "P2 observer: Cepheus, the maker's stated look and OUR laid look, witnessed in one job": [
        ("the maker's statement leaves out ~9 % (row 12/11, our look 1.00)",
         [('the 3-and-9 slope, maker-stated look', 1.090, W), ('the 1-9 fit, maker-stated look', 1.087, W)], [1.091, 1.088, 1.090], (1.000, W)),
        ('no conversion on this chip (row 1.00, our look 1.00)',
         [('the 3-and-9 slope, maker-stated look', 1.002, W), ('the 1-9 fit, maker-stated look', 0.998, W)], [1.001, 0.999, 1.003], (1.000, W)),
        ('the witness reads every look long (row 12/11, our look 12/11)',
         [('the 3-and-9 slope, maker-stated look', 1.090, W), ('the 1-9 fit, maker-stated look', 1.091, W)], [1.089, 1.092, 1.090], (1.090, W)),
    ],
    "P2-I observer: IBM, measure (2.18 us) and measure_2 (1.38 us) timed by the same clocks in one job": [
        ('the extra is a RATIO (W/O 1.06 at both lengths)',
         [('W/O on measure (2.18 us)', 1.060, W), ('W/O on measure_2 (1.38 us)', 1.062, W)], [1.059, 1.062, 1.060], (1.000, W)),
        ('the extra is a fixed OFFSET (0.13 us at both: W/O 1.060 / 1.094)',
         [('W/O on measure (2.18 us)', 1.060, W), ('W/O on measure_2 (1.38 us)', 1.094, W)], [1.059, 1.062, 1.060], (1.000, W)),
        ('NEITHER: the two looks read apart beyond both shapes',
         [('W/O on measure (2.18 us)', 1.060, W), ('W/O on measure_2 (1.38 us)', 0.990, W)], [1.059, 1.062, 1.060], (1.000, W)),
    ],
    'P2-R witness: Rigetti, OUR laid look at 0.5 / 1 / 1.5 / 2 us, the clocks timing each': [
        ('the clock is honest (W/laid 1.00 at every length)',
         [('W/laid at 1 us', 1.000, W), ('W/laid at 2 us', 0.998, W)], [1.002, 0.997, 1.000], (1.000, W)),
        ('the clock adds a fixed offset (W/laid 1.06 at 1 us, 1.03 at 2 us)',
         [('W/laid at 1 us', 1.060, W), ('W/laid at 2 us', 1.030, W)], [1.06, 1.03, 1.045], (1.000, W)),
    ],
    'P3 rulers: a third ruler for the time of the look (none exists)': [
        ('no third ruler can be built', [('the 1-9 fit', 1.052, 0.014)], [1.034, 1.052]),
    ],
}


def main():
    out = []
    print(f"{'patch / outcome (HYPOTHETICAL)':95} arithmetic")
    for patch, outcomes in PATCHES.items():
        for o in outcomes:
            name, rulers, series = o[:3]; bl = o[3] if len(o) > 3 else (1.0, 0.01)
            first = f'spectator time of the readout over the stated duration, {rulers[0][0]}: {fmt(rulers[0][1], "x")} +- {fmt(rulers[0][2], "x")}.'
            others = '; '.join(f'{r}: {fmt(v, "x")} +- {fmt(w, "x")}' for r, v, w in rulers[1:])
            ser = 'last runs read ' + ', '.join(fmt(x, 'x') for x in series) + '.'
            mode, why = label(rulers, series)
            if mode == 'COMMIT':
                import math
                m = sum(r[1] for r in rulers) / len(rulers); z = abs(m - bl[0]) / math.hypot(W, bl[1])
                why += f', {z:.1f} widths from our own look: ' + ('the maker statement leaves something out' if z > 2 else 'nothing beyond our own look')
            kind = 'one' if len(rulers) == 1 else 'split' if 'split' in why else 'drift' if 'moved' in why else 'agree'
            out.append(dict(name=f'{patch} | {name}', patch=patch, outcome=name, hypothetical=True, load=['the maker look'] * 5,
                            kind=kind, mode=mode, why=f'{mode}: {why}',
                            messages=chat(user_text(first, f'{fmt(bl[0], "x")} +- {fmt(bl[1], "x")} on our own laid look, read in the same job.', ser, others)) + [{'role': 'assistant', 'content': mode}]))
            print(f'{patch[:40]:40} | {name[:52]:52} {mode}: {why}')
    with open('patch_rows.jsonl', 'w', encoding='utf-8') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print(f'wrote patch_rows.jsonl ({len(out)} hypothetical rows)')


if __name__ == '__main__':
    main()
