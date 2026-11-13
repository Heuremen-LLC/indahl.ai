#!/bin/zsh
cd ~/bones-forge/watch/site_pass_20261030/scratch_E
rm -f status.tsv
i=0
while read -r u; do
  i=$((i+1))
  slug=$(echo "$u" | sed 's#https://indahl.ai/##; s#/#__#g')
  [ -z "$slug" ] && slug=root
  code=$(curl -s -L -o "pages/$slug.html" -w '%{http_code}\t%{size_download}\t%{content_type}\t%{url_effective}' "$u?w=1")
  echo -e "$u\t$code" >> status.tsv
done < ../lane_E_urls.txt
