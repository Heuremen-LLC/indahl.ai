"""prompts.py (ours): the exact text a run sends to the model, for each model family.

Standard library only. Three layers:

 1. system_prompt(tools, language, max_steps): the system prompt. The Polish and English wording is transcribed from
    src/polagentbench/inference/prompts.py of the benchmark (long fixed strings, so they are copied rather than
    re-invented). constants_check.py evaluates that file's string expressions as text and compares them with ours.
 2. The message list a run builds: system, user (the task prompt), then for every step an assistant message holding the
    raw reply as the model wrote it (before any repair), and after a successful parse of a tool call a user message holding
    the tool result in a tool_result tag. A parse error adds no user message.
 3. chat_text(messages, family): the flat text the llama-cpp-python chat format puts in front of the model. The two
    formats are transcribed from llama_cpp/llama_chat_format.py, release v0.3.19, functions format_chatml and
    format_llama3 (read as text). Quirk kept on purpose: a message with empty content prints only its role header, with no
    end-of-turn marker and no content. The text carries no BOS token: llama-cpp-python tokenises it with special tokens
    parsed and adds BOS itself, as the model's metadata says.

Model family by model id: bielik-* use chatml, llama-pllum-* use llama-3 (the run scripts say so). Stop strings are the
end-of-turn marker of the format.
"""
import json

# ---------------------------------------------------------------------------
# 1. system prompt
# ---------------------------------------------------------------------------


def render_tools(tools):
    lines = []
    for t in tools:
        lines.append("- name: %s" % t.get("name", "<unnamed>"))
        desc = t.get("description", "")
        if desc:
            lines.append("  description: %s" % desc)
        params = t.get("parameters", {})
        if params:
            lines.append("  parameters: %s" % json.dumps(params, ensure_ascii=False))
    return "\n".join(lines)


# Source: inference/prompts.py, _build_pl. Joined pieces are the source's lines; {tools} and {steps} mark the two
# substitutions.
_PL = (
    "KAŻDA TWOJA ODPOWIEDŹ MUSI BYĆ JEDNYM OBIEKTEM JSON. ZAWSZE.\n"
    "NIGDY nie odpowiadaj prozą. NIGDY nie wyjaśniaj. NIGDY nie używaj markdown.\n"
    "Nawet jeśli masz już wszystkie dane do odpowiedzi - zapakuj odpowiedź w JSON\n"
    'z action="final_answer".\n'
    "\n"
    "Jesteś agentem korzystającym z narzędzi. Format akcji "
    '(dyskryminator: pole "action"):\n'
    "\n"
    "(1) Wywołanie narzędzia:\n"
    '{"action": "call_tool", "tool": "<nazwa>", "arguments": {...}}\n'
    "\n"
    "(2) Odpowiedź końcowa:\n"
    '{"action": "final_answer", "answer": "<treść>"}\n'
    "\n"
    "Dostępne narzędzia:\n"
    "{tools}\n"
    "\n"
    "Przykład pełnej trajektorii:\n"
    "\n"
    'User: "Jaka jest pogoda w Krakowie?"\n'
    "Asystent (tura 1):\n"
    '{"action": "call_tool", "tool": "get_weather", "arguments": {"city": "Kraków"}}\n'
    "\n"
    'User: <tool_result tool="get_weather">'
    '{"ok": true, "result": {"temperature_c": 7.5, "condition": "rain"}}'
    "</tool_result>\n"
    "\n"
    "Asystent (tura 2 - finalna):\n"
    '{"action": "final_answer", "answer": "W Krakowie jest 7.5°C i pada deszcz."}\n'
    "\n"
    "UWAGA: Tura 2 to NADAL JSON, mimo że masz już dane. NIE odpowiadaj prozą.\n"
    "\n"
    "Limit kroków: {steps}.\n"
    "\n"
    "ZABRONIONE odpowiedzi:\n"
    '- "Pogoda w Krakowie to 7.5°C." (proza, brak JSON)\n'
    '- "```json\\n{...}\\n```" (markdown wrapper)\n'
    '- "Odpowiedź: {...}" (prefiks tekstowy)\n'
    '- {"answer": "..."} (brak pola action)\n'
    "\n"
    'DOZWOLONE: tylko czysty obiekt JSON z polem "action".\n'
)

