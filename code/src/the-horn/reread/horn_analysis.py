#!/usr/bin/env python3
"""Horn re-read: segment power_4080.csv and sweep files by the field timeline.
Light, single-process. Run on the laptop only.
"""
import csv, math, statistics, glob, os, json

BASE = "/home/ctrai/horn/20260928_091702"

# Field-note anchors, EDT -> UTC unix epoch offsets (EDT = UTC-4)
def edt_to_unix(hh, mm, ss):
    import datetime
    d = datetime.datetime(2026, 9, 28, hh, mm, ss, tzinfo=datetime.timezone.utc)
    return d.timestamp() + 4*3600  # shift EDT wall-clock to UTC instant

ANCHORS = {
    "rec_start":   edt_to_unix(9, 17, 6),
    "site_start":  edt_to_unix(10, 57, 30),
    "antenna_up":  edt_to_unix(11, 11, 25),
    "under_horn":  edt_to_unix(11, 17, 17),
    "yodel":       edt_to_unix(11, 23, 15),
    "tower_photo": edt_to_unix(11, 24, 17),
    "constr_photo":edt_to_unix(11, 27, 2),
    "rec_stop":    edt_to_unix(12, 0, 49),
}

# Coarse three (home/car/site) PLUS the three site sub-conditions Wayfinder
# flagged as separate objects: rain+umbrella, dry+uncovered+outside-fence,
# under-horn+inside-fence (wet throughout after the rain), post-horn observation.
SEGMENTS = [
    ("HOME",                    ANCHORS["rec_start"],  edt_to_unix(10,37,0)),
    ("CAR_GUESS",                edt_to_unix(10,37,0),  ANCHORS["site_start"]),
    ("SITE_RAIN_UMBRELLA",       ANCHORS["site_start"], ANCHORS["antenna_up"]),
    ("SITE_DRY_UNCOVERED_OUTFENCE", ANCHORS["antenna_up"], ANCHORS["under_horn"]),
    ("UNDER_HORN_INFENCE",       ANCHORS["under_horn"], ANCHORS["tower_photo"]),
    ("POST_HORN_OBSERVATION",    ANCHORS["tower_photo"], ANCHORS["rec_stop"]),
]

def load_power():
    rows = []
    with open(os.path.join(BASE, "power_4080.csv")) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append((float(row["unix_time"]), float(row["db_4070_4090"]), float(row["db_4000_4160"])))
    return rows

def seg_stats(rows, t0, t1):
    narrow = [n for (t,n,w) in rows if t0 <= t < t1]
    wide   = [w for (t,n,w) in rows if t0 <= t < t1]
    if not narrow:
        return None
    def stats(x):
        return dict(n=len(x), mean=round(statistics.mean(x),3),
                    median=round(statistics.median(x),3),
                    stdev=round(statistics.pstdev(x),3) if len(x)>1 else 0.0,
                    min=round(min(x),3), max=round(max(x),3))
    return dict(narrow=stats(narrow), wide=stats(wide), t0=t0, t1=t1, dur_s=round(t1-t0,1))

def find_4080_bin(sweep_path):
    """Return dB of the 4080-4081 MHz bin (index 4 of the 4076-4081 row)."""
    with open(sweep_path) as f:
        r = csv.reader(f)
        for row in r:
            row = [c.strip() for c in row]
            lo, hi = float(row[2]), float(row[3])
            if lo <= 4080e6 < hi:
                vals = [float(x) for x in row[6:]]
                # 5 bins of 1MHz spanning lo..hi; bin containing 4080-4081 is index 4 here (4076..4081)
                return vals[-1], vals  # last bin = 4080-4081
    return None, None

def wideband_snapshot(sweep_path):
    """Return dict freq_mhz(int) -> dB, using each row's max bin (coarse 5MHz granularity is fine for presence/absence)."""
    out = {}
    with open(sweep_path) as f:
        r = csv.reader(f)
        for row in r:
            row = [c.strip() for c in row]
            lo = float(row[2]); bin_w = float(row[4])
            vals = [float(x) for x in row[6:]]
            for i, v in enumerate(vals):
                fmhz = int((lo + i*bin_w) / 1e6)
                out[fmhz] = v
    return out

