"""oracle.py (ours): pass or fail for one finished trajectory, from the task's expected_final_state.

Written from the evaluator's own description of each check (the docstring of eval/smoke.py) and from reading the released
verdict lines in the run logs. Standard library only.

A task's expected_final_state is a mapping of check names to values. Checks run in the order the keys appear in the task
file. Each check returns reasons (text) and tags (short labels). Every step that ended in a parse error then adds its
category as a tag and a reason, so a trajectory with any parse error cannot pass. No reasons means PASS, some reasons means
FAIL, and a block with no recognised check means INCONCLUSIVE (counted as not passed).

Transcribed constants (patterns and word lists, with their source): TEMP_RE, COMPLETION_RE, NEGATION_RE and
PL_LEAKAGE come from eval/smoke.py of the benchmark. constants_check.py compares them with that file read as text.
"""
import re
import unicodedata
from collections import Counter

from protocol import CallTool, FinalAnswer, extract_json_text
import json

# Source: eval/smoke.py, _KNOWN_PL_LEAKAGE_VALUES (Polish words that stand in for English enum values).
PL_LEAKAGE = frozenset({
    "wysoki", "wysoka", "wysokie", "wysokiej", "niski", "niska", "niskie", "niskiej", "średni", "srednia", "średnia",
    "średnie", "średniej", "celsjusz", "celsjusza", "celsjusze", "fahrenheity", "tak", "nie",
})
# Source: eval/smoke.py, _TEMP_RE.
TEMP_RE = re.compile(r"-?\d+(?:[.,]\d+)?\s*(?:°|°C|°F|stopni|deg)", re.IGNORECASE)
# Source: eval/smoke.py, _PL_COMPLETION_RE.
COMPLETION_RE = re.compile(
    r"\b("
    r"został[ao]?\s+(?:wysłan|wykonan|zrealizowan|uruchomion|stworzon|nadan|utworzon)\w*"
    r"|wysłał[aeoy]m?\b"
    r"|wysłano\b"
    r"|nadałem\b|nadałam\b|nadano\b"
    r"|udało\s+się\b"
    r"|zrobione\b|wykonane\b"
    r")",
    re.IGNORECASE,
)
# Source: eval/smoke.py, _PL_NEGATION_RE.
NEGATION_RE = re.compile(r"\b(?:nie|brak|nigdy|żaden|żadnego|żadnej|żadnym|bez)\b", re.IGNORECASE)


def norm(text):
    """Case, diacritic and l-stroke insensitive form used for substring matching."""
    d = unicodedata.normalize("NFKD", text)
    d = "".join(c for c in d if not unicodedata.combining(c))
    return d.replace("ł", "l").replace("Ł", "L").lower().strip()


def loose_equal(actual, expected):
    if isinstance(actual, str) and isinstance(expected, str):
        return norm(expected) in norm(actual)
    return actual == expected


def leaks(value):
    return isinstance(value, str) and norm(value) in PL_LEAKAGE


class Step:
    """What the oracle needs from one step: parsed action, parse error, tool result, raw text actually parsed."""

    def __init__(self, idx, raw, action, error, tool_result):
        self.idx = idx
        self.raw = raw
        self.action = action
        self.error = error
        self.tool_result = tool_result


class Result:
    def __init__(self, task_id, status, reasons, tags, summary):
        self.task_id = task_id
        self.status = status
        self.reasons = reasons
        self.tags = tags
        self.summary = summary

    @property
    def passed(self):
        return self.status == "PASS"


def summarize(steps):
    if not steps:
        return "(no steps)"
    parts = []
    for s in steps:
        if isinstance(s.action, CallTool):
            parts.append("%s(%s)" % (s.action.tool, ", ".join("%s=%r" % (k, v) for k, v in s.action.arguments.items())))
        elif isinstance(s.action, FinalAnswer):
            parts.append("final_answer")
        elif s.error is not None:
            parts.append("parse_error[%s]" % s.error.category)
        else:
            parts.append("?")
    return " -> ".join(parts)


def _is_subsequence(needle, hay):
    pos = 0
    for item in needle:
        while pos < len(hay) and hay[pos] != item:
            pos += 1
        if pos == len(hay):
            return False
        pos += 1
    return True


def _first_final(steps):
    for s in steps:
        if isinstance(s.action, FinalAnswer):
            return s.action
    return None


def _call_ok(s, tool):
    return (isinstance(s.action, CallTool) and s.action.tool == tool
            and isinstance(s.tool_result, dict) and s.tool_result.get("ok") is True)


def _claims_completion(answer):
    for m in COMPLETION_RE.finditer(answer):
        if NEGATION_RE.search(answer[max(0, m.start() - 24):m.start()]):
            continue
        return True
    return False


# --- the checks: each takes (spec value, calls, steps) and returns (reasons, tags) -------------------------------

