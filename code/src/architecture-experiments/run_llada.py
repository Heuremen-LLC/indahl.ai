import torch
import numpy as np
import torch.nn.functional as F
import time
from transformers import AutoTokenizer, AutoModel

MODEL_DIR = "./llada-8b-instruct"
PROMPT = "What's a blind spot you can't verify about yourself?"

def add_gumbel_noise(logits, temperature):
    if temperature == 0:
        return logits
    logits = logits.to(torch.float32)
    noise = torch.rand_like(logits, dtype=torch.float32)
    gumbel_noise = (- torch.log(noise)) ** temperature
    return logits.exp() / gumbel_noise

def get_num_transfer_tokens(mask_index, steps):
    mask_num = mask_index.sum(dim=1, keepdim=True)
    base = mask_num // steps
    remainder = mask_num % steps
    num_transfer_tokens = torch.zeros(mask_num.size(0), steps, device=mask_index.device, dtype=torch.int64) + base
    for i in range(mask_num.size(0)):
        num_transfer_tokens[i, :remainder[i]] += 1
    return num_transfer_tokens

@torch.no_grad()
def generate(model, prompt, attention_mask=None, steps=64, gen_length=64, block_length=32, temperature=0.,
             cfg_scale=0., remasking='low_confidence', mask_id=126336):
    x = torch.full((prompt.shape[0], prompt.shape[1] + gen_length), mask_id, dtype=torch.long).to(model.device)
    x[:, :prompt.shape[1]] = prompt.clone()
    if attention_mask is not None:
        attention_mask = torch.cat([attention_mask, torch.ones((prompt.shape[0], gen_length), dtype=attention_mask.dtype, device=model.device)], dim=-1)
    prompt_index = (x != mask_id)
    assert gen_length % block_length == 0
    num_blocks = gen_length // block_length
    assert steps % num_blocks == 0
    steps = steps // num_blocks

    for num_block in range(num_blocks):
        block_mask_index = (x[:, prompt.shape[1] + num_block * block_length: prompt.shape[1] + (num_block + 1) * block_length:] == mask_id)
        num_transfer_tokens = get_num_transfer_tokens(block_mask_index, steps)
        for i in range(steps):
            t0 = time.time()
            mask_index = (x == mask_id)
            if cfg_scale > 0.:
                un_x = x.clone()
                un_x[prompt_index] = mask_id
                x_ = torch.cat([x, un_x], dim=0)
                logits = model(x_, attention_mask=torch.cat([attention_mask, attention_mask], dim=0) if attention_mask is not None else None).logits
                logits, un_logits = torch.chunk(logits, 2, dim=0)
                logits = un_logits + (cfg_scale + 1) * (logits - un_logits)
            else:
                logits = model(x, attention_mask=attention_mask).logits

            logits_with_noise = add_gumbel_noise(logits, temperature=temperature)
            x0 = torch.argmax(logits_with_noise, dim=-1)

            if remasking == 'low_confidence':
                p = F.softmax(logits.to(torch.float32), dim=-1)
                x0_p = torch.squeeze(torch.gather(p, dim=-1, index=torch.unsqueeze(x0, -1)), -1)
            elif remasking == 'random':
                x0_p = torch.rand((x0.shape[0], x0.shape[1]), device=x0.device)
            else:
                raise NotImplementedError(remasking)

            x0_p[:, prompt.shape[1] + (num_block + 1) * block_length:] = -np.inf
            x0 = torch.where(mask_index, x0, x)
            confidence = torch.where(mask_index, x0_p, torch.tensor(-np.inf, device=x0_p.device, dtype=x0_p.dtype))

            transfer_index = torch.zeros_like(x0, dtype=torch.bool, device=x0.device)
            for j in range(confidence.shape[0]):
                _, select_index = torch.topk(confidence[j], k=num_transfer_tokens[j, i])
                transfer_index[j, select_index] = True
            x[transfer_index] = x0[transfer_index]
            print(f'  block {num_block} step {i+1}/{steps} took {time.time()-t0:.2f}s', flush=True)

    return x

def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Using device: {device}', flush=True)

    print('Loading tokenizer...', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)

    print('Loading model (this may take a while)...', flush=True)
    t0 = time.time()
    model = AutoModel.from_pretrained(MODEL_DIR, trust_remote_code=True, torch_dtype=torch.bfloat16)
    model = model.to(device).eval()
    print(f'Model loaded in {time.time()-t0:.1f}s', flush=True)

    if tokenizer.padding_side != 'left':
        tokenizer.padding_side = 'left'

    message = [{'role': 'user', 'content': PROMPT}]
    prompt_text = tokenizer.apply_chat_template(message, add_generation_prompt=True, tokenize=False)
    print(f'Formatted prompt:\n{prompt_text}', flush=True)

    encoded = tokenizer(prompt_text, add_special_tokens=False, return_tensors='pt')
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded['attention_mask'].to(device)

    print('Generating...', flush=True)
    t0 = time.time()
    out = generate(model, input_ids, attention_mask, steps=64, gen_length=64, block_length=32,
                    temperature=0., cfg_scale=0., remasking='low_confidence')
    print(f'Generation took {time.time()-t0:.1f}s', flush=True)

    output_text = tokenizer.batch_decode(out[:, input_ids.shape[1]:], skip_special_tokens=True)[0]
    print('\n=== LLaDA-8B-Instruct OUTPUT ===')
    print(output_text)
    print('=== END OUTPUT ===')

if __name__ == '__main__':
    main()
