"""tasks.py (ours): load a task file into a plain object and build the starting state of its tool environment.

Task files are YAML (read with miniyaml.py). Required keys and types follow the benchmark's task description: id,
category, environment, language_variant, prompt, available_tools, initial_state_path, expected_final_state, max_steps,
constraints, and the optional strict_match and hardcoded_state. Unknown keys are refused, as in the original.
"""
import json
import os

import miniyaml

CATEGORIES = {"TOOL_SELECTION", "STATEFUL", "CONSTRAINT", "RECOVERY"}
VARIANTS = {"EN_EN", "PL_EN", "PL_EN_PL_DESC"}
KNOWN = {"id", "category", "environment", "language_variant", "prompt", "available_tools", "initial_state_path",
         "expected_final_state", "max_steps", "constraints", "strict_match", "hardcoded_state"}


class Task:
    def __init__(self, d, path):
        extra = set(d) - KNOWN
        if extra:
            raise ValueError("%s: unknown keys %s" % (path, sorted(extra)))
        for k in ("id", "category", "environment", "language_variant", "prompt", "initial_state_path"):
            if not isinstance(d.get(k), str) or not d[k]:
                raise ValueError("%s: %s must be a non-empty string" % (path, k))
        if d["category"] not in CATEGORIES or d["language_variant"] not in VARIANTS:
            raise ValueError("%s: bad category or language_variant" % path)
        tools = d.get("available_tools", [])
        if not isinstance(tools, list) or not all(isinstance(t, dict) for t in tools):
            raise ValueError("%s: available_tools must be a list of mappings" % path)
        steps = d.get("max_steps", 8)
        if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
            raise ValueError("%s: max_steps must be a positive integer" % path)
        self.id = d["id"]
        self.environment = d["environment"]
        self.language_variant = d["language_variant"]
        self.prompt = d["prompt"]
        self.tools = tools
        self.tool_names = [t["name"] for t in tools if "name" in t]
        self.initial_state_path = d["initial_state_path"]
        self.expected = d.get("expected_final_state") or {}
        self.max_steps = steps
        self.strict_match = bool(d.get("strict_match", False))
        self.hardcoded_state = d.get("hardcoded_state")
        self.path = path

    def initial_state(self):
        p = os.path.join(os.path.dirname(self.path), self.initial_state_path)
        if not os.path.exists(p):
            return {}
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def reset_state(self):
        """What the environment is reset with: the state file, plus the two reserved keys set from the task."""
        st = dict(self.initial_state())
        if self.strict_match:
            st["__strict_match"] = True
        if self.hardcoded_state:
            st["__overrides"] = self.hardcoded_state
        return st


def load_task(path):
    d = miniyaml.load_file(path)
    if not isinstance(d, dict):
        raise ValueError("%s: top level must be a mapping" % path)
    return Task(d, path)


def load_dir(directory):
    out = {}
    for name in sorted(os.listdir(directory)):
        if name.endswith((".yaml", ".yml")):
            t = load_task(os.path.join(directory, name))
            out[t.id] = t
    return out
