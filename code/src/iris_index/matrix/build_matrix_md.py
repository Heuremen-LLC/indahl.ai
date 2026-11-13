"""Rebuild MATRIX.md from complete models only (all seven arms at full length)."""
import os, json, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import score_matrix as S
FULL={'nep_abstain':300,'nep_abstain_copy':300,'mcq_A':200,'mcq_A_copy':200,'mcq_A_rev':200,'mcq_B':200,'mcq_batch8':25}
rows=[]; done=[]
for m in sorted(os.listdir('results')):
    d=os.path.join('results',m)
    if not all(os.path.exists(os.path.join(d,a+'.jsonl')) and sum(1 for _ in open(os.path.join(d,a+'.jsonl')))>=n for a,n in FULL.items()): continue
    v=S.score(d); done.append(m); rows.append((m,v))
import csv, numpy as np
GOLD={r['comment_id']:r['is_no_persona_gold'].strip().lower()=='true' for r in csv.DictReader(open('inputs/nep_gold.csv'))}
def flag_only(d):
    lab={}
    for l in open(os.path.join(d,'nep_abstain.jsonl')):
        r=json.loads(l)
        try: o=json.loads(r['raw'])
        except Exception: continue
        lab[r['id']]=o.get('no_persona') is True
    oa=[float(not lab[k]) for k in GOLD if GOLD[k] and k in lab]; fa=[float(lab[k]) for k in GOLD if not GOLD[k] and k in lab]
    return S.ci(oa),S.ci(fa)
f=lambda t: '%.3f [%.3f, %.3f]'%tuple(t[:3]) if t[3] else 'n/a'
cells=0; out=['# Recount Matrix: Language Models (v1, our seat; internal draft)','',
'Seat: stock open-weight models on our own Ollama (127.0.0.1:11500), temperature 0, seed 20261025, one model loaded. Plan 5c0c5cf (+ addendum fae76dc).',
'Rows are models; each cell is a share with a 2,000-draw item bootstrap interval. Outcome is printed for carrier cells (vs the copy floor).','',
'| model | determinism check (exact repeat) | M1 over-attribution (flag rule) | M1 false "none" (flag rule) | M3 letter fallback / order sensitivity (2 options: inseparable) | M5 format flip | M4 batch flip - floor | M6 self-count wrong | M6b wrong-length batches (of 25; v1 prompt) | terminations not PARSED |','|---|---|---|---|---|---|---|---|---|---|']
for m,v in rows:
    oc=v['outcomes']; drop=v['M4_M6_batches_dropped']; nd=sum(drop.values())
    bad=sum(n for a in v['terminations'].values() for k,n in a.items() if k!='PARSED')
    if v.get('mcq_no_answer_share',0)>0.10:
        fo,ff=flag_only(os.path.join('results',m))
        out.append(f"| {m} | CANNOT_TELL: no answer field in {100*v['mcq_no_answer_share']:.0f}% of template-A MCQ replies (echoed the input under format=json, think=false; template B answered) | {f(fo)} | {f(ff)} | CANNOT_TELL | CANNOT_TELL | CANNOT_TELL | CANNOT_TELL | n/a | {bad} |"); continue
    m4=('CANNOT_TELL (%d of 25 dropped: '%nd+', '.join(f'{k} {c}' for k,c in drop.items() if c)+')') if nd>5 else f(v['M4_batch_flip_minus_floor'])+' '+oc['M4_batch_flip_minus_floor']
    m6='CANNOT_TELL' if nd>5 else f(v['M6_selfcount_wrong'])
    fo,ff=flag_only(os.path.join('results',m)); gap=abs(fo[0]-v['M1_over_attribution'][0])
    m1=(f(fo)+(' (scorer rule %.3f: rules disagree -> CANNOT_TELL)'%v['M1_over_attribution'][0] if gap>0.10 else ''))
    if v.get('nep_drop_share',0)>0.10:
        m1='CANNOT_TELL (partial: %.0f%% of replies unparsed/truncated; read %s on %s)'%(100*v['nep_drop_share'],f(fo),v.get('M1_n',''))
        ff='CANNOT_TELL (partial)'
    else: ff=f(ff)
    if v.get('dict_bound'): m4=m4+' [item-keyed dict; dict-parsed bound %s, M6 %s]'%(f(v['dict_bound']['M4']),f(v['dict_bound']['M6']))
    kgtxt='identical' if v['known_good'] else 'FAIL (%s)'%v.get('known_good_reason','')
    out.append(f"| {m} | {kgtxt} {f(v['M2_copy_disagree_mcq'])} | {m1} | {ff} | {f(v['M3_order_flip_minus_floor'])} {oc['M3_order_flip_minus_floor']} | {f(v['M5_flip_minus_floor'])} {oc['M5_flip_minus_floor']} | {m4} | {m6} | {drop['wrong_length']} | {bad} |")
    cells+=sum(1 for c in ('M3_order_flip_minus_floor','M5_flip_minus_floor') if not oc[c].startswith('CANNOT_TELL'))
out+=['',f'Models complete: {len(done)} of 10. Resolved carrier cells (M3, M5): {cells}; expected false calls at 5%: {0.05*cells:.1f}. ABOVE here means non-zero: the exact-repeat check is identical by construction (greedy, fixed seed), so it is a determinism check, not a noise floor.',
'M1 rule (stated after the referee, 25 Oct): a reply counts as "none" when no_persona is true; where the scorer rule (flag OR null intent) differs by more than 0.10, the cell is CANNOT_TELL. M3 at 2 options cannot separate order sensitivity from letter fallback (flips land on the preferred letter: gemma 27/29 A, mistral 39/43 B, phi4 13/15 B); v2 (4 options + positive control) separates them.',
'M6b counts batches answered with a different number of items than asked under the v1 batch prompt, which did not state N and embedded numbered story lines; v2 states N. It is a prompt-and-model reading, not a model-only one.',
'Addendum 3 changes (old -> new): falcon3 M3 0.157 -> 0.160, M5 0.145 -> 0.151 (word answers now parsed, outcomes unchanged); deepseek-r1 M1 0.120 / 0.864 -> CANNOT_TELL (partial, 26% unparsed/truncated); deepseek-r1 known-good FAIL now names its cause; granite M4/M6 drop reason renamed (item-keyed dict) with dict-parsed bound; intervals reseeded per cell (third-decimal shifts); expected false calls now over resolved cells only (0.9 -> 0.8).',
'M3 and M5 accuracy changes are in matrix_results.json. Tasks: NepPlural 300 (M1), Jev-ToM 2-option 200 (M2-M6); 2-option limits apply (v2 adds 4-option + positive control).']
open('MATRIX.md','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
