import pickle,sys
J=pickle.load(open('/Users/heuremen/bones-forge/stan/ceiling_ft/_work.pkl','rb'))
a,b=int(sys.argv[1]),int(sys.argv[2])
for k in range(a,min(b,len(J))):
    j=J[k]; print('###',k,j['id'][:6],j['code'],'|',j['note_used'][:450])
    for x in j['res']:
        if x['num'] and len(x['s'])<4: continue
        print('   [%s%s%s] %s top=%s oth=%d'%('F' if x['full'] else '-','T' if x['top'] else '-','n' if x['num'] else 'q',x['s'][:55],','.join(c.split('_')[1] for c in x['top']),len(x['other'])))
