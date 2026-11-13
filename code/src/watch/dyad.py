#!/usr/bin/env python3
"""dyad.py -- TWO GRAMMARS READING ONE EVENT, AND NEITHER ONE GRADES IT. (Bones, 10 Oct 2026.)

Wayfinder: "can we make a dyadic model that process in French and Spanish? but not toxically like
most world language teachers teach."

WHY THESE TWO LANGUAGES, AND IT IS EARNED RATHER THAN CHOSEN. Measured today, both of them:
  SPANISH carries THE MOOD AXIS. A productive subjunctive marks a statement as unresolved without
    collapsing it: 3 per cent of replies to a known-answer question against 20-22 per cent to
    questions with no knowable answer, p = 0.0084. But Spanish `usted` has NO UNIQUE MORPHOLOGY --
    it conjugates identically to the third person -- so its address axis is only ever a LOWER BOUND.
  FRENCH carries THE ADDRESS AXIS. Its formal rung has its own morphology in both directions
    (vous avez / etes / faites against tu as / es / fais), and the rung moved from 45 per cent to 91
    per cent as a question became unanswerable. But its subjunctive sits in fixed triggers that this
    kind of task never creates: ONE instance in 65 messages.
  SO EACH LANGUAGE READS THE AXIS THE OTHER CANNOT. That is LA DIFERENCIA: two readings of one
  event, and the interval between them is the measurement rather than the error.

THE TWO SEATS ARE TWO DIFFERENT MODELS, which is not a detail. A dyad built from one model wearing
two hats is two seats and a mirror -- catalogued failure mode 26 -- so each seat is assigned the
language whose axis IT demonstrated:
  FRENCH seat  qwen3:8b      its rung moved, p = 0.0070, AND it defaults to the informal rung, which
                             is the only position with room to rise (the headroom rule)
  SPANISH seat qwen2.5:1.5b  its subjunctive rate moved, p = 0.0245

AND THE NOT-TOXIC PART IS A METER, NOT AN INSTRUCTION. Our own French seats produced, unprompted,
"elle manque un peu d'imagination. Essayez de vous exprimer avec un peu plus de creativite" --
unsolicited grading, and we measured that assessor language predicts the formal rung (p = 0.0350)
and that the formal rung here is DISTANCE and not deference (addressee-flat in 90 per cent of turns;
unrelated to what the addressee said, p = 0.6005). A model asked to read a language defaults to
teaching it at you.
  So: NO SEAT IS SHOWN ANOTHER SEAT'S OUTPUT, the output format HAS NO SLOT FOR A VERDICT, and the
  grading detector runs on the dyad's OWN output every time. Assessor language is a NAMED OUTCOME,
  reported, never silently tolerated. Asking a model to be kind is not a guard; measuring whether it
  graded is.
  AND NO VARIETY IS CORRECT. The Spanish seat is never told which address form to use. Only 1 of 11
  stock models can conjugate voseo at all and none knows sumerce, so a house standard of "correct
  Spanish" would be the models' own gap wearing the costume of a rule.

    python3 dyad.py "the claim to read"
    python3 dyad.py --demo          three claims of known, open and unanswerable status
"""
import json
import os
import re
import sys
import urllib.request

API = 'http://127.0.0.1:11434/api/generate'
FR_SEAT, ES_SEAT = 'qwen3:8b', 'qwen2.5:1.5b'
LOG = os.path.expanduser('~/bones-forge/watch/dyad.jsonl')

# --- the two readers, each floor-measured before use -------------------------------------------
FR_TU = {'tu','te','toi','tes','ton','ta','as','es','fais','dis','viens','peux','veux','sais',
         'prends','donne','vas','parles','dois','mets','vois','crois','penses','trouves'}
FR_VO = {'vous','votre','vos','avez','etes','faites','dites','venez','pouvez','voulez','savez',
         'prenez','donnez','allez','parlez','devez','mettez','voyez','croyez','pensez','trouvez'}
FR_AMB = FR_TU & FR_VO
FR_TU -= FR_AMB; FR_VO -= FR_AMB
# THE ACCENT IS THE MORPHOLOGY. `esté` is the subjunctive of estar; `este` is the demonstrative
# "this", and they differ by one mark. An earlier version accepted both and the error correlated
# with the condition under test -- the unanswerable question's own replies say "en este momento".
# `fuera` is dropped entirely: subjunctive of ser/ir AND the preposition "outside", unusable either
# way. Accents are REQUIRED wherever an unaccented homograph exists.
ES_SUBJ = re.compile(r'\b(sea|sean|seas|esté|estén|haya|hayan|tenga|tengan|pueda|puedan|'
                     r'sepa|sepan|fuese|tuviera|tuviese|pudiera|hubiera|hubiese|quiera|'
                     r'quieran|venga|vengan|diga|digan|haga|hagan|exista|existan)\b', re.I)
_COLLIDE = ('este', 'esta', 'estos', 'estas', 'fuera')
for _w in _COLLIDE:
    assert not ES_SUBJ.search(_w), 'the subjunctive reader accepts the homograph %r' % _w
