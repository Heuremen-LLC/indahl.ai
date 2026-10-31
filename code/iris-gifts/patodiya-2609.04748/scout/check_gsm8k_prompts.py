# usage: python3 -I check_gsm8k_prompts.py gsm8k_rows_dir bridge_raw.jsonl.gz [summary.json]
# Known-good for the live arm: renders the GSM8K bridge prompt for items 0-499 with the Qwen2.5 chat template (system + user + assistant header, as in the
# GGUF's embedded template) and the system text printed in harness/run_gsm8k.py, and compares sha256 with prompt_sha256 in the authors' log.
# Also compares the gold answer (text after '####') with the gold in the authors' summary.json.
import sys, os, json, glob, gzip, hashlib, re
rows_dir, raw = sys.argv[1], sys.argv[2]
summ = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
SYSTEM = ("You are a helpful assistant. Solve the math problem step by step and "
          "end your response with the final answer on its own line in the form "
          "#### <number>")
items = {}
for f in sorted(glob.glob(os.path.join(rows_dir, "rows_*.json"))):
    for r in json.load(open(f))["rows"]:
        items[r["row_idx"]] = r["row"]
def render(q):
    return "<|im_start|>system\n" + SYSTEM + "<|im_end|>\n<|im_start|>user\n" + q + "<|im_end|>\n<|im_start|>assistant\n"
logged = {}
with gzip.open(raw, "rt") as fh:
    for l in fh:
        r = json.loads(l); logged.setdefault(r["item_idx"], set()).add(r["prompt_sha256"])
ok = bad = 0; multi = 0; first_bad = None
for i in sorted(logged):
    h = hashlib.sha256(render(items[i]["question"]).encode()).hexdigest()
    if len(logged[i]) > 1: multi += 1
    if h in logged[i] and len(logged[i]) == 1: ok += 1
    else:
        bad += 1; first_bad = first_bad if first_bad is not None else i
print("items logged", len(logged), "| prompt sha256 equal to our rendering:", ok, "| not equal:", bad, "| items with more than one hash:", multi, "| first mismatch:", first_bad)
if summ:
    g_ok = sum(1 for s in summ if re.findall(r"####\s*([\-\d,\.]+)", items[s["item_idx"]]["answer"])[-1].replace(",", "").rstrip(".") == s["gold"])
    print("gold in summary.json equals the dataset answer after '####':", g_ok, "of", len(summ))
