"""protocol.py (ours): turn one raw model reply into a tool call, a final answer, or a parse error.

Written from the protocol description in the benchmark's docs/protocol.md and from reading the released step records.
Standard library only. The original validates with pydantic; here the same checks are written out by hand, including the
text of the validation error messages that appear in the released step records (string_type, extra_forbidden, missing)
and the two others the schema can raise (string_too_short, dict_type), which no released record contains.

Rules, in order:
 1. Look for a fenced block (three backticks, optional json/JSON tag). If its stripped body is not empty, that is the
    candidate text. Otherwise scan for the first balanced {...} (braces inside JSON strings do not count).
 2. No candidate -> no_json_found. json.loads fails -> invalid_json. Top level not an object -> invalid_json.
 3. "action" not call_tool/final_answer -> unknown_action.
 4. Schema: call_tool needs tool (string, 1+ chars) and may have arguments (object, default {}); final_answer needs
    answer (string, 1+ chars). Any other key -> schema_violation.
Repair (opt-in): {"action": "<tool name>", "arguments": {...}} becomes a call_tool, nothing else is repaired.
"""
import json
import math

PYDANTIC_DOCS_VERSION = "2.13"  # appears in the URL line of the released error messages
UNION_TITLE = "tagged-union[CallTool,FinalAnswer]"


class CallTool:
    kind = "call_tool"

    def __init__(self, tool, arguments):
        self.tool = tool
        self.arguments = arguments

    def to_jsonable(self):
        return {"action": "call_tool", "tool": self.tool, "arguments": _finite(self.arguments)}


class FinalAnswer:
    kind = "final_answer"

    def __init__(self, answer):
        self.answer = answer

    def to_jsonable(self):
        return {"action": "final_answer", "answer": self.answer}


class ParseError:
    def __init__(self, category, message):
        self.category = category
        self.message = message

    def to_jsonable(self):
        return {"category": self.category, "message": self.message}


class ActionResult:
    def __init__(self, action=None, error=None):
        self.action = action
        self.error = error

    @property
    def ok(self):
        return self.action is not None


