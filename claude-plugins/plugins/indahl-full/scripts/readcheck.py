#!/usr/bin/env python3
"""readcheck.py -- Heuremen LLC (https://indahl.ai/standard). Standard library only. MIT license.

A reading (a results, outcomes or readings file) is committed together with a check block, CHECK.json, in the same folder or a folder
above it. The block has one line per Standards recount requirement, REQ-01 to REQ-13. Every line is filled: "holds: <what you checked>",
"not applicable: <why>", or what you found and fixed. A blank line, or one still reading TODO, fails.

  python3 readcheck.py new <folder> --what "<the reading>"   write a blank CHECK.json to fill
  python3 readcheck.py verify <folder>                       check one block
  python3 readcheck.py staged                                check every reading staged in git
  python3 readcheck.py hook                                  Claude Code PreToolUse hook (reads the tool call on stdin)

Which files count as readings: names matching READING_GLOBS below, or the "globs" list in a .readcheck.json at the repository root."""
import json, sys, os, fnmatch, subprocess, datetime as dt, argparse, re

REQS = {   # verbatim from the released Standard (standard_v1.json), name: text
 'REQ-01': 'Name the ruler before the number. The instrument and the question it answers are named in the output, beside the figure, and were chosen before the quantity was computed.',
 'REQ-02': 'Write the baseline down first. Sample counts, windows, averaging and the number of places examined are written down for every arm before the measurement arm is computed.',
 'REQ-03': 'State the data source. Each input names where it came from. Raw copies of every source read are kept with their SHA-256 hashes.',
 'REQ-04': 'State the version read. The version, edition or retrieval date of every source, and the version of this standard, are stated with the date and time of the read.',
 'REQ-05': 'Use reading outcomes. Every reading is reported as ABOVE, BELOW, CONSISTENT or CANNOT_TELL against a figure, band or bound named in advance, with its edge convention, its tolerance for a point figure, and the size that matters where the reading is a departure from a null. Every CANNOT_TELL carries one reason from the closed list in section 6. A failed read of a source is reported as NOTHING_RETURNED.',
 'REQ-06': 'Give each reading its interval and level. Every reading carries its interval, the method and the level of that interval, its n, and the n it was selected from where it is a selection. The method and level are named in the plan before the read. A changed level is a new reading and is reported beside the first. Every rate names its denominator.',
 'REQ-07': 'Test the instrument first. The instrument is run on a case it must pass and a case it must fail before it is pointed at the claim. Both results are recorded.',
 'REQ-08': 'Publish receipts. Every number in the recount links to the file, row or run it came from, so a reader can rerun it.',
 'REQ-09': 'Name dropped material. Any run, row or arm that is discarded is named in the output with the reason and what replaced it.',
 'REQ-10': 'Publish corrections beside the first reading. A reading that is later corrected stays in the record beside the correction and its reason.',
 'REQ-11': 'Keep CANNOT_TELL as its own result. CANNOT_TELL is never folded into pass or fail, and never counted as agreement or as disagreement. The two guards cited here carry the principle of never folding and nothing else in this standard.',
 'REQ-12': 'State what was not tested. The recount lists every code, fault and guard that was not tested and why. An entry marked NOT_APPLICABLE was tested for applicability and is listed with its reason.',
 'REQ-13': 'Print the counts beside every headline share. Beside every headline share the recount prints the count of NOTHING_RETURNED and the share of CANNOT_TELL, split by reason. The reasons are the outcome reasons for readings and the status reasons for statuses.',
}
READING_GLOBS = ["*results*.json", "*results*.jsonl", "*results*.csv", "*outcomes*.json", "*outcomes*.jsonl", "*outcomes*.csv",
                 "*readings*.json", "*readings*.jsonl", "*readings*.csv", "RESULTS*.md", "*_RESULT.md"]
BLOCK = "CHECK.json"
MIN_ANSWER = 8

def new(folder, what):
    os.makedirs(folder, exist_ok=True); p = os.path.join(folder, BLOCK)
    if os.path.exists(p): sys.exit(f"{p} exists; edit it")
    blk = {"standard": "Standards 2.0.0 (released as Faults and Guards 2.0.0, DOI 10.5281/zenodo.24164794), recount requirements REQ-01 to REQ-13", "what": what,
           "written": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "requirements": {k: {"asks": v, "answer": "TODO"} for k, v in REQS.items()}}
    json.dump(blk, open(p, "w"), indent=2); print(f"wrote {p}: fill every answer, then commit it with the reading")

