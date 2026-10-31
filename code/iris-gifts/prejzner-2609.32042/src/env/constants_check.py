"""constants_check.py (ours): compare the constants we transcribed with the benchmark's source files, read as TEXT.

Nothing from the benchmark is imported or run. Its Python files are parsed with the standard `ast` module and only literal
values are read out (tables, patterns, string templates); the f-string templates of the system prompt and of the tool-result
message are evaluated by a tiny evaluator that knows only constants, names and json.dumps. Checks:
  1. CITIES and NEIGHBOURS equal the benchmark's _CITIES and _NEIGHBOURS (values, number types, order).
  2. The oracle word list and the three oracle patterns equal the benchmark's.
  3. Our Polish and English system prompts equal the benchmark's templates, for every distinct tool list in the task files
     and several step limits.
  4. The three f-string templates of the tool list rendering are the ones we implement.
  5. Our tool-result message equals the benchmark's template for sample observations.
  6. Our fence finder equals the benchmark's fence pattern on 200000 random strings.
  7. The shape of the benchmark's agent loop (read as syntax trees): how the messages are built, which text goes into the
     assistant message, when the tool result is added, what the model is called with. There are no logged prompts to test
     message building against, so this is the check we have for it.
Usage: python3 -I constants_check.py
"""
import ast
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import oracle  # noqa: E402
import prompts  # noqa: E402
import protocol  # noqa: E402
import tasks as taskmod  # noqa: E402
import weather  # noqa: E402

THEIRS = os.environ.get("PAB_THEIRS") or os.path.normpath(os.path.join(HERE, "..", "..", "theirs"))
SRC = os.path.join(THEIRS, "src", "polagentbench")
FAILS = []


