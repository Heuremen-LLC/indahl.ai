#!/bin/bash
# build_arxiv.sh -- the arXiv submission package in one command (23 Oct 2026; was hand-built until now). Steps, each refusing on failure:
#   1 BUILD   copy main.tex, refs.bib, figures/ to a clean dir; tectonic compiles it and keeps main.bbl.
#   2 INLINE  arXiv wants no .bib: the .bbl replaces \bibliography{refs} (and the \bibliographystyle line is dropped).
#   3 PACK    ~/Desktop/arxiv_submission_<YYYYMMDD>.tar.gz = main.tex (inlined) + only the figure files main.tex uses. Older same-day tar renamed.
#   4 VERIFY  unpack the tar into an empty dir, compile it as arXiv would, and compare with the live heuremen.org paper: same page count,
#             same text (whitespace-normalised), no "??" or [?] unresolved references.
set -euo pipefail
B="$HOME/bones-forge"; P="$B/arxiv_one_readout"; OUT="$HOME/Desktop/arxiv_submission_$(date +%Y%m%d).tar.gz"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
echo "== 1 BUILD"
mkdir -p "$W/b" && cp -p "$P/main.tex" "$P/refs.bib" "$W/b/" && cp -Rp "$P/figures" "$W/b/"
(cd "$W/b" && tectonic -k main.tex >/dev/null 2>&1) || { echo "REFUSED: tectonic could not build main.tex"; exit 1; }
[ -s "$W/b/main.bbl" ] || { echo "REFUSED: no main.bbl"; exit 1; }
echo "== 2 INLINE"
mkdir -p "$W/a/figures"
python3 - "$W/b/main.tex" "$W/b/main.bbl" "$W/a/main.tex" <<'EOF'
import sys, re
tex = open(sys.argv[1]).read(); bbl = open(sys.argv[2]).read()
assert tex.count('\\bibliography{refs}') == 1, 'REFUSED: expected exactly one \\bibliography{refs}'
tex = re.sub(r'^\\bibliographystyle\{[^}]*\}\s*\n', '', tex, flags=re.M)
tex = tex.replace('\\bibliography{refs}', bbl.strip())
open(sys.argv[3], 'w').write(tex)
EOF
for f in $(grep -o 'figures/[A-Za-z0-9_.-]*' "$W/a/main.tex" | sort -u); do
  src="$W/b/$f"; [ -f "$src" ] || src="$W/b/$f.pdf"; [ -f "$src" ] || { echo "REFUSED: $f not found"; exit 1; }; cp -p "$src" "$W/a/figures/"; done
echo "  figures: $(ls "$W/a/figures" | tr '\n' ' ')"
echo "== 3 PACK"
[ -f "$OUT" ] && { O="$HOME/.Trash/superseded_builds_$(date +%Y%m%d)"; mkdir -p "$O"; mv "$OUT" "$O/$(basename "${OUT%.tar.gz}").superseded_$(date +%H%M%S).tar.gz"; }
(cd "$W/a" && COPYFILE_DISABLE=1 tar -czf "$OUT" main.tex figures)
echo "  $OUT ($(stat -f %z "$OUT") bytes, sha256 $(shasum -a 256 "$OUT" | cut -c1-16))"
echo "== 4 VERIFY"
mkdir -p "$W/t" && tar -xzf "$OUT" -C "$W/t" && (cd "$W/t" && tectonic main.tex >/dev/null 2>&1) || { echo "REFUSED: the tar does not compile"; exit 1; }
"$B/qvenv/bin/python3" - "$W/t/main.pdf" "$B/heuremen.org/a-readout-is-not-an-idle.pdf" <<'EOF'
import sys, re
from pypdf import PdfReader
a, b = PdfReader(sys.argv[1]), PdfReader(sys.argv[2])
ta = ' '.join(''.join(p.extract_text() or '' for p in a.pages).split()); tb = ' '.join(''.join(p.extract_text() or '' for p in b.pages).split())
print(f'  pages: tar {len(a.pages)}, live {len(b.pages)} | text identical: {ta == tb} | unresolved refs: {len(re.findall(r"\[\?\]|\?\?", ta))}')
assert len(a.pages) == len(b.pages), 'REFUSED: page count differs from the live paper'
assert not re.findall(r'\[\?\]|\?\?', ta), 'REFUSED: unresolved references'
if ta != tb:
    i = next(k for k in range(min(len(ta), len(tb))) if ta[k] != tb[k]); print('  first difference:', repr(ta[max(0,i-60):i+60]), '|', repr(tb[max(0,i-60):i+60]))
    raise SystemExit('REFUSED: text differs from the live paper (rebuild the live PDF first, or check main.tex)')
print('  VERIFIED')
EOF
