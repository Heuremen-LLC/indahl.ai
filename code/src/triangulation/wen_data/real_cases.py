#!/usr/bin/env python3
"""real_cases.py -- Wen cases built from the house's OWN reads (6 Oct 2026, Wayfinder and Bones). Parsed from the read files, never typed.
Every look read on disk (look_3and9_*.txt: six chips, every day) becomes three cases per chip-day -- W/O, T/O, T/W -- each read on two
rulers (the 3-and-9 slope, the 1-9 fit; value = the reads' mean, width = the reads' own widths combined), with the reads in firing order as
the series. Labelled by the SAME arithmetic Wen trains on (seven_cases.label). These are measurement numbers from our runs on our accounts:
inside LEGAL.md (inputs = our data, target = the arithmetic label). Phoenix is held out by chip: real_train.jsonl (five chips) and
real_test.jsonl (Phoenix) so a round can train on five chips and be judged on the sixth.
Run: python3 real_cases.py"""
import glob, json, math, os, re
from wen_common import chat, user_text
from seven_cases import fmt, label

READS = os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run/data/reads')
LINE = re.compile(r'^(ibm_\w+) read (\d+): maker ([\d.]+) us \| W fit 1-9 ([\d.]+)\+-([\d.]+) \| W 3-and-9 ([\d.]+)\+-([\d.]+) \| T fit 1-9 ([\d.]+)\+-([\d.]+) \| T 3-and-9 ([\d.]+)\+-([\d.]+)')
QTY = {'W/O': 'spectator time of the readout over the stated duration', 'T/O': 'measured qubit time of the readout over the stated duration',
       'T/W': 'measured qubit time over spectator time'}
BASE = {'W/O': (1.0, 0.01, 'when the look is laid by us (Rigetti 0.99-1.01)'), 'T/O': (1.0, 0.05, 'T = O'), 'T/W': (1.0, 0.05, 'T = W')}


def ratio(a, wa, b, wb):
    r = a / b
    return r, r * math.hypot(wa / a, wb / b)


def main():
    groups = {}
    for f in sorted(glob.glob(os.path.join(READS, 'look_3and9_*.txt'))):
        day = re.search(r'_(\d{8})\.txt$', f).group(1)
        tag = os.path.basename(f)
        for line in open(f):
            m = LINE.match(line.strip())
            if not m:
                continue
            chip, rd, O = m.group(1), int(m.group(2)), float(m.group(3))
            Wf, wWf, W39, wW39, Tf, wTf, T39, wT39 = map(float, m.groups()[3:])
            g = groups.setdefault((chip, tag), {'day': day, 'reads': []})
            g['reads'].append({'read': rd, '1-9 fit': {'W/O': ratio(Wf, wWf, O, 1e-9), 'T/O': ratio(Tf, wTf, O, 1e-9), 'T/W': ratio(Tf, wTf, Wf, wWf)},
                               '3-and-9 slope': {'W/O': ratio(W39, wW39, O, 1e-9), 'T/O': ratio(T39, wT39, O, 1e-9), 'T/W': ratio(T39, wT39, W39, wW39)}})
    rows = []
    for (chip, tag), g in groups.items():
        R = sorted(g['reads'], key=lambda r: r['read'])
        for q in QTY:
            rulers = []
            for rn in ('3-and-9 slope', '1-9 fit'):
                v = [r[rn][q][0] for r in R]; w = [r[rn][q][1] for r in R]
                rulers.append((f'the {rn}', sum(v) / len(v), math.sqrt(sum(x * x for x in w)) / len(w)))
            series = [r['1-9 fit'][q][0] for r in R]
            # the 'moved' test compares PER-READ values, so it needs the per-read width (the rulers' widths are of the n-read mean:
            # sqrt(n) too narrow). Fixed 6 Oct after the first pass called shot noise 'the chip moved' on 16 rows.
            per_read = [(n, v, w * math.sqrt(len(R))) for n, v, w in rulers]
            mode, why = label(rulers, series) if 'split' in label(rulers, series)[1] else label(per_read, series)
            first = f'{QTY[q]} on {chip}, {rulers[0][0]}: {fmt(rulers[0][1], "x")} +- {fmt(rulers[0][2], "x")}.'
            others = '; '.join(f'{n}: {fmt(v, "x")} +- {fmt(w, "x")}' for n, v, w in rulers[1:])
            b, bw, bt = BASE[q]
            ser = ('last runs read ' + ', '.join(fmt(x, 'x') for x in series) + '.') if len(series) > 1 else 'one run so far.'
            kind = 'one' if len(rulers) == 1 else 'split' if 'split' in why else 'drift' if 'moved' in why else 'agree'
            rows.append(dict(name=f'{chip} {q} ({tag})', chip=chip, quantity=q, source=tag, kind=kind, mode=mode, why=f'{mode}: {why}', real=True,
                             messages=chat(user_text(first, f'{fmt(b, "x")} +- {fmt(bw, "x")} {bt}.', ser, others)) + [{'role': 'assistant', 'content': mode}]))
    # PER-READ cases (6 Oct, aimed at Wen's holes: split rulers, drift): each single read's two rulers with that read's own widths, the day's other
    # reads in firing order as the series. Real agree / split / drift cases from our own instrument, one per read and quantity.
    for (chip, tag), g in groups.items():
        R = sorted(g['reads'], key=lambda r: r['read'])
        for i, r in enumerate(R):
            for q in QTY:
                rulers = [(f'the {rn}', r[rn][q][0], r[rn][q][1]) for rn in ('3-and-9 slope', '1-9 fit')]
                series = [x['1-9 fit'][q][0] for x in R[:i + 1]][-3:]
                mode, why = label(rulers, series)
                first = f'{QTY[q]} on {chip}, {rulers[0][0]}: {fmt(rulers[0][1], "x")} +- {fmt(rulers[0][2], "x")}.'
                others = '; '.join(f'{n}: {fmt(v, "x")} +- {fmt(w, "x")}' for n, v, w in rulers[1:])
                b, bw, bt = BASE[q]
                ser = ('last runs read ' + ', '.join(fmt(x, 'x') for x in series) + '.') if len(series) > 1 else 'one run so far.'
                kind = 'one' if len(rulers) == 1 else 'split' if 'split' in why else 'drift' if 'moved' in why else 'agree'
                rows.append(dict(name=f'{chip} {q} read {r["read"]} ({tag})', chip=chip, quantity=q, source=tag, kind=kind, mode=mode, why=f'{mode}: {why}', real=True,
                                 messages=chat(user_text(first, f'{fmt(b, "x")} +- {fmt(bw, "x")} {bt}.', ser, others)) + [{'role': 'assistant', 'content': mode}]))
    tr = [r for r in rows if r['chip'] != 'ibm_phoenix']; te = [r for r in rows if r['chip'] == 'ibm_phoenix']
    for path, part in (('real_train.jsonl', tr), ('real_test.jsonl', te)):
        with open(path, 'w', encoding='utf-8') as f:
            for r in part:
                f.write(json.dumps(r) + '\n')
    from collections import Counter
    print(f'{len(rows)} real cases from {len(groups)} chip-days: train (five chips) {len(tr)}, test (Phoenix) {len(te)}')
    print('labels:', dict(Counter(r['mode'] for r in rows)), '| by quantity:', {q: dict(Counter(r['mode'] for r in rows if r['quantity'] == q)) for q in QTY})
    for r in rows:
        print(f"  {r['name']:62} {r['why']}")


if __name__ == '__main__':
    main()
