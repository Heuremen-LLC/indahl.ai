#!/usr/bin/env python3
"""readcheck.py: the check block a reading carries before it enters a results file, a paper, a page or a public ledger.
Heuremen LLC, 30 Oct 2026. Spec: SPEC.md beside this file. Standard library only.
  readcheck.py new <folder> --packs Q,L,P,O --what "<the reading>"   append a dated template entry to <folder>/CHECKS.md
  readcheck.py check <CHECKS.md>                                       exit 0 only if the LAST entry is complete
  readcheck.py check-staged <CHECKS.md>                                exit 0 only if the staged diff adds a complete entry (used by the hook)
A field is answered when its text starts with holds:, fixed:, caught:, n/a: or cannot tell: and carries at least 12 more characters.
Packs: Q quantum hardware, L language-model evaluations, P public copy, O live operations. The core fields are always required."""
import sys, os, re, datetime, subprocess
CORE = [('I', 'the none built first, like for like; what the gate drops, by arm'), ('II', 'gap: item flips counted against the repeat floor before any net'),
        ('III', 'sign: do the cells agree in sign; product or sum'), ('V', 'ruler named, two side by side where they can disagree'),
        ('VI', 'four outcomes, both alternatives (zero and the size that matters) tested'), ('R', 'counts, dates, versions read from the record; post hoc labelled')]
PACKS = {'Q': [('QA', "vendor's number is the same quantity; record the job ran under; rebuttal tested"), ('QB', 'idle/none like for like, same job'),
               ('QC', 'known-good, floor, ceiling, synth plants every alternative'), ('QD', 'four outcomes, copies by gap, chips by value, units'),
               ('QE', 'more than two answers; post hoc labelled; no mechanism named'), ('QF', 'history and times from the job record; plans before jobs'),
               ('QG', 'referees got raw files; flags acted on; paper, site and bill agree')],
         'L': [('L1', 'parser hand-read before any rate'), ('L2', 'no rate seen before the hand-check'), ('L3', 'setup/harness/extraction named on both sides'),
               ('L4', 'repeat floor per machine; run-time server settings recorded'), ('L5', 'recount from released files, keys matched'),
               ('L6', 'unread/dropped counted by reason, per arm'), ('L7', 'gold not built from the labeller it scores'), ('L8', 'paired; seed width; position copy floor; batch'),
               ('L9', 'prompt does not contain the answer'), ('L10', 'pinned name is not pinned behaviour'), ('L11', 'aged datasets/tools substituted with counts and an addendum'),
               ('L12', 'same-family referee or labeller disclosed')],
         'P': [('P1', 'quotes verbatim'), ('P2', 'every figure says where it lives and which version'), ('P3', 'setting labels match the source'),
               ('P4', 'no cause where only a rule-out was measured'), ('P5', 'every interval says what it is'), ('P6', 'summary no stronger than the reading'),
               ('P7', 'ledger first, one release path, verified live'), ('P8', 'rendered page checked, scripts served'), ('P9', 'house style rules'), ('P10', 'post hoc labelled')],
         'O': [('O1', 'new job registered with the scheduler and the watch'), ('O2', 'failures called failures'), ('O3', 'GPU budget set before sharing a GPU'), ('O4', 'liveness by completed work'),
               ('O5', 'paths absolute, PATH set'), ('O6', 'one GPU job per machine')]}
ANS = re.compile(r'^\s*-?\s*([A-Z]+\d*)\s*[:|]\s*(holds|fixed|caught|n/a|cannot tell)\s*:\s*(.{12,})$', re.I)
def entries(text):
    parts = re.split(r'(?m)^## (?=\d{4}-\d{2}-\d{2})', text); return [p for p in parts[1:]]
def missing(entry):
    m = re.search(r'(?m)^packs:\s*([A-Z,\s]*)$', entry); packs = [x.strip() for x in (m.group(1) if m else '').split(',') if x.strip()]
    need = [k for k, _ in CORE] + [k for p in packs for k, _ in PACKS.get(p, [])]
    got = {m.group(1).upper() for m in (ANS.match(l) for l in entry.splitlines()) if m}
    return [k for k in need if k.upper() not in got], packs
def new(folder, packs, what):
    p = os.path.join(folder, 'CHECKS.md'); d = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    L = [f'## {d} {what}', f'packs: {",".join(packs)}', '(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)']
    L += [f'- {k}: TODO ({desc})' for k, desc in CORE] + [f'- {k}: TODO ({desc})' for pk in packs for k, desc in PACKS[pk]]
    open(p, 'a').write(('\n' if os.path.exists(p) else '# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.\n\n') + '\n'.join(L) + '\n')
    print('appended a template entry to', p)
def check_text(text, src):
    es = entries(text)
    if not es: print(f'REFUSED {src}: no dated entry'); return 1
    miss, packs = missing(es[-1])
    if miss: print(f'REFUSED {src}: last entry leaves unanswered: ' + ', '.join(miss)); return 1
    print(f'ok {src}: last entry complete (core + packs {",".join(packs) or "none"})'); return 0
if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'new':
        packs = a[a.index('--packs') + 1].split(',') if '--packs' in a else []; what = a[a.index('--what') + 1] if '--what' in a else ''
        bad = [p for p in packs if p not in PACKS]
        if bad: sys.exit('unknown pack: ' + ','.join(bad))
        new(a[1], packs, what)
    elif a and a[0] == 'check': sys.exit(check_text(open(a[1]).read(), a[1]))
    elif a and a[0] == 'check-staged':
        f = a[1]; added = subprocess.run(['git', 'diff', '--cached', '-U0', '--', f], capture_output=True, text=True).stdout
        text = '\n'.join(l[1:] for l in added.splitlines() if l.startswith('+') and not l.startswith('+++'))
        sys.exit(check_text(text, f + ' (staged additions)'))
    else: print(__doc__); sys.exit(2)
