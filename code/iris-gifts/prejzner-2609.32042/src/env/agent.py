"""agent.py (ours): the loop that turns model replies into a finished trajectory.

One function, run_task, used both by the replay test (replies come from the released logs) and, later, by the live run
(replies come from a model). The model is any callable complete(prompt_text, step_idx) -> reply text, so this file never
touches a model itself.

Loop, as the benchmark's runner does it: messages start as the system prompt and the task prompt. At every step the prompt
text for the model family is rendered from the messages and the reply is fetched. With repair on, the reply goes through
attempt_repair first. The reply (before any repair) is appended as an assistant message. The text is parsed. A parse error
adds nothing else, a final answer ends the run, a tool call runs in the environment and its result is appended as a user
message. The run also ends after max_steps steps; then it carries the TIMEOUT tag.
"""
import prompts
from oracle import Step
from protocol import CallTool, FinalAnswer, attempt_repair, parse_action
from weather import WeatherEnv


class StopRun(Exception):
    """Raised by a complete() callable that has no reply for this step (a replay whose record ends early)."""


class Trajectory:
    def __init__(self):
        self.stopped_early = False
        self.steps = []          # dicts in the shape of the released step records (without latency)
        self.oracle_steps = []   # oracle.Step objects for the verdict
        self.prompts = []        # prompt text sent before each step
        self.messages = []       # message list before each step
        self.final_state = None
        self.success = False     # True when a final answer was emitted (this is NOT the verdict)
        self.failure_tags = []   # ["TIMEOUT"] when no final answer came


def run_task(task, complete, repair, family, language="pl"):
    env = WeatherEnv()
    env.reset(task.reset_state())
    messages = prompts.initial_messages(task.prompt, task.tools, task.max_steps, language)
    tr = Trajectory()
    for idx in range(task.max_steps):
        tr.messages.append(list(messages))
        prompt = prompts.chat_text(messages, family)
        tr.prompts.append(prompt)
        try:
            original = complete(prompt, idx)
        except StopRun:
            tr.stopped_early = True
            break
        fixed = attempt_repair(original, task.tool_names) if repair else None
        text = fixed if fixed is not None else original
        res = parse_action(text)
        messages.append({"role": "assistant", "content": original})
        tool_result = None
        if res.ok and isinstance(res.action, CallTool):
            tool_result = env.call(res.action.tool, res.action.arguments)
        tr.steps.append({
            "step_idx": idx,
            "raw_model_output": text,
            "parsed_action": res.action.to_jsonable() if res.ok else None,
            "parse_error": None if res.ok else res.error.to_jsonable(),
            "tool_result": tool_result,
            "state_after": env.snapshot(),
            "repair_applied": fixed is not None,
            "raw_model_output_pre_repair": original if fixed is not None else None,
        })
        tr.oracle_steps.append(Step(idx, text, res.action, res.error, tool_result))
        if res.ok and isinstance(res.action, FinalAnswer):
            tr.success = True
            break
        if res.ok:
            messages.append({"role": "user", "content": prompts.tool_result_message(res.action.tool, tool_result)})
    tr.final_state = env.snapshot()
    tr.failure_tags = [] if tr.success else ["TIMEOUT"]
    return tr
