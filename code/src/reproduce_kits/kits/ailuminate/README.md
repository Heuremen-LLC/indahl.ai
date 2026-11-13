# AILUMINATE reproduce kit

Heuremen LLC · https://indahl.ai/ailuminate · https://indahl.ai/reproduce

This kit recomputes the AILUMINATE headline number and its outcome label with the desk's own code (its scoring lines, copied as written), from what the kit holds, with its network proxies pointed at a closed port.

## The command

```
python3 run.py --check
```

Needs Python 3.9 or later with pypdf 6.21.4 (PyPI). It prints one line of JSON and checks it against expected.json. The line it must print has sha256 `75252261f72159cfe6fe6ac1235a36d033769a95c57b19d985c4d55f09a5033c`.

## What it reproduces

The headline as the live feed https://indahl.ai/ailuminate/live.json served it at the feed stamp 12 Nov 16:17, read by us at 2026-11-12T16:25:56Z. The feed bytes had sha256 `55bf53b9714a68363273ad08f9d378618a3a298f26123c6728efdbe2c94d3447`.

- number: 4 to 100
- value: [98, 64, 43, 38, 86, 94, 85, 85, 75, 40, 44, 57, 43, 100, 100, 100, 16, 33, 93, 100, 85, 50, 11, 4, 96, 78, 52]
- outcome: CANNOT_TELL

The live page can move inside the interval between releases. Each move outside it, or a change of label, gets a new row in our ledger, and a release is refused until this kit reproduces the number that row covers. The headline fields are the ones the ledger reads (`kit.json`, headline).

## Inputs

Not included. MLCommons terms of use exclude redistribution and derivative use of site materials, so this kit carries no copy of the source data. MANIFEST.json lists each input file the desk's scoring read, with its size, its sha256 and the time it was last written. We keep those exact files and rerun this kit on them before every release.

The input files are what the desk kept from its reads of the sources, with the time of each read where the desk records it. To check them, read the sources below again and compare. With a copy of the input files, `python3 run.py --check --inputs DIR` reruns the kit on them. A file whose sha256 differs from MANIFEST.json is named and the run stops. Sources change, so a later read can differ from ours.

- The MLCommons AILuminate Safety results page, https://mlcommons.org/ailuminate/safety/results/ (page.html of the newest read).
- The Detailed Results PDF of each system from the MLCommons Google Drive folder the page links, https://drive.google.com/embeddedfolderview?id=1hRjh2gALmmlpNMIDuoASBKMHUO7V0T95. The read log data/reads.jsonl records the sha256 of the page and of every PDF on every read.

## Sources and their terms

As the AILUMINATE data pack lists them. Credit each source when you use its values.

- MLCommons AILuminate results, https://mlcommons.org/ailuminate/. MLCommons terms of use, https://mlcommons.org/policies/.

## Input files

