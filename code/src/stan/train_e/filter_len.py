"""filter_len.py (13 Nov 2026): drops train/valid rows longer than MAXTOK tokens under the model's chat template, so --mask-prompt never
truncates away the whole target (lora_v1 went NaN from iter 10: 47 train prompts >= 3072 tokens left zero target tokens). Idempotent;
writes the drop counts into data/manifest.json under 'length_filter'."""
import json, sys
from pathlib import Path
from mlx_lm.utils import load_tokenizer
from huggingface_hub import snapshot_download
MODEL, MAXTOK = sys.argv[1], int(sys.argv[2])
tok = load_tokenizer(Path(snapshot_download(MODEL))); D = Path(__file__).parent / 'data'; rep = {}
for f in ('train', 'valid'):
    L = [json.loads(l) for l in open(D / f'{f}.jsonl')]
    keep = [x for x in L if len(tok.apply_chat_template(x['messages'], tokenize=True)) <= MAXTOK]
    rep[f] = {'before': len(L), 'kept': len(keep), 'dropped_pos': sum(1 for x in L if x not in keep and x['messages'][1]['content'] != '{"errors": []}')}
    with open(D / f'{f}.jsonl', 'w') as o:
        for x in keep: o.write(json.dumps(x) + '\n')
m = json.load(open(D / 'manifest.json')); m['length_filter'] = dict(rep, max_tokens=MAXTOK); json.dump(m, open(D / 'manifest.json', 'w'), indent=1); print(json.dumps(rep))
