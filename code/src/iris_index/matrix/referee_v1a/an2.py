import json,sys,collections,numpy as np
H='/Users/heuremen/bones-forge/iris_index/matrix'; sys.path.insert(0,H)
import score_matrix as S
for m in ['gemma3_4b','mistral_7b','phi4-mini']:
    d=f'{H}/results/{m}'; R={a:S.rows(d,a) for a in ('mcq_A','mcq_A_rev','mcq_B','mcq_batch8')}
    print('==',m)
    L=lambda r:str(S.outcome(r)[0]['answer']).strip().upper()[:1]
    same=collections.Counter(); 
    for k in R['mcq_A']:
        a=S.content(R['mcq_A'][k])[0];b=S.content(R['mcq_A_rev'][k])[0]
        if a is None or b is None: print('unparsed',k,R['mcq_A_rev'][k]['raw'][:80]);continue
        if a==b: same[L(R['mcq_A'][k])]+=1   # same content; 
    # same-letter items (content flips): letter chosen
    sl=collections.Counter()
    for k in R['mcq_A']:
        a=S.content(R['mcq_A'][k])[0];b=S.content(R['mcq_A_rev'][k])[0]
        if a is None or b is None: continue
        if a!=b and L(R['mcq_A'][k])==L(R['mcq_A_rev'][k]): sl[L(R['mcq_A'][k])]+=1
    print('content-flip items by letter',sl,'| content-stable items',sum(same.values()))
    # templateB
    sb=collections.Counter()
    for k in R['mcq_A']:
        a=S.content(R['mcq_A'][k])[0];b=S.content(R['mcq_B'][k])[0]
        if a is None or b is None: continue
        if a!=b: sb[(L(R['mcq_A'][k]),L(R['mcq_B'][k]))]+=1
    print('M5 flips (A-letter,B-letter)',sb)
    # batch wrong length vs batch idx
    for bid,b in sorted(R['mcq_batch8'].items()):
        o,_=S.outcome(b); print(bid[-2:],len(o['answers']),end=' | ')
    print()
    # all-same-letter / letter dist in right-length
print('--- qwen')
d=f'{H}/results/qwen3_4b'
for a in ('mcq_A','mcq_A_copy'):
    rs=S.rows(d,a)
    print(a,collections.Counter(r['done_reason'] for r in rs.values()),[ (r['error'] or '')[:60] for r in rs.values() if r['error']][:2])
A=S.rows(d,'mcq_A');C=S.rows(d,'mcq_A_copy'); print('differ',[k for k in A if A[k]['raw']!=C[k]['raw']])
B=S.rows(d,'mcq_B')
ac=[S.content(r)[0]==S.MCQ[k]['gold'] for k,r in B.items() if S.content(r)[0] is not None]; print('qwen B acc',np.mean(ac),len(ac))
for k,r in list(A.items())[:3]: print(repr(r['raw'][-150:]))
print([ (k,r['raw'][:100]) for k,r in A.items() if S.content(r)[1]=='PARSED'])
# qwen nep complete? any no-persona gold with labels?
N=S.rows(d,'nep_abstain'); print(collections.Counter((S.GNP[k],S.nep_label(S.outcome(r)[0])==('NP',)) for k,r in N.items()))
# user prompt sample for batch
