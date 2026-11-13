#!/bin/bash
# render.sh -- THE ONLY WAY A LIGERA PAGE BECOMES A PDF. (Bones, 9 Oct 2026.)
#
# A box reached a public page because the render procedure verified NUMBERS and nothing verified
# CHARACTERS. Then the character check I wrote only ran when I remembered to run it, which is the
# same fault one level up. So the gate is IN the render path: no PDF is produced from a source
# carrying an unvetted codepoint.
#
#   ./render.sh LAS_ECUACIONES.html ~/Desktop/LAS_ECUACIONES.pdf
set -euo pipefail
SRC="$1"; OUT="$2"
LIG="$HOME/bones-forge/ligera"
[ -f "$SRC" ] || SRC="$LIG/$SRC"
# ABSOLUTE, ALWAYS. A relative path became file://LAS_ECUACIONES.html, which is not a URL, and
# Chrome wrote nothing -- caught only because the render line checks for "bytes written" instead of
# assuming success. Resolve it before building the URL.
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
case "$OUT" in /*) ;; *) OUT="$PWD/$OUT";; esac
"$HOME/bones-forge/qvenv/bin/python3" "$HOME/bones-forge/watch/glyph_scan.py" --file "$SRC" || {
  echo "  RENDER REFUSED: $SRC did not pass the glyph gate. No PDF written." >&2
  exit 1
}
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$OUT" --virtual-time-budget=4000 "file://$SRC" 2>&1 \
  | grep -o "[0-9]* bytes written to file .*" || { echo "  CHROME WROTE NOTHING" >&2; exit 1; }
# and verify the output carries every source codepoint, which is the second seat
"$HOME/bones-forge/qvenv/bin/python3" - "$SRC" "$OUT" <<'PY'
import sys, os, re
sys.path.insert(0, os.path.expanduser('~/bones-forge/watch'))
import glyph_scan as g
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8', errors='replace').read()
want = {ord(c) for c in s if ord(c) > 127} | {c for c in g.entities(s) if c > 127}
have = g.pdf_codepoints(out) or set()
miss = sorted(c for c in want if c not in have)
if miss:
    print('  POST-RENDER CHECK FAILED -- in the source, absent from the PDF font map:')
    for c in miss:
        print(f'    U+{c:04X}')
    sys.exit(1)
print(f'  post-render: all {len(want)} source codepoints present in the PDF')
PY
