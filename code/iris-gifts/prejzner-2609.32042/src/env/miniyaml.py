"""miniyaml.py (ours): a small YAML reader for the task files of arXiv 2609.32042.

Standard library only. The task files use a narrow YAML subset: comments, block mappings, block sequences, flow
mappings and sequences on one line, double and single quoted scalars, plain scalars. Anything outside that subset
(anchors, tags, block scalars with | or >, multi-line scalars, tabs, multiple documents) raises YamlError rather than
being guessed at. Mapping order is kept (Python dicts). Plain scalars resolve the way the common YAML 1.1 loaders do
for the types that appear in the tasks: null, bool (true/false/yes/no/on/off in three cases), decimal int, float with a
dot. Plain scalars that look like other YAML 1.1 types (hex, octal, binary, sexagesimal, dates, inf, nan) raise, so a
silent type change cannot slip in.
"""
import re


class YamlError(ValueError):
    pass


_NULLS = {"~", "null", "Null", "NULL", ""}
_TRUE = {"yes", "Yes", "YES", "true", "True", "TRUE", "on", "On", "ON"}
_FALSE = {"no", "No", "NO", "false", "False", "FALSE", "off", "Off", "OFF"}
_INT = re.compile(r"^[-+]?(?:0|[1-9][0-9_]*)$")
_FLOAT = re.compile(r"^[-+]?(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9_]+)(?:[eE][-+][0-9]+)?$")
_SUSPECT = re.compile(
    r"^[-+]?(?:0[0-9_]+|0x[0-9a-fA-F_]+|0b[01_]+|[0-9][0-9_]*(?::[0-5]?[0-9])+(?:\.[0-9_]*)?)$"
    r"|^\d{4}-\d{1,2}-\d{1,2}|^[-+]?\.(?:inf|Inf|INF)$|^\.(?:nan|NaN|NAN)$|^<<$|^=$"
)


def _plain(token):
    """Resolve one plain (unquoted) scalar."""
    if token in _NULLS:
        return None
    if token in _TRUE:
        return True
    if token in _FALSE:
        return False
    if _SUSPECT.match(token):
        raise YamlError("plain scalar %r looks like an unsupported YAML type" % token)
    if _INT.match(token):
        return int(token.replace("_", ""))
    if _FLOAT.match(token):
        return float(token.replace("_", ""))
    if token[:1] in "&*!|>%@`" and token != "":
        raise YamlError("unsupported YAML indicator at start of %r" % token)
    return token


_ESC = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
    "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": " ", "P": " ",
}


