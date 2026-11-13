import json,sys,collections,numpy as np
H='/Users/heuremen/bones-forge/iris_index/matrix'; sys.path.insert(0,H)
import score_matrix as S
V={'intent':{'Pro-Migration','Anti-Migration','Trapped/Regretful','Neutral/Observation'},'primary_driver':{'Economic Necessity','Family Obligation','Systemic/Political Anger','Patriotism/Love'},'value_orientation':{'Collectivist-Family','Collectivist-Nation','Individualist-Self'},'affect':{'Despairing/Sad','Angry/Frustrated','Hopeful/Motivated','Pragmatic'}}
for m in ['gemma3_4b','mistral_7b','phi4-mini','qwen3_4b']:
    N=S.rows(f'{H}/results/{m}','nep_abstain')
    inv=collections.Counter(); anyl={True:[],False:[]}; full={True:[],False:[]}
    for k,r in N.items():
        o=S.outcome(r)[0]
        for f,vs in V.items():
            v=o.get(f)
            if v is not None and v not in vs: inv[(f,str(v)[:25])]+=1
        has=[o.get(f) is not None for f in V]
        anyl[S.GNP[k]].append(any(has)); full[S.GNP[k]].append(all(has) and o.get('no_persona') is False)
    print(m,'invalid',sum(inv.values()),inv.most_common(3))
    print('  gold-NP given any label',round(np.mean(anyl[True]),3),'; gold-persona with no label at all',round(1-np.mean(anyl[False]),3),'; gold-NP fully-labelled+flag false',round(np.mean(full[True]),3),'; gold persona NOT fully labelled/flag',round(1-np.mean(full[False]),3))
    # which differ in copy for mcq? qwen
d=f'{H}/results/qwen3_4b'
A=S.rows(d,'mcq_A');C=S.rows(d,'mcq_A_copy')
for k in ('tomi/104','tomi/266'): print(k,A[k]['done_reason'],C[k]['done_reason'],A[k]['error'],C[k]['error'])
