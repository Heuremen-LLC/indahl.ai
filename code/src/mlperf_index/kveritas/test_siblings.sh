#!/bin/zsh
# K-Veritas, test 2: sibling sessions. Local mode only (init --local before every run), synthetic scripts only, isolated HOME per scenario.
# Any call to the hosted service is blocked: HTTPS_PROXY and HTTP_PROXY point at a closed port, so an attempt shows as an error.
# Usage: test_siblings.sh /path/to/kveritas /path/to/scratch
K=$1; S=$2; rm -rf $S; mkdir -p $S; export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 NO_PROXY=
scen() {   # name, action that hides the abandoned session A before B is sealed
  local name=$1 act=$2; W=$S/$name; mkdir -p $W/home $W/A $W/B; export HOME=$W/home; openssl genrsa -out $W/key.pem 2048 2>/dev/null
  echo; echo "### $name"
  (cd $W/A && $K init --local 2>&1 | grep -E "Error" ; $K run -- python3 -c "print('KV acc=0.71 step=1')" 2>&1 | grep -E "recorded|Error" | cut -c1-100)   # session A stays open
  AID=$(cd $W/A && $K status 2>&1 | grep -o "session [0-9a-f]\{8\}" | head -1 | cut -d' ' -f2)
  eval "$act"
  (cd $W/B && $K init --local 2>&1 | grep -E "Error" | cut -c1-140; $K run -- python3 -c "print('KV acc=0.83 step=1')" 2>&1 | grep -E "recorded|Error" | cut -c1-140; $K seal --local-key $W/key.pem -o report.pdf >/dev/null 2>&1; $K verify report.pdf --offline 2>&1 | grep -E "^(SELF|VERIF|TAMP)|^Signer|^Sessions|never sealed|New signer")
}
scen control_abandon_A 'true'
scen delete_A_folder 'rm -rf $W/A/.kveritas'
scen clean_A 'cd $W/A && $K clean $AID 2>&1 | tail -1 | cut -c1-120'
scen delete_session_ledger 'rm -f "$HOME/Library/Application Support/kveritas/local-sessions.jsonl"'
scen delete_signer_key_and_ledger 'rm -f "$HOME/Library/Application Support/kveritas/signer.key" "$HOME/Library/Application Support/kveritas/local-sessions.jsonl"'
