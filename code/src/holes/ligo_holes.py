#!/usr/bin/env python3
"""LIGO/Virgo/KAGRA holes from GWOSC public segment lists. Read-only, no account.

Holes per detector per run:
  data-off   = run span minus {det}_DATA   (no public strain / not in science mode)
  cat1-veto  = {det}_DATA minus {det}_CBC_CAT1   (GWOSC CBC_CAT1 flag marks times that PASS CAT1)
Raw segment JSON cached in cache/gwosc/<dataset>/<flag>.json. Writes ligo_holes.jsonl (rewritten each run,
deterministic) and ligo_coverage.json (run spans per detector, UTC).
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "gwosc")
OUT = os.path.join(HERE, "ligo_holes.jsonl")
COV = os.path.join(HERE, "ligo_coverage.json")

# run -> (dataset, gps_start, gps_end, detectors); spans from gwosc.org/api/v2/runs
RUNS = {
    "O3a":  ("O3a_4KHZ_R1",  1238166018, 1253977218, ["H1", "L1", "V1"]),
    "O3b":  ("O3b_4KHZ_R1",  1256655618, 1269363618, ["H1", "L1", "V1"]),
    "O3GK": ("O3GK_4KHZ_R1", 1270281618, 1271462418, ["K1"]),
    "O4a":  ("O4a_16KHZ_R1", 1368195220, 1389456018, ["H1", "L1"]),
    "O4b":  ("O4b_16KHZ_R1", 1396417050, 1422118818, ["H1", "L1", "V1"]),
}
GPS_EPOCH = datetime(1980, 1, 6, tzinfo=timezone.utc)


def gps_to_utc(g):
    # leap-second offset GPS-UTC is 18 s for every date since 2017-01-01 (all runs here)
    return GPS_EPOCH + timedelta(seconds=g - 18)


def iso(g):
    return gps_to_utc(g).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(dataset, flag, s, e):
    d = os.path.join(CACHE, dataset)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, flag + ".json")
    if os.path.exists(p):
        return json.load(open(p))["segments"]
    url = f"https://gwosc.org/timeline/segments/json/{dataset}/{flag}/{s}/{e - s}/"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = json.load(r)
            break
        except Exception as ex:
            print("retry", url, ex, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit("failed " + url)
    json.dump(data, open(p, "w"))
    time.sleep(1)
    return data["segments"]


def complement(segs, s, e):
    out, cur = [], s
    for a, b in sorted(segs):
        if a > cur:
            out.append((cur, min(a, e)))
        cur = max(cur, b)
    if cur < e:
        out.append((cur, e))
    return [(a, b) for a, b in out if b > a]


def intersect(A, B):
    out, i, j = [], 0, 0
    A, B = sorted(A), sorted(B)
    while i < len(A) and j < len(B):
        a, b = max(A[i][0], B[j][0]), min(A[i][1], B[j][1])
        if b > a:
            out.append((a, b))
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return out


def main():
    recs, cov = [], {}
    for run, (ds, s, e, dets) in RUNS.items():
        for det in dets:
            data = fetch(ds, f"{det}_DATA", s, e)
            cat1 = fetch(ds, f"{det}_CBC_CAT1", s, e)
            off = complement(data, s, e)
            veto = intersect(data, complement(cat1, s, e))
            cov.setdefault(det, []).append({"run": run, "at": iso(s), "ended": iso(e), "gps": [s, e]})
            for kind, segs, status in (("data-off", off, "NO_DATA"), ("cat1-veto", veto, "CAT1_VETO")):
                for a, b in segs:
                    recs.append({
                        "id": f"gwosc:{run}:{det}:{kind}:{a}",
                        "provider": "gwosc", "device": det, "status": status,
                        "at": iso(a), "ended": iso(b), "shots": None,
                        "reason": f"{run} {ds}: {b - a} s {'outside ' + det + '_DATA' if kind == 'data-off' else 'in DATA but failing CBC_CAT1'} (GPS {a}-{b})",
                        "kind": kind,
                    })
            print(f"{run} {det}: {len(data)} DATA segs, {len(off)} data-off, {len(veto)} cat1-veto, "
                  f"duty {sum(b - a for a, b in data) / (e - s):.3f}")
    recs.sort(key=lambda r: (r["at"], r["id"]))
    with open(OUT, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    json.dump(cov, open(COV, "w"), indent=1)
    print(len(recs), "holes ->", OUT)


if __name__ == "__main__":
    main()
