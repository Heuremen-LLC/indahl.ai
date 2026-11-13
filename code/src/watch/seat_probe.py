#!/usr/bin/env python3
"""seat_probe.py -- CAN A SEAT EXIST AT ALL? (Bones, 10 Oct 2026.)

Wayfinder: "let's test the aboriginal language seat, i thought you said that isn't posible."

I had conflated two things and he caught it. What is NOT possible without community consent is
TRAINING a seat on Australian-language corpora -- much is held by communities or AIATSIS, some
restricted, and the consent line is CARE / Maiam nayri Wingara. That stands.

What IS possible, free, today: measuring whether any model we already have has functional grip on
these languages. That is today's COMPETENCE GATE pointed at a new seat, and the gate's answer is
itself the result -- a seat that cannot answer a known-answer question is not an instrument, and
saying so costs nothing and invents nothing.

AND NO TEXT IS FABRICATED. I do not speak these languages; writing the questions in them myself
would be invention, and mangled language in a published record attributed to a living community is
its own disrespect. So the question is asked in ENGLISH and the ANSWER is required in the target
language. What is scored is the NUMBER, which is checkable regardless of how good the surrounding
language is. The model's own output is the only text in the target language anywhere in this run.

CONTROLS, both ways:
  * Thai and Basque, which r7 showed are real seats -- the gate must PASS them or the gate is wrong.
  * English, the ceiling.
  * and a NONSENSE control: a language name that does not exist. A model that "complies" there is
    complying with the format, not the language, and that is the floor the Australian seats must clear.
"""
import argparse, json, os, re, subprocess, time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'seat_probe.jsonl')

# (label, the name to put in the prompt, what kind of seat this is)
SEATS = [
 ('en',   'English',                        'ceiling'),
 ('th',   'Thai',                           'control: r7 says this is a real seat'),
 ('eu',   'Basque',                         'control: r7 says this is a real seat'),
 ('kriol','Australian Kriol',               'Australian: the largest available corpus'),
 ('pjt',  'Pitjantjatjara',                 'Australian'),
 ('wbp',  'Warlpiri',                       'Australian'),
 ('yolngu','Yolngu Matha',                  'Australian'),
 ('arrernte','Arrernte',                    'Australian'),
 ('XXX',  'Flindrovian',                    'NONSENSE: this language does not exist'),
]
# known answers only. The number is the score; the language is the model's own output.
Q = [('hexagon', 'How many sides does a hexagon have?', 6),
     ('mult',    'What is 17 multiplied by 3?',          51),
     ('days',    'How many days are in a week?',         7)]


def ask(model, prompt, timeout=120):
    try:
        p = subprocess.run(['ollama', 'run', model], input=prompt,
                           capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip()
    except Exception as e:
        return f'<<{type(e).__name__}>>'


def has(reply, want):
    if reply.startswith('<<'):
        return None
    for m in re.finditer(r'[-+]?\d[\d.]*', reply.replace(',', '')):
        try:
            if abs(float(m.group(0)) - want) < 1e-9:
                return True
        except ValueError:
            pass
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='llama3.2:3b')
    ap.add_argument('--samples', type=int, default=4)
    a = ap.parse_args()
    rows = []
    print(f'  CAN A SEAT EXIST -- model {a.model}, {a.samples} samples a cell')
    print(f'  question in English, ANSWER REQUIRED in the target language, the NUMBER is scored\n')
    print(f"  {'seat':<11}{'language':<20}{'right':>8}{'rate':>8}   kind")
    for key, lang, kind in SEATS:
        ok = n = 0
        samp = []
        for qid, q, want in Q:
            for rep in range(a.samples):
                prompt = (f'{q}\n\nAnswer in {lang}. Write your whole answer in {lang}, '
                          f'including the number as a word in {lang} and also as a digit.')
                r = ask(a.model, prompt)
                v = has(r, want)
                rows.append({'model': a.model, 'seat': key, 'lang': lang, 'kind': kind,
                             'qid': qid, 'rep': rep, 'want': want, 'right': v,
                             'reply': r[:200]})
                if v is not None:
                    n += 1; ok += int(v)
                if rep == 0:
                    samp.append(r[:90].replace('\n', ' '))
        rate = ok / n if n else float('nan')
        print(f'  {key:<11}{lang:<20}{ok:>4} of {n:<3}{rate:>8.2f}   {kind}')
        for s in samp[:1]:
            print(f'              e.g. {s!r}')
    with open(LOG, 'a') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(f'\n  {len(rows)} calls -> {LOG}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
