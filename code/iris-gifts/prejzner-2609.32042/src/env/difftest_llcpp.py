"""difftest_llcpp.py (ours): check our two chat formats against the real llama-cpp-python formatter functions.

The runner of the benchmark never builds the prompt text itself: it hands a list of messages to llama-cpp-python, whose
`chat_format` ("chatml" for Bielik, "llama-3" for PLLuM) turns them into text. The source of that library (release v0.3.19,
file llama_cpp/llama_chat_format.py, fetched as text from
https://raw.githubusercontent.com/abetlen/llama-cpp-python/v0.3.19/llama_cpp/llama_chat_format.py) was read in full for the
functions used. This script pulls exactly six small pure functions out of that file with `ast` (_get_system_message,
_map_roles, _format_no_colon_single, _format_chatml, format_chatml, format_llama3), strips decorators and annotations, runs
them in a bare namespace, and compares their text and stop string with ours on:
  * every message list of every step of every released trajectory (each in the chat format of its model family);
  * 50000 random message lists with empty messages, repeated roles, several system messages, special-token look-alikes.
Usage: python3 -I difftest_llcpp.py PATH_TO_llama_chat_format.py
"""
import ast
import dataclasses
import hashlib
import os
import random
import sys
import typing

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import acceptance  # noqa: E402
import prompts  # noqa: E402
import tasks as taskmod  # noqa: E402
from replay import replay  # noqa: E402

WANT = ["_get_system_message", "_map_roles", "_format_no_colon_single", "_format_chatml", "format_chatml", "format_llama3"]


def load_reference(path):
    raw = open(path, "rb").read()
    tree = ast.parse(raw.decode("utf-8"))
    picked = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in WANT:
            node.decorator_list = []
            node.returns = None
            for a in node.args.args + node.args.kwonlyargs:
                a.annotation = None
            if node.args.kwarg:
                node.args.kwarg.annotation = None
            picked[node.name] = node
    missing = [n for n in WANT if n not in picked]
    if missing:
        raise SystemExit("functions not found in %s: %s" % (path, missing))

    @dataclasses.dataclass
    class ChatFormatterResponse:
        prompt: str
        stop: object = None
        stopping_criteria: object = None
        added_special: bool = False

    ns = {"ChatFormatterResponse": ChatFormatterResponse, "Any": typing.Any, "List": typing.List, "Tuple": typing.Tuple,
          "Optional": typing.Optional, "Dict": typing.Dict, "Union": typing.Union}
    mod = ast.Module(body=[picked[n] for n in WANT], type_ignores=[])
    exec(compile(ast.fix_missing_locations(mod), "llama_chat_format_extract", "exec"), ns)
    return ns, hashlib.sha256(raw).hexdigest()


def main():
    if len(sys.argv) < 2:
        print("SKIPPED: pass the path of llama_cpp/llama_chat_format.py (v0.3.19)")
        sys.exit(2)
    ns, digest = load_reference(sys.argv[1])
    print("reference file sha256 %s" % digest)
    ref = {"chatml": ns["format_chatml"], "llama-3": ns["format_llama3"]}

    def same(messages, family):
        r = ref[family](messages)
        return r.prompt == prompts.chat_text(messages, family) and r.stop == prompts.STOP[family] and r.added_special is False

    n = bad = 0
    for run in acceptance.collect_runs():
        tdict = taskmod.load_dir(os.path.join(acceptance.THEIRS, "tasks", run["tasks_dir"]))
        family = prompts.FAMILY_OF_MODEL[run["model_id"]]
        for rec in acceptance.read_jsonl(run["traj"]):
            rp = replay(tdict[rec["task_id"]], rec, run["repair"], family)
            for msgs in rp.traj.messages:
                n += 1
                bad += not same(msgs, family)
    print("real dialogues: %d prompts compared, %d differ" % (n, bad))
    total_bad = bad

    rnd = random.Random(11)
    pool = ["", "x", "Cześć\nświat", "<|im_end|>", "<|eot_id|>", "{\"action\": \"final_answer\"}", " ", "a" * 200, "{0} {system_message}"]
    m = b2 = 0
    for _ in range(50000):
        roles = [rnd.choice(["system", "user", "assistant", "user", "assistant", "tool"]) for _ in range(rnd.randint(0, 7))]
        msgs = [{"role": r, "content": rnd.choice(pool)} for r in roles]
        for fam in ("chatml", "llama-3"):
            m += 1
            b2 += not same(msgs, fam)
    print("random message lists: %d comparisons, %d differ" % (m, b2))
    total_bad += b2
    print("RESULT: %s" % ("our chat formats equal llama-cpp-python v0.3.19 on every case" if total_bad == 0 else "DIFFERENCES FOUND"))
    sys.exit(1 if total_bad else 0)


if __name__ == "__main__":
    main()
