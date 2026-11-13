import json,os,collections
R='/Users/heuremen/bones-forge/iris_index/matrix/results'
for m in ['gemma3_4b','mistral_7b','phi4-mini','qwen3_4b']:
    print('==',m)
    for a in ['nep_abstain','mcq_A','mcq_A_rev','mcq_batch8']:
        p=f'{R}/{m}/{a}.jsonl'
        if not os.path.exists(p): print(a,'missing'); continue
        rs=[json.loads(l) for l in open(p)]
        print('--',a,len(rs),collections.Counter(r['done_reason'] for r in rs),'err',sum(bool(r['error']) for r in rs))
        for i in (0,7,60):
            if i<len(rs): print('  ',repr(rs[i]['raw'][:300]))
