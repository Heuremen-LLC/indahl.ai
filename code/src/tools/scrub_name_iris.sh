#!/bin/bash
# Waits for the running S1 round (pid given) to end, then renames the old-name files in iris_index/claims_stack and their callers, and republishes the public copy.
# Never edits a script while bash is reading it: runs only after the pid is gone.
PID="$1"; D=~/bones-forge/iris_index/claims_stack
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
cd "$D" || exit 1
[ -f publish_sad_live.py ] && mv publish_sad_live.py publish_model_live.py
[ -f status_sad_live.json ] && mv status_sad_live.json status_model_live.json
for f in publish_model_live.py run_s1.sh run_s1b.sh CLAIMS_STACK_PLAN.md; do [ -f "$f" ] && sed -i '' -e 's/publish_sad_live\.py/publish_model_live.py/g' -e 's/status_sad_live\.json/status_model_live.json/g' -e "s/'sad_live'/'model_live'/g" -e 's/the SAD live block/the MODEL live block/g' -e 's/hardware vendors in SAD/hardware vendors on the MODEL desk/g' "$f"; done
P=~/bones-forge/public_mirror/indahl.ai/code/iris/claims_stack
rm -f "$P"/publish_sad_live.py "$P"/status_sad_live.json; cp publish_model_live.py run_s1.sh run_s1b.sh CLAIMS_STACK_PLAN.md "$P"/ 2>/dev/null
bash ~/bones-forge/ledger/push_public.sh "Rename the old-name files in claims_stack after the round ended" 2>&1 | tail -1
# switch the worker and the API to the new key and ship, then drop the old key
python3 - <<'PY'
import os
R=os.path.expanduser('~/bones-forge')
p=R+'/cloudflare-workers/heuremen-door/worker.js'; w=open(p).read(); w=w.replace("(await env.IRIS_BENCH.get('sad_live')) || (await env.IRIS_BENCH.get('model_live'))","env.IRIS_BENCH.get('model_live')"); open(p,'w').write(w)
p=R+'/indahl-ai/api.js'; s=open(p).read(); s=s.replace("kv(env, 'sad_live')","kv(env, 'model_live')"); open(p,'w').write(s)
PY
cp ~/bones-forge/indahl-ai/api.js ~/bones-forge/public_mirror/indahl.ai/code/api/api.js
bash ~/bones-forge/ledger/ship.sh "MODEL live block reads its own key" 2>&1 | tail -1
cd ~/bones-forge/cloudflare-workers/heuremen-door && CLOUDFLARE_ACCOUNT_ID=f069aa0c8534706cb64f7cc3658dd894 npx wrangler kv key delete sad_live --namespace-id ecb59d96b07c43bdac14271687eae5af --remote --force >/dev/null 2>&1
echo "scrub done $(date -u +%FT%TZ)" >> ~/bones-forge/archive/scrub_name_iris.log
