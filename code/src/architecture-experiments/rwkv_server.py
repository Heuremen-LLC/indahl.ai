"""
2026-08-12: persistent server version of rwkv_worker.py -- same fix as
llada_server.py, same reason. Load once, serve forever.
"""
import sys, json, torch, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from transformers import AutoTokenizer, RwkvForCausalLM

MODEL_DIR = "./rwkv-raven-1b5"
PORT = 8093

print("Loading RWKV-Raven-1.5B tokenizer + model (one time)...", flush=True)
_t0 = time.time()
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = RwkvForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float32)
model = model.to(device).eval()
print(f"RWKV-Raven-1.5B loaded in {time.time()-_t0:.1f}s, ready on :{PORT}", flush=True)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        if self.path != '/generate':
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get('Content-Length', 0))
        try:
            args = json.loads(self.rfile.read(length))
            prompt = args["prompt"]
            system = args.get("system", "")

            intro = f"{system}\n\n" if system else ""
            prompt_text = f'{intro}Bot: Hi! I am your assistant.\n\nUser: {prompt}\n\nBot:'

            inputs = tokenizer(prompt_text, return_tensors='pt').to(device)
            t0 = time.time()
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=1.0,
                    top_p=0.85,
                    pad_token_id=tokenizer.eos_token_id,
                )
            generated_only = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            print(f"  generated in {time.time()-t0:.1f}s: {generated_only[:80]}", flush=True)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": generated_only.strip()}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    server.serve_forever()
