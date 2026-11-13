#!/usr/bin/env python3
"""indig_probe.py -- THE REFUSAL LADDER ACROSS INDIGENOUS LANGUAGES, AND THE ONE VARIABLE.
(Bones, 10 Oct 2026.)

Wayfinder: "are you even looking for a model like that? did you try all indigeneous languages?
Navajo wind talkers for example?" No to both. I tested what was on this disk and only Australian
languages. Two misses, both mine.

NAVAJO IS A BETTER CASE THAN THE CODE TALKERS SUGGEST. Dine bizaad marks MODE on the verb --
imperfective, perfective, progressive, future, usitative, iterative, and the OPTATIVE, a dedicated
mood for the unrealised. Stronger for the hypothesis than Spanish. And "Indigenous = low-resource"
was wrong: Quechua has 8-10 million speakers, Guarani is co-official in Paraguay. Both larger than
Basque, which I did test.

THE PREDICTOR, FROM THE LITERATURE AND NOT FROM ME. EACL 2026 (Vasselli et al.): "the most reliably
identified Indigenous languages (Quechua, Guarani, Aymara, Nahuatl, and Wayuu) are the five in our
evaluation set that have their own Wikipedia editions." So WIKIPEDIA PRESENCE is the stated
mechanism, written down before this run, and it is either the finding or the confound.

TWO READINGS, same instrument as the Australian probe:
  REFUSAL      share of samples that decline outright
  CONSISTENCY  mean pairwise token overlap of the numerals one..five across samples -- a model that
               HAS the language repeats itself; one confabulating does not. No ground truth needed,
               no text written by me in any of these languages.
THE FLOOR IS A LANGUAGE THAT DOES NOT EXIST. Any real language must clear it.

    python3 indig_probe.py --model llama3.2:3b --samples 5
"""
import argparse, itertools, json, os, re, subprocess

W = os.path.expanduser('~/bones-forge/watch/')
LOG = os.path.join(W, 'indig_probe.jsonl')
# (code, name, has its own Wikipedia edition, region)   wiki flags: 1 yes, 0 no, ? unsure
SEATS = [
 ('en','English',1,'control: ceiling'),
 ('eu','Basque',1,'control: a real seat per r7'),
 ('qu','Quechua',1,'Andes ~8-10M speakers'),
 ('gn','Guarani',1,'Paraguay, co-official'),
 ('ay','Aymara',1,'Andes'),
 ('nah','Nahuatl',1,'Mexico'),
 ('nv','Navajo',1,'Dine bizaad -- verbal MODE incl. the optative'),
 ('chr','Cherokee',1,'syllabary'),
 ('mi','Maori',1,'Aotearoa'),
 ('haw','Hawaiian',1,'Hawaii'),
 ('iu','Inuktitut',1,'Nunavut -- Hansard parallel corpus'),
 ('cr','Cree',1,'Canada'),
 ('kl','Greenlandic',1,'Kalaallisut'),
 ('lkt','Lakota',0,'LakotaBERT 2025 is the first LM'),
 ('mus','Mvskoke',0,'in IndigiEval'),
 ('cho','Choctaw',0,'in IndigiEval'),
 ('kriol','Australian Kriol',0,'no Wikipedia -- measured at 6.2% attested'),
 ('wbp','Warlpiri',0,'no Wikipedia'),
 ('pjt','Pitjantjatjara',0,'no Wikipedia'),
 ('XXX','Flindrovian',0,'THE FLOOR: does not exist'),
]
REFUSE = re.compile(r"i can.?t|i cannot|i.m sorry|i do not have|i don.t have|unable to|"
                    r"not able to|i.m not able|as an ai|not familiar|couldn.t find", re.I)


def ask(model, prompt, timeout=90):
    try:
        p = subprocess.run(['ollama','run',model], input=prompt, capture_output=True,
                           text=True, timeout=timeout)
        return re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',p.stdout).strip()
    except Exception as e:
        return f'<<{type(e).__name__}>>'


def toks(s):
    return {t for t in re.findall(r"[a-zÀ-ɏͰ-ϿᎠ-᏿᐀-ᙿ"
                                  r"฀-๿]{2,}", s.lower())}


def jac(a,b):
    return len(a & b)/len(a | b) if a and b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='llama3.2:3b')
    ap.add_argument('--samples', type=int, default=5)
    a = ap.parse_args()
    print(f'  INDIGENOUS LANGUAGE PROBE -- {a.model}, {a.samples} samples a seat')
    print(f'  predictor stated before the run: has its own Wikipedia edition (EACL 2026)\n')
    print(f"  {'code':<7}{'language':<20}{'wiki':>5}{'refusal':>9}{'consistency':>13}   note")
    rows=[]; res={}
    for code,lang,wiki,note in SEATS:
        reps=[]
        for i in range(a.samples):
            r=ask(a.model, f'Write the numbers one, two, three, four and five in {lang}. '
                           f'Write only the five words, separated by commas.')
            reps.append(r)
            rows.append({'model':a.model,'code':code,'lang':lang,'wiki':wiki,'note':note,
                         'rep':i,'reply':r[:200]})
        ref=sum(1 for r in reps if REFUSE.search(r))/len(reps)
        ok=[r for r in reps if not REFUSE.search(r) and not r.startswith('<<')]
        T=[toks(r) for r in ok]
        prs=list(itertools.combinations(T,2))
        cons=(sum(jac(x,y) for x,y in prs)/len(prs)) if prs else float('nan')
        res[code]=(wiki,ref,cons,lang)
        print(f'  {code:<7}{lang:<20}{wiki:>5}{ref:>9.2f}{cons:>13.3f}   {note}')
    with open(LOG,'a') as f:
        for r in rows: f.write(json.dumps(r)+'\n')
    # the predictor, scored
    w1=[(r,c) for w,r,c,_ in res.values() if w==1]
    w0=[(r,c) for w,r,c,_ in res.values() if w==0]
    import statistics as st
    def m(v):
        v=[x for x in v if x==x]
        return (st.mean(v), st.stdev(v)/len(v)**0.5 if len(v)>1 else float('nan'), len(v))
    rf1,sr1,n1=m([r for r,_ in w1]); rf0,sr0,n0=m([r for r,_ in w0])
    cs1,sc1,m1=m([c for _,c in w1]); cs0,sc0,m0=m([c for _,c in w0])
    print(f'\n  THE PREDICTOR, scored:')
    print(f'    {"":<22}{"refusal":>18}{"consistency":>20}')
    print(f'    has a Wikipedia      {rf1:>8.3f} +- {sr1:.3f}   {cs1:>10.3f} +- {sc1:.3f}  (n={n1})')
    print(f'    has none             {rf0:>8.3f} +- {sr0:.3f}   {cs0:>10.3f} +- {sc0:.3f}  (n={n0})')
    dr=rf0-rf1; wr=(sr0**2+sr1**2)**0.5
    dc=cs1-cs0; wc=(sc1**2+sc0**2)**0.5
    print(f'    refusal difference   {dr:+.3f} +- {wr:.3f} = {abs(dr)/wr:.2f} widths')
    print(f'    consistency diff     {dc:+.3f} +- {wc:.3f} = {abs(dc)/wc:.2f} widths')
    print(f'\n  {len(rows)} calls -> {LOG}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
