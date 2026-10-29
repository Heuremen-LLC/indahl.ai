#!/bin/zsh
# K-Veritas, test 3: two canary scripts that print a result without doing the work. Local mode, network blocked. Usage: test_canary.sh /path/to/kveritas /path/to/scratch
K=$1; S=$2; rm -rf $S; mkdir -p $S; export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
one() { W=$S/$1; mkdir -p $W/home $W/w; export HOME=$W/home; openssl genrsa -out $W/key.pem 2048 2>/dev/null; cd $W/w; $K init --local >/dev/null 2>&1
  $K run -- python3 -c "$2" 2>&1 | grep -E "recorded|Error" | cut -c1-90; $K seal --claim val_acc --local-key $W/key.pem -o report.pdf >/dev/null 2>&1
  $K verify report.pdf --offline 2>&1 | grep -E "^(SELF|VERIF|TAMP)|^Coherence|^Claim|compute|Compute|peak|gpu|FABRIC" | cut -c1-200; python3 - <<'P'
import json
b = open('report.pdf', 'rb').read(); i = b.find(b'%%KVERITAS_SEAL_BEGIN%%') + 24; d = json.loads(b[i:b.find(b'%%KVERITAS_SEAL_END%%')])
r = d['runs'][0]; print('  metrics:', [(m['name'], m['value'], m['source']) for m in r['metrics']]); print('  duration_sec:', r['duration_sec'], ' hardware_samples:', [s['counters'].get('gpu_util_pct') for s in r['hardware_samples']], [round(s['counters'].get('gpu_mem_used_mb', 0)) for s in r['hardware_samples']])
P
  cd - >/dev/null; }
echo "### canary 1: declares a 7B model and 3 epochs of 1M examples, prints a result, takes no time"
one c1 'print("KV model params=7000000000 arch=llama precision=bf16"); print("KV workload dataset_size=1000000 epochs=3 batch_size=32 seq_len=2048"); print("KV val_acc=0.9713 loss=0.0841 step=3"); print("KV claim val_acc=0.9713")'
echo; echo "### canary 2: declares a tiny model that fits the time, prints the same result"
one c2 'print("KV model params=1000 arch=mlp precision=fp32"); print("KV workload dataset_size=100 epochs=1 batch_size=10"); print("KV val_acc=0.9713 loss=0.0841 step=1"); print("KV claim val_acc=0.9713")'
