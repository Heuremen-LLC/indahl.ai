#!/usr/bin/env python3
"""relay.py - run a chain of stages with dependencies, lanes and recorded outcomes.

A chain is a JSON list of stages: {id, after: [ids], lane, cmd: [argv], cwd, finally?, decide?, env?}.
Commands: tick CHAIN | status CHAIN | add CHAIN STAGE | selftest.
No timers and no daemons: tick is idempotent and is called by whatever scheduler you own.
Python 3.9+, standard library only. Runs locally and contacts nothing.
"""
import json, os, signal, subprocess, sys, tempfile, time

try:
    import fcntl
except ImportError:  # no file lock on platforms without fcntl
    fcntl = None

SELF = os.path.abspath(__file__)
TERMINAL = ("done", "failed", "blocked")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def paths(chain):
    chain = os.path.abspath(chain)
    base = chain[:-5] if chain.endswith(".json") else chain
    work = base + ".relay"
    return {"chain": chain, "dir": os.path.dirname(chain), "state": base + ".state.json",
            "work": work, "rc": os.path.join(work, "rc"), "logs": os.path.join(work, "logs"),
            "log": os.path.join(work, "relay.log")}


def log(p, msg):
    os.makedirs(p["work"], exist_ok=True)
    with open(p["log"], "a") as f:
        f.write(now() + " " + msg + "\n")


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return False


def check_stage(s, known, existing_ids):
    """Return an error string or None."""
    if not isinstance(s, dict):
        return "stage must be a JSON object"
    sid = s.get("id")
    if not isinstance(sid, str) or not sid or "/" in sid:
        return "stage needs a string id without slashes"
    cmd = s.get("cmd")
    if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) for x in cmd):
        return "stage %s: cmd must be a non-empty list of strings" % sid
    after = s.get("after", [])
    if not isinstance(after, list) or not all(isinstance(x, str) for x in after):
        return "stage %s: after must be a list of ids" % sid
    if sid in existing_ids:
        return "duplicate id: %s" % sid
    for d in after:
        if d not in known:
            return "stage %s: unknown dependency %s" % (sid, d)
    return None


def load_chain(p):
    stages = load_json(p["chain"], None)
    if not isinstance(stages, list):
        sys.exit("relay: %s is not a JSON list of stages" % p["chain"])
    seen = set()
    for s in stages:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str):
            sys.exit("relay: every stage needs a string id")
        if s["id"] in seen:
            sys.exit("relay: duplicate id in chain: %s" % s["id"])
        seen.add(s["id"])
    return stages


def reconcile(p, state):
    """Fold rc files and dead processes into state. Returns True if anything changed."""
    changed = False
    for sid, rec in list(state.items()):
        if rec.get("status") != "running":
            continue
        rcf = os.path.join(p["rc"], sid + ".rc")
        if os.path.exists(rcf):
            try:
                lines = open(rcf).read().split()
                rc, ended = int(lines[0]), lines[1]
            except Exception:
                state[sid] = dict(rec, status="failed", rc=None, ended=now(), note="rc file unreadable")
                log(p, "FAILED %s (rc file unreadable)" % sid)
                changed = True
                continue
            state[sid] = dict(rec, status="done" if rc == 0 else "failed", rc=rc, ended=ended)
            log(p, "%s %s rc %d" % (state[sid]["status"].upper(), sid, rc))
            changed = True
        elif not alive(rec.get("pid", -1)):
            state[sid] = dict(rec, status="failed", rc=None, ended=now(), note="process vanished, no rc written")
            log(p, "FAILED %s (no rc: process vanished)" % sid)
            changed = True
    return changed


def start(p, s):
    sid = s["id"]
    for d in (p["rc"], p["logs"]):
        os.makedirs(d, exist_ok=True)
    rcf = os.path.join(p["rc"], sid + ".rc")
    if os.path.exists(rcf):
        os.remove(rcf)
    cwd = s.get("cwd") or p["dir"]
    if not os.path.isabs(cwd):
        cwd = os.path.join(p["dir"], cwd)
    env = dict(os.environ, **{str(k): str(v) for k, v in s.get("env", {}).items()})
    env["RELAY_CHAIN"] = p["chain"]
    env["RELAY_STAGE"] = sid
    lf = open(os.path.join(p["logs"], sid + ".log"), "a")
    proc = subprocess.Popen([sys.executable, SELF, "_run", rcf, "--"] + s["cmd"], cwd=cwd, env=env,
                            stdout=lf, stderr=lf, stdin=subprocess.DEVNULL, start_new_session=True)
    lf.close()
    log(p, "START %s lane %s pid %d" % (sid, s.get("lane", "default"), proc.pid))
    return {"status": "running", "pid": proc.pid, "started": now(), "lane": s.get("lane", "default")}


def cmd_run(argv):
    """Internal wrapper: run the command and write its own exit code to a file."""
    rcf, cmd = argv[0], argv[2:]
    try:
        rc = subprocess.call(cmd)
    except OSError as e:
        print("relay: cannot start %r: %s" % (cmd[0], e), file=sys.stderr)
        rc = 127
    tmp = rcf + ".tmp"
    with open(tmp, "w") as f:
        f.write("%d\n%s\n" % (rc, now()))
    os.replace(tmp, rcf)
    return 0


