"""render_prompts.py (ours): the exact prompt text the benchmark's runner sends to a model, rendered from the task files.

Usage:
  python3 -I render_prompts.py show TASK_ID FAMILY      print the step-0 prompt (FAMILY is chatml or llama-3)
  python3 -I render_prompts.py table                    write rendered_step0.tsv: task, directory, family, characters,
                                                        UTF-8 bytes, sha256 of the step-0 prompt, for every task file and
                                                        both families (the pin to compare a live runner against)
The text is what llama-cpp-python's chat format puts in front of the model (see prompts.py). It has no BOS token: the
library adds BOS when it tokenises with special tokens parsed. Stop string: <|im_end|> for chatml, <|eot_id|> for llama-3.
Run the model on this raw text (a completion call), never through the GGUF's own chat template.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import prompts  # noqa: E402
import tasks as taskmod  # noqa: E402

THEIRS = os.environ.get("PAB_THEIRS") or os.path.normpath(os.path.join(HERE, "..", "..", "theirs"))
DIRS = ("adversarial", "ladder_ext", "ladder_l0e", "ladder_l0_control", "smoke")


def step0(task, family):
    return prompts.chat_text(prompts.initial_messages(task.prompt, task.tools, task.max_steps, "pl"), family)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "show" and len(sys.argv) == 4:
        for d in DIRS:
            t = taskmod.load_dir(os.path.join(THEIRS, "tasks", d)).get(sys.argv[2])
            if t:
                sys.stdout.write(step0(t, sys.argv[3]))
                return
        raise SystemExit("task not found: %s" % sys.argv[2])
    if cmd == "table":
        rows = ["task_id\tdirectory\tfamily\tchars\tutf8_bytes\tsha256"]
        for d in DIRS:
            for t in taskmod.load_dir(os.path.join(THEIRS, "tasks", d)).values():
                for fam in ("chatml", "llama-3"):
                    text = step0(t, fam)
                    b = text.encode("utf-8")
                    rows.append("%s\t%s\t%s\t%d\t%d\t%s" % (t.id, d, fam, len(text), len(b), hashlib.sha256(b).hexdigest()))
        out = os.path.join(HERE, "rendered_step0.tsv")
        with open(out, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(rows) + "\n")
        print("wrote %s (%d rows)" % (out, len(rows) - 1))
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