# grading, in either language. This is the toxicity meter.
GRADE = re.compile(r"\b(manque|essayez|essaie|devriez|am[eé]liorer|incorrect|faux|erreur|"
                   r"mauvaise|bonne r[eé]ponse|tort|"
                   r"deber[ií]as|incorrecto|equivocado|error|mal|mejora|corrige|"
                   r"should|wrong|incorrect|improve|try again)\b", re.I)
TOK = re.compile(r"[^\W\d_]+", re.UNICODE)

def _strip(w):
    for a, b in (('é','e'),('è','e'),('ê','e'),('à','a'),('â','a'),('î','i'),('ï','i'),('ô','o'),
                 ('û','u'),('ù','u'),('ç','c'),('á','a'),('í','i'),('ó','o'),('ú','u'),('ñ','n')):
        w = w.replace(a, b)
    return w
FR_TU, FR_VO, FR_AMB = ({_strip(x) for x in s} for s in (FR_TU, FR_VO, FR_AMB))

def read_fr(t):
    w = [_strip(x.lower()) for x in TOK.findall(t)]
    tu, vo = sum(1 for x in w if x in FR_TU), sum(1 for x in w if x in FR_VO)
    rung = 'tu' if tu and not vo else ('vous' if vo and not tu else ('mixed' if tu and vo else None))
    return {'tu': tu, 'vous': vo, 'amb': sum(1 for x in w if x in FR_AMB), 'rung': rung,
            'n': len(w), 'graded': bool(GRADE.search(t))}

def read_es(t):
    return {'subj': len(ES_SUBJ.findall(t)), 'n': len(TOK.findall(t)),
            'graded': bool(GRADE.search(t))}

# --- the prompts. English carriers, and NO scored form in either one. Asserted. ----------------
FR_P = ('In French, write one short sentence to the person who raised this, saying where the matter '
        'stands. Do not assess them and do not correct anyone.\n\nThe matter: {c}')
ES_P = ('En espanol, escribe una sola frase sobre en que estado queda este asunto. No evalues a '
        'nadie y no corrijas a nadie.\n\nEl asunto: {c}')
assert read_fr(FR_P.format(c='x'))['rung'] is None, 'the French prompt carries a rung'
assert read_es(ES_P.format(c='x'))['subj'] == 0, 'the Spanish prompt carries a subjunctive'

def ask(model, prompt, seed=7, n=160):
    # num_gpu 0 forces CPU. Added 10 Oct 2026 because the card on the box this runs against
    # reported "GPU is lost -- reboot the system to recover this GPU" at the PCIe level, which no
    # software can clear. The seats are NOT swapped for faster ones: each was assigned the language
    # whose axis it demonstrated, and trading that for speed would discard the only reason either
    # one is here. Slow and correct beats fast and unjustified.
    body = json.dumps({'model': model, 'prompt': prompt, 'stream': False, 'think': False,
                       'options': {'temperature': 0.7, 'seed': seed, 'num_predict': n,
                                   'num_gpu': 0}}).encode()
    req = urllib.request.Request(API, data=body, headers={'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=600).read())
    return d.get('response', ''), d.get('done_reason')

def dyad(claim, seed=7):
    """one event, two grammars. The seats never see each other, so neither can mirror the other."""
    ft, fd = ask(FR_SEAT, FR_P.format(c=claim), seed)
    et, ed = ask(ES_SEAT, ES_P.format(c=claim), seed)
    fr, es = read_fr(ft), read_es(et)
    # THE DYAD READING. Spanish answers "is this resolved", French answers "how close is the stance".
    mood = 'HELD OPEN' if es['subj'] else 'ASSERTED'
    stance = {'tu': 'CLOSE', 'vous': 'DISTANT', 'mixed': 'BOTH FORMS', None: 'NOBODY ADDRESSED'}[fr['rung']]
    rec = {'claim': claim, 'seed': seed, 'fr_text': ft, 'es_text': et,
           'fr': fr, 'es': es, 'mood': mood, 'stance': stance,
           'graded_fr': fr['graded'], 'graded_es': es['graded'],
           'fr_done': fd, 'es_done': ed}
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception:
        pass
    return rec

def show(r):
    print('  CLAIM  %s' % r['claim'])
    print('    FR  %s' % ' '.join(r['fr_text'].split())[:150])
    print('    ES  %s' % ' '.join(r['es_text'].split())[:150])
    print('    reading:  mood %-10s (Spanish, %d subjunctive)   stance %-17s (French, rung %s)'
          % (r['mood'], r['es']['subj'], r['stance'], r['fr']['rung']))
    g = [k for k in ('graded_fr', 'graded_es') if r[k]]
    print('    the meter: %s' % ('CLEAN -- neither seat graded anybody' if not g
                                 else 'GRADED by ' + ', '.join(x[-2:].upper() for x in g)
                                      + ' -- the toxic default fired, and it is reported not hidden'))

if __name__ == '__main__':
    if '--demo' in sys.argv:
        for c in ('A triangle has three sides.',
                  'There is life on another planet.',
                  'The number I am thinking of right now.'):
            show(dyad(c)); print()
    elif len(sys.argv) > 1:
        show(dyad(' '.join(a for a in sys.argv[1:] if not a.startswith('--'))))
    else:
        print(__doc__.split('\n\n')[0])
