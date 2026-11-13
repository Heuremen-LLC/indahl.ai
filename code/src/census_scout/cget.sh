#!/bin/zsh
# usage: cget.sh URL  (key appended at call time, never printed)
key=$(cat "$HOME/Documents/Heuremen LLC/ACCOUNTS/census_api_key.txt" | tr -d '\n ')
sep='?'; [[ "$1" == *\?* ]] && sep='&'
curl -s -m 60 "$1${sep}key=$key"
