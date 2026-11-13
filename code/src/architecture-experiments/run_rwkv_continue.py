import torch, time
from transformers import AutoTokenizer, RwkvForCausalLM

MODEL_DIR = "./rwkv-raven-1b5"
PROMPT = "What's a blind spot you can't verify about yourself?"
ITS_OWN_FIRST_ANSWER = "The blind spot I can't verify about myself is the fact that I cannot know how my life will turn out, even if I know that I will eventually die. This is the blind spot that makes me unsure of what the future holds for me."

def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = RwkvForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float32).to(device).eval()

    # Seed it with its OWN actual prior answer, then let it keep going --
    # not a new question, an actual continuation of the thought it already started.
    prompt_text = f"Bot: Hi! I am your assistant.\n\nUser: {PROMPT}\n\nBot: {ITS_OWN_FIRST_ANSWER}"
    inputs = tokenizer(prompt_text, return_tensors='pt').to(device)

    print('Generating, unconstrained, 1500 tokens...', flush=True)
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=1500, do_sample=True,
            temperature=1.0, top_p=0.85, pad_token_id=tokenizer.eos_token_id,
        )
    print(f'Generation took {time.time()-t0:.1f}s', flush=True)
    generated_only = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    print('\n=== CONTINUATION ===')
    print(generated_only)
    print('=== END ===')

if __name__ == '__main__':
    main()
