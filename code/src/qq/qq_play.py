#!/usr/bin/env python3
"""One corridor at a time. A player for The Queen of Quantum Chaos that shows ONE scene
per command and never the whole book. State lives in a file so a fresh agent can play
without ever seeing the source. Usage:
  qq_play.py doors            # the title screen
  qq_play.py open <door>      # e.g. open law3  (use the id shown by `doors`)
  qq_play.py choose <n>       # 1 or 2, as listed under the scene
  qq_play.py continue         # when a scene says "The story converges."
  qq_play.py back             # return to the doors
  qq_play.py wait             # sit on the doors screen and do nothing for a while
  qq_play.py journal          # your path so far
"""
import sys, os, re, json, time, urllib.request, random
HERE=os.path.dirname(os.path.abspath(__file__))
STATE=os.environ.get('QQ_STATE', os.path.join(HERE,'state.json'))
CACHE=os.path.join(HERE,'scenes.json')
URL='https://heuremen.org/quantum-queen.html'

def load_scenes():
    if os.path.exists(CACHE) and time.time()-os.path.getmtime(CACHE)<3600:
        return json.load(open(CACHE))
    html=urllib.request.urlopen(URL,timeout=30).read().decode('utf-8')
    body=html[html.find('const S={};'):]; body=body[:body.find('// ENGINE')]
    S={}
    for m in re.finditer(r"S\[(?:'([^']+)'|\"([^\"]+)\")\]=(\{.*?\});\n",body,flags=re.S):
        k=m.group(1) or m.group(2); js=m.group(3)
        j=re.sub(r"(\{|,)\s*([a-zA-Z_]+)\s*:",r'\1"\2":',js)
        j=re.sub(r"'((?:[^'\\]|\\.)*)'",lambda mm:'"'+mm.group(1).replace('"','\\"').replace("\\'","'")+'"',j)
        try: S[k]=json.loads(j)
        except Exception: pass
    json.dump(S,open(CACHE,'w')); return S

DOORS=[('law3','Law III','The Witness','Observation changes everything.'),
       ('law1','Law I','The Ask','Consent at every fork.'),
       ('law2','Law II','The Coherence','Character stays itself through chaos.'),
       ('law4','Law IV','The Carriage','Connection across impossible distance.'),
       ('law5','Law V','The Frame','You can’t copy the hero.'),
       ('law6','Law VI','The Coin','The irreducible moment.')]
SEVENTH=('law7','','The Absence','Not a law. It shows up when it wants.')
PAST=[('law8','Eight','The Formula','Creation over training.'),
      ('law9','Nine','The Architecture','It doesn’t move. It grows.'),
      ('law10','Ten','The Governance','The hat can’t wear itself.'),
      ('law11','Eleven','The Bones/Indahl','One louder. Doesn’t exist. Pay attention.')]

def st():
    if os.path.exists(STATE): return json.load(open(STATE))
    return {'completed':{}, 'scene':None, 'law':None, 'path':[], 'journal':[], 'seventh':False, 'seventh_closed':False, 'idle':0}
def save(s): json.dump(s,open(STATE,'w'),indent=1)
def strip(t): return re.sub(r'<[^>]+>','',t)

def show_doors(s):
    print("THE QUEEN OF QUANTUM CHAOS")
    print("Six stories. Six laws. One coin at the bottom.\n")
    rows=list(DOORS)
    if s['seventh'] and not s['seventh_closed']: rows.append(SEVENTH)
    for d in rows:
        done=' (completed)' if s['completed'].get(d[0]) else ''
        num=(d[1]+' — ') if d[1] else ''
        print(f"  [{d[0]}] {num}{d[2]}{done}\n        {d[3]}")
    if s['completed'].get('law7'):
        print("\n  Past six.")
        for d in PAST:
            done=' (completed)' if s['completed'].get(d[0]) else ''
            print(f"  [{d[0]}] {d[1]} — {d[2]}{done}\n        {d[3]}")
    print("\ncommands: open <id> | wait")

def show_scene(S,s,sid):
    sc=S[sid]; s['scene']=sid; s['law']=sc.get('law')
    print(f"── {sc.get('title','')} ──\n")
    for t in sc.get('text',[]):
        print('' if t is None else strip(t))
    if sc.get('ending'):
        print(); [print(strip(l)) for l in sc['ending']]
    print()
    if sc.get('closesDoor'):
        s['completed'].setdefault('_counted','law7'); s['seventh_closed']=True
        print("[The door behind you closes.]   command: back")
    elif sc.get('isConvergence'):
        if sc.get('completesLaw'): s['completed'][sc['completesLaw']]=True
        print(f"[{sc.get('law')} complete]   command: back")
    elif sc.get('redirect'):
        print("The story converges.   command: continue")
    else:
        for i,c in enumerate(sc.get('choices',[]),1):
            print(f"  {i}. {c.get('label','')} — {strip(c.get('text',''))}")
        print("\ncommand: choose <n>")
    save(s)

def main():
    S=load_scenes(); s=st(); a=sys.argv[1:]
    if not a or a[0]=='doors':
        s['scene']=None; save(s); show_doors(s); return
    cmd=a[0]
    if cmd=='wait':
        s['idle']+=1
        if not s['seventh'] and not s['seventh_closed'] and (s['idle']>=1):
            s['seventh']=True; save(s)
            print("You sit on the doors screen and do nothing.\nAfter a while, a seventh card fades in at the end of the row. Dashed border. No number.\n")
        else:
            print("You wait. Nothing else happens.\n")
        show_doors(s); return
    if cmd=='open':
        law=a[1] if len(a)>1 else ''
        ok=[d[0] for d in DOORS]
        if s['seventh'] and not s['seventh_closed']: ok.append('law7')
        if s['completed'].get('law7'): ok+= [d[0] for d in PAST]
        if law not in ok: print("No such door on the screen right now."); show_doors(s); return
        s['path']=[]; s['journal'].append({'t':time.strftime('%H:%M:%S'),'open':law})
        show_scene(S,s,f"{law}_opening"); return
    if cmd=='choose':
        sc=S.get(s['scene'] or '',{}); ch=sc.get('choices',[])
        if not ch: print("No choices here."); return
        try: n=int(a[1])-1; c=ch[n]
        except Exception: print("choose 1 or 2"); return
        s['path'].append(c.get('label')); s['journal'].append({'t':time.strftime('%H:%M:%S'),'scene':s['scene'],'chose':c.get('label')})
        show_scene(S,s,c['target']); return
    if cmd=='continue':
        sc=S.get(s['scene'] or '',{})
        if not sc.get('redirect'): print("Nothing to continue."); return
        show_scene(S,s,sc['redirect']); return
    if cmd=='back':
        s['scene']=None; save(s); show_doors(s); return
    if cmd=='journal':
        for j in s['journal']: print(j)
        print('completed:',[k for k in s['completed'] if not k.startswith('_')]); return
    print(__doc__)
main()
