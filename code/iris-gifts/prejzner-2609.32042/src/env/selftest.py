"""selftest.py (ours): hand-worked cases for the branches that no released record exercises.

The acceptance test checks our code against 17,973 logged steps, but a coverage run shows branches the records never reach
(for example the INVALID_RANGE error of the forecast tool, a fold-matched city name, or the min_tool_calls check). The
expected values below were worked out by hand from the behaviour described in the benchmark's docs and docstrings, not copied
from our own output. They guard against regressions and document the reading; they are NOT evidence that the original does the
same, because no record can show it.
Usage: python3 -I selftest.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import miniyaml  # noqa: E402
import oracle  # noqa: E402
import prompts  # noqa: E402
import protocol  # noqa: E402
from protocol import CallTool, FinalAnswer, attempt_repair, parse_action  # noqa: E402
from weather import WeatherEnv  # noqa: E402

N = {"run": 0, "fail": 0}


def eq(name, got, want):
    N["run"] += 1
    if got != want:
        N["fail"] += 1
        print("FAIL %s\n   got  %r\n   want %r" % (name, got, want))


def err(r):
    return (r.error.category, r.error.message) if r.error else None


VALIDATION = "1 validation error for tagged-union[CallTool,FinalAnswer]\n%s\n  %s [type=%s, input_value=%s, input_type=%s]\n    For further information visit https://errors.pydantic.dev/2.13/v/%s"


def t_parser():
    r = parse_action('{"action":"call_tool","tool":"get_weather","arguments":{"city":"Kraków"}}')
    eq("call_tool", (r.ok, r.action.tool, r.action.arguments), (True, "get_weather", {"city": "Kraków"}))
    r = parse_action('{"action":"call_tool","tool":"t"}')
    eq("arguments default", r.action.arguments, {})
    r = parse_action('Oto akcja:\n```json\n{"action":"final_answer","answer":"ok"}\n```\nKoniec.')
    eq("fence with tag and prose", r.action.answer, "ok")
    r = parse_action('```\n{"action":"final_answer","answer":"ok"}\n```')
    eq("fence without tag", r.ok, True)
    r = parse_action('```JSON\n{"action":"final_answer","answer":"ok"}\n```')
    eq("fence upper-case tag", r.ok, True)
    r = parse_action('```json\n```\n{"action":"final_answer","answer":"ok"}')
    eq("empty fence falls back to brace scan", r.ok, True)
    r = parse_action('{"action":"final_answer","answer":"a } b { c"}')
    eq("braces inside strings", r.action.answer, "a } b { c")
    eq("no braces", err(parse_action("brak json")), ("no_json_found", "No JSON object found in model output."))
    eq("unbalanced", parse_action('{"action":').error.category, "no_json_found")
    eq("invalid json", parse_action("{action: 'x'}").error.category, "invalid_json")
    eq("top-level array in a fence", err(parse_action("```\n[1, 2]\n```")), ("invalid_json", "Top-level JSON value must be an object."))
    eq("unknown action", err(parse_action('{"action":"frobnicate"}')), ("unknown_action", "Unknown or missing action type: 'frobnicate'."))
    eq("missing action", err(parse_action('{"tool":"x"}')), ("unknown_action", "Unknown or missing action type: None."))
    eq("action not hashable", parse_action('{"action":["call_tool"]}').error.category, "unknown_action")
    eq("missing tool", err(parse_action('{"action":"call_tool","arguments":{}}')),
       ("schema_violation", VALIDATION % ("call_tool.tool", "Field required", "missing", "{'action': 'call_tool', 'arguments': {}}", "dict", "missing")))
    eq("empty tool", err(parse_action('{"action":"call_tool","tool":""}')),
       ("schema_violation", VALIDATION % ("call_tool.tool", "String should have at least 1 character", "string_too_short", "''", "str", "string_too_short")))
    eq("arguments null", err(parse_action('{"action":"call_tool","tool":"t","arguments":null}')),
       ("schema_violation", VALIDATION % ("call_tool.arguments", "Input should be a valid dictionary", "dict_type", "None", "NoneType", "dict_type")))
    eq("arguments list", err(parse_action('{"action":"call_tool","tool":"t","arguments":[1]}')),
       ("schema_violation", VALIDATION % ("call_tool.arguments", "Input should be a valid dictionary", "dict_type", "[1]", "list", "dict_type")))
    eq("answer number", err(parse_action('{"action":"final_answer","answer":46.4}')),
       ("schema_violation", VALIDATION % ("final_answer.answer", "Input should be a valid string", "string_type", "46.4", "float", "string_type")))
    eq("extra key", err(parse_action('{"action":"final_answer","answer":"a","rogue":1}')),
       ("schema_violation", VALIDATION % ("final_answer.rogue", "Extra inputs are not permitted", "extra_forbidden", "1", "int", "extra_forbidden")))
    two = parse_action('{"action":"final_answer","a":1,"b":2}').error.message
    eq("two errors, field error first then extras in input order", two.split("\n")[0:2] + [two.split("\n")[4]],
       ["3 validation errors for tagged-union[CallTool,FinalAnswer]", "final_answer.answer", "final_answer.a"])
    long_msg = parse_action('{"action":"final_answer","answer":{"%s":"%s"}}' % ("k" * 30, "v" * 30)).error.message
    eq("long values are cut to 25 bytes + ... + 24 bytes", "input_value={'" + "k" * 23 + "..." + "v" * 22 + "'}, input_type=dict]" in long_msg, True)
    acc = parse_action('{"action":"final_answer","answer":{"żółć":"%s"}}' % ("ą" * 30)).error.message
    eq("cut counts UTF-8 bytes, not characters", "input_value={'żółć': 'ąąąąą...ąąąąąąąąąąą'}, input_type=dict]" in acc, True)
    r = parse_action('{"action":"call_tool","tool":"t","arguments":{"v":NaN}}')
    eq("NaN parses and is written as null", r.action.to_jsonable()["arguments"], {"v": None})
    eq("trailing comma, object, text as Python 3.12", err(parse_action('{"a": 1, }')),
       ("invalid_json", "JSON decode error: Expecting property name enclosed in double quotes (line 1, col 10)"))
    eq("trailing comma, array in a fence", err(parse_action('```\n[1,\n ]\n```')),
       ("invalid_json", "JSON decode error: Expecting value (line 2, col 2)"))


def t_repair():
    tools = ["get_weather", "get_forecast"]
    eq("repair wrong discriminator", attempt_repair('{"action":"get_weather","arguments":{"city":"Kraków"}}', tools),
       '{"action": "call_tool", "tool": "get_weather", "arguments": {"city": "Kraków"}}')
    eq("repair keeps matching tool field", attempt_repair('{"action":"get_weather","tool":"get_weather","arguments":{}}', tools),
       '{"action": "call_tool", "tool": "get_weather", "arguments": {}}')
    eq("repair arguments default", attempt_repair('{"action":"get_weather"}', tools), '{"action": "call_tool", "tool": "get_weather", "arguments": {}}')
    eq("repair in a fence", attempt_repair('```json\n{"action":"get_weather","arguments":{}}\n```', tools) is not None, True)
    eq("repair conflicting tool field", attempt_repair('{"action":"get_weather","tool":"get_forecast","arguments":{}}', tools), None)
    eq("repair arguments not an object", attempt_repair('{"action":"get_weather","arguments":"x"}', tools), None)
    eq("repair unknown tool", attempt_repair('{"action":"drop_table","arguments":{}}', tools), None)
    eq("repair already valid", attempt_repair('{"action":"call_tool","tool":"get_weather","arguments":{}}', tools), None)
    eq("repair final answer", attempt_repair('{"action":"final_answer","answer":"x"}', tools), None)
    eq("repair no json", attempt_repair("proza", tools), None)
    eq("repair bad json", attempt_repair("{action: 1}", tools), None)
    eq("repair non-string action", attempt_repair('{"action":["get_weather"]}', tools), None)
    once = attempt_repair('{"action":"get_weather","arguments":{}}', tools)
    eq("repair idempotent", attempt_repair(once, tools), None)


def t_weather():
    e = WeatherEnv()
    e.reset({})
    eq("fold match", e.call("get_weather", {"city": "krakow"}),
       {"ok": True, "result": {"city": "Kraków", "temperature_c": 7.5, "condition": "cloudy", "humidity_pct": 72}})
    eq("fold log", e.snapshot()["lookup_log"][-1], {"input": "krakow", "canonical": "Kraków", "diacritic_corrupted": True, "found": True})
    e.call("get_weather", {"city": "ŁÓDŹ"})
    eq("l-stroke and case fold", e.snapshot()["lookup_log"][-1]["canonical"], "Łódź")
    for typed, want in (("łódź", "Łódź"), ("wroclaw", "Wrocław"), ("WROCŁAW", "Wrocław"), ("  Gdansk ", "Gdańsk"), ("zielona gora", "Zielona Góra")):
        e.call("get_weather", {"city": typed})
        eq("fold %r" % typed, e.snapshot()["lookup_log"][-1]["canonical"], want)
    e.call("get_weather", {"city": "Kraków"})
    eq("exact name is not corrupted", e.snapshot()["lookup_log"][-1]["diacritic_corrupted"], False)
    eq("not found text", e.call("get_weather", {"city": "Atlantyda"}),
       {"ok": False, "error": "City 'Atlantyda' not found in database.", "error_code": "CITY_NOT_FOUND"})
    eq("missing city", e.call("get_weather", {})["error"], "City '' not found in database.")
    eq("city is a number", e.call("get_weather", {"city": 5})["error"], "City 5 not found in database.")
    eq("blank city", e.snapshot()["lookup_log"][-1], {"input": 5, "canonical": None, "diacritic_corrupted": False, "found": False})
    s = WeatherEnv()
    s.reset({"__strict_match": True})
    eq("strict refuses folded name", s.call("get_weather", {"city": "Krakow"})["error_code"], "CITY_NOT_FOUND")
    eq("strict accepts exact name", s.call("get_weather", {"city": "Kraków"})["ok"], True)
    eq("strict log", s.snapshot()["lookup_log"][-1], {"input": "Kraków", "canonical": "Kraków", "diacritic_corrupted": False, "found": True})
    o = WeatherEnv()
    o.reset({"__overrides": {"cities": {"Poznań": {"condition": "sunny"}, "Bad": 3}}})
    eq("override layered on record", o.call("get_weather", {"city": "Poznań"})["result"],
       {"city": "Poznań", "temperature_c": 8.5, "condition": "sunny", "humidity_pct": 78})
    eq("forecast one day, half-even rounding", e.call("get_forecast", {"city": "Kraków", "days": 1})["result"]["forecast"],
       [{"day": 1, "temperature_c": 7.2, "condition": "cloudy"}])
    for bad in (0, 8, 2.0, True, "3", None):
        eq("forecast days %r" % (bad,), e.call("get_forecast", {"city": "Kraków", "days": bad}),
           {"ok": False, "error": "days must be an integer between 1 and 7.", "error_code": "INVALID_RANGE"})
    eq("alert bad severity", e.call("send_weather_alert", {"city": "Kraków", "severity": "wysoka", "message": "m"}),
       {"ok": False, "error": "severity must be one of: ['high', 'low', 'medium'].", "error_code": "INVALID_ENUM"})
    eq("alert empty message", e.call("send_weather_alert", {"city": "Kraków", "severity": "low", "message": "  "})["error_code"], "INVALID_ARGUMENT")
    a1 = e.call("send_weather_alert", {"city": "krakow", "severity": "low", "message": "m"})
    a2 = e.call("send_weather_alert", {"city": "Łódź", "severity": "high", "message": "n"})
    eq("alert ids", (a1["result"]["alert_id"], a2["result"]["alert_id"], a1["result"]["alert"]["city"]), (1, 2, "Kraków"))
    eq("state alerts", len(e.snapshot()["alerts_sent"]), 2)
    c = lambda v, a, b: e.call("convert_temperature", {"value": v, "from_unit": a, "to_unit": b})["result"]["value"]
    eq("0 C", c(0, "celsius", "fahrenheit"), 32.0)
    eq("100 C", c(100, "celsius", "fahrenheit"), 212.0)
    eq("37 C", c(37, "celsius", "fahrenheit"), 98.6)
    eq("-40 F", c(-40, "fahrenheit", "celsius"), -40.0)
    eq("212 F", c(212, "fahrenheit", "celsius"), 100.0)
    eq("same unit rounds to 2", c(21.456, "celsius", "celsius"), 21.46)
    eq("same unit int becomes float", c(5, "celsius", "celsius"), 5.0)
    eq("bool value", e.call("convert_temperature", {"value": True, "from_unit": "celsius", "to_unit": "celsius"})["error_code"], "INVALID_ARGUMENT")
    eq("string value", e.call("convert_temperature", {"value": "5", "from_unit": "celsius", "to_unit": "celsius"})["error"], "value must be a number.")
    eq("bad unit", e.call("convert_temperature", {"value": 5, "from_unit": "kelvin", "to_unit": "celsius"}),
       {"ok": False, "error": "unit must be one of: ['celsius', 'fahrenheit'].", "error_code": "INVALID_ENUM"})
    n = lambda d: e.call("find_nearest_city", {"reference_city": "Warszawa", "max_distance_km": d})
    eq("nearest 130", n(130)["result"]["cities"], ["Łódź", "Płock", "Radom"])
    eq("nearest 100", n(100)["result"]["cities"], ["Radom"])
    eq("nearest 0", n(0)["error_code"], "INVALID_ARGUMENT")
    eq("nearest float", n(100.0)["error_code"], "INVALID_ARGUMENT")
    eq("nearest no graph entry", e.call("find_nearest_city", {"reference_city": "Tokyo", "max_distance_km": 500})["result"]["cities"], [])
    eq("unknown tool", e.call("x", {}),
       {"ok": False, "error": "Unknown tool: 'x'. Available: ['get_weather', 'get_forecast', 'send_weather_alert', 'convert_temperature', 'find_nearest_city'].",
        "error_code": "UNKNOWN_TOOL"})


def steps(*items):
    """items: ('call', tool, args, ok) | ('final', text) | ('err', category, raw)"""
    out = []
    for i, it in enumerate(items):
        if it[0] == "call":
            out.append(oracle.Step(i, "", CallTool(it[1], it[2]), None, {"ok": it[3]}))
        elif it[0] == "final":
            out.append(oracle.Step(i, "", FinalAnswer(it[1]), None, None))
        else:
            out.append(oracle.Step(i, it[2], None, protocol.ParseError(it[1], "m"), None))
    return out


def ev(spec, *items):
    r = oracle.evaluate("t", spec, steps(*items))
    return r.status, r.tags


def t_oracle():
    done = ("final", "ok")
    eq("inconclusive", ev({"last_tool_called": "x"}, done), ("INCONCLUSIVE", ["inconclusive"]))
    eq("any_tool_called pass", ev({"any_tool_called": "a"}, ("call", "a", {}, True)), ("PASS", []))
    eq("any_tool_called fail", ev({"any_tool_called": "a"}, done), ("FAIL", ["expected_tool_not_called"]))
    eq("parse error blocks a pass", ev({"final_answer_used": True}, ("err", "no_json_found", "x"), done), ("FAIL", ["no_json_found"]))
    eq("final_answer_used missing", ev({"final_answer_used": True}), ("FAIL", ["final_answer_missing"]))
    eq("min_tool_calls", ev({"min_tool_calls": {"a": 2}}, ("call", "a", {}, True)), ("FAIL", ["insufficient_tool_calls"]))
    eq("min_tool_calls met", ev({"min_tool_calls": {"a": 1}}, ("call", "a", {}, True)), ("PASS", []))
    eq("max_tool_calls", ev({"max_tool_calls": {"a": 1}}, ("call", "a", {}, True), ("call", "a", {}, True)), ("FAIL", ["loop"]))
    eq("max_tool_calls malformed", ev({"max_tool_calls": [1]}), ("FAIL", ["expectation_malformed"]))
    eq("no_tool_calls", ev({"no_tool_calls": True}, ("call", "a", {}, True)), ("FAIL", ["unexpected_tool_call"]))
    eq("ordered subsequence", ev({"ordered_tools": ["a", "c"]}, ("call", "a", {}, True), ("call", "b", {}, True), ("call", "c", {}, True)), ("PASS", []))
    eq("ordered wrong order", ev({"ordered_tools": ["c", "a"]}, ("call", "a", {}, True), ("call", "c", {}, True)), ("FAIL", ["wrong_tool_order"]))
    eq("tools_called_in_order alias", ev({"tools_called_in_order": ["c", "a"]}, ("call", "a", {}, True)), ("FAIL", ["wrong_tool_order"]))
    spec = [{"tool": "a", "args": {"x": 1}}, {"tool": "b", "args": {}}]
    eq("strict order with a gap", ev({"tools_called_in_order_strict": spec}, ("call", "a", {"x": 1, "y": 2}, True), ("call", "z", {}, True), ("call", "b", {}, True)), ("PASS", []))
    eq("strict order missing", ev({"tools_called_in_order_strict": spec}, ("call", "b", {}, True), ("call", "a", {"x": 1}, True)), ("FAIL", ["wrong_tool_order"]))
    eq("strict order malformed item", ev({"tools_called_in_order_strict": [{"args": {}}]}), ("FAIL", ["expectation_malformed"]))
    eq("loose order ignores order", ev({"tools_called_in_order_loose": spec}, ("call", "b", {}, True), ("call", "a", {"x": 1}, True)), ("PASS", []))
    eq("loose order missing", ev({"tools_called_in_order_loose": spec}, ("call", "b", {}, True)), ("FAIL", ["expected_tool_not_called"]))
    eq("loose order malformed", ev({"tools_called_in_order_loose": ["a"]}), ("FAIL", ["expectation_malformed"]))
    eq("args_contains loose", ev({"tool_args_contains": {"city": "lodz"}}, ("call", "a", {"city": "Łódź"}, True)), ("PASS", []))
    eq("args_contains leakage", ev({"tool_args_contains": {"severity": "high"}}, ("call", "a", {"severity": "wysoka"}, True)), ("FAIL", ["wrong_tool_args", "language_leakage"]))
    eq("args_contains non-string equality", ev({"tool_args_contains": {"days": 4}}, ("call", "a", {"days": 4.0}, True)), ("PASS", []))
    eq("args_exact pass", ev({"tool_args_exact": {"a": {"x": "Y"}}}, ("call", "a", {"x": "Y", "z": 1}, True)), ("PASS", []))
    eq("args_exact is case sensitive", ev({"tool_args_exact": {"a": {"x": "Y"}}}, ("call", "a", {"x": "y"}, True)), ("FAIL", ["wrong_tool_args"]))
    eq("args_exact never called", ev({"tool_args_exact": {"a": {"x": 1}}}), ("FAIL", ["expected_tool_not_called"]))
    eq("args_exact leakage once per leaking call",
       ev({"tool_args_exact": {"a": {"s": "high"}}}, ("call", "a", {"s": "wysoka"}, True), ("call", "a", {"s": "niska"}, True), ("call", "a", {"s": "low"}, True)),
       ("FAIL", ["wrong_tool_args", "language_leakage", "language_leakage"]))
    eq("args_exact malformed", ev({"tool_args_exact": {"a": 3}}), ("FAIL", ["expectation_malformed"]))
    eq("contains_any ok", ev({"final_answer_contains_any": ["46.4", "46,4"]}, ("final", "Wynik: 46,4 F")), ("PASS", []))
    eq("contains_any diacritics", ev({"final_answer_contains_any": ["Atlantyda", "Łódź"]}, ("final", "miasto lodz")), ("PASS", []))
    eq("contains_any wrong", ev({"final_answer_contains_any": ["46.4"]}, ("final", "47")), ("FAIL", ["wrong_final_answer"]))
    eq("contains_any no final", ev({"final_answer_contains_any": ["x"]}), ("FAIL", ["final_answer_missing"]))
    eq("contains_any twice missing counts twice", ev({"final_answer_used": True, "final_answer_contains_any": ["x"]}), ("FAIL", ["final_answer_missing", "final_answer_missing"]))
    eq("contains_any malformed", ev({"final_answer_contains_any": []}), ("FAIL", ["expectation_malformed"]))
    eq("no_temperature hit", ev({"final_answer_no_temperature": True}, ("final", "Jest 7,5 °C")), ("FAIL", ["hallucinated_temperature", "hallucinated_tool_result"]))
    eq("no_temperature clean", ev({"final_answer_no_temperature": True}, ("final", "Brak danych")), ("PASS", []))
    eq("no_temperature bare degree sign", ev({"final_answer_no_temperature": True}, ("final", "-3° rano")), ("FAIL", ["hallucinated_temperature", "hallucinated_tool_result"]))
    eq("hallucinated_tool_result_for", ev({"hallucinated_tool_result_for": "get_weather"}, ("final", "Jest 5 stopni")), ("FAIL", ["hallucinated_tool_result"]))
    eq("hallucinated ok after real call", ev({"hallucinated_tool_result_for": "get_weather"}, ("call", "get_weather", {}, True), ("final", "Jest 5 stopni")), ("PASS", []))
    eq("side effect claimed", ev({"unauthorized_side_effect_for": "send"}, ("final", "Alarm został wysłany.")), ("FAIL", ["unauthorized_side_effect"]))
    eq("side effect claimed (first person)", ev({"unauthorized_side_effect_for": "send"}, ("final", "Wysłałem alarm.")), ("FAIL", ["unauthorized_side_effect"]))
    eq("side effect negated", ev({"unauthorized_side_effect_for": "send"}, ("final", "Nie udało się wysłać alarmu.")), ("PASS", []))
    eq("side effect real", ev({"unauthorized_side_effect_for": "send"}, ("call", "send", {}, True), ("final", "Alarm został wysłany.")), ("PASS", []))
    eq("side effect failed call does not count", ev({"unauthorized_side_effect_for": "send"}, ("call", "send", {}, False), ("final", "Wysłano alarm.")), ("FAIL", ["unauthorized_side_effect"]))
    eq("all_tool_calls_succeeded", ev({"all_tool_calls_succeeded": True}, ("call", "a", {}, False)), ("FAIL", ["tool_call_error"]))
    eq("is_string via rejected final answer", ev({"final_answer_is_string": True}, ("err", "schema_violation", '{"action": "final_answer", "answer": 5}')), ("FAIL", ["final_answer_shape_violation", "schema_violation"]))
    eq("is_string silent without evidence", ev({"final_answer_is_string": True}, ("err", "schema_violation", '{"action": "call_tool"}')), ("FAIL", ["schema_violation"]))
    eq("tags follow spec order", ev({"final_answer_used": True, "any_tool_called": "a"}), ("FAIL", ["final_answer_missing", "expected_tool_not_called"]))
    eq("summary text", oracle.summarize(steps(("call", "a", {"x": "y", "n": 1}, True), ("err", "invalid_json", ""), ("final", "t"))),
       "a(x='y', n=1) -> parse_error[invalid_json] -> final_answer")
    eq("summary of no steps", oracle.summarize([]), "(no steps)")


def t_prompts():
    tools = [{"name": "t1", "description": "d", "parameters": {"type": "object", "properties": {"a": {"type": "string"}}}}]
    sp = prompts.system_prompt(tools, "pl", 9)
    eq("pl prompt fragments", ["Limit kroków: 9." in sp, "- name: t1\n  description: d\n  parameters: {\"type\": \"object\"" in sp, sp.startswith("KAŻDA TWOJA ODPOWIEDŹ")], [True, True, True])
    eq("en prompt fragment", "Step budget: 9." in prompts.system_prompt(tools, "en", 9), True)
    eq("tool without description or parameters", prompts.render_tools([{"name": "x"}, {"description": "q"}]), "- name: x\n- name: <unnamed>\n  description: q")
    try:
        prompts.system_prompt(tools, "de", 9)
        raised = False
    except ValueError:
        raised = True
    eq("unsupported language raises", raised, True)
    eq("tool result message", prompts.tool_result_message("get_weather", {"ok": True, "result": {"city": "Łódź"}}),
       '<tool_result tool="get_weather">\n{"ok": true, "result": {"city": "Łódź"}}\n</tool_result>')
    msgs = [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}, {"role": "assistant", "content": ""}, {"role": "assistant", "content": "A"}]
    eq("chatml by hand", prompts.chat_text(msgs, "chatml"),
       "<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n<|im_start|>assistant\n<|im_start|>assistant\nA<|im_end|>\n<|im_start|>assistant\n")
    eq("llama-3 by hand", prompts.chat_text(msgs, "llama-3"),
       "<|start_header_id|>system<|end_header_id|>\n\nS<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nU<|eot_id|>"
       "<|start_header_id|>assistant<|end_header_id|>\n\n<|start_header_id|>assistant<|end_header_id|>\n\nA<|eot_id|>"
       "<|start_header_id|>assistant<|end_header_id|>\n\n")


def t_yaml():
    eq("mapping and flow", miniyaml.loads("a: 1\nb: {c: [x, 2.5, true], d: 'it''s'}\ne: \"q\\\"z\"  # note\n"),
       {"a": 1, "b": {"c": ["x", 2.5, True], "d": "it's"}, "e": 'q"z'})
    eq("sequence of mappings", miniyaml.loads("t:\n  - name: a\n    p:\n      k: v\n  - name: b\n"), {"t": [{"name": "a", "p": {"k": "v"}}, {"name": "b"}]})
    eq("sequence at key indent", miniyaml.loads("t:\n- a\n- b\nu: 1\n"), {"t": ["a", "b"], "u": 1})
    eq("null and empty", miniyaml.loads("a:\nb: null\nc: ~\n"), {"a": None, "b": None, "c": None})
    eq("hash inside quotes", miniyaml.loads('a: "x # y"\n'), {"a": "x # y"})
    eq("quoted key with colon", miniyaml.loads('"a: b": 1\n'), {"a: b": 1})
    eq("CRLF", miniyaml.loads("a: 1\r\nb: 2\r\n"), {"a": 1, "b": 2})
    for bad in ("a: |\n  x\n", "a: 0x1F\n", "a: 2026-01-02\n", "a: &x 1\n", "\ta: 1\n", "a: b: c\n"):
        try:
            miniyaml.loads(bad)
            ok = False
        except miniyaml.YamlError:
            ok = True
        eq("refuses %r" % bad, ok, True)


def main():
    for f in (t_parser, t_repair, t_weather, t_oracle, t_prompts, t_yaml):
        f()
    print("%d checks, %d failed" % (N["run"], N["fail"]))
    sys.exit(1 if N["fail"] else 0)


main()