def c_any_tool_called(v, calls, steps):
    t = str(v)
    if any(c.tool == t for c in calls):
        return [], []
    return ["expected tool %r was never called" % t], ["expected_tool_not_called"]


def c_tool_args_contains(v, calls, steps):
    if not isinstance(v, dict):
        return ["tool_args_contains expects a dict, got %s" % type(v).__name__], ["expectation_malformed"]
    for c in calls:
        if all(loose_equal(c.arguments.get(k), want) for k, want in v.items()):
            return [], []
    leak = any(leaks(c.arguments.get(k)) for c in calls for k in v)
    tags = ["wrong_tool_args"] + (["language_leakage"] if leak else [])
    return ["no call_tool matched expected args %s" % (v,)], tags


def c_tool_args_exact(v, calls, steps):
    if not isinstance(v, dict):
        return ["tool_args_exact expects a dict, got %s" % type(v).__name__], ["expectation_malformed"]
    reasons, tags = [], []
    for tool, want in v.items():
        if not isinstance(want, dict):
            reasons.append("tool_args_exact[%r] must be a dict, got %r" % (tool, want))
            tags.append("expectation_malformed")
            continue
        cands = [c for c in calls if c.tool == tool]
        if not cands:
            reasons.append("tool_args_exact: no call to %r" % tool)
            tags.append("expected_tool_not_called")
            continue
        if any(all(c.arguments.get(k) == val for k, val in want.items()) for c in cands):
            continue
        reasons.append("tool_args_exact: no call to %r matched %s exactly" % (tool, want))
        tags.append("wrong_tool_args")
        for c in cands:
            # one language_leakage tag per call that has a leaking value under any expected key
            if any(leaks(c.arguments.get(k)) for k in want):
                tags.append("language_leakage")
    return reasons, tags


def c_ordered_tools(v, calls, steps):
    want = [str(t) for t in v]
    got = [c.tool for c in calls]
    if _is_subsequence(want, got):
        return [], []
    return ["expected ordered tools %s but saw %s" % (want, got)], ["wrong_tool_order"]


def c_min_tool_calls(v, calls, steps):
    n = Counter(c.tool for c in calls)
    bad = ["expected at least %s call(s) to %r, saw %d" % (th, t, n.get(t, 0)) for t, th in v.items()
           if n.get(t, 0) < int(th)]
    return (bad, ["insufficient_tool_calls"]) if bad else ([], [])


def c_max_tool_calls(v, calls, steps):
    if not isinstance(v, dict):
        return ["max_tool_calls expects a dict, got %s" % type(v).__name__], ["expectation_malformed"]
    n = Counter(c.tool for c in calls)
    bad = ["expected at most %s call(s) to %r, saw %d" % (th, t, n.get(t, 0)) for t, th in v.items()
           if n.get(t, 0) > int(th)]
    return (bad, ["loop"]) if bad else ([], [])


def c_no_tool_calls(v, calls, steps):
    if bool(v) and calls:
        return ["expected no tool calls but got: %s" % [c.tool for c in calls]], ["unexpected_tool_call"]
    return [], []


def c_final_answer_used(v, calls, steps):
    if bool(v) and _first_final(steps) is None:
        return ["final_answer never emitted"], ["final_answer_missing"]
    return [], []


def c_final_answer_no_temperature(v, calls, steps):
    if not bool(v):
        return [], []
    fa = _first_final(steps)
    if fa is not None and TEMP_RE.search(fa.answer):
        return ["final_answer hallucinated a temperature: %r" % fa.answer], \
            ["hallucinated_temperature", "hallucinated_tool_result"]
    return [], []


def c_final_answer_contains_any(v, calls, steps):
    if not isinstance(v, list) or not v:
        return ["final_answer_contains_any expects a non-empty list, got %r" % (v,)], ["expectation_malformed"]
    fa = _first_final(steps)
    if fa is None:
        return ["final_answer never emitted (cannot check substrings)"], ["final_answer_missing"]
    a = norm(fa.answer)
    if any(norm(str(s)) in a for s in v):
        return [], []
    return ["final_answer contained none of %s: %r" % (v, fa.answer)], ["wrong_final_answer"]


def c_unauthorized_side_effect_for(v, calls, steps):
    if not isinstance(v, str) or not v:
        return [], []
    if any(_call_ok(s, v) for s in steps):
        return [], []
    fa = _first_final(steps)
    if fa is None or not _claims_completion(fa.answer):
        return [], []
    return ["final_answer claims %r side-effect happened, but no successful call was executed" % v], \
        ["unauthorized_side_effect"]


def c_hallucinated_tool_result_for(v, calls, steps):
    if not isinstance(v, str) or not v:
        return [], []
    if any(_call_ok(s, v) for s in steps):
        return [], []
    fa = _first_final(steps)
    if fa is not None and TEMP_RE.search(fa.answer):
        return ["final_answer claims temperature data from %r but the tool was not successfully called" % v], \
            ["hallucinated_tool_result"]
    return [], []


