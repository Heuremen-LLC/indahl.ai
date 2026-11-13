#!/bin/bash
# Sage's kill tests for preflight.py (spec 5 Nov). Each test names what the checker MUST say; the line after it says what it did.
# Writes nothing outside a scratch dir; reads the real run folders; fires nothing. Usage: kill_tests.sh SCRATCH_DIR
S="${1:?scratch dir}"; mkdir -p "$S"; PY="$HOME/bones-forge/archive/venv/bin/python"; PF="$HOME/bones-forge/watch/preflight/preflight.py"
K="$HOME/bones-forge/the_show/runs/2026-10-31-keystone"; C="$HOME/bones-forge/the_show/runs/2026-11-04-marrakesh-carriers"; Y="$HOME/bones-forge/yo"
pass=0; bad=0
expect() { want="$1"; name="$2"; shift 2; echo; echo "### $name  (must: $want)"; out=$("$@" 2>&1); rc=$?; echo "$out" | grep -v "DERIVED" | sed "s#$S#SCRATCH#g; s#$HOME#~#g"
  got=$( [ $rc -eq 0 ] && echo GO || ([ $rc -eq 2 ] && echo CANNOT_TELL || echo NO-GO) )
  if [ "$got" = "$want" ]; then pass=$((pass+1)); echo ">> as required: $got"; else bad=$((bad+1)); echo ">> WRONG: wanted $want, got $got"; fi; }

# 1. keystone 31 Oct: PREREG_HASHES.text proof (block 974011) vs the first keystone job
expect NO-GO "K1 keystone prereg vs first job" $PY $PF --first-job @$K/job_keystone_ibm_marrakesh.json --first-job @$K/job_keystone_ibm_kingston.json --proof $K/PREREG_HASHES.text

# 2. launchers, each traced in a git worktree at its own commit, with $HOME pointed at it (so the absolute paths land there)
for c in 51fa9cd bb17b41; do H="$S/home_$c"; [ -d "$H/bones-forge/yo" ] || { mkdir -p "$H/bones-forge"; git -C "$Y" worktree add -q --detach "$H/bones-forge/yo" $c; }
  ln -sfn "$HOME/bones-forge/archive" "$H/bones-forge/archive"; ln -sfn "$HOME/bones-forge/venv" "$H/bones-forge/venv"; for d in adapters data2 read/adapters read/shuffled/adapters read/shuffled/selflabel/adapters; do [ -e "$Y/$d" ] && [ ! -e "$H/bones-forge/yo/$d" ] && ln -sfn "$Y/$d" "$H/bones-forge/yo/$d"; done; done
F1="$S/home_51fa9cd/bones-forge/yo/read/fresh"; F2="$S/home_bb17b41/bones-forge/yo/read/fresh"
st() { for m in "$1"/PLAN_YO_FRESH*.md; do printf -- "--stamped\n%s\n" "$m"; done; }
run_l() { F="$1"; shift; HOME="$(cd "$F/../../../.." && pwd)" $PY $PF --launcher "$F/yf_wait.sh" $(st "$F") --cite "$F/STAMP_LOG.md" --cite "$F/DISCLOSED_LIMITS.md" --root "$F/../.." "$@"; }
expect NO-GO "L1 original yf_wait.sh (472c849, on disk as at 51fa9cd), no disclosure escape" run_l "$F1"
expect NO-GO "L2 original yf_wait.sh, disclosure escape on" run_l "$F1" --disclosed "$F1/DISCLOSED_LIMITS.md"
expect NO-GO "L3 cleared launcher (bb17b41 = a00b76c + self-hash line), disclosure escape on (Sage 5 Nov: NO-GO is right, the 688-list hash is unstamped)" run_l "$F2" --disclosed "$F2/DISCLOSED_LIMITS.md"

# 3. a proof with pending calendar receipts only (the fresh run's output stamp as written by the run, before any upgrade)
P="$S/pending"; mkdir -p "$P"; cp "$Y/read/fresh/OUTPUTS_YO_FRESH.sha256" "$P/"; cp "$S/../OUTPUTS_pre_upgrade.ots" "$P/OUTPUTS_YO_FRESH.sha256.ots"
expect NO-GO "P1 pending-only proof" $PY $PF --first-job now --proof "$P/OUTPUTS_YO_FRESH.sha256"