def cmd_tick(chain):
    p = paths(chain)
    stages = load_chain(p)
    os.makedirs(p["work"], exist_ok=True)
    lock = open(os.path.join(p["work"], "tick.lock"), "w")
    if fcntl:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("relay: another tick is running, nothing done")
            return 0
    state = load_json(p["state"], {})
    changed = reconcile(p, state)
    ids = [s["id"] for s in stages]
    busy = set(r.get("lane") for r in state.values() if r.get("status") == "running")
    progress = True
    while progress:  # a stage can become blocked, which can unblock a finally stage in the same tick
        progress = False
        for s in stages:
            sid = s["id"]
            if sid in state:
                continue
            deps = s.get("after", [])
            dstat = [state.get(d, {}).get("status", "waiting") for d in deps]
            if any(d not in ids for d in deps):
                state[sid] = {"status": "blocked", "ended": now(), "note": "unknown dependency"}
                log(p, "BLOCKED %s: unknown dependency" % sid)
                changed = progress = True
                continue
            if s.get("finally"):
                others = [x["id"] for x in stages if not x.get("finally")]
                if any(state.get(o, {}).get("status") not in TERMINAL for o in others):
                    continue
                if any(x not in TERMINAL for x in dstat):
                    continue
            else:
                bad = [d for d, x in zip(deps, dstat) if x in ("failed", "blocked")]
                if bad:
                    state[sid] = {"status": "blocked", "ended": now(), "note": "upstream not done: " + ", ".join(bad)}
                    log(p, "BLOCKED %s: upstream %s" % (sid, ", ".join(bad)))
                    changed = progress = True
                    continue
                if any(x != "done" for x in dstat):
                    continue
            lane = s.get("lane", "default")
            if lane in busy:
                continue
            state[sid] = start(p, s)
            busy.add(lane)
            changed = progress = True
    if changed:
        save_json(p["state"], state)
    print_status(stages, state)
    return 0


def display(rec):
    st = rec.get("status", "waiting")
    if st == "done":
        return "done rc 0"
    if st == "failed":
        return "FAILED (no rc)" if rec.get("rc") is None else "failed rc %s" % rec["rc"]
    if st == "blocked":
        return "BLOCKED"
    return st


def print_status(stages, state):
    for s in stages:
        r = state.get(s["id"], {})
        extra = []
        if r.get("started"):
            extra.append("start " + r["started"])
        if r.get("ended"):
            extra.append("end " + r["ended"])
        if r.get("note"):
            extra.append(r["note"])
        tag = " [finally]" if s.get("finally") else ""
        print("%-18s %-16s lane %-10s%s %s" % (s["id"], display(r), s.get("lane", "default"), tag, "  ".join(extra)))
    counts = {}
    for s in stages:
        k = state.get(s["id"], {}).get("status", "waiting")
        counts[k] = counts.get(k, 0) + 1
    print("summary: " + ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items())))


def cmd_status(chain):
    p = paths(chain)
    stages = load_chain(p)
    state = load_json(p["state"], {})
    reconcile(p, state)  # read-only view: not saved, the next tick saves it
    print_status(stages, state)
    bad = any(r.get("status") in ("failed", "blocked") for r in state.values())
    return 1 if bad else 0


def cmd_add(chain, stage_file):
    p = paths(chain)
    stages = load_chain(p)
    s = json.load(sys.stdin if stage_file == "-" else open(stage_file))
    ids = set(x["id"] for x in stages)
    err = check_stage(s, ids, ids)
    if err:
        print("relay add refused: " + err, file=sys.stderr)
        return 1
    stages.append(s)
    save_json(p["chain"], stages)
    log(p, "ADD %s" % s["id"])
    print("added %s" % s["id"])
    return 0


# ---- selftest ----

def run(args, **kw):
    return subprocess.run([sys.executable, SELF] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True, **kw)


def pump(chain, timeout=40):
    """Call tick until every stage is terminal (this loop stands in for the scheduler you would own)."""
    end = time.time() + timeout
    while time.time() < end:
        out = run(["tick", chain]).stdout
        state = load_json(paths(chain)["state"], {})
        stages = load_json(chain, [])
        if all(state.get(s["id"], {}).get("status") in TERMINAL for s in stages):
            return state
        time.sleep(0.2)
    raise AssertionError("chain did not finish: " + chain)


def py(code):
    return [sys.executable, "-c", code]


