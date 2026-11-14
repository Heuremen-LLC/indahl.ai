#!/usr/bin/env python3
"""watch_guard.py: a Claude Code PreToolUse hook that refuses a background watch which can only report success.

Claude Code lets the agent wait on work in two ways: a Bash command run in the background (run_in_background) whose exit is reported
as "completed (exit code 0)", and the Monitor tool, whose stdout lines become notifications. Both report what the WAIT did, not what
the JOB did. The common silent failures this hook refuses before the watch starts:

  1. SUCCESS-ONLY WAIT. `until grep -q "DONE" job.log; do sleep 5; done`. If the job crashes, "DONE" never appears, the loop never
     exits, and the agent hears nothing: silence reads as "still running". The pattern must also match the failure states.
  2. SUCCESS-ONLY STREAM. `tail -f job.log | grep "DONE"` in a Monitor: a crash, a traceback or a refusal produces no event.
  3. BUFFERED STREAM. `tail -f x | grep pattern` without --line-buffered: matches sit in grep's buffer and never arrive.
  4. EXIT CODE AS VERDICT. A wait that ends with exit 0 says the wait condition matched. If the matched line can itself say the job
     failed (e.g. "DONE ... rc 1"), the loop exits 0 either way; the agent must read the line, not the exit code. (Reported as advice.)
  5. SELF-MATCHING PGREP (14 Nov). `until ! pgrep -f "ship.sh"; do ...` never ends: the shell running the wait has "ship.sh" in its
     own command line, so pgrep -f always finds it. Wait on the PID (`while kill -0 PID`) or bracket one letter ("[s]hip.sh").
  6. PADDED COUNT (14 Nov). `[ "$(wc -l < f)" = "2" ]` never matches on macOS: wc pads its count with spaces. Compare numbers (-eq).
  7. NO DEADLINE (14 Nov). A background until/while loop with no deadline waits forever when its condition can never come true,
     and nothing distinguishes it from a healthy wait. Every background wait needs one (SECONDS, a counter, or timeout).

Reads the hook JSON on stdin. Exit 0 = allow. Exit 2 with a message on stderr = refuse (Claude Code shows the message to the model).
Standard library only. Nothing leaves the machine. Heuremen LLC, https://indahl.ai. MIT."""
import json, re, sys

FAIL = re.compile(r'fail|error|err\b|traceback|exception|refus|denied|killed|abort|panic|fatal|timeout|timed out|oom|exit|rc\s*\[?1|'
                  r'rc\s*\[?\^?0|non-?zero|crash|stopped|cancel|not found|unreachable|stale', re.I)

def patterns(cmd):
    """The search patterns a watch waits on: arguments of grep/rg/egrep and of [[ ... =~ ... ]] tests."""
    pats = []
    for m in re.finditer(r'\b(?:grep|egrep|rg|fgrep)\b((?:\s+-{1,2}[\w-]+(?:=\S+)?)*)\s+(?:-e\s+)?("([^"]*)"|\'([^\']*)\'|(\S+))', cmd):
        pats.append(m.group(3) if m.group(3) is not None else (m.group(4) if m.group(4) is not None else m.group(5)))
    pats += re.findall(r'=~\s*"?([^"\]]+)', cmd)
    return [p for p in pats if p]

def check(tool, inp):
    cmd = inp.get('command') or ''
    # 14 Nov: judge the shell, not the text it carries. Heredoc bodies (<<'EOF' ... EOF) are data, and prose inside them tripped the checks.
    cmd = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", '<<HEREDOC', cmd, flags=re.S)
    background = tool == 'Monitor' or (tool == 'Bash' and inp.get('run_in_background'))
    if not background or not cmd: return None
    waits = re.search(r'\buntil\b|\bwhile\b', cmd) is not None
    streams = re.search(r'tail\s+-[a-zA-Z]*f|tail\s+--follow|inotifywait\s+-m|journalctl\s+-f|\bwatch\b', cmd) is not None
    if not (waits or streams): return None
    if waits and tool == 'Bash':
        for m in re.finditer(r'pgrep\s+(?:-\w+\s+)*-\w*f\w*\s+(?:-\w+\s+)*("([^"]*)"|\'([^\']*)\'|(\S+))', cmd):
            pat = m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))
            try: hit = re.search(pat, cmd) is not None
            except re.error: hit = pat in cmd
            if hit:
                return ('SELF-MATCHING PGREP: pgrep -f ' + repr(pat) + ' also matches the shell running this wait, because its command line '
                        'contains the same text, so the loop can never end. Wait on the PID instead (while kill -0 PID; do ...) or bracket '
                        'one letter so the pattern no longer matches itself, e.g. "[' + pat[:1] + ']' + pat[1:] + '".')
        if re.search(r'"\$\(\s*wc\s+-[lcw]\b[^)]*\)"\s*!?=\s*"?\d', cmd):
            return ('PADDED COUNT: this wait compares the output of wc as a string. macOS wc pads its count with spaces ("       2"), so '
                    'the string never equals the number and the loop never ends. Compare numbers: [ "$(wc -l < f)" -eq 2 ].')
        if not re.search(r'\bSECONDS\b|\btimeout\b|\bgtimeout\b|deadline|\$\(\(|\(\(|-l[te]\s+\$?\w|-g[te]\s+\$?\w|\bdate\s+\+%s', cmd):
            return ('NO DEADLINE: this background wait has no deadline. If its condition can never come true (a crashed job, a pattern '
                    'that matches itself, a typo in a path) it waits forever and looks exactly like a healthy wait. Add one, for example '
                    'start the loop with `end=$((SECONDS+1800)); until COND || [ $SECONDS -ge $end ]; do sleep 10; done` and print '
                    'TIMED_OUT when it expires, or wrap the job itself in timeout.')
    pats = patterns(cmd)
    if not pats: return None
    if streams and '|' in cmd and re.search(r'\|\s*(grep|egrep)\b', cmd) and '--line-buffered' not in cmd:
        return ('BUFFERED STREAM: this watch pipes a follow (tail -f or similar) into grep without --line-buffered, so matches can sit in '
                "grep's buffer and never arrive. Add --line-buffered to every grep in the pipe.")
    if not any(FAIL.search(p) for p in pats):
        return ('SUCCESS-ONLY WATCH: every pattern this watch waits on (' + ', '.join(repr(p) for p in pats[:4]) + ') matches only the '
                'good outcome. If the job crashes, is refused or hangs, the watch stays silent and silence reads as "still running". '
                'Add the failure states to the same pattern, for example "DONE|FAIL|ERROR|Traceback|rc [1-9]|Killed", and give the wait a '
                'deadline. When it fires, read the matched line: the wait exiting 0 says the pattern matched, not that the job succeeded.')
    return None