def main():
    rows = load_power()
    print(f"Loaded {len(rows)} power rows, span {rows[0][0]:.1f} to {rows[-1][0]:.1f} ({rows[-1][0]-rows[0][0]:.0f}s)")

    print("\n=== SEGMENT STATS (power_4080.csv) ===")
    results = {}
    for name, t0, t1 in SEGMENTS:
        s = seg_stats(rows, t0, t1)
        results[name] = s
        if s:
            gap = s['narrow']['mean'] - s['wide']['mean']
            print(f"{name:28s} dur={s['dur_s']:7.1f}s n={s['narrow']['n']:5d} "
                  f"narrow(4070-4090) mean={s['narrow']['mean']:7.3f} median={s['narrow']['median']:7.3f} sd={s['narrow']['stdev']:6.3f} "
                  f"| wide(4000-4160) mean={s['wide']['mean']:7.3f} median={s['wide']['median']:7.3f} sd={s['wide']['stdev']:6.3f} "
                  f"| narrow-wide gap={gap:6.3f}")

    with open("/tmp/horn_segment_stats.json", "w") as f:
        json.dump(results, f, indent=2)

    # Fine timeline: 30s bins across full run, to see continuous trace + flips
    print("\n=== 30s-BINNED TRACE (narrowband mean) around site arrival through teardown ===")
    t_start = ANCHORS["site_start"] - 120
    t_end = ANCHORS["rec_stop"]
    binsize = 30
    nbins = int((t_end - t_start)//binsize) + 1
    sums = [0.0]*nbins; cnts=[0]*nbins
    for t,n,w in rows:
        if t_start <= t < t_end:
            idx = int((t-t_start)//binsize)
            sums[idx]+=n; cnts[idx]+=1
    trace = []
    for i in range(nbins):
        if cnts[i]:
            tmid = t_start + i*binsize + binsize/2
            trace.append((tmid, sums[i]/cnts[i], cnts[i]))
    for tmid, mean, cnt in trace:
        import datetime
        edt = datetime.datetime.fromtimestamp(tmid, tz=datetime.timezone.utc) - datetime.timedelta(hours=4)
        print(f"{edt.strftime('%H:%M:%S')} EDT  mean={mean:7.3f} dB  n={cnt}")

    with open("/tmp/horn_trace_30s.json","w") as f:
        json.dump(trace, f, indent=2)

    # Sky/ground flip search: look for ~60s period step changes after antenna_up
    print("\n=== FLIP CHECK: 10s bins from antenna_up to under_horn end ===")
    t0f, t1f = ANCHORS["antenna_up"]-30, ANCHORS["tower_photo"]
    bs = 10
    nb = int((t1f-t0f)//bs)+1
    s2=[0.0]*nb; c2=[0]*nb
    for t,n,w in rows:
        if t0f<=t<t1f:
            idx=int((t-t0f)//bs); s2[idx]+=n; c2[idx]+=1
    flip_trace=[]
    for i in range(nb):
        if c2[i]:
            tmid=t0f+i*bs+bs/2
            flip_trace.append((tmid, s2[i]/c2[i]))
    import datetime
    for tmid, mean in flip_trace:
        edt = datetime.datetime.fromtimestamp(tmid, tz=datetime.timezone.utc) - datetime.timedelta(hours=4)
        print(f"{edt.strftime('%H:%M:%S')} EDT  mean={mean:7.3f} dB")
    with open("/tmp/horn_flip_10s.json","w") as f:
        json.dump(flip_trace, f, indent=2)

    # Reverberation check: autocorrelation of residuals in SITE_TEARDOWN segment
    print("\n=== AUTOCORRELATION (teardown segment, lag 1..60 samples ~ lag*0.33s) ===")
    seg = [n for (t,n,w) in rows if ANCHORS["tower_photo"]<=t<ANCHORS["rec_stop"]]
    if len(seg) > 120:
        m = statistics.mean(seg)
        resid = [x-m for x in seg]
        var = sum(r*r for r in resid)/len(resid)
        acs = []
        for lag in range(1, 61):
            num = sum(resid[i]*resid[i+lag] for i in range(len(resid)-lag))
            denom = (len(resid)-lag)*var
            ac = num/denom if denom else 0
            acs.append(ac)
        peak_lag = max(range(len(acs)), key=lambda i: acs[i])+1
        print(f"n={len(seg)} peak autocorr={acs[peak_lag-1]:.3f} at lag={peak_lag} (~{peak_lag*0.33:.1f}s)")
        print("first 10 lags:", [round(a,3) for a in acs[:10]])
        with open("/tmp/horn_autocorr.json","w") as f:
            json.dump(acs, f, indent=2)

    # Comb-line heartbeat across the 17 sweep files
    print("\n=== 20 MHz COMB LINE (4080-4081 MHz bin) ACROSS 17 SWEEPS ===")
    sweep_files = sorted(glob.glob(os.path.join(BASE, "sweep_*.csv")))
    combs = []
    for sp in sweep_files:
        stamp = os.path.basename(sp).replace("sweep_","").replace(".csv","")
        val, allvals = find_4080_bin(sp)
        combs.append((stamp, val))
        print(f"{stamp}  4080-4081MHz bin = {val}")
    with open("/tmp/horn_comb_by_sweep.json","w") as f:
        json.dump(combs, f, indent=2)

    # Wideband absence check: compare a home sweep vs a horn sweep
    print("\n=== WIDEBAND PRESENCE/ABSENCE: home (091706) vs horn (111814) ===")
    home_snap = wideband_snapshot(os.path.join(BASE, "sweep_091706.csv"))
    horn_snap = wideband_snapshot(os.path.join(BASE, "sweep_111814.csv"))
    # crude noise floor per snapshot = median
    home_floor = statistics.median(home_snap.values())
    horn_floor = statistics.median(horn_snap.values())
    print(f"home median floor={home_floor:.2f} dB, horn median floor={horn_floor:.2f} dB, diff={home_floor-horn_floor:.2f} dB")
    THRESH = 10.0
    present_home_absent_horn = []
    present_horn_absent_home = []
    for fmhz in sorted(set(home_snap) & set(horn_snap)):
        h = home_snap[fmhz]; k = horn_snap[fmhz]
        if h - home_floor > THRESH and k - horn_floor < THRESH/2:
            present_home_absent_horn.append((fmhz, round(h,1), round(k,1)))
        if k - horn_floor > THRESH and h - home_floor < THRESH/2:
            present_horn_absent_home.append((fmhz, round(h,1), round(k,1)))
    print(f"Bins clearly above floor at home but not at horn ({THRESH}dB thresh): {len(present_home_absent_horn)}")
    for x in present_home_absent_horn[:40]:
        print("  ", x)
    print(f"Bins clearly above floor at horn but not at home: {len(present_horn_absent_home)}")
    for x in present_horn_absent_home[:40]:
        print("  ", x)
    with open("/tmp/horn_wideband_diff.json","w") as f:
        json.dump(dict(home_floor=home_floor, horn_floor=horn_floor,
                        present_home_absent_horn=present_home_absent_horn,
                        present_horn_absent_home=present_horn_absent_home), f, indent=2)

if __name__ == "__main__":
    main()