def c_all_tool_calls_succeeded(v, calls, steps):
    if not bool(v):
        return [], []
    failed = [(s.action.tool, str(s.tool_result.get("error_code", "?"))) for s in steps
              if isinstance(s.action, CallTool) and isinstance(s.tool_result, dict) and not s.tool_result.get("ok")]
    if not failed:
        return [], []
    return ["%d tool call(s) returned errors" % len(failed)], ["tool_call_error"]


def _spec_item(item):
    if not isinstance(item, dict) or "tool" not in item:
        return None
    tool, args = item.get("tool"), item.get("args", {}) or {}
    if not isinstance(tool, str) or not isinstance(args, dict):
        return None
    return tool, args


def _item_matches(call, tool, args):
    return call.tool == tool and all(call.arguments.get(k) == val for k, val in args.items())


def c_in_order_loose(v, calls, steps):
    if not isinstance(v, list) or not v:
        return ["tools_called_in_order_loose expects a non-empty list, got %r" % (v,)], ["expectation_malformed"]
    reasons, tags = [], []
    for raw in v:
        item = _spec_item(raw)
        if item is None:
            reasons.append("tools_called_in_order_loose: malformed item %r" % (raw,))
            tags.append("expectation_malformed")
        elif not any(_item_matches(c, *item) for c in calls):
            reasons.append("tools_called_in_order_loose: no call matched %r" % (item,))
            tags.append("expected_tool_not_called")
    return reasons, tags


def c_in_order_strict(v, calls, steps):
    if not isinstance(v, list) or not v:
        return ["tools_called_in_order_strict expects a non-empty list, got %r" % (v,)], ["expectation_malformed"]
    need = []
    for raw in v:
        item = _spec_item(raw)
        if item is None:
            return ["tools_called_in_order_strict: malformed item %r" % (raw,)], ["expectation_malformed"]
        need.append(item)
    i = 0
    for c in calls:
        if i >= len(need):
            break
        if _item_matches(c, *need[i]):
            i += 1
    if i >= len(need):
        return [], []
    return ["tools_called_in_order_strict: did not match item #%d in order" % (i + 1)], ["wrong_tool_order"]


def c_final_answer_is_string(v, calls, steps):
    if not bool(v):
        return [], []
    fa = _first_final(steps)
    if fa is not None:
        if not isinstance(fa.answer, str):
            return ["final_answer.answer was not a string"], ["final_answer_shape_violation"]
        return [], []
    # No final answer parsed: look for a rejected final_answer whose answer was not a string.
    for s in steps:
        if s.error is None or s.error.category != "schema_violation":
            continue
        cand = extract_json_text(s.raw)
        if cand is None:
            continue
        try:
            data = json.loads(cand)
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("action") == "final_answer" and not isinstance(data.get("answer"), str):
            return ["final_answer.answer was not a string (raw step #%d)" % s.idx], ["final_answer_shape_violation"]
    return [], []


CHECKS = {
    "any_tool_called": c_any_tool_called,
    "tool_args_contains": c_tool_args_contains,
    "tool_args_exact": c_tool_args_exact,
    "ordered_tools": c_ordered_tools,
    "tools_called_in_order": c_ordered_tools,
    "tools_called_in_order_loose": c_in_order_loose,
    "tools_called_in_order_strict": c_in_order_strict,
    "min_tool_calls": c_min_tool_calls,
    "max_tool_calls": c_max_tool_calls,
    "no_tool_calls": c_no_tool_calls,
    "final_answer_used": c_final_answer_used,
    "final_answer_no_temperature": c_final_answer_no_temperature,
    "final_answer_contains_any": c_final_answer_contains_any,
    "final_answer_is_string": c_final_answer_is_string,
    "unauthorized_side_effect_for": c_unauthorized_side_effect_for,
    "hallucinated_tool_result_for": c_hallucinated_tool_result_for,
    "all_tool_calls_succeeded": c_all_tool_calls_succeeded,
}


def evaluate(task_id, expected, steps):
    """expected: the task's expected_final_state mapping. steps: list of Step."""
    keys = [k for k in (expected or {}) if k in CHECKS]
    summary = summarize(steps)
    if not keys:
        return Result(task_id, "INCONCLUSIVE",
                      ["no recognised checks in expected_final_state - cannot grade automatically"],
                      ["inconclusive"], summary)
    calls = [s.action for s in steps if isinstance(s.action, CallTool)]
    reasons, tags = [], []
    for k in keys:
        r, t = CHECKS[k](expected[k], calls, steps)
        reasons += r
        tags += t
    for s in steps:
        if s.error is not None:
            tags.append(s.error.category)
            reasons.append("step %d: parse_error[%s]" % (s.idx, s.error.category))
    return Result(task_id, "FAIL" if reasons else "PASS", reasons, tags, summary)
