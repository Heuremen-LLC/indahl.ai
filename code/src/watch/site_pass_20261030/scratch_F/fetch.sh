#!/bin/zsh
u="$1"; id="${u##*/}"
curl -s -m 30 -o pages/$id.html -w "$id %{http_code} %{size_download} %{time_total} %{content_type}\n" "$u?w=1"
