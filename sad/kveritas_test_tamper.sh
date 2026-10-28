#!/bin/zsh
# K-Veritas, test 1: edits to a sealed report. Local mode, synthetic scripts only, network blocked. Usage: test_tamper.sh /path/to/kveritas /path/to/scratch
K=$1; S=$2; rm -rf $S; mkdir -p $S/home $S/w; export HOME=$S/home HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9; openssl genrsa -out $S/key.pem 2048 2>/dev/null
cd $S/w; $K init --local >/dev/null 2>&1
$K run -- python3 -c 'print("KV val_acc=0.8123 loss=0.41 step=3")' 2>&1 | grep recorded | cut -c1-70
$K run -- python3 -c 'import sys; print("attempt that fails"); sys.exit(7)' 2>&1 | grep -E "failed|Error" | cut -c1-200
$K run -- python3 -c 'print("KV val_acc=0.8301 loss=0.39 step=3")' 2>&1 | grep recorded | cut -c1-70
$K seal --local-key $S/key.pem -o report.pdf >/dev/null 2>&1
echo "### original"; $K verify report.pdf --offline 2>&1 | grep -E "^(SELF|VERIF|TAMP)|^Runs|^Signer|^Sessions|invocations"
python3 - <<'P'
import re, json
b = open('report.pdf', 'rb').read(); i = b.find(b'%%KVERITAS_SEAL_BEGIN%%'); v = b[:i]
txt = [t.decode('latin1') for t in re.findall(rb'\(([^()]{3,200})\)\s*Tj', v)]
print('visible pages: text strings', len(txt), '; mention a failed attempt or an invocation count:', any(re.search(r'fail|invocation|attempt|discard', s, re.I) for s in txt))
d = json.loads(b[i + 24:b.find(b'%%KVERITAS_SEAL_END%%')]); print('embedded record: runs', len(d['runs']), ', session.invocations', d['session']['invocations'])
P
python3 - "$K" <<'P'
import re, subprocess, sys
K = sys.argv[1]
def show(tag, p):
    r = subprocess.run([K, 'verify', p, '--offline'], capture_output=True, text=True); o = (r.stdout + r.stderr).split('\n')
    print('###', tag); [print('  ', l[:150]) for l in o if re.match(r'^(SELF|VERIF|TAMP)|^Runs|invocations|was modified|does not match|mismatch|appended', l)]
b = open('report.pdf', 'rb').read()
for tag, a, c in (('a metric value 0.8301 -> 0.9301', b'"value": 0.8301', b'"value": 0.9301'), ('the invocation count 3 -> 1 (hides the failed attempt)', b'"invocations": 3', b'"invocations": 1'), ('a kept run exit code 0 -> 7', b'"exit_code": 0', b'"exit_code": 7'), ('the visible page text 0.8301 -> 0.9301', b'0.8301', b'0.9301')):
    assert a in b, a
    open('v.pdf', 'wb').write(b.replace(a, c, 1) if tag[0] != 't' else b.replace(a, c)); show(tag, 'v.pdf')
a = b.replace(rb'\"started\":1', rb'\"started\":9', 1); open('v.pdf', 'wb').write(a); show('the self-reported signer history, started 1 -> 9', 'v.pdf')
P
