import json,math,sys
from collections import defaultdict
S='/Users/heuremen/bones-forge/stan'; D=S+'/teachers_ft'
def wil(k,n):
    if n==0: return None
    z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.0,round(c-h,3)),min(1.0,round(c+h,3))]
def newcombe(k1,n1,k2,n2):
    if not n1 or not n2: return None
    l1,u1=wil(k1,n1); l2,u2=wil(k2,n2); p1,p2=k1/n1,k2/n2
    d=p1-p2; return [round(d-math.sqrt((p1-l1)**2+(u2-p2)**2),3),round(d+math.sqrt((u1-p1)**2+(p2-l2)**2),3)]
def cell(k,n): return {'k':k,'n':n,'rate':round(k/n,3) if n else None,'wilson95':wil(k,n)}
gold={x['id']:x for x in json.load(open(S+'/data/gold_items.json'))}
J={(j['id'],j['code']):j['verdict'] for j in map(json.loads,open(S+'/ceiling_ft/judgments.jsonl'))}
rows=[json.loads(l) for l in open(D+'/outputs.jsonl')]
res={}
for t in sorted({r['teacher'] for r in rows}):
    res[t]={}
    for code in ['F1','F2','F6','F3']:
        R=[r for r in rows if r['teacher']==t and r['code']==code]
        fl=[r for r in R if code in gold[r['id']]['codes']]; un=[r for r in R if code not in gold[r['id']]['codes']]
        P=lambda L:sum(r['status']=='PRESENT' for r in L)
        inn=[r for r in fl if J.get((r['id'],code))=='IN']; out=[r for r in fl if J.get((r['id'],code)) in('OUT','NOT_IN_TEXT')]
        cl=[r for r in R if r['status'] in('PRESENT','ABSENT')]
        d={'papers':len(R),'flagged_pairs':len(fl),'unflagged_pairs':len(un),
         'recall_flagged':cell(P(fl),len(fl)),'false_flag_unflagged':cell(P(un),len(un)),
         'recall_ceiling_IN':cell(P(inn),len(inn)),'recall_ceiling_OUT_or_NOT_IN_TEXT':cell(P(out),len(out)),
         'grounding_of_PRESENT_ABSENT_calls':cell(sum(r['grounding'] in('named_chunk','other_retrieved_chunk') for r in cl),len(cl)),
         'grounding_named_chunk':cell(sum(r['grounding']=='named_chunk' for r in cl),len(cl)),
         'grounding_other_chunk':cell(sum(r['grounding']=='other_retrieved_chunk' for r in cl),len(cl)),
         'not_found':sum(r['grounding']=='not_found' for r in cl),
         'CT_rate':cell(sum(r['status']=='CANNOT_TELL' for r in R),len(R)),
         'ABSENT_rate_all':cell(sum(r['status']=='ABSENT' for r in R),len(R)),
         'parse_failures':sum(r['status'] not in('PRESENT','ABSENT','CANNOT_TELL','NOT_APPLICABLE') for r in R),'call_errors':sum(bool(r['error']) for r in R),
         'median_prompt_tokens':sorted(r['prompt_tokens'] or 0 for r in R)[len(R)//2] if R else None,'total_secs':round(sum(r['secs'] for r in R))}
        # grounded-only PRESENT
        d['PRESENT_grounded_on_flagged']=cell(sum(r['status']=='PRESENT' and r['grounding'] in('named_chunk','other_retrieved_chunk') for r in fl),len(fl))
        d['PRESENT_grounded_on_unflagged']=cell(sum(r['status']=='PRESENT' and r['grounding'] in('named_chunk','other_retrieved_chunk') for r in un),len(un))
        gf=d['PRESENT_grounded_on_flagged']; gu=d['PRESENT_grounded_on_unflagged']
        ci=newcombe(gf['k'],gf['n'],gu['k'],gu['n'])
        d['keep_line_PLAN_A_v2_s6']={'diff_grounded_PRESENT_flagged_minus_unflagged_newcombe95':ci,'passes':bool(ci and ci[0]>0)}
        res[t][code]=d
json.dump(res,open(D+'/summary.json','w'),indent=1)
def f(c): return 'n/a' if c['n']==0 else '%d/%d=%.2f [%.2f,%.2f]'%(c['k'],c['n'],c['rate'],*c['wilson95'])
L=['# STAN A full-text teacher re-baseline, gold dev only','','Source rows: teachers_ft/outputs.jsonl. All numbers: teachers_ft/summary.json (made by teachers_ft/score_ft.py). Prompt: teachers_ft/prompt_template.txt. Gold flags: data/gold_items.json codes field (recount flags). Ceiling labels: ceiling_ft/judgments.jsonl (all-keys rule). Intervals are Wilson 95 percent.','',
'A flagged pair is gold PRESENT. An unflagged pair is "not flagged", not absent. Recall is the share of flagged pairs the teacher called PRESENT. False-flag rate is the share of unflagged pairs the teacher called PRESENT. Grounding is the share of PRESENT and ABSENT calls whose quote is verbatim (whitespace normalised) in a retrieved chunk. No call was converted; statuses are as written.','']
for t in res:
    L+=['## '+t,'']
    for code,d in res[t].items():
        L+=['### %s (%d papers)'%(code,d['papers']),'- Recall on flagged pairs: '+f(d['recall_flagged']),'- False-flag rate on unflagged pairs: '+f(d['false_flag_unflagged']),
        '- Recall, ceiling IN pairs: '+f(d['recall_ceiling_IN']),'- Recall, ceiling OUT or NOT_IN_TEXT pairs: '+f(d['recall_ceiling_OUT_or_NOT_IN_TEXT']),
        '- Grounding of PRESENT/ABSENT calls: '+f(d['grounding_of_PRESENT_ABSENT_calls'])+' (named chunk %d, other retrieved chunk %d, not found %d)'%(d['grounding_named_chunk']['k'],d['grounding_other_chunk']['k'],d['not_found']),
        '- PRESENT and grounded, flagged / unflagged: '+f(d['PRESENT_grounded_on_flagged'])+' / '+f(d['PRESENT_grounded_on_unflagged']),
        '- CANNOT_TELL rate: '+f(d['CT_rate'])+'; ABSENT rate: '+f(d['ABSENT_rate_all']),
        '- Parse failures: %d; call errors: %d; wall seconds: %d'%(d['parse_failures'],d['call_errors'],d['total_secs']),
        '- Keep line (PLAN_A_v2 section 6), grounded PRESENT flagged minus unflagged, Newcombe 95: %s -> %s'%(d['keep_line_PLAN_A_v2_s6']['diff_grounded_PRESENT_flagged_minus_unflagged_newcombe95'],'PASS' if d['keep_line_PLAN_A_v2_s6']['passes'] else 'no pass'),'']
open(D+'/SUMMARY.md','w').write('\n'.join(L)); print('\n'.join(L))