def check(name, ok, detail=""):
    print("%-6s %s%s" % ("OK" if ok else "FAIL", name, (" -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def parse(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as fh:
        return ast.parse(fh.read())


def assigned(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return node.value
    raise KeyError(name)


def function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise KeyError(name)


def evaluate_fstring(node, env):
    """Evaluate a JoinedStr made of constants, names and json.dumps(name, ensure_ascii=False)."""
    def ev(n):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return env[n.id]
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "dumps":
            kw = {k.arg: ev(k.value) for k in n.keywords}
            return json.dumps(*[ev(a) for a in n.args], **kw)
        raise ValueError("unsupported node %s" % ast.dump(n)[:80])
    if isinstance(node, ast.Constant):
        return node.value
    out = []
    for part in node.values:
        if isinstance(part, ast.Constant):
            out.append(part.value)
        else:
            assert isinstance(part, ast.FormattedValue) and part.conversion == -1 and part.format_spec is None
            out.append(str(ev(part.value)))
    return "".join(out)


def main():
    # 1 tables
    w = parse("environments/weather.py")
    cities = ast.literal_eval(assigned(w, "_CITIES"))
    neigh = ast.literal_eval(assigned(w, "_NEIGHBOURS"))
    check("city table identical (keys, order, values, number types)",
          json.dumps(cities, ensure_ascii=False) == json.dumps(weather.CITIES, ensure_ascii=False),
          "%d vs %d cities" % (len(cities), len(weather.CITIES)))
    check("neighbour graph identical",
          json.dumps(neigh, ensure_ascii=False) == json.dumps({k: [list(t) for t in v] for k, v in weather.NEIGHBOURS.items()}, ensure_ascii=False))
    check("severity and unit sets",
          ast.literal_eval(assigned(w, "_VALID_SEVERITY")) == set(weather.SEVERITIES)
          and ast.literal_eval(assigned(w, "_VALID_TEMP_UNIT")) == set(weather.UNITS))
    # tool name list: the return statement of available_tool_names is a list literal
    fn = function(w, "available_tool_names")
    check("tool name list and order", ast.literal_eval(fn.body[-1].value) == weather.TOOL_NAMES)

    # 2 oracle constants
    s = parse("eval/smoke.py")
    leak = assigned(s, "_KNOWN_PL_LEAKAGE_VALUES")
    check("Polish leakage word list", set(ast.literal_eval(leak.args[0])) == set(oracle.PL_LEAKAGE))
    for theirs, ours in (("_TEMP_RE", oracle.TEMP_RE), ("_PL_COMPLETION_RE", oracle.COMPLETION_RE), ("_PL_NEGATION_RE", oracle.NEGATION_RE)):
        call = assigned(s, theirs)
        pat = call.args[0].value
        flag_names = [n.attr for n in ast.walk(call) if isinstance(n, ast.Attribute)]
        check("pattern %s" % theirs, pat == ours.pattern and "IGNORECASE" in flag_names and bool(ours.flags & re.IGNORECASE))

    # 3 system prompts
    p = parse("inference/prompts.py")
    tool_lists = {}
    for d in ("adversarial", "ladder_ext", "ladder_l0e", "ladder_l0_control", "smoke"):
        for t in taskmod.load_dir(os.path.join(THEIRS, "tasks", d)).values():
            tool_lists[json.dumps(t.tools, ensure_ascii=False)] = t.tools
    tool_lists["[]"] = []
    tool_lists["odd"] = [{"name": "x"}, {"description": "no name", "parameters": {"a": [1, 2]}}, {"name": "y", "description": "{steps} {tools}"}]
    for lang, fname in (("pl", "_build_pl"), ("en", "_build_en")):
        ret = [n for n in function(p, fname).body if isinstance(n, ast.Return)][0].value
        bad = 0
        n = 0
        for tools in tool_lists.values():
            for steps in (3, 5, 8, 10, 12):
                theirs = evaluate_fstring(ret, {"tools_block": prompts.render_tools(tools), "max_steps": steps})
                bad += theirs != prompts.system_prompt(tools, lang, steps)
                n += 1
        check("system prompt (%s) equals the benchmark template: %d tool lists x 5 limits = %d renders" % (lang, len(tool_lists), n), bad == 0, "%d differ" % bad)

    # 4 tool list rendering templates
    rt = function(p, "_render_tools")
    got = sorted(ast.unparse(n) for n in ast.walk(rt) if isinstance(n, ast.JoinedStr))
    want = sorted(["f'- name: {name}'", "f'  description: {description}'", "f'  parameters: {json.dumps(parameters, ensure_ascii=False)}'"])
    check("tool list rendering templates", got == want, "%s" % got)
    keys = sorted(c.value for n in ast.walk(rt) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                  for c in n.args[:1] if isinstance(c, ast.Constant))
    check("tool list rendering reads name, description, parameters (defaults <unnamed>, '', {})", keys == ["description", "name", "parameters"])

    # 5 tool result message
    r = parse("inference/llama_cpp_runner.py")
    ret = [n for n in function(r, "_format_tool_result").body if isinstance(n, ast.Return)][0].value
    obs = [{"ok": True, "result": {"city": "Łódź", "temperature_c": 8.0}}, {"ok": False, "error": "x \"q\"", "error_code": "E"}, {}]
    bad = sum(evaluate_fstring(ret, {"tool_name": nm, "observation": o}) != prompts.tool_result_message(nm, o)
              for nm in ("get_weather", "ż") for o in obs)
    check("tool result message equals the benchmark template", bad == 0)

    # 6 fence finder against the benchmark's fence pattern
    pr = parse("protocol.py")
    call = assigned(pr, "_FENCE_RE")
    pat, flags = call.args[0].value, [n.attr for n in ast.walk(call) if isinstance(n, ast.Attribute)]
    rx = re.compile(pat, re.DOTALL if "DOTALL" in flags else 0)
    rnd = random.Random(7)
    atoms = ["```", "`", "json", "JSON", "Json", " ", "\n", "\t", "{", "}", "a", "\"", "\\", "x y", " ", "\x1c"]
    bad = 0
    N = 200000
    for _ in range(N):
        text = "".join(rnd.choice(atoms) for _ in range(rnd.randint(0, 14)))
        m = rx.search(text)
        a = m.group(1) if m else None
        b = protocol._fenced_body(text)
        if a != b:
            bad += 1
            if bad <= 3:
                print("   differ on %r: regex %r ours %r" % (text, a, b))
    check("fence finder equals the benchmark fence pattern on %d random strings" % N, bad == 0, "%d differ" % bad)

    # 7 shape of the agent loop
    def same(node, expr):
        return ast.dump(node) == ast.dump(ast.parse(expr, mode="eval").body)

    loop_fn = function(r, "agent_loop")
    top = {ast.unparse(st.targets[0]) if isinstance(st, ast.Assign) else ast.unparse(st.target): st.value
           for st in loop_fn.body if isinstance(st, (ast.Assign, ast.AnnAssign))}
    check("system prompt built from the task's tools, the prompt language and the task's max_steps",
          same(top["system_prompt"], "build_system_prompt(available_tools=task.available_tools, language=prompt_language, max_steps=task.max_steps)"))
    check("messages start as system prompt then task prompt",
          same(top["messages"], "[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': task.prompt}]"))
    check("tool names offered to repair", same(top["available_tool_names"], "[t['name'] for t in task.available_tools if 'name' in t]"))
    loop = [st for st in loop_fn.body if isinstance(st, ast.For)][0]
    check("one step per allowed step", same(loop.iter, "range(task.max_steps)"))
    body = loop.body
    first = body[0]
    check("model called with the message list and the seed", ast.unparse(first) == "original_text, latency_ms, usage = complete_chat(messages, seed)")
    appends = [(i, ast.unparse(st.value)) for i, st in enumerate(body) if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)
               and ast.unparse(st.value.func) == "messages.append"]
    texts = [a[1] for a in appends]
    check("exactly two message appends in the loop, in this order",
          texts == ["messages.append({'role': 'assistant', 'content': original_text})",
                    "messages.append({'role': 'user', 'content': _format_tool_result(action.tool, observation)})"])
    heads = [ast.unparse(st).split("\n")[0] for st in body]
    i_parse = heads.index("result = parse_action(text_to_parse)")
    i_asst = appends[0][0]
    i_ok = heads.index("if not result.ok:")
    check("assistant message (pre-repair text) is added right after parsing and before any branch", i_asst == i_parse + 1 and i_asst < i_ok)
    check("tool result message is the last statement of the loop body", appends[1][0] == len(body) - 1)
    check("repair text rule", any(ast.unparse(st) == "text_to_parse = repaired_text if repaired_text is not None else original_text" for st in body))
    # parse errors and final answers continue/break without adding a user message
    def has_user_append(node):
        return any(isinstance(n, ast.Call) and ast.unparse(n.func) == "messages.append" and "'user'" in ast.unparse(n) for n in ast.walk(node))
    branch_if = [st for st in body if isinstance(st, ast.If)]
    check("no user message inside the parse-error or final-answer branches", not any(has_user_append(b) for b in branch_if))
    check("timeout tag when no final answer",
          any(ast.unparse(st) == "if not final_answer_emitted:\n    failure_tags.append(FailureTag.TIMEOUT)" for st in loop_fn.body))
    # what the model is called with
    cc = [n for n in ast.walk(function(r, "_complete_chat")) if isinstance(n, ast.Call) and ast.unparse(n.func) == "llm.create_chat_completion"][0]
    kws = {k.arg: ast.unparse(k.value) for k in cc.keywords}
    check("create_chat_completion gets only messages, temperature, top_p, max_tokens, seed",
          kws == {"messages": "list(messages)", "temperature": "self.temperature", "top_p": "self.top_p", "max_tokens": "self.max_tokens", "seed": "seed"},
          str(kws))
    ll = [n for n in ast.walk(function(r, "_ensure_llm")) if isinstance(n, ast.Call) and ast.unparse(n.func) == "Llama"][0]
    check("Llama(...) gets only model_path, n_ctx, n_gpu_layers, chat_format, verbose",
          sorted(k.arg for k in ll.keywords) == ["chat_format", "model_path", "n_ctx", "n_gpu_layers", "verbose"], str([k.arg for k in ll.keywords]))
    check("environment reset with the state file plus the two reserved keys",
          ast.unparse(loop_fn.body[1]) == "reset_state = dict(initial_state)"
          and "reset_state['__strict_match'] = True" in ast.unparse(loop_fn.body[2])
          and "reset_state['__overrides'] = task.hardcoded_state" in ast.unparse(loop_fn.body[3])
          and ast.unparse(loop_fn.body[4]) == "env.reset(reset_state)")

    print("\n%s" % ("ALL CONSTANT CHECKS PASSED" if not FAILS else "FAILED: %s" % FAILS))
    sys.exit(1 if FAILS else 0)


main()
