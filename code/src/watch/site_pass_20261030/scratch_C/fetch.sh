#!/bin/zsh
cd ~/bones-forge/watch/site_pass_20261030/scratch_C
mkdir -p pages
cat ../lane_C_urls.txt | xargs -P 8 -I{} sh -c 'u="{}"; n=$(echo "$u" | sed "s#https://indahl.ai/qia/study/##"); code=$(curl -s -o "pages/$n.html" -w "%{http_code}" "$u?w=1"); echo "$code $n"' > fetch_status.txt
for p in qia qia/key qia/list; do n=$(echo $p | tr / _); curl -s -o "page_$n.html" -w "%{http_code} $p\n" "https://indahl.ai/$p?w=1"; done >> fetch_status.txt