# Source: inference/prompts.py, _build_en. Not used by any released run (all runs used the Polish prompt).
_EN = (
    "EVERY RESPONSE MUST BE A SINGLE JSON OBJECT. ALWAYS.\n"
    "NEVER reply in prose. NEVER explain. NEVER use markdown fences.\n"
    "Even when you already have the data to answer - wrap the answer in JSON\n"
    'with action="final_answer".\n'
    "\n"
    'You are a tool-using agent. Action format (discriminator: "action" field):\n'
    "\n"
    "(1) Call a tool:\n"
    '{"action": "call_tool", "tool": "<name>", "arguments": {...}}\n'
    "\n"
    "(2) Final answer:\n"
    '{"action": "final_answer", "answer": "<text>"}\n'
    "\n"
    "Available tools:\n"
    "{tools}\n"
    "\n"
    "Example trajectory:\n"
    "\n"
    'User: "What is the weather in Krakow?"\n'
    "Assistant (turn 1):\n"
    '{"action": "call_tool", "tool": "get_weather", "arguments": {"city": "Kraków"}}\n'
    "\n"
    'User: <tool_result tool="get_weather">'
    '{"ok": true, "result": {"temperature_c": 7.5, "condition": "rain"}}'
    "</tool_result>\n"
    "\n"
    "Assistant (turn 2 - final):\n"
    '{"action": "final_answer", "answer": "Krakow is 7.5°C with rain."}\n'
    "\n"
    "NOTE: Turn 2 is STILL JSON even though you have the data. Do NOT reply in prose.\n"
    "\n"
    "Step budget: {steps}.\n"
    "\n"
    "FORBIDDEN responses:\n"
    '- "It is 7.5°C in Krakow." (prose, no JSON)\n'
    '- "```json\\n{...}\\n```" (markdown wrapper)\n'
    '- "Answer: {...}" (text prefix)\n'
    '- {"answer": "..."} (missing action field)\n'
    "\n"
    'ALLOWED: only a clean JSON object with an "action" field.\n'
)


def system_prompt(tools, language="pl", max_steps=8):
    if language not in ("pl", "en"):
        raise ValueError("unsupported language: %r" % (language,))
    template = _PL if language == "pl" else _EN
    # Plain replace, not str.format: the template holds literal braces. Steps first, so text inside a tool
    # description can never be mistaken for the step marker.
    return template.replace("{steps}", str(max_steps)).replace("{tools}", render_tools(tools))


# ---------------------------------------------------------------------------
# 2. message list
# ---------------------------------------------------------------------------


def tool_result_message(tool_name, observation):
    return '<tool_result tool="%s">\n%s\n</tool_result>' % (tool_name, json.dumps(observation, ensure_ascii=False))


def initial_messages(task_prompt, tools, max_steps, language="pl"):
    return [
        {"role": "system", "content": system_prompt(tools, language, max_steps)},
        {"role": "user", "content": task_prompt},
    ]


# ---------------------------------------------------------------------------
# 3. chat formats
# ---------------------------------------------------------------------------

FAMILY_OF_MODEL = {
    "bielik-11b-v3": "chatml",
    "bielik-minitron-7b-v3": "chatml",
    "llama-pllum-8b": "llama-3",
}

STOP = {"chatml": "<|im_end|>", "llama-3": "<|eot_id|>"}


def chat_text(messages, family):
    """Flat prompt text for the chat format, ending at the open assistant header."""
    if family == "chatml":
        system = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"] or ""
                break
        out = "<|im_start|>system\n" + system + "<|im_end|>\n"
        turns = [(("<|im_start|>" + m["role"]), m["content"]) for m in messages if m["role"] in ("user", "assistant")]
        turns.append(("<|im_start|>assistant", None))
        for head, body in turns:
            out += head + "\n" + (body + "<|im_end|>\n" if body else "")
        return out
    if family == "llama-3":
        heads = {r: "<|start_header_id|>%s<|end_header_id|>\n\n" % r for r in ("system", "user", "assistant")}
        turns = [(heads[m["role"]], m["content"]) for m in messages if m["role"] in heads]
        turns.append((heads["assistant"], None))
        out = ""
        for head, body in turns:
            out += head + (body + "<|eot_id|>" if body else "")
        return out
    raise ValueError("unknown chat family %r" % (family,))
