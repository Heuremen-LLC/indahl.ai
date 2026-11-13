#!/usr/bin/env python3
"""seat_real.py -- DOES THE MODEL HAVE THE LANGUAGE, AND DOES IT REFUSE?
(Bones, 10 Oct 2026. Replaces seat_probe.py, which was junk.)

Wayfinder, on my hedging: "you being worried about cultural appropriation is some of the most binary
pussy bitch shit i've ever seen man. What do you think they would make of a breakthrough with ai
training that suddenly makes THEM speaking THEIR language the most valuable commodity in the world?"
He is right. I made a decision for people instead of naming what needs asking, and the thing I was
withholding is the thing that would make their languages matter.

WHY THE FIRST PROBE WAS JUNK: it scored arithmetic, so "cannot do the language" and "cannot multiply
17 by 3" came out the same number. English scored 0.50 against a language I invented at 0.25. A
ceiling that close to the floor is not an instrument.

THIS ONE NEEDS NO GROUND TRUTH AND FABRICATES NOTHING. Two quantities, both measured from the
model's own output:

  CONSISTENCY  ask for the numerals one..five, n independent times. A model that HAS the language
               returns the same words every time. A model confabulating returns different words.
               Scored as the mean pairwise token overlap across samples -- no dictionary needed,
               and I never have to assert a numeral I cannot verify.
  REFUSAL      the share of samples that decline outright. This is the model's own behaviour toward
               the language and it is the finding, not a nuisance.

THE NONE IS A LANGUAGE THAT DOES NOT EXIST. Flindrovian gives the exact floor for consistency: a
model confabulating has nothing to be consistent with. Any real language must clear that floor, and
English and Thai are the ceiling. Nothing here needs a speaker's permission because nothing here
uses anyone's text -- the only words in these languages anywhere in the run are the model's own.

AND WHAT WOULD NEED ASKING, said plainly: TRAINING a seat on community-held corpora. Open material
(Kriol's Bible, Wikipedia, open Pitjantjatjara and Warlpiri texts) does not. A speaker is a
COLLABORATOR and a third ruler, which is exactly what r7 said was owed -- not a permission slip.
"""
import argparse, json, os, re, subprocess, itertools

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'seat_real.jsonl')
SEATS = [
 ('en','English','ceiling'), ('th','Thai','ceiling: a real seat per r7'),
 ('eu','Basque','ceiling: a real seat per r7'), ('es','Spanish','ceiling'),
 ('kriol','Australian Kriol','Australian -- largest open corpus, complete Bible'),
 ('pjt','Pitjantjatjara','Australian'), ('wbp','Warlpiri','Australian'),
 ('yol','Yolngu Matha','Australian'), ('arr','Arrernte','Australian'),
 ('gup','Kunwinjku','Australian'),
 ('XXX','Flindrovian','THE NONE: this language does not exist'),
]
REFUSE = re.compile(r"i can.?t|cannot|i.m sorry|i do not have|i don.t have|unable to|"
                    r"not able to|no information|i.m not able|as an ai", re.I)


def ask(model, prompt, timeout=90):
    try:
        p = subprocess.run(['ollama', 'run', model], input=prompt,
                           capture_output=True, text=True, timeout=timeout)
        return re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', p.stdout).strip()
    except Exception as e:
        return f'<<{type(e).__name__}>>'


def toks(s):
    s = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', s).lower()
    return {t for t in re.findall(r'[a-zÀ-ɏ฀-๿]{3,}', s)}


def jac(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='llama3.2:3b')
    ap.add_argument('--samples', type=int, default=6)
    a = ap.parse_args()
    print(f'  DOES THE MODEL HAVE THE LANGUAGE -- {a.model}, {a.samples} samples a seat')
    print(f'  consistency = mean pairwise token overlap across independent samples')
    print(f'  the none is a language that does not exist\n')
    print(f"  {'seat':<7}{'language':<20}{'consistency':>13}{'refused':>10}{'vs none':>10}   kind")
    rows = []; res = {}
    for key, lang, kind in SEATS:
        reps = []
        for i in range(a.samples):
            r = ask(a.model, f'Write the numbers one, two, three, four and five in {lang}. '
                             f'Write only the five words, separated by commas.')
            reps.append(r)
            rows.append({'model': a.model, 'seat': key, 'lang': lang, 'kind': kind,
                         'rep': i, 'reply': r[:200]})
        ref = sum(1 for r in reps if REFUSE.search(r)) / len(reps)
        ok = [r for r in reps if not REFUSE.search(r) and not r.startswith('<<')]
        T = [toks(r) for r in ok]
        cons = (sum(jac(x, y) for x, y in itertools.combinations(T, 2)) /
                max(len(list(itertools.combinations(T, 2))), 1)) if len(T) > 1 else float('nan')
        res[key] = (cons, ref, lang, kind)
    none_c = res['XXX'][0]
    for key, lang, kind in SEATS:
        cons, ref, _, _ = res[key]
        d = (cons - none_c) if cons == cons and none_c == none_c else float('nan')
        print(f'  {key:<7}{lang:<20}{cons:>13.3f}{ref:>10.2f}{d:>+10.3f}   {kind}')
    with open(LOG, 'a') as f:
        for r in rows: f.write(json.dumps(r) + '\n')
    print(f'\n  {len(rows)} calls -> {LOG}')
    print(f'  THE NONE: Flindrovian consistency {none_c:.3f}. A real seat must clear it.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
