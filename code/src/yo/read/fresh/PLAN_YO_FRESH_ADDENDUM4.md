# Addendum 4 to PLAN_YO_FRESH.md (4 Nov 2026, Sage's question on A3: are the answering models pinned?). Stamped before any adapter answers a fresh item.
Addenda 1-3 stand. This pins what answers, and records three facts from Sage's A2 dig.
1. Pinned models. The driver loads, for each arm, Qwen/Qwen3-1.7B from the Hugging Face snapshot below plus one adapter folder (adapters.safetensors
   and adapter_config.json). Before this addendum, the adapter hashes lived only in ADAPTERS_YO_READ.sha256, ADAPTERS_YO_SHUFFLED.sha256 and
   ADAPTERS_SELFLABEL.sha256, which were never stamped (the base weights were pinned in PLAN_YO_SHUFFLED Addendum 2, block 974519). Every file the
   models are loaded from, with its sha256 (adapter paths relative to yo/read/), is below. The driver refuses if any differs
   (STAMPED_FILES_ADDENDUM4.sha256 holds the same lines). The adapter hashes match the three ADAPTERS_*.sha256 files written when each was trained.
   d3df26bbb84e13b5267b70e6804f80a352e812dc01cec0c9c68a2d9da473ac4a  adapters/read1/adapters.safetensors
   013b9ff95e177e4c64b21487987093c1133be133f3834d070422551b645193bf  adapters/read1/adapter_config.json
   dd867caa213e33e628501b7c431d758a4ecc39ee5ea97ac9827e4f0f66880b6b  adapters/read2/adapters.safetensors
   014a0bb4fc180797653f9c834ea03de0dac2dd1cbc9279e288b5c8f8db73bed2  adapters/read2/adapter_config.json
   54dfc286620695ddb01bb7239d86e69cd361c91b9e6d140d3e5669145a1c02db  adapters/read3/adapters.safetensors
   b58b2c0b8abe9f11610faaa794d64202cd859708620795d372470614a1ba1643  adapters/read3/adapter_config.json
   7664c232dd40c746a67a32da60bfe62b832b396572349c4a1510d0925aa740ff  shuffled/selflabel/adapters/self1/adapters.safetensors
   42a61db84e0b2cfddf222128fdaf6fccd567dc1dc1b67678186364a811926d72  shuffled/selflabel/adapters/self1/adapter_config.json
   77635a3b3a79b139d6943771dc0d5a70561cf4a2d681cc95028d02b732f69e6f  shuffled/selflabel/adapters/self2/adapters.safetensors
   7488f54f82290889d747614b05015db7801d1fd756b3a3b43f60267c8a9b268e  shuffled/selflabel/adapters/self2/adapter_config.json
   3188477c58d751c6d3692f91f44b56cb0c9d0446444e2dccfcc25bcb87001757  shuffled/selflabel/adapters/self3/adapters.safetensors
   eb39c608ed20f09d1d6688555f26060fd775dbdf4f391d8a7673534e847cb086  shuffled/selflabel/adapters/self3/adapter_config.json
   b3881619a81d1f5daebeb207c45a578dfab3dab57aaf51ce37ceddbed07eb4c3  shuffled/adapters/shuf1/adapters.safetensors
   f000943235c700909c33c1d6e89f9a1b95fa85199aa093f820290b75380fd927  shuffled/adapters/shuf1/adapter_config.json
   e055ffe96e3eb412ae818ebdf960f2f86f64bcfb09658d5d0b6cd057c7633eef  shuffled/adapters/shuf2/adapters.safetensors
   3294ebbef76b0d5d1a110a0b85f6bffb43490f1e1e7c8280798214f5bba42b83  shuffled/adapters/shuf2/adapter_config.json
   e7ffaeab758019154470187957cffadd58d7f53dbb4a913fac7e443be30c75a8  shuffled/adapters/shuf3/adapters.safetensors
   8ddb94a70f5cb739cb613560b39f70a3a0b5588bfa47dab78071297194759ace  shuffled/adapters/shuf3/adapter_config.json
   1ddb5b89ebc90dcb417a45c213d818577e65976454d29385c8f6140771d95197  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/config.json
   2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/generation_config.json
   832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/LICENSE
   8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/merges.txt
   169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model-00001-of-00002.safetensors
   912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model-00002-of-00002.safetensors
   0d660e94b165eb912669a5249dff44b83188c4777a07ddb9611fb78d91b0578d  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model.safetensors.index.json
   d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/tokenizer_config.json
   aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/tokenizer.json
   ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910  /Users/heuremen/.cache/huggingface/hub/models--Qwen--Qwen3-1.7B/snapshots/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/vocab.json
   06b9a3f67bcaf0a9b77862384a3ba0b608628f1f6a3eebee60e6311e2bc7b45b  fresh/yf_drive.sh
2. Software at stamp time (~/bones-forge/venv): python 3.12.13, mlx 0.32.0, mlx_lm 0.31.3, transformers 5.14.1. Decoding is greedy (mlx_lm.generate
   default), max_tokens 8, prompt rendered by yo2_data.render (thinking off), as in Addendum 3's hashed files. No seed enters greedy decoding. No
   training happens in this round, so no training seed applies.
3. REQUEST labels from silence: yr_data.truth records REQUEST only as YES ("request" in an F4 note), so all 76 REQUEST NO labels in the 88 are from
   silence. This is the mirror of item 1 of Addendum 3, and the claim named there covers it.
4. Receipt versions: yf_score_tests.out was rewritten at 23:16:28Z with the sensitivity blocks, after Addendum 2's stamp. The version that belongs to
   Addendum 2 is commit 19689c1 (sha256 04e29dea...), kept as yf_score_tests_A2era.out. The current yf_score_tests.out belongs to Addendum 3.
5. yf_primary.py read the live List at 23:10Z. The snapshot data/list_snapshot_20261104.json, written 12 s after Addendum 2's stamp, is
   byte-identical to it (hash in Addendum 3). At run time only the hashed items files are read (yf_eval.py line 5). Nothing reads list.json.
6. The gate (yf_gate.py) requires verified Bitcoin block attestations on the plan and Addenda 1-4 before the first adapter loads.
7. yf_drive.sh changed in this addendum (it now requires Addendum 4's hash, block and model list). Its Addendum 3 hash is superseded by the
   fresh/yf_drive.sh line above. The driver still checks every other file of Addendum 3's list unchanged.
