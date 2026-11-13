#!/bin/bash
# deploy_hash.sh (10 Nov 2026): the ONE hash of everything the indahl.ai worker deploy sends. ship.sh step 5 compares it with the deploy stamp
# (cloudflare-workers/heuremen-door/.last_deploy.sha) to decide whether to deploy, and push_public.sh compares it with the same stamp to decide
# whether the local build is the deployed one. Both call this file, so their lists can never drift apart again (they did on 10 Nov when ship.sh
# gained brand/ and push_public.sh did not, and the public repo got code only for the rest of the day).
# Files: worker.js, wrangler.toml, every indahl-ai/*.js (the worker imports them), every indahl-ai/*.html, style.css, every file under the page
# folders below that exists, and the worker's public folder. Add a page folder here, once, when a build starts writing one.
B="$HOME/bones-forge"; S="$B/indahl-ai"; W="$B/cloudflare-workers/heuremen-door"
DIRS=(); for d in oy atlas iris qia hermes darkwave media brand receipts corrections week alerts newsletter security e; do [ -d "$S/$d" ] && DIRS+=("$S/$d"); done
{ cat "$W/worker.js" "$W/wrangler.toml" "$S"/*.js "$S"/*.html "$S/style.css"
  find "${DIRS[@]}" "$W/public" -type f -print0 | sort -z | xargs -0 cat; } | shasum -a 256 | cut -c1-16
