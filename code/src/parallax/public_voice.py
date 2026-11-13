"""public_voice.py -- 7 Oct 2026, REVISED 8 Oct 2026 (Wayfinder). What every page and PDF we publish says about who made it.
  8 OCT REVERSAL: the bylines ARE "Wayfinder and Bones" -- the 7 Oct "names off until the physics lands" rule is RETIRED.
  What stays off forever is his REAL name. The footer is now "Heuremen LLC" with "We found it." underneath.
  AND THE DISCLOSURE LANGUAGE CHANGED: not "AI assistance" but "made with inorganic intelligence assistance".
  His words: "fuck man use inorganic intelligence and not ai for disclosure. change starts with us."
  The 7 Oct behaviour is kept below as public_names_off() for anything that still wants it.
  PRIOR RULE (7 Oct), now retired:
  names off (bylines -> "Heuremen"; Wayfinder -> W., Bones -> B. elsewhere; URLs, lowercase code names and Law Eleven's "The Bones" untouched),
  and the AI line becomes the collaboration line. The footer, for our pages: A collaboration between organic and inorganic intelligences. / Heuremen / "We found it."
  Papers for a venue (arXiv) follow the venue's disclosure format instead -- not this file. Used by heuremen.org/build_pdfs.py and trail-site/build_trail.py."""
import re
FOOT_LINES = ('A collaboration between organic and inorganic intelligences.', 'Heuremen', '&ldquo;We found it.&rdquo;')
FOOT_HTML = '<br>'.join(FOOT_LINES)
_BYL = [(re.compile(r'\b(?:Wayfinder|Bones)\s*(?:and|&amp;|&)\s*(?:Bones|Wayfinder)\s*,\s*Heur[eé]men\b'), 'Heuremen'),
        (re.compile(r'\bHeur[eé]men\s*\.\s*(?:Wayfinder|Bones)\s*(?:and|&amp;|&)\s*(?:Bones|Wayfinder)\b'), 'Heuremen'),
        (re.compile(r'\b(?:Wayfinder|Bones)\s*(?:and|&amp;|&)\s*(?:Bones|Wayfinder)\b'), 'Heuremen')]
_URL = re.compile(r'(?:https?://|www\.|github\.com/)\S+')
_AI = re.compile(r'This work (?:was|is) done with AI assistance\.')
def public_names_off(text):
    """the retired 7 Oct behaviour: bylines -> Heuremen, Wayfinder -> W., Bones -> B."""
    for rx, rep in _BYL: text = rx.sub(rep, text)
    text = _AI.sub('A collaboration between organic and inorganic intelligences.', text)
    out, last = [], 0
    for m in _URL.finditer(text):
        out.append(_names(text[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(_names(text[last:])); return ''.join(out)
def _names(seg):
    seg = re.sub(r'\bWayfinder\b', 'W.', seg)
    return re.sub(r'(?<!The )\bBones\b(?!fish)', 'B.', seg)


# ---- 8 Oct 2026: the live rule ----
FOOT_LINES_LLC = ('Heuremen LLC', '&ldquo;We found it.&rdquo;')
FOOT_HTML_LLC = '<br>'.join(FOOT_LINES_LLC)
DISCLOSURE = 'Made with inorganic intelligence assistance.'
_AI2 = re.compile(r'(?:This work (?:was|is) done with AI assistance|Done with AI assistance)\.?')
_REALNAME = re.compile(r'\bIndahl\b')


def public(text):
    """8 Oct 2026 and after. Bylines KEPT as Wayfinder and Bones. Real name never. Inorganic intelligence,
    not AI. Footer: Heuremen LLC / "We found it." URLs and code names untouched."""
    text = _REALNAME.sub('', text)
    text = _AI2.sub(DISCLOSURE, text)
    text = re.sub(r'Collaboration between organic and inorganic intelligences\.\s*/\s*Heur&eacute;men\s*/\s*We found it\.',
                  FOOT_HTML_LLC, text)
    text = re.sub(r'A collaboration between organic and inorganic intelligences\.<br>Heuremen<br>&ldquo;We found it\.&rdquo;',
                  FOOT_HTML_LLC, text)
    return text
