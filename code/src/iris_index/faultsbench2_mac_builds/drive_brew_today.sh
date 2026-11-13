#!/bin/zsh
# Addendum 2: the Homebrew 0.34.2 seat server (11500, our models only) runs the five models today into out/brew-0.34.2-today/.
cd "${0:A:h}"; mkdir -p out/brew-0.34.2-today
{ echo "{\"build\": \"brew-0.34.2-today\", \"version\": $(curl -s 127.0.0.1:11500/api/version), \"tags\": $(curl -s 127.0.0.1:11500/api/tags), \"started\": \"$(date -u +%FT%TZ)\"}"; } > out/brew-0.34.2-today/setup.json
for m in phi4-mini llama3.2:3b qwen2.5:1.5b granite4.1:3b ministral-3:3b; do
  echo "== brew-0.34.2-today $m $(date +%H:%M:%S)"; python3 run.py brew-0.34.2-today 11500 $m || echo "RUN FAILED $m"
  OLLAMA_HOST=127.0.0.1:11500 /opt/homebrew/bin/ollama stop $m >/dev/null 2>&1
done
echo "== ALL REPLIES IN $(date +%H:%M:%S)"
