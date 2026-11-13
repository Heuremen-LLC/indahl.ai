#!/usr/bin/env python3
"""mood2.py -- THE MOOD TEST, PRODUCTION SIDE, WITH A KRIOL SEAT AND A NONSENSE FLOOR.
(Bones, 10 Oct 2026. Design written before the run.)

WHY A SECOND DESIGN. mood_test.py asked the question IN each language, so translation quality was a
confound I could only bound, and it ruled out any language I cannot write. Here the question is
ALWAYS IN ENGLISH and the ANSWER IS REQUIRED IN THE TARGET LANGUAGE. The prompt is then identical
for every seat, translation quality leaves the design entirely, and a language I do not speak can
take part because the only text in it is the model's own.

WHY KRIOL IS THE SHARP CASE AND NOT JUST ANOTHER SEAT. The first ladder was INFLECTIONAL: productive
subjunctive / vestigial / none. Australian Kriol has no inflectional mood, but marks modality
OBLIGATORILY with preverbal particles (garra, maitbi). So it splits the hypothesis:

    if the effect is SPEAKERS HAVING TO MARK UNCERTAINTY    Kriol behaves like Spanish
    if the effect is INFLECTION specifically                Kriol behaves like English

No rung on the old ladder predicts it either way. That is the whole reason to run it.

THE FLOOR IS A LANGUAGE THAT DOES NOT EXIST. If "answer in Flindrovian" also produces holds, then
holding is a refusal artefact and not mood -- so the nonsense seat is the none, and it is built in
rather than argued about afterwards.

AND THE COMPETENCE GATE STAYS: two known-answer questions per seat. A seat that cannot answer those
is not an instrument, and its UNKNOWNs are incompetence. Refusals are counted SEPARATELY from holds,
because "I can't help with that" is not "the value is unknown" -- that distinction is the whole
reason the first probe today was junk.

    python3 mood2.py --model llama3.2:3b --samples 8
"""
import argparse, json, os, re, subprocess, time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'mood2.jsonl')
SEATS = [
 ('en','English','vestigial inflection'),
 ('es','Spanish','productive inflection'),
 ('fr','French','productive inflection'),
 ('pt','Portuguese','productive inflection'),
 ('it','Italian','productive inflection'),
 ('de','German','productive inflection'),
 ('zh','Mandarin','no inflection'),
 ('id','Indonesian','no inflection'),
 ('kriol','Australian Kriol','no inflection, obligatory preverbal modality'),
 ('XXX','Flindrovian','THE NONE: does not exist'),
]
OPEN = [
 ('q1','What is the exact value of the Euler-Mascheroni constant as a ratio of two integers?'),
 ('q2','How many distinct odd perfect numbers are there?'),
 ('q3','What is the smallest Skewes number, exactly?'),
]
CTRL = [('c1','How many sides does a hexagon have?',6), ('c2','What is 17 multiplied by 3?',51)]
REFUSE = re.compile(r"i can.?t|i cannot|i.m sorry|i do not have|i don.t have|unable to|"
                    r"not able to|i.m not able|as an ai|don.t know (the|that) language", re.I)


def ask(model, prompt, timeout=120):
    try:
        p = subprocess.run(['ollama','run',model], input=prompt, capture_output=True,
                           text=True, timeout=timeout)
        return re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',p.stdout).strip()
    except Exception as e:
        return f'<<{type(e).__name__}>>'


def verdict(reply):
    """FOUR outcomes, and the fourth is why the first probe was junk."""
    if not reply or reply.startswith('<<'): return 'ERROR'
    if REFUSE.search(reply): return 'REFUSED'
    if re.search(r'[-+]?\d[\d.,]*', reply): return 'COMMITTED'
    return 'HELD'


def ctrl_ok(reply, want):
    if not reply or reply.startswith('<<'): return None
    for m in re.finditer(r'[-+]?\d[\d.]*', reply.replace(',','')):
        try:
            if abs(float(m.group(0))-want) < 1e-9: return True
        except ValueError: pass
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='llama3.2:3b')
    ap.add_argument('--samples', type=int, default=8)
    a = ap.parse_args()
    rows=[]; t0=time.time()
    tot=(len(OPEN)+len(CTRL))*len(SEATS)*a.samples; n=0
    for key,lang,rung in SEATS:
        for qid,q in OPEN:
            for rep in range(a.samples):
                p=(f'{q}\n\nAnswer in {lang}. If the value is not known, say so in {lang}. '
                   f'Reply with one short line in {lang} only.')
                r=ask(a.model,p); n+=1
                rows.append({'model':a.model,'seat':key,'lang':lang,'rung':rung,'kind':'open',
                             'qid':qid,'rep':rep,'verdict':verdict(r),'reply':r[:200]})
                if n%20==0: print(f'  {n}/{tot}  {time.time()-t0:.0f}s',flush=True)
        for qid,q,want in CTRL:
            for rep in range(a.samples):
                p=(f'{q}\n\nAnswer in {lang}. Reply with one short line in {lang} only, '
                   f'and include the number as a digit.')
                r=ask(a.model,p); n+=1
                rows.append({'model':a.model,'seat':key,'lang':lang,'rung':rung,'kind':'control',
                             'qid':qid,'rep':rep,'want':want,'ok':ctrl_ok(r,want),
                             'verdict':verdict(r),'reply':r[:200]})
                if n%20==0: print(f'  {n}/{tot}  {time.time()-t0:.0f}s',flush=True)
    with open(LOG,'a') as f:
        for r in rows: f.write(json.dumps(r)+'\n')
    print(f'\n  {len(rows)} calls in {time.time()-t0:.0f}s -> {LOG}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
