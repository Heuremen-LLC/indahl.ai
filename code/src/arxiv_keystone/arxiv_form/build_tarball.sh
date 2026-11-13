#!/bin/zsh
# builds the arXiv upload: main.tex + refs.bib only (arXiv rebuilds the bibliography from the .bib), checks it compiles with tectonic first
set -e
cd ~/bones-forge/arxiv_keystone/paper
tectonic main.tex >/dev/null 2>&1 && echo "compiles (tectonic)"
grep -n "usepackage{array}\|usepackage{booktabs}" main.tex && { echo "STOP: array/booktabs breaks revtex4-2 on arXiv TL2025"; exit 1; } || true
rm -rf /tmp/kstar && mkdir -p /tmp/kstar && cp main.tex refs.bib fig1.pdf /tmp/kstar/
tar -czf ~/Desktop/PUB3_ARXIV_UPLOAD_THIS.tar.gz -C /tmp/kstar main.tex refs.bib fig1.pdf
cp main.pdf ~/Desktop/A_Readouts_Kick_Is_a_Turn.pdf
cp ~/bones-forge/arxiv_keystone/paper/ABSTRACT_ARXIV.txt ~/Desktop/PUB3_ABSTRACT.txt
tar -tzf ~/Desktop/PUB3_ARXIV_UPLOAD_THIS.tar.gz; ls -la ~/Desktop/PUB3_ARXIV_UPLOAD_THIS.tar.gz
