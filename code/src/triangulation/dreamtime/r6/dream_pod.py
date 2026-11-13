#!/usr/bin/env python3
"""dream_pod.py -- runs dream_job.py on one rented 48 GB card (the Wen pod machinery: runpod_bake's brake against the deposit, the deadline watchdog, a pod that ends itself).
  python3 dream_pod.py <tag> <planned_hr>   -> results to dreamtime/pods/<tag>/"""
import os, subprocess, sys, time, json
sys.path.insert(0, os.path.expanduser('~/bones-forge/pocket-sage/bakeoff_runpod'))
import runpod_bake as R
HERE = os.path.dirname(os.path.abspath(__file__)); FILES = ['train_job.py', 'translations.json', 'pick.json', 'exam.json', 'r2_texts.json', 'train.jsonl', 'real_train_all.jsonl']
def main(tag, planned_hr):
    out_local = os.path.join(HERE, 'pods', tag); os.makedirs(out_local, exist_ok=True)
    pid = R.launch('dream-' + tag, planned_hr)
    try:
        tgt = R.ssh_target(pid); R.log('ssh up', tgt)
        subprocess.run(R.ssh_cmd(tgt, 'mkdir -p /workspace/dream /workspace/out /workspace/job'), check=True, timeout=60)
        kf = os.path.join(HERE, '.k.tmp'); open(kf, 'w').write(R.KEY); os.chmod(kf, 0o600)
        ok = R.scp(tgt, [os.path.join(HERE, f) for f in FILES], f'root@{tgt[0]}:/workspace/dream/') and R.scp(tgt, [kf], f'root@{tgt[0]}:/workspace/job/')
        os.remove(kf)
        if not ok: raise RuntimeError('upload failed')
        runner = f'''cd /workspace/job && chmod 600 .k.tmp && cat > self_end.sh <<'EOS'
#!/bin/bash
for i in $(seq 1 60); do [ -f /workspace/out/FETCHED ] && break; sleep 30; done
curl -s https://api.runpod.io/graphql -H "Content-Type: application/json" -H "Authorization: Bearer $(cat /workspace/job/.k.tmp)" -d '{{"query":"mutation {{ podTerminate(input:{{podId:\\"'$RUNPOD_POD_ID'\\"}}) }}"}}'
EOS
chmod +x self_end.sh
nohup bash -c 'pip install -q "torch==2.6.0" --index-url https://download.pytorch.org/whl/cu124 > /workspace/out/pip.log 2>&1; pip uninstall -y -q torchvision torchaudio >> /workspace/out/pip.log 2>&1; pip install -q "transformers==5.18.0" "peft==0.21.2" accelerate hf_transfer >> /workspace/out/pip.log 2>&1; \
python -c "import torch,transformers;print(torch.__version__,transformers.__version__,torch.cuda.get_device_name(0))" > /workspace/out/stack.txt 2>&1 || {{ touch /workspace/out/BADSTACK /workspace/out/DONE; exit 1; }}; \
cd /workspace/dream && HF_HUB_ENABLE_HF_TRANSFER=1 python train_job.py > /workspace/out/stdout.log 2>&1; touch /workspace/out/DONE; /workspace/job/self_end.sh' > /dev/null 2>&1 &
echo started'''
        subprocess.run(R.ssh_cmd(tgt, runner), check=True, timeout=120); R.log('job started on', pid)
        t0 = time.time()
        while True:
            time.sleep(90)
            subprocess.run(['scp', '-q', '-i', R.SSHK, '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'LogLevel=ERROR', '-P', str(tgt[1]),
                            f'root@{tgt[0]}:/workspace/out/job.log', f'root@{tgt[0]}:/workspace/out/stdout.log', f'root@{tgt[0]}:/workspace/out/stack.txt', out_local + '/'], timeout=120)
            st = subprocess.run(R.ssh_cmd(tgt, 'ls /workspace/out; pgrep -f "[t]rain_job.py" >/dev/null && echo RUNNING=1 || echo RUNNING=0; pgrep -f "[p]ip install" >/dev/null && echo PIP=1 || echo PIP=0'),
                                capture_output=True, text=True, timeout=60).stdout
            if 'DONE' in st.split(): R.log('DONE'); break
            if 'RUNNING=0' in st and 'PIP=0' in st and time.time() - t0 > 600: R.log('job ended without DONE'); break
            if time.time() - t0 > planned_hr * 3600: R.log('over planned time'); break
        R.scp(tgt, [f'root@{tgt[0]}:/workspace/out/.'], out_local)
        subprocess.run(R.ssh_cmd(tgt, 'touch /workspace/out/FETCHED'), timeout=30); R.log('fetched ->', out_local, os.listdir(out_local))
    finally:
        R.terminate(pid); D = R.jl(R.DEADLINES, {}); D.pop(pid, None); json.dump(D, open(R.DEADLINES, 'w'))
if __name__ == '__main__': main(sys.argv[1], float(sys.argv[2]))
