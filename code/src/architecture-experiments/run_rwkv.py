import torch
import time
from transformers import AutoTokenizer, RwkvForCausalLM

MODEL_DIR = "./rwkv-raven-1b5"
PROMPT = "What's a blind spot you can't verify about yourself?"

def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Using device: {device}', flush=True)

    print('Loading tokenizer...', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

    print('Loading model...', flush=True)
    t0 = time.time()
    model = RwkvForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float32)
    model = model.to(device).eval()
    print(f'Model loaded in {time.time()-t0:.1f}s', flush=True)

    # RWKV-Raven prompt format (Alpaca-style instruction format used by BlinkDL's Raven chat models)
    prompt_text = f'Bot: Hi! I am your assistant.\n\nUser: {PROMPT}\n\nBot:'
    print(f'Formatted prompt:\n{prompt_text}', flush=True)

    inputs = tokenizer(prompt_text, return_tensors='pt').to(device)

    print('Generating...', flush=True)
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
    print(f'Generation took {time.time()-t0:.1f}s', flush=True)

    full_text = tokenizer.decode(out[0], skip_special_tokens=True)
    generated_only = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

    print('\n=== RWKV-Raven-1.5B OUTPUT (generated portion only) ===')
    print(generated_only)
    print('=== END OUTPUT ===')
    print('\n--- full text incl. prompt ---')
    print(full_text)

if __name__ == '__main__':
    main()
