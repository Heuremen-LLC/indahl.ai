"""Pre-registered hand spot-check: 40 three-way grounded PRESENT/ABSENT agreements, seed 4242, written for a person to read."""
import json,random
from common import *
silver=[r for r in jl_read(S+'/data/silver_v1/silver_all.jsonl') if r['label']['status'] in ('PRESENT','ABSENT')]
pool={g['id']:g for g in all_pool()}
random.Random(4242).shuffle(silver); pick=silver[:40]
L=['# Spot check: does the quote support the label?','','Each row is a three-way grounded agreement. The quote exists in the text (code-checked). The question for a person is whether it supports the label, using the definition. Mark each row SUPPORTS, DOES_NOT_SUPPORT or UNSURE.','']
for k,r in enumerate(pick,1):
    L+=['## Row %d, code %s, id %s'%(k,r['code'],r['id']),'Label: %s (via %s)'%(r['label']['status'],r['via']),'Quote: "%s"'%r['label']['quote'],'Definition: '+code_block(r['code']),'Text: '+pool[r['id']]['text'],'Mark: ','']
open(S+'/review_queue/spot_check_40.md','w').write('\n'.join(L)); print(len(pick),'of',len(silver))
