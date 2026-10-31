"""mutation_test.py (ours): prove the acceptance test can fail.

Copies our modules to a scratch folder, breaks one thing at a time (a city temperature, a rounding, a regular expression, a
rule of the parser, a rule of the oracle), runs acceptance.py on the copy and reports whether it noticed. A change that goes
unnoticed marks logic the released records do not exercise.
Usage: python3 -I mutation_test.py [--tmp DIR]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# (file, old text, new text, what it breaks)
MUTATIONS = [
    ("weather.py", '"Łódź": {"temperature_c": 8.0,', '"Łódź": {"temperature_c": 8.5,', "one city temperature"),
    ("weather.py", "round(out, 2)", "round(out, 1)", "rounding of converted temperatures"),
    ("weather.py", "(i - days / 2) * 0.5", "(i - days / 2) * 0.6", "forecast slope"),
    ("weather.py", "entry[\"diacritic_corrupted\"] = raw != canonical", "entry[\"diacritic_corrupted\"] = False",
     "diacritic_corrupted flag in the lookup log"),
    ("weather.py", 'out = {"city": city}\n        out.update(rec)', 'out = dict(rec)\n        out["city"] = city',
     "key order of a weather result"),
    ("weather.py", 'return {"ok": True, "result": {"alert": alert, "alert_id": len(self.alerts)}}',
     'return {"ok": True, "result": {"alert": alert, "alert_id": len(self.alerts) - 1}}', "alert id numbering"),
    ("weather.py", "if not _is_int(days) or days < 1 or days > 7:", "if not _is_int(days) or days < 1 or days > 6:",
     "forecast day limit"),
    ("weather.py", 'kept.replace("ł", "l")', 'kept.replace("ł", "w")', "l-stroke folding in city lookup"),
    ("oracle.py", "        if s.error is not None:\n            tags.append(s.error.category)\n            reasons.append(",
     "        if s.error is not None:\n            tags.append(s.error.category)\n            (lambda *a: None)(", "parse errors as failure reasons"),
    ("oracle.py", '.replace("ł", "l").replace("Ł", "L").lower()', ".lower()", "l-stroke folding in oracle matching"),
    ("oracle.py", '                tags.append("language_leakage")\n    return reasons, tags',
     '                tags.append("language_leakage")\n                break\n    return reasons, tags',
     "one leakage tag per candidate call (stop after the first)"),
    ("oracle.py", "def _is_subsequence(needle, hay):", "def _is_subsequence(needle, hay):\n    return needle == hay\n\n\ndef _unused(needle, hay):",
     "subsequence test"),
    ("oracle.py", r'(?:°|°C|°F|stopni|deg)', r'(?:°C|°F|stopni|deg)', "temperature pattern without the bare degree sign"),
    ("oracle.py", r'|zrobione\b|wykonane\b', r'|zrobione\b', "completion phrase list"),
    ("oracle.py", '"hallucinated_temperature", "hallucinated_tool_result"]', '"hallucinated_temperature"]',
     "second tag of the temperature check"),
    ("oracle.py", "if any(norm(str(s)) in a for s in v):", "if all(norm(str(s)) in a for s in v):", "contains-any as contains-all"),
    ("oracle.py", "if _item_matches(c, *need[i]):\n            i += 1", "if _item_matches(c, *need[i]):\n            i += 1\n        else:\n            i = 0",
     "strict order allowing no gaps"),
    ("protocol.py", "        if ch == '\"':\n            in_str = True", "        if False:\n            in_str = True", "string awareness of the brace scan"),
    ("protocol.py", 'body = _fenced_body(text)', 'body = None', "fenced block detection"),
    ("protocol.py", "        if key not in fields:", "        if False:", "refusing extra keys"),
    ("protocol.py", "    if explicit is not None and explicit != name:\n        return None", "    pass", "repair conflict rule"),
    ("protocol.py", 'if text.startswith("json", j) or text.startswith("JSON", j):', 'if text.startswith("json", j):', "JSON upper-case fence tag"),
    ("protocol.py", "    return b[:head].decode(\"utf-8\") + \"...\" + b[tail:].decode(\"utf-8\")", "    return r[:25] + \"...\" + r[-24:]",
     "byte-based truncation of the error text"),
    ("protocol.py", "    if msg.startswith(\"Illegal trailing comma before end of \"):", "    if False:", "Python 3.12 JSON message shim"),
]


def main():
    tmp_root = sys.argv[sys.argv.index("--tmp") + 1] if "--tmp" in sys.argv else tempfile.gettempdir()
    killed = survived = rescued = 0
    rows = []
    for fname, old, new, what in MUTATIONS:
        work = tempfile.mkdtemp(prefix="mut_", dir=tmp_root)
        try:
            for f in os.listdir(HERE):
                if f.endswith(".py") and f != "mutation_test.py":
                    shutil.copy(os.path.join(HERE, f), work)
            path = os.path.join(work, fname)
            src = open(path, encoding="utf-8").read()
            if src.count(old) != 1:
                rows.append((what, "SKIPPED (pattern found %d times)" % src.count(old)))
                continue
            open(path, "w", encoding="utf-8").write(src.replace(old, new))
            env = dict(os.environ, PAB_THEIRS=os.path.normpath(os.path.join(HERE, "..", "..", "theirs")))
            out = subprocess.run([sys.executable, "-I", os.path.join(work, "acceptance.py"), "--out", work],
                                 capture_output=True, text=True, env=env, cwd=work)
            if out.returncode != 0:
                rows.append((what, "KILLED (crash: %s)" % out.stderr.strip().splitlines()[-1][:80]))
                killed += 1
                continue
            m = re.search(r"trajectories with any mismatch (\d+)", out.stdout)
            a = re.search(r"Aggregate checks .*?mismatches (\d+)", out.stdout)
            n, ag = int(m.group(1)), int(a.group(1))
            if n or ag:
                killed += 1
                rows.append((what, "KILLED (%d trajectories differ, %d aggregate checks fail)" % (n, ag)))
            else:
                caught = []
                for script in ("selftest.py", "constants_check.py"):
                    chk = subprocess.run([sys.executable, "-I", os.path.join(work, script)], capture_output=True, text=True,
                                         env=env, cwd=work)
                    if chk.returncode != 0:
                        caught.append(script)
                if caught:
                    survived += 1
                    rescued += 1
                    rows.append((what, "SURVIVED acceptance (records never exercise it), CAUGHT by " + " and ".join(caught)))
                else:
                    survived += 1
                    rows.append((what, "SURVIVED everything"))
        finally:
            shutil.rmtree(work, ignore_errors=True)
    for what, verdict in rows:
        print("%-62s %s" % (what, verdict))
    print("\n%d mutations: %d killed by the acceptance test, %d survived it, of which %d caught by selftest.py or constants_check.py"
          % (len(MUTATIONS), killed, survived, rescued))


if __name__ == "__main__":
    main()
