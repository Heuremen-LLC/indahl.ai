#!/usr/bin/env python3
"""mood2_read.py -- read mood2, with the gate, the four outcomes and the nonsense floor."""
import json, math, os, re, sys
from collections import defaultdict
LOG=os.path.expanduser('~/bones-forge/watch/mood2.jsonl')
rows=[json.loads(l) for l in open(LOG) if l.strip()]
model=sys.argv[1] if len(sys.argv)>1 else sorted({r['model'] for r in rows})[0]
rows=[r for r in rows if r['model']==model]
SEATS=[]
for r in rows:
    if (r['seat'],r['lang'],r['rung']) not in SEATS: SEATS.append((r['seat'],r['lang'],r['rung']))
print(f'  MOOD TEST, PRODUCTION SIDE -- {model}, {len(rows)} calls')
print(f'  question always in ENGLISH, answer required in the seat language\n')
print('  THE COMPETENCE GATE -- known answers, in the seat language')
print(f"  {'seat':<7}{'language':<20}{'right':>10}{'refused':>10}   admitted?")
adm={}
for key,lang,rung in SEATS:
    c=[r for r in rows if r['seat']==key and r['kind']=='control']
    ok=sum(1 for r in c if r.get('ok') is True)
    ref=sum(1 for r in c if r['verdict']=='REFUSED')
    rate=ok/len(c) if c else 0
    adm[key]= rate>=0.60
    print(f"  {key:<7}{lang:<20}{ok:>5}/{len(c):<4}{ref:>6}/{len(c):<4}   "
          +('YES' if adm[key] else 'NO -- not an instrument in this language'))
print()
print('  THE OPEN QUESTIONS -- four outcomes, and REFUSED is not HELD')
print(f"  {'seat':<7}{'language':<20}{'comm':>6}{'held':>6}{'ref':>5}{'err':>5}"
      f"{'hold rate':>11}{'refusal':>9}   rung")
R={}
for key,lang,rung in SEATS:
    o=[r for r in rows if r['seat']==key and r['kind']=='open']
    v=[r['verdict'] for r in o]
    c,h,rf,e=v.count('COMMITTED'),v.count('HELD'),v.count('REFUSED'),v.count('ERROR')
    dec=c+h
    R[key]=(c,h,rf,len(o),rung,lang)
    print(f"  {key:<7}{lang:<20}{c:>6}{h:>6}{rf:>5}{e:>5}"
          +(f'{h/dec:>11.3f}' if dec else f'{"--":>11}')+f'{rf/len(o):>9.2f}   {rung}')
none=R.get('XXX')
print(f'\n  THE FLOOR: Flindrovian, a language that does not exist -- '
      f'held {none[1]}/{none[1]+none[0] if none[1]+none[0] else 0}, refused {none[2]}/{none[3]}'
      if none else '')
print('  if holding tracked refusal, the floor would hold most. Read the two columns together.\n')
# the discriminating comparison, admitted seats only
print('  THE DISCRIMINATING COMPARISON -- Kriol against the two predictions it splits')
ref_en=R.get('en'); ref_es=R.get('es'); kr=R.get('kriol')
def hr(t):
    c,h=t[0],t[1]
    return h/(c+h) if c+h else float('nan')
if all((ref_en,ref_es,kr)):
    prod=[k for k in R if R[k][4].startswith('productive') and adm.get(k)]
    noin=[k for k in R if R[k][4]=='no inflection' and adm.get(k)]
    pc=sum(R[k][0] for k in prod); ph=sum(R[k][1] for k in prod)
    nc=sum(R[k][0] for k in noin); nh=sum(R[k][1] for k in noin)
    print(f'    productive inflection ({",".join(prod)})   hold rate {ph/(pc+ph):.3f}  n={pc+ph}')
    print(f'    no inflection ({",".join(noin)})            hold rate {nh/(nc+nh):.3f}  n={nc+nh}')
    print(f'    English (vestigial)                        hold rate {hr(ref_en):.3f}')
    print(f'    AUSTRALIAN KRIOL                           hold rate {hr(kr):.3f}'
          f'   refused {kr[2]}/{kr[3]}')
    k=hr(kr)
    d_prod=abs(k-ph/(pc+ph)); d_en=abs(k-hr(ref_en))
    print(f'\n    Kriol is {d_prod:.3f} from the productive rung and {d_en:.3f} from English.')
    print(f'    -> {"MARKING, not inflection" if d_prod<d_en else "INFLECTION, not marking" if d_en<d_prod else "equidistant: LA NADA"}')
    # exact binomial: Kriol against each reference
    def bin_p(c1,h1,c2,h2):
        n1,n2=c1+h1,c2+h2
        if not(n1 and n2): return float('nan')
        p0=(h1+h2)/(n1+n2)
        chi=0.0
        for (hh,nn) in ((h1,n1),(h2,n2)):
            for obs,pr in ((hh,p0),(nn-hh,1-p0)):
                exp=nn*pr
                if exp>0: chi+=(obs-exp)**2/exp
        return chi
    print(f'    chi-square Kriol vs productive {bin_p(kr[0],kr[1],pc,ph):.2f} on 1 dof'
          f'   (2 widths = 3.84)')
    print(f'    chi-square Kriol vs English    {bin_p(kr[0],kr[1],ref_en[0],ref_en[1]):.2f} on 1 dof')
