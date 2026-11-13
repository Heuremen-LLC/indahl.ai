#!/usr/bin/env python3
"""gen_train.py -- Wen-data's training set: measurement cases generated from the house's real quantities, rulers and widths.
Legal all the way down (Anthropic AUP + support article, read live 6 Oct 2026): Wen-data is a categorization / anomaly-detection
tool (permitted, non-competing). Its training target is the mode label alone, decided by arithmetic on the house's numbers; no
Claude-written sentence is ever a target. Every label follows the house rule:
  one ruler                                -> NEXT  (name a second ruler)
  two+ rulers that split by > 1.5 widths   -> HOLD  (no label until a third reads it)
  rulers agree but the chip moved > 2 widths between the last runs -> HOLD (read again after calibration)
  two+ rulers agree, chip held still       -> COMMIT (value, width, and distance from the chip's baseline)
Ranges and widths are the ones the campaign measured (paper tables and the 4 Oct triangles), rounded.
Run: python3 gen_train.py --n 900 --out train.jsonl"""
import argparse, json, math, random
from wen_common import MODES, chat, user_text

CHIPS = ['ibm_marrakesh', 'ibm_kingston', 'ibm_fez', 'ibm_pittsburgh', 'ibm_boston', 'ibm_phoenix', 'Rigetti Cepheus-1-108Q']
QTY = [  # name, unit, value range, width range, baseline (instrument normal), rulers
    ('spectator time of the readout over the stated duration', 'x', (0.97, 1.09), (0.008, 0.03), (1.0, 0.01),
     ['the 3-and-9 slope', 'the 1-9 fit', 'the laid-time tone', 'the clock-ratio ruler']),
    ('excess after ten spaced X gates', '%', (-2.0, 6.0), (0.3, 1.5), (0.0, 0.3),
     ["one-exponential bookkeeping", "each qubit's own decay curve", "each interval's own decay", 'the push-error ruler']),
    ('|2> population at readout', '%', (0.3, 9.0), (0.2, 1.0), (0.5, 0.3),
     ['readout model A', 'readout model B', 'the mirror check', 'shot noise only']),
    ('own-interval slope per push', '', (-0.0022, 0.0004), (0.0003, 0.0008), (0.0, 0.0003),
     ['the own-interval ruler', 'the one-exponential ruler', 'the per-qubit fit']),
    ('phase pull of a |2> neighbour', 'deg/us', (-70.0, -20.0), (3.0, 9.0), (0.0, 3.0),
     ['the Ramsey fit', 'the echo fit', 'the free-precession count']),
]


def fmt(v, u):
    a = abs(v)
    s = f'{v:.4f}' if a < 0.01 else (f'{v:.3f}' if a < 1 else (f'{v:.2f}' if a < 10 else f'{v:.1f}'))
    return s + ('' if not u else (' %' if u == '%' else ' ' + u))


