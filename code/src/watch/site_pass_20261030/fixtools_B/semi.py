import re
LOWER_KEEP = {'arxiv','ibm','ibmq','pdf','api','sd','se','rb','zz','cz','sx','qpu','dd','zne','pec','qaoa','vqe','ghz','mcm','cnot','sqd','pp','mhz','khz'}
UPPER_KEEP = re.compile(r'[_0-9]|[A-Z]|^(arxiv|ibm|ibmq|pdf|api|e\.g|i\.e|sd|se|rb|zz|cz|sx|qpu|dd|zne|pec|qaoa|vqe)$')
def protect(t):
    """split into [(is_quote, segment)] so that quoted words are left alone"""
    spans = []
    for m in re.finditer(r'“[^”]*”|"[^"]*"|(?<![\w])\'[^\']{3,}?\'(?![\w])', t):
        spans.append((m.start(), m.end()))
    out = []; pos = 0
    for a, b in spans:
        if a > pos: out.append((False, t[pos:a]))
        out.append((True, t[a:b])); pos = b
    if pos < len(t): out.append((False, t[pos:]))
    return out
def de_semi(t):
    if ';' not in t: return t
    segs = protect(t)
    depth = 0; res = []
    for qi, (isq, s) in enumerate(segs):
        if isq:
            res.append(s); continue
        o = []; i = 0
        while i < len(s):
            ch = s[i]
            if ch in '([': depth += 1
            elif ch in ')]': depth = max(0, depth - 1)
            if ch == ';':
                # skip following spaces, and a second semicolon
                j = i + 1
                while j < len(s) and s[j] in ' ;': j += 1
                nxt = s[j:j + 40]
                prev = ''.join(o).rstrip()
                rest_is_end = (j >= len(s)) and qi == len(segs) - 1
                if rest_is_end: i = j; continue
                if prev.endswith('.'): sep = ' '
                elif depth > 0: sep = ', '
                else: sep = '. '
                # capitalise only an ordinary word
                m = re.match(r'([A-Za-z][A-Za-z\-]*)', nxt)
                tok = nxt.split(' ')[0]
                ident = bool(re.search(r'[_0-9=<>/]', tok)) or (m is not None and (len(m.group(1)) == 1 and m.group(1) != 'a')) or (m is not None and m.group(1) in LOWER_KEEP)
                cap = bool(m) and sep in ('. ', ' ') and m.group(1)[0].islower() and m.group(1).islower() and not ident
                if sep == '. ' and m and ident and not nxt[0].isupper(): sep = ', '
                if j < len(s) and cap: s = s[:j] + s[j].upper() + s[j + 1:]
                o = list(prev); o.append(sep.rstrip(' ') if sep != ' ' else '')
                o.append(' ' if sep in (' ', ', ', '. ') else '')
                i = j; continue
            o.append(ch); i += 1
        res.append(''.join(o))
    return ''.join(res)
if __name__ == '__main__':
    for t in ["L=6 value 0.236 ± 0.005 is shot noise only; PEC bounds printed at L=2 and 4 only; L=6 PEC in Appendix F is a projection",
              "result.; does not reproduce", "the paper (text vs own table; per-job vs total) is off; ibm_fez reads high; the delta is small", "He said “a; b” and then; stopped", "ends with semi;", "x 1.2; 3 > 4 (a; b; c)"]:
        print(repr(de_semi(t)))
