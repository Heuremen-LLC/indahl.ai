#!/bin/bash
set -e
mkdir -p /Users/heuremen/bones-forge/cloudflare-workers/_private
cp /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/worker.js /Users/heuremen/bones-forge/cloudflare-workers/_private/heuremen-door-worker-source-20261114.js
cp /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/wrangler.toml /Users/heuremen/bones-forge/cloudflare-workers/_private/heuremen-door-wrangler-20261114.toml
cp /Users/heuremen/bones-forge/field-runs/worker-clean/build/worker.js /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/worker.js
cp /Users/heuremen/bones-forge/field-runs/worker-clean/build/wrangler.toml /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/wrangler.toml
rm -f /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/worker_public.js /Users/heuremen/bones-forge/cloudflare-workers/heuremen-door/wrangler_public.toml
echo installed
