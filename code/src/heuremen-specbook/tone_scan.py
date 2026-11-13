"""tone_scan.py -- business pages state; they do not argue, pitch or repeat (23 Oct 2026, from six catches in one afternoon,
all made by the human reader, none by the writer: Faults entry 45, Guards entry 39). Business pages only (indahl.ai).
  A ARGUE   phrasing that persuades or explains why instead of stating (pitch voice).
  B SLOGAN  a page header carrying a second line under its headline (a tagline over a fact).
  C REPEAT  one content word twice inside a page header (kicker, headline and any line under it). A page-wide version (3+ uses
            anywhere) was tried first and fired on 11 lines of the approved site, where repeats are section and step names: narrowed.
Usage: python3 tone_scan.py FILE.html ...   (exit 1 on any hit)"""
import re, html, sys, os
ARGUE = [r"\bso (?:that )?you can\b", r"\bwhich means\b", r"\bwe help\b", r"\byou(?:'|’)ll\b", r"\bactually\b", r"\bhonest(?:ly)?\b",
         r"\btrust(?:ed(?! flaggers?\b)|worthy)?\b", r"\bensur(?:e|es|ing)\b", r"\bworld[- ]class\b", r"\bholds? up\b", r"\bbefore you see it\b",
         r"\bworth checking\b", r"\bdeliberately\b", r"\bwe do not force\b", r"\bnever one\b", r"\bdecided later\b", r"\bstart with a\b"]
STOP = set("""about above after again against also among another because been before being below between both cannot could
does doing during each either every from further have having into itself more most other ought same should some such than that
their them then there these they this those through under until very were what when where which while with within without would
your yours ours engagement engagements indahl heuremen quantum inorganic research intelligence systems audit idle iris
privacy terms security contact inquiries""".split())
def visible(s):
    s = re.sub(r'(?s)<(script|style|form|nav|footer|header)\b.*?</\1>', ' ', s)
    s = re.sub(r'(?s)<p class="foot">.*?</p>', ' ', s); s = re.sub(r'(?s)<title>.*?</title>|<meta[^>]*>', ' ', s)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())
def scan(path):
    s = open(path, encoding='utf-8', errors='replace').read(); t = visible(s); hits = []
    # 10 Nov 2026 (WIKI ship): ARGUE reads our own voice. A third party's sentence quoted verbatim as the stated figure under test, marked
    # <span class="quote">, is their voice and is not ours to reword ("the home of trusted information online", Wikimedia Foundation homepage).
    # Only ARGUE skips it, and only inside that span. SLOGAN and REPEAT read the page as before.
    ta = visible(re.sub(r'(?s)<span class="quote">.*?</span>', ' ', s))
    # 10 Nov 2026 (SOCIAL ship): "trusted flagger" is a legal term, EU Digital Services Act (Regulation (EU) 2022/2065) Article 22, and
    # the name of a field in the DSA reports read on /social. ARGUE skips only that exact phrase ("trusted flagger" or "trusted flaggers"),
    # by the negative lookahead on "trusted" in ARGUE above. "trust", "trustworthy" and "trusted" before any other word still hit.
    for a in ARGUE:
        for m in re.finditer(a, ta, re.I): hits.append(('A ARGUE', m.group(0)))
    if re.search(r'<section class="hero">.*?<h1>.*?</h1>\s*<p class="sub">', s, re.S): hits.append(('B SLOGAN', 'header has a line under its headline'))
    from collections import Counter
    hero = re.search(r'(?s)<section class="hero">(.*?)</section>', s)
    ht = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<p class="actions">.*?</p>', ' ', hero.group(1)))).split()) if hero else ''
    c = Counter(w.lower()[:6] for w in re.findall(r"[A-Za-z]{6,}", ht) if w.lower() not in STOP)
    for stem, k in c.items():
        if k >= 2: hits.append(('C REPEAT', f'{stem}* x{k} in the header'))
    return hits
if __name__ == '__main__':
    bad = 0
    for f in sys.argv[1:]:
        for kind, h in scan(f): print(f'  {kind:8} {os.path.basename(f)}: {h}'); bad += 1
    print(f'tone scan: {len(sys.argv)-1} pages; hits: {bad}'); sys.exit(1 if bad else 0)
