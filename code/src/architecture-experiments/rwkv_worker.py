"""
2026-08-12: worker wrapper around the 8/7 cross-architecture-triangulation
run_rwkv.py -- same model, same proven generation params, parameterized via
stdin JSON instead of a hardcoded PROMPT so it's callable as a tool.
"""
import sys, json, torch
from transformers import AutoTokenizer, RwkvForCausalLM

MODEL_DIR = "./rwkv-raven-1b5"

def main():
    args = json.loads(sys.stdin.read())
    prompt = args["prompt"]
    system = args.get("system", "")

    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = RwkvForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float32)
    model = model.to(device).eval()

    # RWKV-Raven prompt format (Alpaca-style, per BlinkDL's chat convention)
    intro = f"{system}\n\n" if system else ""
    prompt_text = f'{intro}Bot: Hi! I am your assistant.\n\nUser: {prompt}\n\nBot:'

    inputs = tokenizer(prompt_text, return_tensors='pt').to(device)
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
    sys.stdout.write(generated_only.strip())

if __name__ == '__main__':
    main()