def _finite(x):
    """JSON output of the original turns NaN and infinity into null; do the same before comparing."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: _finite(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_finite(v) for v in x]
    return x


# ---------------------------------------------------------------------------
# Step 1: find the candidate JSON text
# ---------------------------------------------------------------------------

_FENCE = "```"


def _fenced_body(text):
    """Body of the first ``` ... ``` block: after an optional json/JSON tag and any whitespace, up to the next ```."""
    i = text.find(_FENCE)
    while i != -1:
        j = i + 3
        if text.startswith("json", j) or text.startswith("JSON", j):
            j += 4
        while j < len(text) and text[j].isspace():
            j += 1
        k = text.find(_FENCE, j)
        if k != -1:
            return text[j:k]
        i = text.find(_FENCE, i + 1)
    return None


def extract_json_text(text):
    body = _fenced_body(text)
    if body is not None:
        body = body.strip()
        if body:
            return body
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


# ---------------------------------------------------------------------------
# Step 4: schema check, with the validation-error text
# ---------------------------------------------------------------------------

def _short_repr(v):
    """repr(v), cut to its first 25 and last 24 UTF-8 bytes (joined by ...) when longer than 50 bytes. The cut is by
    bytes, moved to a character boundary: the released messages show this (a repr with accented letters keeps fewer
    than 25 characters at the front)."""
    r = repr(v)
    b = r.encode("utf-8")
    if len(b) <= 50:
        return r
    head, tail = 25, len(b) - 24
    while head > 0 and (b[head] & 0xC0) == 0x80:
        head -= 1
    while tail < len(b) and (b[tail] & 0xC0) == 0x80:
        tail += 1
    return b[:head].decode("utf-8") + "..." + b[tail:].decode("utf-8")


def _err(loc, kind, msg, value):
    return {"loc": loc, "type": kind, "msg": msg, "value": value}


def _validation_text(errors):
    n = len(errors)
    out = ["%d validation error%s for %s" % (n, "" if n == 1 else "s", UNION_TITLE)]
    for e in errors:
        out.append(e["loc"])
        out.append("  %s [type=%s, input_value=%s, input_type=%s]" % (
            e["msg"], e["type"], _short_repr(e["value"]), type(e["value"]).__name__))
        out.append("    For further information visit https://errors.pydantic.dev/%s/v/%s" % (
            PYDANTIC_DOCS_VERSION, e["type"]))
    return "\n".join(out)


def _check_str(prefix, name, data):
    errs = []
    v = data[name]
    loc = "%s.%s" % (prefix, name)
    if not isinstance(v, str):
        errs.append(_err(loc, "string_type", "Input should be a valid string", v))
    elif len(v) < 1:
        errs.append(_err(loc, "string_too_short", "String should have at least 1 character", v))
    return errs


def validate(data):
    """data is a dict whose "action" is call_tool or final_answer. Returns (Action, None) or (None, message)."""
    kind = data["action"]
    errs = []
    if kind == "call_tool":
        fields = ("action", "tool", "arguments")
        if "tool" not in data:
            errs.append(_err("call_tool.tool", "missing", "Field required", data))
        else:
            errs += _check_str(kind, "tool", data)
        if "arguments" in data and not isinstance(data["arguments"], dict):
            errs.append(_err("call_tool.arguments", "dict_type", "Input should be a valid dictionary", data["arguments"]))
    else:
        fields = ("action", "answer")
        if "answer" not in data:
            errs.append(_err("final_answer.answer", "missing", "Field required", data))
        else:
            errs += _check_str(kind, "answer", data)
    for key, value in data.items():
        if key not in fields:
            errs.append(_err("%s.%s" % (kind, key), "extra_forbidden", "Extra inputs are not permitted", value))
    if errs:
        return None, _validation_text(errs)
    if kind == "call_tool":
        return CallTool(data["tool"], data.get("arguments", {}) if "arguments" in data else {}), None
    return FinalAnswer(data["answer"]), None


def _json_error_as_py312(exc, doc):
    """The released messages were written by Python 3.12. Python 3.13 and later name a trailing comma ("Illegal trailing
    comma before end of object/array", positioned at the comma) where 3.12 said "Expecting property name enclosed in
    double quotes" (objects) or "Expecting value" (arrays), positioned at the first non-blank character after the comma.
    Return (message, line, column) as 3.12 would give them, so the text does not depend on the Python we run."""
    msg = exc.msg
    pos = exc.pos
    if msg.startswith("Illegal trailing comma before end of "):
        msg = ("Expecting property name enclosed in double quotes" if msg.endswith("object")
               else "Expecting value")
        pos += 1
        while pos < len(doc) and doc[pos] in " \t\n\r":
            pos += 1
        lineno = doc.count("\n", 0, pos) + 1
        colno = pos - doc.rindex("\n", 0, pos) if lineno > 1 else pos + 1
        return msg, lineno, colno
    return msg, exc.lineno, exc.colno


def parse_action(text):
    """Never raises. Returns ActionResult with exactly one of action / error set."""
    cand = extract_json_text(text)
    if cand is None:
        return ActionResult(error=ParseError("no_json_found", "No JSON object found in model output."))
    try:
        data = json.loads(cand)
    except json.JSONDecodeError as exc:
        msg, lineno, colno = _json_error_as_py312(exc, cand)
        return ActionResult(error=ParseError("invalid_json", "JSON decode error: %s (line %d, col %d)" % (msg, lineno, colno)))
    if not isinstance(data, dict):
        return ActionResult(error=ParseError("invalid_json", "Top-level JSON value must be an object."))
    name = data.get("action")
    if name not in ("call_tool", "final_answer"):
        return ActionResult(error=ParseError("unknown_action", "Unknown or missing action type: %r." % (name,)))
    action, message = validate(data)
    if action is None:
        return ActionResult(error=ParseError("schema_violation", message))
    return ActionResult(action=action)


# ---------------------------------------------------------------------------
# Opt-in repair
# ---------------------------------------------------------------------------

def attempt_repair(text, available_tools):
    """Rewrite {"action": "<tool>", "arguments": {...}} to a call_tool object. None when it does not apply."""
    cand = extract_json_text(text)
    if cand is None:
        return None
    try:
        data = json.loads(cand)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    name = data.get("action")
    if name in ("call_tool", "final_answer"):
        return None
    if not isinstance(name, str) or name not in available_tools:
        return None
    explicit = data.get("tool")
    if explicit is not None and explicit != name:
        return None
    args = data.get("arguments", {})
    if not isinstance(args, dict):
        return None
    return json.dumps({"action": "call_tool", "tool": name, "arguments": args}, ensure_ascii=False)
