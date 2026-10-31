"""replay.py (ours): feed the logged raw model replies of one trajectory, step by step, through our agent loop (parser,
tool environment) and our oracle, and report every place where our output differs from the released record.

The model is never called: complete() hands back the logged reply for the step (the pre-repair text when the record says a
repair fired, otherwise the logged text). If our loop wants a step the record does not have, the replay stops and records a
step_count mismatch. Because the replies are the logged ones, the only thing that can differ is what our code does with them.
"""
import json

import agent
import oracle
from protocol import _finite


def cj(x):
    """Canonical JSON text, order and number types kept, so 7 and 7.0 and true are not confused. NaN and infinity become
    null first, as the released records were written that way."""
    return json.dumps(_finite(x), ensure_ascii=False)


class Replay:
    def __init__(self):
        self.mismatches = []     # (kind, step_idx or -1, ours, theirs)
        self.checked_fields = 0
        self.n_logged = 0
        self.n_ours = 0
        self.traj = None
        self.result = None
        self.final_emitted = False

    def cmp(self, kind, idx, ours, theirs):
        self.checked_fields += 1
        a, b = cj(ours), cj(theirs)
        if a != b:
            self.mismatches.append((kind, idx, a, b))


def replay(task, rec, repair, family):
    rp = Replay()
    logged = rec["steps"]
    rp.n_logged = len(logged)

    def complete(prompt, idx):
        if idx >= len(logged):
            raise agent.StopRun()
        s = logged[idx]
        return s["raw_model_output_pre_repair"] if s["repair_applied"] else s["raw_model_output"]

    tr = agent.run_task(task, complete, repair, family)
    if tr.stopped_early:
        rp.mismatches.append(("step_count", -1, "we would run step %d" % len(tr.steps), "record stops after %d steps" % len(logged)))
    rp.traj = tr
    rp.n_ours = len(tr.steps)
    if rp.n_ours != rp.n_logged and not tr.stopped_early:
        rp.mismatches.append(("step_count", -1, "we stop after %d steps" % rp.n_ours, "record has %d steps" % rp.n_logged))
    for ours, theirs in zip(tr.steps, logged):
        i = ours["step_idx"]
        for key in ("repair_applied", "raw_model_output", "raw_model_output_pre_repair", "parsed_action", "tool_result", "state_after"):
            rp.cmp(key, i, ours[key], theirs[key])
        pe_o, pe_t = ours["parse_error"], theirs["parse_error"]
        if pe_o is None or pe_t is None:
            rp.cmp("parse_error", i, pe_o, pe_t)
        else:
            rp.cmp("parse_error.category", i, pe_o["category"], pe_t["category"])
            rp.cmp("parse_error.message", i, pe_o["message"], pe_t["message"])
    rp.cmp("final_state", -1, tr.final_state, rec["final_state"])
    rp.cmp("success", -1, tr.success, rec["success"])
    rp.cmp("failure_tags(trajectory)", -1, tr.failure_tags, rec["failure_tags"])
    rp.final_emitted = tr.success
    rp.result = oracle.evaluate(task.id, task.expected, tr.oracle_steps)
    return rp
