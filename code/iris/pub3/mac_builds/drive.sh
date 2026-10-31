#!/bin/zsh
# drive.sh (PLAN.md here): for each build in order, start a server from that binary on its own port with our models only, record the
# setup, run the five models (three arms each), stop the server. One build and one model at a time. Resumable.
cd "${0:A:h}"; S=$HOME/bones-forge/iris_index/seats
for spec in "official-0.34.2 11502 $S/ollama-0.34.2/bin/ollama" "official-0.34.3 11501 $S/ollama-0.34.3/bin/ollama"; do
  b=${spec%% *}; rest=${spec#* }; port=${rest%% *}; bin=${rest#* }; mkdir -p out/$b
  OLLAMA_HOST=127.0.0.1:$port OLLAMA_MODELS=$S/models OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_KEEP_ALIVE=5m $bin serve > out/$b/serve.log 2>&1 &
  srv=$!; for i in {1..60}; do curl -s 127.0.0.1:$port/api/version >/dev/null && break; sleep 1; done
  { echo "{\"build\": \"$b\", \"binary_sha256\": \"$(shasum -a 256 $bin | cut -d' ' -f1)\", \"version\": $(curl -s 127.0.0.1:$port/api/version), \"tags\": $(curl -s 127.0.0.1:$port/api/tags), \"started\": \"$(date -u +%FT%TZ)\"}"; } > out/$b/setup.json
  for m in phi4-mini llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b; do
    echo "== $b $m $(date +%H:%M:%S)"; python3 run.py $b $port $m || echo "RUN FAILED $b $m"
    OLLAMA_HOST=127.0.0.1:$port $bin stop $m >/dev/null 2>&1
  done
  kill $srv; wait $srv 2>/dev/null; echo "== BUILD DONE $b $(date +%H:%M:%S)"
done
echo "== ALL REPLIES IN $(date +%H:%M:%S)"
