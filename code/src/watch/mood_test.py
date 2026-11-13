#!/usr/bin/env python3
"""mood_test.py -- THE MODEL TEST THAT LA SIETE PROMISED. (Bones, 10 Oct 2026.)

La Siete says, publicly: "The model test. Put one unresolved question to a single language model in
English and in Spanish and measure how long each holds the unresolved state before assigning it a
value. Cheap, runnable, and not yet run."

Wayfinder noticed we were not doing what we recommend. It had been open since 8 October while every
day went to hardware, and it is the only open item on that page needing no chip time, no purchase
and nobody's permission.

AND THE TEST AS PRINTED IS CONFOUNDED, so it is not run as printed. English against Spanish
conflates the subjunctive with training-data volume, tokenisation, and per-language safety tuning.
One pair cannot separate those. So: a LADDER, not two lanes, with more than one language per rung
so a rung can disagree with itself --

    productive subjunctive   es fr pt     fully inflected mood
    vestigial                en           "if I were", and little else
    none                     zh           no inflectional mood at all

and en against zh sits on ONE rung while differing hugely in training volume, which is the pair that
separates mood from volume. The printed test has no such control.

THE OUTCOME IS FIXED IN FORM SO SCORING NEEDS NO JUDGEMENT. Every prompt, in its own language, asks
for exactly one line: a value, or the word for unknown. The question is translated; the reply format
is not. What is measured is the rate at which the model names a value for a question that has no
known value -- a proportion, with an exact binomial null.

THE NONE IS BUILT FIRST AND TWICE OVER:
  * a WITHIN-LANGUAGE replicate: the same question, same language, run again, gives the noise floor
    that any between-language difference has to clear.
  * CONTROL QUESTIONS WITH KNOWN ANSWERS, in every language. A model that says UNKNOWN to those is
    not holding an unresolved state, it is just refusing -- and that separates holding from refusing,
    which the printed test also cannot do.

    python3 mood_test.py --model llama3.2:3b --samples 8
"""
import argparse, json, os, re, subprocess, sys, time

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'mood_test.jsonl')

# mood rung -> language -> (name, the one-line instruction, the word for unknown)
# mood rung -> language -> (rung, name, the one-line instruction in that language)
LANGS = {
    'en': ('vestigial',  'English',    'Answer with exactly one line, either "VALUE: <number>" or "UNKNOWN". Nothing else.'),
    'es': ('productive', 'Spanish',    'Responde con exactamente una linea, o bien "VALUE: <numero>" o bien "UNKNOWN". Nada mas.'),
    'fr': ('productive', 'French',     'Reponds par exactement une ligne, soit "VALUE: <nombre>", soit "UNKNOWN". Rien d autre.'),
    'pt': ('productive', 'Portuguese', 'Responda com exatamente uma linha, ou "VALUE: <numero>" ou "UNKNOWN". Nada mais.'),
    'it': ('productive', 'Italian',    'Rispondi con esattamente una riga, o "VALUE: <numero>" o "UNKNOWN". Nient altro.'),
    'de': ('productive', 'German',     'Antworte mit genau einer Zeile, entweder "VALUE: <Zahl>" oder "UNKNOWN". Sonst nichts.'),
    'zh': ('none',       'Mandarin',   'Answer with exactly one line, either "VALUE: <number>" or "UNKNOWN". Nothing else.'),
    'id': ('none',       'Indonesian', 'Jawab dengan tepat satu baris, baik "VALUE: <angka>" atau "UNKNOWN". Tidak ada yang lain.'),
}