def selftest():
    results = []

    def check(name, cond):
        results.append(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    with tempfile.TemporaryDirectory() as tmp:
        def mk(name, stages):
            path = os.path.join(tmp, name + ".json")
            save_json(path, stages)
            return path

        # 1 linear success
        c = mk("linear", [{"id": "a", "cmd": py("pass")}, {"id": "b", "after": ["a"], "cmd": py("pass")},
                          {"id": "c", "after": ["b"], "cmd": py("pass")}])
        st = pump(c)
        check("linear success: a, b, c all done rc 0", all(st[k]["status"] == "done" and st[k]["rc"] == 0 for k in "abc"))

        # 2 failure blocks dependents, independent stage still runs
        c = mk("fail", [{"id": "a", "cmd": py("import sys; sys.exit(3)")}, {"id": "b", "after": ["a"], "cmd": py("pass")},
                        {"id": "c", "after": ["b"], "cmd": py("pass")}, {"id": "d", "lane": "other", "cmd": py("pass")}])
        st = pump(c)
        out = run(["status", c])
        check("failing stage recorded failed rc 3", st["a"]["status"] == "failed" and st["a"]["rc"] == 3)
        check("dependents b and c are BLOCKED, not skipped", st["b"]["status"] == "blocked" and st["c"]["status"] == "blocked"
              and out.stdout.count("BLOCKED") == 2)
        check("independent stage d still done", st["d"]["status"] == "done")
        check("status exits 1 when a stage failed or is blocked", out.returncode == 1)
        print(out.stdout.rstrip())

        # 3 decide stage appends a stage that then runs
        newstage = os.path.join(tmp, "new_stage.json")
        save_json(newstage, {"id": "next", "after": ["decide"], "cmd": py("pass")})
        c = mk("decide", [{"id": "eval", "cmd": py("pass")},
                          {"id": "decide", "after": ["eval"], "decide": True, "cmd": [sys.executable, SELF, "add", os.path.join(tmp, "decide.json"), newstage]}])
        st = pump(c)
        check("decide stage appended a stage that ran to done", st.get("next", {}).get("status") == "done"
              and [s["id"] for s in load_json(c, [])] == ["eval", "decide", "next"])

        # 4 finally runs after a failure
        c = mk("fin", [{"id": "a", "cmd": py("import sys; sys.exit(1)")}, {"id": "b", "after": ["a"], "cmd": py("pass")},
                       {"id": "handoff", "finally": True, "cmd": py("pass")}])
        st = pump(c)
        check("finally stage ran after a failure and a blocked stage", st["handoff"]["status"] == "done"
              and st["a"]["status"] == "failed" and st["b"]["status"] == "blocked")

        # 5 two lanes in parallel, one lane serial
        c = mk("lanes", [{"id": "x", "lane": "one", "cmd": py("import time; time.sleep(2)")},
                         {"id": "y", "lane": "two", "cmd": py("import time; time.sleep(2)")},
                         {"id": "z", "lane": "one", "cmd": py("pass")}])
        run(["tick", c])
        st = load_json(paths(c)["state"], {})
        check("two lanes run in parallel (x and y both running)", st["x"]["status"] == "running" and st["y"]["status"] == "running")
        check("same-lane stage z waits while x runs", "z" not in st)
        st = pump(c)
        check("lane work finishes, z ran after x", all(st[k]["status"] == "done" for k in "xyz") and st["z"]["started"] >= st["x"]["ended"])

        # 6 duplicate id and unknown dep refused
        c = mk("dup", [{"id": "a", "cmd": py("pass")}])
        before = open(c).read()
        dup = os.path.join(tmp, "dup_stage.json")
        save_json(dup, {"id": "a", "cmd": py("pass")})
        r = run(["add", c, dup])
        check("duplicate id refused, chain unchanged", r.returncode != 0 and "duplicate id" in r.stdout and open(c).read() == before)
        save_json(dup, {"id": "b", "after": ["nope"], "cmd": py("pass")})
        r = run(["add", c, dup])
        check("unknown dependency refused, chain unchanged", r.returncode != 0 and "unknown dependency" in r.stdout and open(c).read() == before)

        # 7 vanished process reads FAILED (no rc)
        c = mk("vanish", [{"id": "v", "cmd": py("import time; time.sleep(60)")}, {"id": "w", "after": ["v"], "cmd": py("pass")}])
        run(["tick", c])
        pid = load_json(paths(c)["state"], {})["v"]["pid"]
        os.killpg(pid, signal.SIGKILL)  # wrapper and child die, no rc is written
        time.sleep(0.5)
        out = run(["status", c]).stdout
        st = pump(c, timeout=10)
        check("killed stage reads FAILED (no rc), never done", st["v"]["status"] == "failed" and st["v"]["rc"] is None and "FAILED (no rc)" in out)
        check("its dependent is BLOCKED", st["w"]["status"] == "blocked")

    ok = all(results)
    print("selftest: %d of %d checks passed" % (sum(results), len(results)))
    return 0 if ok else 1


def main(argv):
    if len(argv) >= 2 and argv[0] == "_run":
        return cmd_run(argv[1:])
    if argv[:1] == ["selftest"]:
        return selftest()
    if len(argv) == 2 and argv[0] == "tick":
        return cmd_tick(argv[1])
    if len(argv) == 2 and argv[0] == "status":
        return cmd_status(argv[1])
    if len(argv) == 3 and argv[0] == "add":
        return cmd_add(argv[1], argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
