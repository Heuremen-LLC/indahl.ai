"""Read-only: public Hugging Face model metadata for the four open-weight repos named in the released files.
Prints repo id, gated flag, license tag, current main sha, size of safetensors files, and the newest main commit at or before 2026-04-16T10:38:59Z
(time of the last change to the authors' dataset). usage: python3 -I model_revisions.py"""
import json, urllib.request
CUT = "2026-04-16T10:38:59"
REPOS = ["Qwen/Qwen2.5-7B-Instruct","mistralai/Mistral-7B-Instruct-v0.3","microsoft/Phi-3.5-mini-instruct","Qwen/Qwen2.5-1.5B-Instruct"]
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"gift-recount-scout"}), timeout=60) as r:
        return json.load(r)
for rp in REPOS:
    print("==", rp)
    try:
        m = get(f"https://huggingface.co/api/models/{rp}?blobs=true")
        lic = [t for t in m.get("tags",[]) if t.startswith("license:")]
        sizes = {s["rfilename"]: s.get("size") for s in m.get("siblings",[]) if s["rfilename"].endswith((".safetensors",".bin"))}
        print(" gated:", m.get("gated"), "| license:", lic, "| current main sha:", m.get("sha"), "| lastModified:", m.get("lastModified"))
        print(" weight files total GB: %.2f" % (sum(v or 0 for v in sizes.values())/1e9), "| n files", len(sizes))
    except Exception as e:
        print(" metadata error:", repr(e))
    try:
        c = get(f"https://huggingface.co/api/models/{rp}/commits/main")
        before = [x for x in c if x["date"][:19] <= CUT]
        print(" commits listed:", len(c), "| newest overall:", c[0]["id"][:12], c[0]["date"])
        if before: print(" newest at or before cut:", before[0]["id"], before[0]["date"], "|", before[0]["title"][:70])
        else: print(" no listed commit at or before cut (list may be truncated); oldest listed:", c[-1]["id"][:12], c[-1]["date"])
    except Exception as e:
        print(" commits error:", repr(e))