def main():
    try: ev = json.load(sys.stdin)
    except Exception: return 0   # not a hook payload; never block on our own parse failure
    msg = check(ev.get('tool_name', ''), ev.get('tool_input') or {})
    if msg:
        print('silent-failure-guard: ' + msg, file=sys.stderr); return 2
    return 0

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        cases = [('Bash', {'command': 'until grep -q "DONE" job.log; do sleep 5; done', 'run_in_background': True}, True),
                 ('Bash', {'command': 'end=$((SECONDS+900)); until grep -qE "DONE|FAIL|rc [1-9]" job.log || [ $SECONDS -ge $end ]; do sleep 5; done', 'run_in_background': True}, False),
                 ('Bash', {'command': 'until grep -qE "DONE|FAIL|rc [1-9]" job.log; do sleep 5; done', 'run_in_background': True}, True),   # no deadline
                 ('Monitor', {'command': 'tail -f run.log | grep --line-buffered "elapsed_steps="'}, True),
                 ('Monitor', {'command': 'tail -f run.log | grep -E --line-buffered "elapsed_steps=|Traceback|Error|Killed"'}, False),
                 ('Monitor', {'command': 'tail -f run.log | grep -E "Traceback|Error"'}, True),
                 ('Bash', {'command': 'until grep -q "DONE" job.log; do sleep 5; done'}, False),   # foreground: not a watch this hook judges
                 ('Bash', {'command': 'python3 train.py', 'run_in_background': True}, False),     # the job itself, not a wait on it
                 ('Bash', {'command': "until ! pgrep -f ship.sh >/dev/null; do sleep 10; done; tail -4 ship.log", 'run_in_background': True}, True),   # 13 Nov: hung all night
                 ('Bash', {'command': 'end=$((SECONDS+900)); while kill -0 4242 2>/dev/null && [ $SECONDS -lt $end ]; do sleep 10; done; tail -4 ship.log', 'run_in_background': True}, False),
                 ('Bash', {'command': 'end=$((SECONDS+900)); until ! pgrep -f "[s]hip.sh" >/dev/null || [ $SECONDS -ge $end ]; do sleep 10; done', 'run_in_background': True}, False),
                 ('Bash', {'command': 'end=$((SECONDS+900)); until [ "$(wc -l < released.txt)" = "2" ] || [ $SECONDS -ge $end ]; do sleep 10; done', 'run_in_background': True}, True),   # 13 Nov: hung all night
                 ('Bash', {'command': 'until [ -s crawl.out ]; do sleep 15; done; cat crawl.out', 'run_in_background': True}, True),   # no deadline
                 ('Bash', {'command': "{ cat <<'EOF'\nwe wait until the twin reads, while Sage checks\nEOF\n} > m.md; python3 send.py m.md; grep -E 'VERDICT|STANDS' out.txt", 'run_in_background': True}, False),   # 14 Nov: prose in a heredoc is not a wait
                 ('Bash', {'command': "cat <<EOF > x\nhi\nEOF\nuntil grep -q DONE j.log; do sleep 5; done", 'run_in_background': True}, True)]   # a real wait after a heredoc is still judged
        bad = 0
        for t, i, want in cases:
            got = check(t, i) is not None
            print(('PASS ' if got == want else 'FAIL ') + t + ': ' + i['command'][:70] + ('  -> refused' if got else '  -> allowed'))
            bad += got != want
        print('selftest: %d cases, %d failed' % (len(cases), bad)); sys.exit(1 if bad else 0)
    sys.exit(main())
