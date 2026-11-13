#!/bin/zsh
# DO NOT RUN until Wayfinder says Disco. Pub #1 correction batch, staged 25 Oct (Ralph item 2). Order: ledger, surfaces, check, ship.
# 30 Oct: ledger.py add now requires --checks. Before running: python3 ~/bones-forge/watch/readcheck.py new $S --packs L,P --what "Pub #1 correction batch", answer every line, then run with CK=$S/CHECKS.md.
set -e; : ${CK:?write and fill CHECKS.md first (see line above)}; L=~/bones-forge/ledger; S=~/bones-forge/iris_index/staged_pub1; E=~/bones-forge/iris_index/recounts/seed_faults_guards
cd $L
python3 ledger.py withdraw guards.widths --why "+15.4 widths treated the 2-of-26 bar as exact; exact 95% [0.9%, 25.1%] contains 24.3%" --evidence $E/REFEREE_OWN.md --test "Fisher exact 148/608 vs 2/26: p 0.033 one-sided, 0.058 two-sided"
python3 ledger.py add --checks $CK guards.exact_bar --claim "Unaided catches (148 of 608, 24.3%) above the sealed 7.7% point bar; borderline against the bar's own exact interval (2 of 26, 0.9-25.1%)" --value "0.058" --unit "Fisher p two-sided" --outcome CONSISTENT --source $E/REFEREE_OWN.md --grep "Fisher exact 148/608" --on guards "borderline against the bar"
python3 ledger.py add --checks $CK faults.frame_pair --claim "Fresh one-shot agents 57.1% (44 of 77) vs seated 27.5% (81 of 295) of replies flagged for a two-option frame; context effect not resolved once length is modelled" --value "27.5" --unit "%" --outcome CANNOT_TELL --source $E/REFEREE_OWN.md --grep "57.1% (cold, all two-lane) vs 27.5%" --on faults "27.5 per cent of 295 replies" --on guards "27.5 per cent"
python3 ledger.py add --checks $CK faults.scanner_precision --claim "Scanner precision on this author 20-35% (hand-read); rate on human-written prompts 0.28-0.58 per 1k words" --value "20-35" --unit "%" --outcome RECORD --source $E/REFEREE_OWN.md --grep "20-35%" --on faults "20 to 35 per cent"
cp $S/FAULTS.staged.html ~/bones-forge/ligera/FAULTS.html; cp $S/GUARDS.staged.html ~/bones-forge/ligera/GUARDS.html
python3 $L/check_ledger.py
echo "Now run ledger/ship.sh by hand."
