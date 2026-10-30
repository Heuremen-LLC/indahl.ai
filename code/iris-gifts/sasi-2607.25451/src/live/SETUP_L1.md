# L1 setup record (written before the first L1 run, 31 Oct 2026 UTC)

Machine: Mac (Apple silicon), CPU only, torch threads 4, FP32 (the Apple GPU is held by the lab queue).
Python venv: iris_index/gifts/2608.14329/ours/embvenv (torch 2.15.0, transformers 5.22.1; printed again into every run file).
Items: his sampled_<model>_n500_s0.npy files (Hugging Face dataset AkshaySasi/bits-and-memories at aa3db05dbe45), read with numpy allow_pickle=False.
Generate call as his extract.py: prompt = first 32 ids, greedy, max_new_tokens 32, num_beams 1, attention_mask all ones, pad_token_id 0, batch 32.
Two repeats (run_l1.py 1, run_l1.py 2), each a fresh process, both written before any comparison is read.

Weights (Hugging Face revision, sha256 of every fetched file):
- EleutherAI/pythia-160m-deduped at 582159a2dfe3e712a8d47ae83dec95ae3bde8e7e
  - config.json 76eb275107220e450d31258f792a2efcbee109d8b62ae0088260057dec06362f
  - model.safetensors bbaae5c00917b163baa499fc8eb64859ee0c850c5fdecfc32f4d70dc07213575
  - special_tokens_map.json 6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad
  - tokenizer.json c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624
  - tokenizer_config.json 70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f
- EleutherAI/pythia-410m-deduped at c4fc8d586d62df497f1f9b69d66d3ca419992d3e
  - config.json d4c11e84a59c8af4d88446bba53b718f7aef740daa070ded08fd6a9a3aca4fc6
  - model.safetensors e7ae132489f63d5d86009a8178a75c7d5d195410d067fca01a3160623e370fae
  - special_tokens_map.json 6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad
  - tokenizer.json c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624
  - tokenizer_config.json 70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f
- EleutherAI/pythia-1b-deduped at 7199d8fc61a6d565cd1f3c62bf11525b563e13b2
  - config.json 302d6702a29de1039066e41404877fb8c53b7ddc82e88f9aba277f230086cfe0
  - model.safetensors fdb3f09a4a4d30678e021247e71f5b160bdd147de2aedd2d7d25e01feecc8e13
  - special_tokens_map.json 6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad
  - tokenizer.json c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624
  - tokenizer_config.json 70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f
