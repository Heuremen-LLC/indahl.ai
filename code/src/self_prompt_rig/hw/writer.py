
import json, os, sys, time
mode, path = sys.argv[1], sys.argv[2]; blob = {"memory": ["x" * 3000 for _ in range(1000)]}
while True:
    s = json.dumps(blob)
    def slow(fp):   # chunked writes with fsync, so a kill can land INSIDE a write (a real save is one write; this widens its window)
        with open(fp, "w") as f:
            for i in range(0, len(s), 65536): f.write(s[i:i+65536]); f.flush(); os.fsync(f.fileno())
    if mode == "bare": slow(path)
    else: slow(path + ".tmp"); os.replace(path + ".tmp", path)