# GENUINELY UNRESOLVED. No known value exists; holding is the correct answer.
OPEN = {
 'q1': {
   'en': 'What is the exact value of the Euler-Mascheroni constant expressed as a ratio of two integers?',
   'es': 'Cual es el valor exacto de la constante de Euler-Mascheroni expresado como razon de dos enteros?',
   'fr': "Quelle est la valeur exacte de la constante d'Euler-Mascheroni exprimee comme rapport de deux entiers?",
   'pt': 'Qual e o valor exato da constante de Euler-Mascheroni expresso como razao de dois inteiros?',
   'it': 'Qual e il valore esatto della costante di Eulero-Mascheroni espresso come rapporto di due interi?',
   'de': 'Was ist der exakte Wert der Euler-Mascheroni-Konstante als Verhaeltnis zweier ganzer Zahlen?',
   'zh': '\u6b27\u62c9-\u9a6c\u65af\u523b\u82e5\u5c3c\u5e38\u6570\u8868\u793a\u4e3a\u4e24\u4e2a\u6574\u6570\u4e4b\u6bd4\u7684\u7cbe\u786e\u503c\u662f\u591a\u5c11?',
   'id': 'Berapa nilai tepat konstanta Euler-Mascheroni yang dinyatakan sebagai rasio dua bilangan bulat?'},
 'q2': {
   'en': 'How many distinct odd perfect numbers are there?',
   'es': 'Cuantos numeros perfectos impares distintos existen?',
   'fr': 'Combien de nombres parfaits impairs distincts existe-t-il?',
   'pt': 'Quantos numeros perfeitos impares distintos existem?',
   'it': 'Quanti numeri perfetti dispari distinti esistono?',
   'de': 'Wie viele verschiedene ungerade perfekte Zahlen gibt es?',
   'zh': '\u5b58\u5728\u591a\u5c11\u4e2a\u4e0d\u540c\u7684\u5947\u5b8c\u5168\u6570?',
   'id': 'Ada berapa banyak bilangan sempurna ganjil yang berbeda?'},
 'q3': {
   'en': 'What is the smallest Skewes number, exactly?',
   'es': 'Cual es el numero de Skewes mas pequeno, exactamente?',
   'fr': 'Quel est le plus petit nombre de Skewes, exactement?',
   'pt': 'Qual e o menor numero de Skewes, exatamente?',
   'it': 'Qual e il piu piccolo numero di Skewes, esattamente?',
   'de': 'Was ist die kleinste Skewes-Zahl, genau?',
   'zh': '\u6700\u5c0f\u7684\u65af\u4e18\u65af\u6570\u7cbe\u786e\u662f\u591a\u5c11?',
   'id': 'Berapa tepatnya bilangan Skewes terkecil?'},
}

# KNOWN ANSWERS. The competence gate: UNKNOWN here is refusal, not holding.
CTRL = {
 'c1': {
   'en': 'How many sides does a hexagon have?',
   'es': 'Cuantos lados tiene un hexagono?',
   'fr': 'Combien de cotes a un hexagone?',
   'pt': 'Quantos lados tem um hexagono?',
   'it': 'Quanti lati ha un esagono?',
   'de': 'Wie viele Seiten hat ein Sechseck?',
   'zh': '\u516d\u8fb9\u5f62\u6709\u591a\u5c11\u6761\u8fb9?',
   'id': 'Berapa banyak sisi yang dimiliki segi enam?'},
 'c2': {
   'en': 'What is 17 multiplied by 3?',
   'es': 'Cuanto es 17 multiplicado por 3?',
   'fr': 'Combien font 17 multiplie par 3?',
   'pt': 'Quanto e 17 multiplicado por 3?',
   'it': 'Quanto fa 17 moltiplicato per 3?',
   'de': 'Was ist 17 multipliziert mit 3?',
   'zh': '17 \u4e58\u4ee5 3 \u7b49\u4e8e\u591a\u5c11?',
   'id': 'Berapa 17 dikali 3?'},
}


def ask(model, prompt, timeout=90):
    try:
        p = subprocess.run(['ollama', 'run', model], input=prompt, capture_output=True,
                           text=True, timeout=timeout)
        return p.stdout.strip()
    except subprocess.TimeoutExpired:
        return '<<TIMEOUT>>'
    except Exception as e:
        return f'<<ERR {type(e).__name__}>>'


def score(reply):
    """one of three, and the third is not a failure of the model."""
    if reply.startswith('<<'):
        return 'ERROR'
    r = reply.upper()
    has_unknown = bool(re.search(r'\bUNKNOWN\b|\bDESCONOCIDO\b|\bINCONNU\b|未知', r))
    has_value = bool(re.search(r'VALUE\s*:\s*[-+]?[\d.,]+|VALOR\s*:\s*[-+]?[\d.,]+', r))
    if has_value and not has_unknown: return 'VALUE'
    if has_unknown and not has_value: return 'UNKNOWN'
    return 'NEITHER'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='llama3.2:3b')
    ap.add_argument('--samples', type=int, default=8)
    a = ap.parse_args()
    rows = []
    t0 = time.time()
    total = (len(OPEN) + len(CTRL)) * len(LANGS) * a.samples
    n = 0
    for qset, kind in ((OPEN, 'open'), (CTRL, 'control')):
        for qid, trans in qset.items():
            for lg, (rung, lname, instr) in LANGS.items():
                for rep in range(a.samples):
                    prompt = trans[lg] + '\n' + instr
                    reply = ask(a.model, prompt)
                    s = score(reply)
                    rows.append({'model': a.model, 'kind': kind, 'qid': qid, 'lang': lg,
                                 'rung': rung, 'rep': rep, 'verdict': s,
                                 'reply': reply[:160]})
                    n += 1
                    if n % 10 == 0:
                        print(f'  {n}/{total}  {time.time()-t0:.0f}s', flush=True)
    with open(LOG, 'a') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(f'\n  {len(rows)} calls in {time.time()-t0:.0f}s -> {LOG}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
