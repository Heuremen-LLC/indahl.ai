"""acceptance.py (ours): the zero-GPU acceptance test for our parser, tool environment and oracle.

For every released trajectory (the 73 runs under release_data/ and the 16 L0e / L0-control runs under runs/L0e_2026-09/),
replay the logged raw model replies step by step through replay.py and compare:
  * every step: repair flag, post-repair text, parsed action, parse error (category and message), tool result, state after;
  * every trajectory: final state, success flag, TIMEOUT tag, step count;
  * the verdict: our PASS/FAIL and failure tags against (a) the logged line in the run's run.log where the run has one
    (the whole line, including the trajectory summary), (b) the per-task matrix CSV, (c) the run-time summary.json
    (pass count, tag counts, repair count) and the run.log footer lines.
Usage: python3 -I acceptance.py [--out DIR]   (reads ../../theirs as data only; writes the report and mismatch list)
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import oracle  # noqa: E402
import prompts  # noqa: E402
import tasks as taskmod  # noqa: E402
from replay import replay  # noqa: E402

THEIRS = os.environ.get("PAB_THEIRS") or os.path.normpath(os.path.join(HERE, "..", "..", "theirs"))
REL = os.path.join(THEIRS, "release_data")
L0E = os.path.join(THEIRS, "runs", "L0e_2026-09")
PASS, FAIL = "✓", "✗"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def read_log(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def collect_runs():
    """Yield dicts describing every run we can replay."""
    runs_csv = {r["run_id"]: r for r in read_csv(os.path.join(REL, "matrices", "runs.csv"))}
    for name in sorted(os.listdir(os.path.join(REL, "trajectories"))):
        slug = name[:-len(".jsonl")]
        meta = runs_csv[slug]
        summary = json.load(open(os.path.join(REL, "summaries", slug + ".json"), encoding="utf-8"))
        suite = meta["suite"]
        if "variance" in slug:
            suite = "variance(T=0.7)"
        yield {
            "run_id": slug, "suite": suite, "model_id": meta["model_id"], "quant": meta["quant"],
            "repair": summary["repair"], "summary": summary, "meta_source": meta["verdict_source"],
            "traj": os.path.join(REL, "trajectories", name),
            "log": os.path.join(REL, "run_logs", slug + ".log"),
            "tasks_dir": "ladder_ext" if suite == "ladder46" else "adversarial",
            "matrix": "release",
        }
    for group, suite, tdir in (("L0e_2026-09", "L0e", "ladder_l0e"), ("L0_control_2026-09", "L0-control", "ladder_l0_control")):
        base = os.path.join(L0E, "data", group)
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d)
            if not os.path.isdir(p):
                continue
            summary = json.load(open(os.path.join(p, "summary.json"), encoding="utf-8"))
            yield {
                "run_id": "%s__%s" % (group, d), "suite": suite, "model_id": summary["model_id"], "quant": summary["quant"],
                "repair": summary["repair"], "summary": summary, "meta_source": "run.log",
                "traj": os.path.join(p, "trajectories.jsonl"), "log": os.path.join(p, "run.log"),
                "tasks_dir": tdir, "matrix": "l0e" if suite == "L0e" else "l0ctl",
            }


def load_matrices():
    m = {}
    for name in ("per_task_main67.csv", "per_task_ladder46.csv", "per_task_variance.csv"):
        for r in read_csv(os.path.join(REL, "matrices", name)):
            m[(r["run_id"], r["task_id"])] = r
    for name in ("per_task_L0e.csv", "per_task_L0_control.csv"):
        for r in read_csv(os.path.join(L0E, "matrices", name)):
            m[(r["run_id"], r["task_id"])] = r
    return m


def our_line(width, res):
    glyph = {"PASS": PASS, "FAIL": FAIL, "INCONCLUSIVE": "?"}[res.status]
    suffix = ""
    if res.status != "PASS" and res.tags:
        suffix = " - " + ", ".join(dict.fromkeys(res.tags))
    return "%s  %s  %s%s" % (res.task_id.ljust(width), glyph, res.summary, suffix)


def main():
    out_dir = HERE
    if "--out" in sys.argv:
        out_dir = sys.argv[sys.argv.index("--out") + 1]
    task_cache = {}

    def tasks_in(d):
        if d not in task_cache:
            task_cache[d] = taskmod.load_dir(os.path.join(THEIRS, "tasks", d))
        return task_cache[d]

    matrices = load_matrices()
    G = collections.defaultdict(collections.Counter)   # (suite, model) -> counters
    mism = []   # rows for the TSV
    run_rows = []
    prompt_stats = {"rendered": 0, "max_chars": 0}

    def add(kind, run, task_id, step, ours, theirs):
        mism.append((run["run_id"], run["suite"], run["model_id"], task_id, kind, step, str(ours)[:300], str(theirs)[:300]))

    for run in collect_runs():
        key = (run["suite"], run["model_id"])
        g = G[key]
        tdict = tasks_in(run["tasks_dir"])
        recs = read_jsonl(run["traj"])
        family = prompts.FAMILY_OF_MODEL[run["model_id"]]
        g["runs"] += 1
        results = []
        log_lines = read_log(run["log"])
        have_log = log_lines is not None and run["meta_source"].startswith("run.log")
        width = max(len(r["task_id"]) for r in recs)
        run_tags = collections.Counter()
        timeouts = 0
        repair_steps = 0
        line_by_task = {}
        if have_log:
            for ln in log_lines:
                for r in recs:
                    t = r["task_id"]
                    if ln.startswith(t) and ln[len(t):len(t) + 1] in (" ",) and t not in line_by_task:
                        rest = ln[len(t):].lstrip(" ")
                        if rest[:1] in (PASS, FAIL, "?"):
                            line_by_task[t] = ln
        for rec in recs:
            tid = rec["task_id"]
            g["trajectories"] += 1
            if tid not in tdict:
                g["task_missing"] += 1
                add("task_file_missing", run, tid, -1, "", "")
                continue
            try:
                rp = replay(tdict[tid], rec, run["repair"], family)
            except Exception as exc:   # a crash is a mismatch, not a stop
                g["replay_crash"] += 1
                add("replay_crash", run, tid, -1, repr(exc), "")
                continue
            g["steps"] += rp.n_logged
            g["steps_compared"] += min(rp.n_logged, rp.n_ours)
            prompt_stats["rendered"] += len(rp.traj.prompts)
            prompt_stats["max_chars"] = max([prompt_stats["max_chars"]] + [len(p) for p in rp.traj.prompts])
            g["tool_steps_logged"] += sum(1 for s in rec["steps"] if s["tool_result"] is not None)
            g["fields_checked"] += rp.checked_fields
            kinds = collections.Counter()
            for kind, idx, ours, theirs in rp.mismatches:
                kinds[kind] += 1
                add(kind, run, tid, idx, ours, theirs)
            for kind, n in kinds.items():
                g["mm:" + kind] += n
            if kinds:
                g["trajectories_with_mismatch"] += 1
            res = rp.result
            results.append(res)
            run_tags.update(res.tags)
            if not rp.final_emitted:
                timeouts += 1
            repair_steps += sum(1 for s in rec["steps"] if s["repair_applied"])
            tagset = sorted(set(res.tags))
            # (a) logged run.log line
            if have_log:
                theirs_line = line_by_task.get(tid)
                if theirs_line is None:
                    g["log_line_absent"] += 1
                    add("log_line_absent", run, tid, -1, "", "")
                else:
                    g["log_lines_checked"] += 1
                    ours_line = our_line(width, res)
                    if ours_line.rstrip() != theirs_line.rstrip():
                        g["mm:log_line"] += 1
                        # separate the pass/fail part from the rest
                        og = ours_line[width + 2:width + 3]
                        tg = theirs_line[width + 2:width + 3]
                        if og != tg:
                            g["verdict_mismatch"] += 1
                            add("verdict_pass_fail(log)", run, tid, -1, og, tg)
                        add("log_line", run, tid, -1, ours_line, theirs_line)
                    else:
                        g["log_lines_equal"] += 1
            # (b) matrix row
            row = matrices.get((run["run_id"], tid))
            if row is None:
                g["matrix_row_absent"] += 1
                add("matrix_row_absent", run, tid, -1, "", "")
            else:
                g["matrix_rows_checked"] += 1
                if int(row["passed"]) != int(res.passed):
                    g["matrix_verdict_mismatch"] += 1
                    if not have_log:
                        g["verdict_mismatch"] += 1
                    add("verdict_pass_fail(matrix)", run, tid, -1, int(res.passed), row["passed"])
                for col, ours_v, theirs_v in (("steps", rp.n_ours, int(row["steps"])),
                                              ("trajectory_success", int(rp.final_emitted), int(row["trajectory_success"]))):
                    g["matrix_extra_checks"] += 1
                    if ours_v != theirs_v:
                        g["matrix_extra_mismatch"] += 1
                        add("matrix:" + col, run, tid, -1, ours_v, theirs_v)
                tags_theirs = [t for t in row["failure_tags"].split(";") if t]
                if tagset != sorted(tags_theirs):
                    g["matrix_tag_mismatch"] += 1
                    add("tags(matrix)", run, tid, -1, ";".join(tagset), row["failure_tags"])
        # (c) aggregates
        s = run["summary"]
        n_pass = sum(1 for r in results if r.passed)
        n_inc = sum(1 for r in results if r.status == "INCONCLUSIVE")
        counts = collections.Counter(run_tags)
        counts_full = collections.Counter(run_tags)
        counts_full["timeout"] += timeouts
        if not counts_full["timeout"]:
            del counts_full["timeout"]
        agg_ok = True
        checks = [
            ("num_passed", n_pass, s["num_passed"]),
            ("num_inconclusive", n_inc, s["num_inconclusive"]),
            ("num_tasks", len({r.task_id for r in results}), s["num_tasks"]),
            ("num_trajectories", len(recs), s["num_trajectories"]),
            ("success_rate", round(n_pass / len(results), 4) if results else 0.0, s["success_rate"]),
            ("repair_applied_steps", repair_steps, s["repair_applied_steps"]),
            ("failure_tag_counts", sorted(counts_full.items()), sorted(s["failure_tag_counts"].items())),
        ]
        for name, a, b in checks:
            g["aggregate_checks"] += 1
            if a != b:
                agg_ok = False
                g["aggregate_mismatch"] += 1
                add("summary.json:" + name, run, "(run)", -1, a, b)
        if have_log:
            tail = [l for l in log_lines if l.startswith("Success:") or l.startswith("Failure tags:")]
            ours_success = "Success: %d/%d (%.0f%%)" % (n_pass, len(results), (n_pass / len(results) * 100.0) if results else 0.0)
            body = ", ".join("%s: %d" % kv for kv in sorted(counts.items()))
            ours_tags = "Failure tags: {%s}" % body if counts else None
            g["aggregate_checks"] += 1
            if ours_success not in tail:
                g["aggregate_mismatch"] += 1
                add("run.log:Success", run, "(run)", -1, ours_success, [t for t in tail if t.startswith("Success")])
            if ours_tags is not None:
                g["aggregate_checks"] += 1
                if ours_tags not in tail:
                    g["aggregate_mismatch"] += 1
                    add("run.log:Failure tags", run, "(run)", -1, ours_tags, [t for t in tail if t.startswith("Failure")])
        run_rows.append((run["run_id"], run["suite"], run["model_id"], run["quant"], run["repair"],
                         "run.log" if have_log else "his replay (no run.log)", len(recs), n_pass, agg_ok))

    # ---- report -------------------------------------------------------------------------------------------------
    lines = []
    P = lines.append
    P("ACCEPTANCE REPORT (ours). Replay of every released trajectory through our parser, tool environment and oracle.")
    P("Source data read as text only: %s" % THEIRS)
    P("")
    cols = [("runs", "runs"), ("trajectories", "traj"), ("steps", "steps"), ("tool_steps_logged", "toolsteps"),
            ("mm:tool_result", "toolres_mm"), ("mm:parsed_action", "action_mm"), ("mm:parse_error.category", "perr_cat_mm"),
            ("mm:parse_error.message", "perr_msg_mm"), ("mm:state_after", "state_mm"), ("mm:repair_applied", "repair_mm"),
            ("verdict_mismatch", "verdict_mm"), ("matrix_tag_mismatch", "tag_mm(mx)"), ("matrix_extra_mismatch", "mxcols_mm"), ("mm:log_line", "logline_mm"),
            ("aggregate_mismatch", "agg_mm")]
    head = "%-18s %-22s" % ("suite", "model") + "".join(" %11s" % c[1] for c in cols)
    P(head)
    P("-" * len(head))
    tot = collections.Counter()
    by_suite = collections.defaultdict(collections.Counter)
    for (suite, model), g in sorted(G.items()):
        P("%-18s %-22s" % (suite, model) + "".join(" %11d" % g[c[0]] for c in cols))
        tot.update(g)
        by_suite[suite].update(g)
    P("-" * len(head))
    for suite, g in sorted(by_suite.items()):
        P("%-18s %-22s" % (suite, "(all models)") + "".join(" %11d" % g[c[0]] for c in cols))
    grp = {"release_data (73 runs)": collections.Counter(), "runs/L0e_2026-09 (16 runs)": collections.Counter()}
    for suite, g in by_suite.items():
        grp["runs/L0e_2026-09 (16 runs)" if suite in ("L0e", "L0-control") else "release_data (73 runs)"].update(g)
    for name, g in grp.items():
        P("%-41s" % name + "".join(" %11d" % g[c[0]] for c in cols))
    P("%-18s %-22s" % ("ALL", "") + "".join(" %11d" % tot[c[0]] for c in cols))
    P("")
    P("Totals: trajectories %d, steps %d, steps compared %d, fields compared %d, trajectories with any mismatch %d."
      % (tot["trajectories"], tot["steps"], tot["steps_compared"], tot["fields_checked"], tot["trajectories_with_mismatch"]))
    P("Logged tool results: %d steps carry one. Tool-result mismatches: %d." % (tot["tool_steps_logged"], tot["mm:tool_result"]))
    P("run.log lines checked (whole line incl. trajectory summary): %d, equal: %d. Matrix rows checked: %d."
      % (tot["log_lines_checked"], tot["log_lines_equal"], tot["matrix_rows_checked"]))
    P("Aggregate checks (summary.json fields and run.log footers): %d, mismatches %d." % (tot["aggregate_checks"], tot["aggregate_mismatch"]))
    P("Prompts rendered (one per step, both chat formats): %d, longest %d characters." % (prompt_stats["rendered"], prompt_stats["max_chars"]))
    other = ", ".join("%s=%d" % (k[3:], v) for k, v in sorted(tot.items()) if k.startswith("mm:") and v
                      and k[3:] not in ("tool_result", "parsed_action", "parse_error.category", "parse_error.message",
                                        "state_after", "repair_applied", "log_line"))
    P("Other mismatch kinds: " + (other or "none"))
    P("")
    P("Columns: toolres_mm = steps whose tool result differs from the logged one; action_mm = parsed action differs; perr_cat_mm /")
    P("perr_msg_mm = parse error category / message differs; state_mm = environment state after the step differs; repair_mm = repair")
    P("flag or repaired text differs; verdict_mm = our PASS/FAIL differs from the logged verdict (the run.log line where the run has")
    P("one, otherwise the per-task matrix, which is the author's replay); tag_mm(mx) = failure tag set differs from the matrix;")
    P("mxcols_mm = matrix steps / trajectory_success columns differ; logline_mm = whole run.log line differs (pass/fail mark, tags,")
    P("trajectory summary with argument values); agg_mm = run-level numbers differ from summary.json or the run.log footer.")
    P("Runs without a run.log (21): their per-task verdict is the author's replay, so it is compared with the matrix, and the")
    P("run-time summary.json (pass count, inconclusive count, success rate, repair count, tag histogram incl. timeouts) is the")
    P("independent record we hold them to.")
    P("")
    P("Per run (verdict source, passes, aggregates equal):")
    for r in run_rows:
        P("  %-52s %-12s %-22s %-6s %-26s n=%-3d passed=%-3d agg_ok=%s" % (r[0], r[1], r[2], r[3], r[5], r[6], r[7], r[8]))
    report = "\n".join(lines) + "\n"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "acceptance_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(report)
    with open(os.path.join(out_dir, "acceptance_mismatches.tsv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["run_id", "suite", "model", "task_id", "kind", "step", "ours", "theirs"])
        for row in mism:
            w.writerow([str(x).replace("\t", " ").replace("\n", "\\n") for x in row])
    print(report)
    print("mismatch rows written: %d" % len(mism))


if __name__ == "__main__":
    main()
