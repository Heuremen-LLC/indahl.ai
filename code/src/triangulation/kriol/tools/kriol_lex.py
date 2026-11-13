#!/usr/bin/env python3
"""kriol_lex.py -- A KRIOL REFERENCE VOCABULARY, READ LOCALLY, NOTHING REDISTRIBUTED.
(Bones, 10 Oct 2026.)

THE BLOCKER THIS REMOVES. I could not tell real Kriol from mangled Kriol, so every Kriol reading was
unverifiable and Kriol could not enter the real test. A reference vocabulary fixes exactly that and
nothing else.

THE SOURCE. Holi Baibul, the Australian Kriol Bible -- translated over 27 years by a team of NATIVE
KRIOL SPEAKERS led by Rev. Canon Gumbuli Wurrumara with the Society for Australian Indigenous
Languages, launched at Katherine NT on 5 May 2007, revised 2019. The only complete Bible in any
Australian Aboriginal language. Verse-per-line text from eBible.org, code rop.

THE LICENCE, AND WHAT IT PERMITS HERE. CC BY-NC-ND 4.0 -- attribution, non-commercial, NO
DERIVATIVES. So: the text is read LOCALLY to count word types, and NOTHING derived from it is
published or redistributed -- no corpus, no dataset, no training. What leaves this script is a
frequency count used as a yes/no check on a model's own output, which is measurement, not
republication. No training on it either. If that line is ever to be crossed it is a conversation
with Ngukurr and the Bible Society, not a licence reading.

AND THE REGISTER CAVEAT, stated up front: this is scripture. It is a reference for WHETHER A WORD IS
KRIOL, not for how Kriol talks about arithmetic. Using it to judge vocabulary is sound; using it to
judge register would be wrong.
"""
import collections, json, os, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'source', 'rop_vpl.txt')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'kriol_lex.json')

freq = collections.Counter()
lines = 0
with open(SRC, encoding='utf-8', errors='replace') as f:
    for line in f:
        # verse-per-line: "BOOK C:V text". Drop the reference, keep the Kriol.
        txt = re.sub(r'^\S+\s+\d+:\d+\s*', '', line).strip()
        if not txt:
            continue
        lines += 1
        for w in re.findall(r"[a-zA-Z][a-zA-Z'\-]*", txt.lower()):
            freq[w] += 1

tot = sum(freq.values())
print(f'  source  {SRC}')
print(f'  {lines:,} verses, {tot:,} word tokens, {len(freq):,} word types')
print(f'\n  the 30 commonest Kriol words in it:')
for i, (w, n) in enumerate(freq.most_common(30)):
    end = '\n' if i % 6 == 5 else '  '
    print(f'    {w:<12}{n:>6}', end=end)
print()
# the words to score with: common enough to be real Kriol, not one-off names
core = {w: n for w, n in freq.items() if n >= 5}
print(f'  {len(core):,} word types appear 5+ times -- the reference set')
json.dump({'source': 'Holi Baibul (Australian Kriol Bible), eBible.org code rop',
           'translators': 'native Kriol speakers led by Rev. Canon Gumbuli Wurrumara, with SAIL',
           'licence': 'CC BY-NC-ND 4.0 -- read locally, nothing derived is redistributed',
           'verses': lines, 'tokens': tot, 'types': len(freq),
           'min_count': 5, 'lex': sorted(core)}, open(OUT, 'w'))
print(f'  -> {OUT}  (word list only, for checking model output; no text)')
