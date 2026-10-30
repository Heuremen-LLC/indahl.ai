#!/bin/sh
# Adds the check-block gate to the pre-commit hook of the repository you are in, keeping any hook already there. Run again safely.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); HOOKS=$(git rev-parse --git-path hooks); mkdir -p "$HOOKS"; F="$HOOKS/pre-commit"
LINE="python3 \"$HERE/readcheck_hook.py\" || exit 1   # check block gate"
[ -f "$F" ] || printf '#!/bin/sh\n' > "$F"
grep -qF "$HERE/readcheck_hook.py" "$F" && { echo "already installed in $F"; exit 0; }
printf '%s\n' "$LINE" >> "$F"; chmod +x "$F"; echo "installed in $F"