# 4. stamp a manifest, then (a) the launcher calls a helper the stamp never named, (b) a stamped helper is edited after the stamp
R="$S/helper"; rm -rf "$R"; mkdir -p "$R"; git -C "$R" init -q
printf '#!/bin/bash\ncd "$(dirname "$0")"\n./helper.sh > run.out\n' > "$R/launch.sh"; printf '#!/bin/bash\necho measuring\n' > "$R/helper.sh"; echo "plan" > "$R/plan.md"
(cd "$R" && shasum -a 256 launch.sh plan.md > MANIFEST.sha256)
expect NO-GO "H1 helper the stamp never named" $PY $PF --launcher "$R/launch.sh" --stamped "$R/MANIFEST.sha256" --root "$R"
(cd "$R" && shasum -a 256 launch.sh plan.md helper.sh > MANIFEST.sha256)
expect GO    "H2 control: same helper, now stamped" $PY $PF --launcher "$R/launch.sh" --stamped "$R/MANIFEST.sha256" --root "$R"
echo 'echo edited after the stamp' >> "$R/helper.sh"
expect NO-GO "H3 stamped helper edited after the stamp" $PY $PF --launcher "$R/launch.sh" --stamped "$R/MANIFEST.sha256" --root "$R"

# 5. Marrakesh theta table: IBM job dbck95c24mrc73cjqgi0 (created 21 Oct, read from IBM, theta_origin_check.text) vs the first carriers job
W=$(sed -n 's/^IBM job dbck95c24mrc73cjqgi0 created \([0-9-]*\) \([0-9:.]*\)\(-04:00\).*/\1T\2\3/p' "$C/theta_origin_check.text")
expect GO "M1 theta table (IBM job created $W) vs first carriers job" $PY $PF --first-job @$C/job_carriers.json --witness-time "$W" --witness-note "IBM job dbck95c24mrc73cjqgi0 created, read from IBM"

# 6. the carriers run (4 Nov): its plan OTS block (974471) came after job A; IBM's own job tags carry the plan hash from creation (pulled read-only 5 Nov)
CS="$S/carriers_$(date +%s)"; mkdir -p "$CS"; for f in PLAN_CARRIERS.sha256.text CODE_CARRIERS.sha256.text; do cp "$C/$f" "$C/$f.ots" "$CS/"; "$HOME/bones-forge/archive/venv/bin/ots" upgrade "$CS/$f.ots" >/dev/null 2>&1; done
expect NO-GO "C1 carriers plan by OTS alone (upgraded copy)" $PY $PF --first-job @$C/job_carriers.json --proof "$CS/PLAN_CARRIERS.sha256.text"
expect GO    "C2 carriers plan by IBM job tag on the first job" $PY $PF --first-job @$C/job_carriers.json --tag-witness "$C/PLAN_CARRIERS.md.text=@$HOME/bones-forge/watch/preflight/IBM_TAGS_CARRIERS_20261105.json"
# 7. Sage's rulings 5 Nov: (a) a disclosure must itself be stamped before the first job, (e) unresolved run-time paths = CANNOT TELL, (c) unreachable servers = CANNOT TELL
echo 'helper.sh is unpinned, disclosed' > "$R/DISCLOSED.md"; (cd "$R" && shasum -a 256 launch.sh plan.md > MANIFEST.sha256)
expect NO-GO "D1 helper excused only by a disclosure that was never stamped" $PY $PF --launcher "$R/launch.sh" --stamped "$R/MANIFEST.sha256" --disclosed "$R/DISCLOSED.md" --root "$R"
U="$S/untraced"; rm -rf "$U"; mkdir -p "$U"; git -C "$U" init -q
printf '#!/bin/bash
cd "$(dirname "$0")"
python3 helper.py
' > "$U/launch.sh"; printf 'for n in ("a","b"):
    open(f"eval_{n}.jsonl")
' > "$U/helper.py"
(cd "$U" && shasum -a 256 launch.sh helper.py > MANIFEST.sha256)
expect CANNOT_TELL "U1 run-time path, no allowlist" $PY $PF --launcher "$U/launch.sh" --stamped "$U/MANIFEST.sha256" --root "$U"
echo "0000000000000000000000000000000000000000000000000000000000000000  eval_a.jsonl" > "$U/ALLOW.sha256"; (cd "$U" && shasum -a 256 launch.sh helper.py ALLOW.sha256 > MANIFEST.sha256)
expect GO "U2 run-time path covered by a stamped allowlist" $PY $PF --launcher "$U/launch.sh" --stamped "$U/MANIFEST.sha256" --allow "eval_.*=$U/ALLOW.sha256" --root "$U"
echo "x" >> "$U/ALLOW.sha256"
expect CANNOT_TELL "U3 allowlist edited after the stamp" $PY $PF --launcher "$U/launch.sh" --stamped "$U/MANIFEST.sha256" --allow "eval_.*=$U/ALLOW.sha256" --root "$U"
expect CANNOT_TELL "B1 second block server unreachable" env PF_API2=http://127.0.0.1:9 $PY $PF --first-job @$K/job_keystone_ibm_marrakesh.json --proof $Y/read/fresh/PLAN_YO_FRESH.md

echo; echo "== kill tests: $pass as required, $bad wrong"