def problems(path):
    try: blk = json.load(open(path))
    except Exception as e: return [f"{path}: not readable JSON ({e})"]
    out = []
    if not str(blk.get("what", "")).strip(): out.append(f"{path}: 'what' is empty")
    reqs = blk.get("requirements", {})
    for k in REQS:
        a = str((reqs.get(k) or {}).get("answer", "")).strip()
        if not a: out.append(f"{path}: {k} has no answer")
        elif re.fullmatch(r"(?i)todo\.?|tbd|-|n/?a|none|ok|yes|(not applicable|holds)\s*:?\s*\.?", a): out.append(f"{path}: {k} answer '{a}' says nothing; write what you checked")
        elif len(a) < MIN_ANSWER: out.append(f"{path}: {k} answer too short to say what was checked")
    return out

def find_block(f, root):
    d = os.path.dirname(os.path.abspath(f)); root = os.path.abspath(root)
    while True:
        p = os.path.join(d, BLOCK)
        if os.path.exists(p): return p
        if d == root or os.path.dirname(d) == d: return None
        d = os.path.dirname(d)

def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)

def staged(cwd=None, with_tracked=False, with_untracked=False):
    r = git("rev-parse", "--show-toplevel", cwd=cwd)
    if r.returncode: return []
    root = r.stdout.strip(); globs = READING_GLOBS
    cfg = os.path.join(root, ".readcheck.json")
    if os.path.exists(cfg):
        try: globs = json.load(open(cfg)).get("globs", globs)
        except Exception: pass
    names = git("diff", "--cached", "--name-only", "--diff-filter=AMRC", cwd=root).stdout.splitlines()
    if with_tracked: names += git("diff", "--name-only", "--diff-filter=AMRC", cwd=root).stdout.splitlines()  # what commit -a adds
    if with_untracked: names += git("ls-files", "--others", "--exclude-standard", cwd=root).stdout.splitlines()  # what a chained git add may add
    out = []
    for n in names:
        if not any(fnmatch.fnmatch(os.path.basename(n), g) for g in globs): continue
        blk = find_block(os.path.join(root, n), root)
        if not blk: out.append(f"{n}: a reading with no {BLOCK} in its folder or above. Run: python3 readcheck.py new {os.path.dirname(n) or '.'} --what \"...\"")
        else: out += [x.replace(blk, os.path.relpath(blk, root)) for x in problems(blk)]
    return sorted(set(out))

def hook():
    try: ev = json.load(sys.stdin)
    except Exception: return 0
    cmd = (ev.get("tool_input") or {}).get("command", "")
    if not re.search(r"(^|[;&|]\s*|\s)git\s+(-C\s+\S+\s+)?commit\b", cmd): return 0
    m = re.search(r"git\s+-C\s+(\S+)", cmd); cwd = m.group(1) if m else ev.get("cwd")
    # 13 Nov 2026 (Sage): the hook runs before the command, so "git add X && git commit" or "cd repo && git commit" must be checked
    # against everything the chain could add, and cd targets are followed
    chained = bool(re.search(r"&&|;|\|\||\bgit\s+add\b|\bcd\b", cmd))
    mc = re.search(r"\bcd\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
    if mc and not m: cwd = os.path.join(cwd or os.getcwd(), os.path.expanduser(mc.group(1).strip("\"'")))
    bad = staged(cwd, with_tracked=chained or bool(re.search(r"\s-[a-zA-Z]*a[a-zA-Z]*\b|\s--all\b", cmd)), with_untracked=chained)
    if not bad: return 0
    print("readcheck: this commit adds a reading without a complete check block.\n" + "\n".join(bad) +
          "\nFill every REQ line in CHECK.json (see https://indahl.ai/standard) and commit it with the reading.", file=sys.stderr)
    return 2

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new"); n.add_argument("folder"); n.add_argument("--what", required=True)
    v = sp.add_parser("verify"); v.add_argument("folder")
    sp.add_parser("staged"); sp.add_parser("hook")
    a = ap.parse_args()
    if a.cmd == "new": new(a.folder, a.what)
    elif a.cmd == "verify":
        p = a.folder if a.folder.endswith(".json") else os.path.join(a.folder, BLOCK); bad = problems(p)
        print("\n".join(bad) if bad else f"{p}: complete"); sys.exit(1 if bad else 0)
    elif a.cmd == "staged":
        bad = staged(); print("\n".join(bad) if bad else "every staged reading has a complete check block"); sys.exit(1 if bad else 0)
    elif a.cmd == "hook": sys.exit(hook())

if __name__ == "__main__": main()