class _Cursor:
    """Character cursor over one logical line, used for flow collections and quoted scalars."""

    def __init__(self, s, i=0):
        self.s = s
        self.i = i

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ""

    def skip_ws(self):
        while self.i < len(self.s) and self.s[self.i] == " ":
            self.i += 1

    def dq(self):
        assert self.s[self.i] == '"'
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                raise YamlError("unterminated double-quoted scalar: %r" % self.s)
            c = self.s[self.i]
            if c == '"':
                self.i += 1
                return "".join(out)
            if c == "\\":
                self.i += 1
                if self.i >= len(self.s):
                    raise YamlError("dangling backslash")
                e = self.s[self.i]
                if e in _ESC:
                    out.append(_ESC[e])
                    self.i += 1
                elif e in "xuU":
                    n = {"x": 2, "u": 4, "U": 8}[e]
                    hexs = self.s[self.i + 1:self.i + 1 + n]
                    if len(hexs) != n or not re.fullmatch(r"[0-9a-fA-F]+", hexs):
                        raise YamlError("bad \\%s escape" % e)
                    out.append(chr(int(hexs, 16)))
                    self.i += 1 + n
                else:
                    raise YamlError("unsupported escape \\%s" % e)
            else:
                out.append(c)
                self.i += 1

    def sq(self):
        assert self.s[self.i] == "'"
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                raise YamlError("unterminated single-quoted scalar: %r" % self.s)
            c = self.s[self.i]
            if c == "'":
                if self.s[self.i + 1:self.i + 2] == "'":
                    out.append("'")
                    self.i += 2
                    continue
                self.i += 1
                return "".join(out)
            out.append(c)
            self.i += 1

    def flow_value(self):
        self.skip_ws()
        c = self.peek()
        if c == "{":
            return self.flow_map()
        if c == "[":
            return self.flow_seq()
        if c == '"':
            return self.dq()
        if c == "'":
            return self.sq()
        j = self.i
        while j < len(self.s) and self.s[j] not in ",]}":
            if self.s[j] == ":" and (j + 1 >= len(self.s) or self.s[j + 1] in " ,]}"):
                break
            j += 1
        tok = self.s[self.i:j].strip()
        self.i = j
        return _plain(tok)

    def flow_seq(self):
        assert self.s[self.i] == "["
        self.i += 1
        out = []
        while True:
            self.skip_ws()
            if self.peek() == "]":
                self.i += 1
                return out
            out.append(self.flow_value())
            self.skip_ws()
            if self.peek() == ",":
                self.i += 1
            elif self.peek() == "]":
                continue
            else:
                raise YamlError("bad flow sequence near %r" % self.s[self.i:])

    def flow_map(self):
        assert self.s[self.i] == "{"
        self.i += 1
        out = {}
        while True:
            self.skip_ws()
            if self.peek() == "}":
                self.i += 1
                return out
            if self.peek() in ('"', "'"):
                key = self.dq() if self.peek() == '"' else self.sq()
            else:
                j = self.i
                while j < len(self.s) and not (self.s[j] == ":" and (j + 1 >= len(self.s) or self.s[j + 1] in " ,]}")):
                    if self.s[j] in ",]}":
                        raise YamlError("flow mapping key without colon near %r" % self.s[self.i:])
                    j += 1
                key = self.s[self.i:j].strip()
                self.i = j
            self.skip_ws()
            if self.peek() != ":":
                raise YamlError("missing colon in flow mapping near %r" % self.s[self.i:])
            self.i += 1
            self.skip_ws()
            if self.peek() in (",", "}"):
                val = None
            else:
                val = self.flow_value()
            if key in out:
                raise YamlError("duplicate key %r" % key)
            out[key] = val
            self.skip_ws()
            if self.peek() == ",":
                self.i += 1
            elif self.peek() == "}":
                continue
            else:
                raise YamlError("bad flow mapping near %r" % self.s[self.i:])


