# R2: false-pass rate by defect class and mode, analysis window, non-stale, human-unacceptable submissions. Two units tried (labelled).
import csv,sys,re,collections
D=sys.argv[1]+'/data/'
rd=lambda f:list(csv.DictReader(open(D+f,encoding='utf-8-sig')))
codes={r['answer_id']:r for r in rd('human_codes_distinct_answers.csv')}
PASS=re.compile(r'\[可不修改\]|\[通過\]')
sub=[];
for s in rd('submissions.csv'):
    p=int(s['problem']); m=s['mode']; d=s['timestamp'][:10]
    if not(4<=p<=9) or not m or not((p<=6 and d=='2026-04-02') or (p>=7 and d=='2026-04-09')): continue
    c=codes.get(s['answer_id'])
    if not c or c['stale']=='1' or c['ok']=='1': continue
    E={k:c[k]=='1' for k in ['E1','E2','E3','E4','E5','E6']}; nok=c['name_ok'] in ('1','1.0')
    cls='type_only' if (E['E4'] or E['E6']) and not(E['E1'] or E['E2'] or E['E3'] or E['E5']) and nok else ('substantive' if (E['E1'] or E['E2'] or E['E3'] or E['E5']) else 'name_only/other')
    sub.append((m,cls,bool(PASS.search(s['label_as_run'])),s['answer_id']))
print('submission level (strict pass = [可不修改] or [通過]):')
for m in 'AB':
    for cls in ['type_only','substantive','name_only/other']:
        x=[r for r in sub if r[0]==m and r[1]==cls]; k=sum(r[2] for r in x)
        print(f'  mode {m} {cls:16s} {k}/{len(x)} = {k/len(x):.0%}' if x else f'  mode {m} {cls} 0')
print('answer level (an answer counts as passed if any of its submissions in that mode passed):')
for m in 'AB':
    for cls in ['type_only','substantive']:
        a=collections.defaultdict(bool); [a.__setitem__(r[3],a[r[3]] or r[2]) for r in sub if r[0]==m and r[1]==cls]
        print(f'  mode {m} {cls:16s} {sum(a.values())}/{len(a)} = {sum(a.values())/max(1,len(a)):.0%}')
