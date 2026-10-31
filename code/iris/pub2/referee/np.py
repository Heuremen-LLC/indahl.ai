import sys
sys.argv=[sys.argv[0],sys.argv[1]]
src=open('recounts/2610.15732/recount.py').read().split("rng=np.random")[0]
exec(src)
F,A=load('forced_single'),load('abstention_baseline')
gnp=gold.is_no_persona_gold.astype(str).str.lower().eq('true').values
print('gold NP share',gnp.mean(), 'n',len(gnp))
idx=np.where(~gnp)[0]
rng=np.random.default_rng(5)
for m in ('gpt','gemini','claude','majority'):
    f=score(F[m],idx); a=score(A[m],idx)
    bs=[]
    for _ in range(1000):
        b=rng.choice(idx,len(idx)); bs.append(score(A[m],b)-score(F[m],b))
    print(m,'persona-only forced %.3f abstain %.3f diff %+.3f [%+.3f,%+.3f]'%(f,a,a-f,*np.percentile(bs,[2.5,97.5])))
# forced predicts NP ever?
print('forced NP predictions', {m:int((F[m]['intent']==NP).sum()) for m in F})