def _strip_comment(line):
    """Remove a trailing comment (a # at line start or after whitespace, outside quotes)."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q == '"':
            if c == "\\":
                i += 1
            elif c == '"':
                q = None
        elif q == "'":
            if c == "'":
                q = None
        else:
            if c == '"' or c == "'":
                # a quote only opens a quoted scalar at a token start
                if i == 0 or line[i - 1] in " [{,:-" :
                    q = c
            elif c == "#" and (i == 0 or line[i - 1] in " \t"):
                return line[:i].rstrip()
        i += 1
    return line.rstrip()


class _Line:
    __slots__ = ("indent", "text", "no")

    def __init__(self, indent, text, no):
        self.indent = indent
        self.text = text
        self.no = no


def _split(text):
    lines = []
    for no, raw in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
        if raw.strip() == "" or raw.lstrip(" ").startswith("#"):
            continue
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise YamlError("line %d: tab indentation is not supported" % no)
        if raw.startswith("---") or raw.startswith("..."):
            raise YamlError("line %d: document markers are not supported" % no)
        body = _strip_comment(raw)
        indent = len(body) - len(body.lstrip(" "))
        lines.append(_Line(indent, body.lstrip(" "), no))
    return lines


def _find_key_end(t):
    """Return the index of the colon that ends the mapping key in t, or -1."""
    if t[:1] == '"':
        c = _Cursor(t)
        c.dq()
        j = c.i
    elif t[:1] == "'":
        c = _Cursor(t)
        c.sq()
        j = c.i
    else:
        j = 0
        while j < len(t):
            if t[j] == ":" and (j + 1 == len(t) or t[j + 1] == " "):
                return j
            if t[j] in "{[" and j == 0:
                return -1
            j += 1
        return -1
    while j < len(t) and t[j] == " ":
        j += 1
    if j < len(t) and t[j] == ":" and (j + 1 == len(t) or t[j + 1] == " "):
        return j
    return -1


def _key(t, colon):
    k = t[:colon].strip()
    if k[:1] == '"':
        return _Cursor(k).dq()
    if k[:1] == "'":
        return _Cursor(k).sq()
    v = _plain(k)
    if not isinstance(v, str):
        raise YamlError("non-string mapping key %r is not supported" % k)
    return v


def _inline(t, no):
    """Parse a value that sits on one line (flow collection, quoted or plain scalar)."""
    c = _Cursor(t)
    c.skip_ws()
    ch = c.peek()
    if ch in ("{", "[", '"', "'"):
        v = c.flow_value()
        c.skip_ws()
        if c.i != len(t):
            raise YamlError("line %d: trailing text after value: %r" % (no, t[c.i:]))
        return v
    if ": " in t or t.endswith(":"):
        raise YamlError("line %d: unsupported nested mapping in plain scalar %r" % (no, t))
    return _plain(t.strip())


class _Parser:
    def __init__(self, lines):
        self.lines = lines
        self.p = 0

    def block(self, indent):
        ln = self.lines[self.p]
        if ln.text == "-" or ln.text.startswith("- "):
            return self.seq(indent)
        if _find_key_end(ln.text) >= 0:
            return self.mapping(indent)
        v = _inline(ln.text, ln.no)
        self.p += 1
        return v

    def mapping(self, indent):
        out = {}
        while self.p < len(self.lines) and self.lines[self.p].indent == indent:
            ln = self.lines[self.p]
            if ln.text == "-" or ln.text.startswith("- "):
                break
            colon = _find_key_end(ln.text)
            if colon < 0:
                raise YamlError("line %d: expected 'key: value', got %r" % (ln.no, ln.text))
            key = _key(ln.text, colon)
            if key in out:
                raise YamlError("line %d: duplicate key %r" % (ln.no, key))
            rest = ln.text[colon + 1:].strip()
            self.p += 1
            if rest == "":
                nxt = self.lines[self.p] if self.p < len(self.lines) else None
                if nxt is not None and nxt.indent > indent:
                    out[key] = self.block(nxt.indent)
                elif nxt is not None and nxt.indent == indent and (nxt.text == "-" or nxt.text.startswith("- ")):
                    out[key] = self.seq(indent)
                else:
                    out[key] = None
            else:
                if rest[0] in "|>":
                    raise YamlError("line %d: block scalars are not supported" % ln.no)
                out[key] = _inline(rest, ln.no)
        if self.p < len(self.lines) and self.lines[self.p].indent > indent:
            raise YamlError("line %d: unexpected indentation" % self.lines[self.p].no)
        return out

    def seq(self, indent):
        out = []
        while self.p < len(self.lines) and self.lines[self.p].indent == indent:
            ln = self.lines[self.p]
            if not (ln.text == "-" or ln.text.startswith("- ")):
                break
            rest = ln.text[1:].lstrip(" ")
            if rest == "":
                self.p += 1
                nxt = self.lines[self.p] if self.p < len(self.lines) else None
                if nxt is not None and nxt.indent > indent:
                    out.append(self.block(nxt.indent))
                else:
                    out.append(None)
                continue
            inner = indent + (len(ln.text) - len(rest))
            if rest[0] in "|>":
                raise YamlError("line %d: block scalars are not supported" % ln.no)
            if rest[0] not in "{[\"'" and _find_key_end(rest) >= 0:
                # "- key: value" starts a mapping whose keys sit at column `inner`
                self.lines[self.p] = _Line(inner, rest, ln.no)
                out.append(self.mapping(inner))
            elif rest.startswith("- "):
                self.lines[self.p] = _Line(inner, rest, ln.no)
                out.append(self.seq(inner))
            else:
                out.append(_inline(rest, ln.no))
                self.p += 1
        return out


def loads(text):
    lines = _split(text)
    if not lines:
        return None
    p = _Parser(lines)
    v = p.block(lines[0].indent)
    if p.p != len(lines):
        raise YamlError("line %d: unparsed content" % lines[p.p].no)
    return v


def load_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        return loads(fh.read())