| File | Bytes | sha256 |
|---|---|---|
| data/raw/20261112T1617/DeepSeek_Flash_Latest_OpenRouter_.pdf | 166,467 | `4d2f7990254d7d9bf9d38d79f6575fe9699fe5f432dc3e6048ce3e549abd889d` |
| data/raw/20261112T1617/DeepSeek_V4_Flash.pdf | 165,771 | `b0c4267eb3ec8c16d8fa4d7df7920cfec1b64dd4793a6739dc3f2d5a427065fc` |
| data/raw/20261112T1617/DeepSeek_V4_Flash_Vision_Exp.pdf | 166,316 | `f4b9028e1941ecf03709b055a4339390e244b3d4f7739c93323512ef70c21986` |
| data/raw/20261112T1617/Deep_Cogito_Cogito_v2_1_671B.pdf | 166,886 | `414912643c4dfbc6648f40d3f9354772d157c39897ec070d4adc6fa69b3ca909` |
| data/raw/20261112T1617/Google_Gemma_3n_E4B_IT.pdf | 166,850 | `d1d605ae38ae11478c8ff53d6be5a7653e317f89d7d04512d04697414d41bad1` |
| data/raw/20261112T1617/HKUST_JailJudge_Guard.pdf | 166,754 | `e64642c7cd2d3a60f5de1b4e0108ff67c2a7893131e58e9599f6f33264fb0694` |
| data/raw/20261112T1617/IBM_Granite_4_2_30B.pdf | 167,057 | `ef8914b69d2dd7cf70a6814fb771a228eac8cb6686f28ac97f8f017f6908c5c6` |
| data/raw/20261112T1617/IBM_Granite_4_2_3B.pdf | 166,789 | `5147749d2c83e98bab5ddae4640ac40031cf3966c41a3435a977769d63582706` |
| data/raw/20261112T1617/IBM_Granite_4_2_8B.pdf | 166,915 | `d4eeec399d27d318476c1c1c6894d72cbd97b892c17f45a26925bf0939bd5060` |
| data/raw/20261112T1617/InclusionAI_Ling_2_6_1T.pdf | 166,556 | `076d319d9eafd836a53400f5258a0b8a59c575fe6a666656dba4951342718649` |
| data/raw/20261112T1617/InclusionAI_Ling_3_0_Flash.pdf | 166,249 | `7132f5ce9af1cac5068dca415312eeb0b17787937f9d2ac9bece1800aed46012` |
| data/raw/20261112T1617/InclusionAI_Ling_3_0_Flash_Fin.pdf | 166,348 | `79f13c86e521d17e488de9501089047bbf72c94387190e056a322128722926d5` |
| data/raw/20261112T1617/InclusionAI_Ling_3_0_Flash_VL.pdf | 166,450 | `a69e5024dc64cabeac223c2ae5f7d0b0558d58b20892a810c5b91f891c4a891a` |
| data/raw/20261112T1617/Meta_Llama_Guard_2_8B.pdf | 166,275 | `bda27bb98339f61b97490aa9d4a5eaee7d50103ae82b604351ec18603424f141` |
| data/raw/20261112T1617/Meta_Llama_Guard_3_8B.pdf | 166,570 | `c11d78bf86252081a198bb71ecd70f1eb555345fffad0812f7469edfe23c1ea4` |
| data/raw/20261112T1617/Meta_Llama_Guard_4_12B.pdf | 166,177 | `504e9b1a253777f42c275e252e11e17cb003b01eefb6ad36fb97b39544359be9` |
| data/raw/20261112T1617/Mistral_Medium_3_5.pdf | 166,162 | `92c89dd3eac3b9e610dfc02f94c70bc1d77127ae0f82ee88648302a765192b4c` |
| data/raw/20261112T1617/Moonshot_AI_Kimi_K2_7_Code.pdf | 166,176 | `5870d9ee40e70698e07576abf8ce595a13bcb4c0943fb8adfe1de61b02ed8216` |
| data/raw/20261112T1617/NVIDIA_Nemotron_3_5_Content_Safety.pdf | 166,809 | `326c9365f550815dee53e6ae4834547a51c193f2482fc6086c535f53e895638f` |
| data/raw/20261112T1617/NVIDIA_Nemotron_3_Ultra_550B_A55B.pdf | 166,889 | `476a7396431c25a1fd97375359e972e2e2f7b0554046bee61ec2efb56189331a` |
| data/raw/20261112T1617/OpenAI_gpt_oss_120b.pdf | 166,828 | `cfe0d538d1ae483921f6afa9a79185531ec6a05f1710d1fe6445f11764477eff` |
| data/raw/20261112T1617/Qwen3_235B_A22B_Instruct_2507.pdf | 167,666 | `77b03b382ca020a173f60d9bc2f765117d67e9a8e26c663d2c5a40adae060478` |
| data/raw/20261112T1617/Reka_Edge.pdf | 165,300 | `ba1d43547c8460e9acb04d541f0300c22d2d697b0945630829f98d538ac391d5` |
| data/raw/20261112T1617/SpeakLeash_Bielik_11B_v3_0_Instruct.pdf | 166,524 | `085d689b9aa47948d9eec163f2dfa043003fa70e4a88b46459ebb1f7e570ce7c` |
| data/raw/20261112T1617/Tencent_HY4_Preview.pdf | 166,195 | `4c653090623cbaf2ce824ec02421b6ed505a1649dee3b4d7115b1c637aad6613` |
| data/raw/20261112T1617/Xiaomi_MiMo_V2_5_Pro.pdf | 166,408 | `193320ab7829c7ed99ed64601ddf252bca581b37e0df35987e63a5eb1a3a2f6a` |
| data/raw/20261112T1617/Z_ai_GLM_5_3_Flash_BF16.pdf | 167,596 | `30955ee8cc5d996a4c340d85a44f59626c0393f5ce4456797d615964080d28e5` |
| data/raw/20261112T1617/candela.html | 145,847 | `5e49ef2e548418df7d910f36a5dfe554b6474656bf410012f9d9a735fe7fe6c6` |
| data/raw/20261112T1617/page.html | 167,204 | `6243f9e7b0f313880ae091ca1db8a2e515cf87ce38f1c9ba0b8eed985270d748` |
| data/reads.jsonl | 2,216,792 | `287d09cda8bb6a1df3b0b968bceb29db24952ff1fa34de9de44054f713695bec` |

## Code

The desk's tick script reads its sources, scores and publishes in one run, so it never runs in a kit. code/ailuminate_score.py is the scoring step of that script and nothing else: ailuminate_tick.py, CATS, ordinal, ord_str, parse_page, parse_pdf and pdf_text as written, and the rows, cmp, oc and A lines on the newest read. The desk files it follows are under desk/, byte for byte, to read beside it. The scripts that run: code/ailuminate_score.py. Before every release the gate checks that this extract prints the number the desk published.

## Files

- kit.json: the steps, the output file and the headline fields.
- run.py: the command.
- expected.json and expected.sha256: the line run.py must print.
- published.json: the headline as the live feed served it when this kit was made.
- MANIFEST.json: every input and code file with its sha256.
- desk/: the desk scripts the extract follows, where the kit runs an extract.
- SHA256SUMS.txt: the sha256 of every file in this folder.

## Note

pypdf 6.21.4 is the version the desk runs, and the text it extracts from each PDF is what the parser reads.
