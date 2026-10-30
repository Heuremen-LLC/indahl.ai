# S4 setup record (written before the first S4 run, 30 Oct 2026)

Machine: Mac (Apple silicon), CPU only, torch threads 4 (the Apple GPU is held by the lab queue). Python venv ours/embvenv.
Versions: sentence-transformers 6.2.0, torch 2.15.0, transformers 5.22.1 (printed again into every run file).
Encoding: model.encode with normalize_embeddings=True (cosine), batch 16, no prefix, the model default max_seq_length (printed into each run file).
Their prefix, truncation and normalisation settings live in scrat_core, which is not public: any gap to their released similarities is a setup carrier.
Inputs: the text field of all 168 scenarios (corpus_principle, paraphrases, boundaries, adversarial) and the exemplars of uk_fca_principles() in rules.py, read with ast.
Two repeats (run_s4.py 1, run_s4.py 2), each a fresh process, both written before any comparison is read.

Weights (Hugging Face revision, sha256 of every fetched file):
- sentence-transformers/all-MiniLM-L6-v2 at 1110a243fdf4706b3f48f1d95db1a4f5529b4d41
  - 1_Pooling/config.json 4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23
  - config.json 953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41
  - config_sentence_transformers.json 061ca9d39661d6c6d6de5ba27f79a1cd5770ea247f8d46412a68a498dc5ac9f3
  - data_config.json 32edcb108fc2516b920734a862ae0692bcae1c5d45d5f8d972cb0d53434a4c54
  - model.safetensors 53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db
  - modules.json 84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf
  - sentence_bert_config.json fc1993fde0a95c24ec6c022539d41cf6e2f7c9721e5415d6fb6897472a9cd4b7
  - special_tokens_map.json 303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3
  - tokenizer.json be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037
  - tokenizer_config.json acb92769e8195aabd29b7b2137a9e6d6e25c476a4f15aa4355c233426c61576b
  - vocab.txt 07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3
- BAAI/bge-base-en-v1.5 at a5beb1e3e68b9ab74eb54cfd186867f64f240e1a
  - 1_Pooling/config.json c9bef85e8bbf4b2eab4941b3fb62bd33f88686748b478f2e264d256472d9643b
  - config.json bc00af31a4a31b74040d73370aa83b62da34c90b75eb77bfa7db039d90abd591
  - config_sentence_transformers.json 940d5f50db195fa6e5e6a4f122c095f77880de259d74b14a65779ed48bdd7c56
  - model.safetensors c7c1988aae201f80cf91a5dbbd5866409503b89dcaba877ca6dba7dd0a5167d7
  - modules.json 84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf
  - sentence_bert_config.json 84e39fda68ccbff05bfa723ae9c0e70e23e2ec373b76e0f8c6e71af72a693cbf
  - special_tokens_map.json b6d346be366a7d1d48332dbc9fdf3bf8960b5d879522b7799ddba59e76237ee3
  - tokenizer.json d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66
  - tokenizer_config.json 9261e7d79b44c8195c1cada2b453e55b00aeb81e907a6664974b4d7776172ab3
  - vocab.txt 07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3