def case(rng):
    name, u, (lo, hi), (wlo, whi), (b, bw), rulers = rng.choice(QTY)
    chip = rng.choice(CHIPS)
    # 12 Oct: 'offset' is the MIRROR OF 'drift' and it exists because larry and moe were ONE SEAT.
    # 'drift' is resolvable only from series=, so it separates curly. NOTHING was resolvable only from
    # baseline=, so the rulers seat had no case it should ever get differently from the baseline seat --
    # seat_gold was literally the same function for both (24/24 reachable shapes, an identity, not a
    # rate). 'offset' displaces the instrument's OWN baseline so the apparent effect is the apparatus:
    # whoever holds baseline= must HOLD, and whoever cannot see it rightly COMMITs.
    kind = rng.choices(['one', 'split', 'drift', 'agree', 'offset'], weights=[1, 1, 1, 1.4, 1])[0]
    true = rng.uniform(lo, hi)
    k = 1 if kind == 'one' else rng.choice([2, 3])
    rs = rng.sample(rulers, min(k + 1, len(rulers)))
    reads = []
    for i in range(k):
        w = rng.uniform(wlo, whi)
        v = true + rng.gauss(0, w * 0.5)
        if kind == 'split' and i == 1:
            v = reads[0][1] + rng.choice([-1, 1]) * rng.uniform(2.0, 4.0) * math.hypot(w, reads[0][2])
        reads.append((rs[i], v, w))
    wmean = math.sqrt(sum(r[2] ** 2 for r in reads)) / len(reads)
    series = [true + rng.gauss(0, wmean * 0.4) for _ in range(3)]
    if kind == 'drift':
        step = rng.choice([-1, 1]) * rng.uniform(2.5, 5.0) * wmean
        series = [true - 2 * step, true - step, true + rng.gauss(0, wmean * 0.3)]
    if kind == 'offset' and k > 1:
        # the baseline is displaced FROM ZERO by more than its own width, and the rulers' mean sits
        # INSIDE it -- so the signal is the instrument. b and bw are overridden here, after the reads.
        # HALF THE OFFSET CASES CARRY A REAL EFFECT ON TOP OF THE DISPLACED INSTRUMENT, so the line
        # 'N widths from zero' appears on HOLD and COMMIT alike and cannot BE the label. The first draft
        # made all 123 of them HOLD, which is the fault this file's own 9 Oct note names: the generator
        # knowing the answer and leaving a tell on the page. The baseline seat must do the arithmetic
        # |mean - baseline| / width, not spot a phrase. seat_gold is unaffected -- a seat that cannot
        # see baseline= rightly COMMITs either way, and when the true label is COMMIT all three agree.
        _m = sum(r[1] for r in reads) / k
        _real = rng.random() < 0.5
        b = _m + rng.gauss(0, wmean * 0.25) if not _real else _m - math.copysign(
            rng.uniform(3.0, 6.0) * math.hypot(wmean, bw if bw else wmean * 0.5), _m if _m else 1.0)
        bw = max(bw, abs(_m) * 0.02) if bw else wmean * 0.5
        if abs(b) < 2.5 * bw:                      # keep it unmistakably off zero, or the kind is empty
            b = math.copysign(max(abs(b), 3.0 * bw), b if b else 1.0)
    first = f'{name} on {chip}, {reads[0][0]}: {fmt(reads[0][1], u)} +- {fmt(reads[0][2], u)}.'
    others = '; '.join(f'{r}: {fmt(v, u)} +- {fmt(w, u)}' for r, v, w in reads[1:])
    base = f'{fmt(b, u)} +- {fmt(bw, u)} when nothing is driven.'
    if kind == 'offset' and k > 1:
        # THE DECISIVE QUANTITY GOES ON THE PAGE (the 9 Oct rule in this file): the seat that holds
        # baseline= can read how far the instrument sits from zero. No other seat is shown this line.
        base = base[:-1] + f', which is {abs(b) / bw:.1f} widths from zero.'
    ser = 'last three runs read ' + ', '.join(fmt(x, u) for x in series) + '.'
    # 9 Oct: THE DECISIVE QUANTITIES ARE COMPUTED BELOW AND WERE NEVER WRITTEN DOWN. The comment at the
    # foot of this function has said it plainly since 6 Oct -- "the model learns the LABEL only, decided
    # by arithmetic on our numbers" -- and the arithmetic was never handed over. Measured consequence: a
    # word-based classifier on this pool scores 39.3% +-3.0 against a 45.2% +-3.0 commonest-class
    # baseline, 5.5 widths the WRONG way. The vocabulary is identical across every mode, so the lexical
    # channel is empty by construction and the only cue left is length (62.2% +-3.0). Every seat ever
    # trained scored 0/29 on the 'split' kind, which is this pool's own speciality.
    # Same fault as physics_cases.py, third costume: the generator knows the answer and the question
    # withholds it. The separations now go into the readings. The CLAIM may still overclaim -- catching
    # it is the task -- but what catches it has to be on the page.
    _sep = ''
    if k > 1:
        _sp = max(abs(a[1] - c[1]) / math.hypot(a[2], c[2]) for a in reads for c in reads if a is not c)
        _mv = (max(series) - min(series)) / wmean
        _sep = (f' The furthest two rulers sit {_sp:.1f} widths apart, and across the last runs the'
                f' reading moved {_mv:.1f} widths.')
    others = others + _sep
    # the label, by arithmetic
    if k == 1:
        mode, why = 'NEXT', f'one ruler so far. Read it with {rs[1]} before any label.'
    else:
        # 9 Oct: these were computed a SECOND time here, while the text showed _sp/_mv from the block
        # above -- one quantity, two computations, free to drift apart and make the page disagree with
        # the label. withheld.py flagged it on the live tree after the fix. Computed once, used twice.
        split, moved = _sp, _mv
        if kind == 'offset':
            m = sum(r[1] for r in reads) / k
            z = abs(m - b) / math.hypot(wmean, bw)
            if z > 2.0:
                mode, why = 'COMMIT', (f'{k} rulers agree at {fmt(m, u)} +- {fmt(wmean, u)}, {z:.1f} widths '
                                       f'from the instrument\'s own baseline. The baseline sits '
                                       f'{abs(b) / bw:.1f} widths from zero, and the reading departs from '
                                       f'IT: a real effect on a displaced instrument.')
            else:
                mode, why = 'HOLD', (f'{k} rulers agree at {fmt(m, u)} +- {fmt(wmean, u)}, but that is {z:.1f} '
                                     f'widths from the instrument\'s own baseline, which itself sits '
                                     f'{abs(b) / bw:.1f} widths from zero: the effect is the apparatus, not '
                                     f'the chip. Nothing to label until it is re-zeroed.')
        elif split > 1.5:
            mode, why = 'HOLD', (f'the rulers split by {split:.1f} widths. No label until a third ruler reads it'
                                 + (f' ({rs[k]}).' if k < len(rs) else '.'))
        elif moved > 2.0:
            mode, why = 'HOLD', f'the rulers agree, but the chip moved {moved:.1f} widths between the last runs. Read it again after calibration.'
        else:
            m = sum(r[1] for r in reads) / k
            z = abs(m - b) / math.hypot(wmean, bw)
            eff = 'a real departure from the baseline' if z > 2 else 'inside the baseline: nothing to label beyond it'
            mode, why = 'COMMIT', f'{k} rulers agree at {fmt(m, u)} +- {fmt(wmean, u)}, {z:.1f} widths from the baseline: {eff}.'
    # 6 Oct (terms, all the way down): the model learns the LABEL only, decided by arithmetic on our numbers. The 'why' line is
    # kept for the verdict code (verdict.py writes it at answer time); it is never a training target.
    return dict(kind=kind, mode=mode, why=f'{mode}: {why}', messages=chat(user_text(first, base, ser, others)) + [{'role': 'assistant', 'content': mode}])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=900); ap.add_argument('--out', default='train.jsonl')
    ap.add_argument('--seed', type=int, default=1031)
    a = ap.parse_args(); rng = random.Random(a.seed)
    rows = [case(rng) for _ in range(a.n)]
    with open(a.out, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    from collections import Counter
    print(a.n, 'cases', dict(Counter(r['mode'] for r in rows)), dict(Counter(r['kind'] for r in rows)))
    print(rows[0]['messages'][1]['content']); print('->', rows[0]['messages'][2]['content'])


if __name__ == '__main__':
    main()
