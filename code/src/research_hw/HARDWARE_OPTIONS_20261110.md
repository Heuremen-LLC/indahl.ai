# Hardware options for local training and inference, $7-8k (hard max $10k)

Researched 10 Nov 2026 from live pages. Every price carries its source URL and the date the source gives. Lines marked ESTIMATE are our arithmetic with the working shown. Vendor compute figures are marked "vendor" or "derived" (derived = vendor sparse FP4 figure halved per step, which is how third-party sheets get dense numbers).

Companion note: /Users/heuremen/bones-forge/research_hw/MUSE_GLIMMER_20261110.md. Muse Glimmer is a 29.6B dense model. Q4 is about 18 GB to run, FP8 about 35 GB, BF16 about 62 GB, QLoRA about 23 GB at seq 1024 and 26-36 GB at 4-8K. So every option below that has 48 GB or more runs it and QLoRA-tunes it. One correction to that note: the 128 GB DGX Spark list price went from $4,699 to $6,950 on 2 Oct 2026 (sources below).

## 0. The market in one paragraph

The 2026 memory shortage has broken the old price ladder. The RTX PRO 6000 Blackwell that launched at about $8,565 now lists at $16,000 on NVIDIA's marketplace, $16,399 at Newegg and $19,999 at B&H, and the cheapest used one on eBay is $15,450. The RTX 5090 (MSRP $1,999) sells for $5,100 to $9,400. Two 5090s cost $10k to $19k. Used A100 80GB starts near $11k and used H100 PCIe near $30-36k. So the three headline cards in the brief are out of budget today. What is in budget: GB10 boxes (DGX Spark and OEM twins, $5,449 to $6,950), used 48 GB pro cards (RTX A6000 about $4,250-5,100), Strix Halo 128 GB boxes (about $3,450-3,500), a Mac Studio M5 Ultra 96 GB ($5,499), and cloud hours.

## 1. Prices (every row: URL and date)

| Item | Price | Source and date |
|---|---|---|
| RTX PRO 6000 Blackwell Workstation, new | $16,000 NVIDIA marketplace; from $16,399 Newegg; $19,999 B&H | https://www.thundercompute.com/blog/nvidia-rtx-pro-6000-pricing (updated 9 Nov 2026) |
| RTX PRO 6000, used | $15,450 eBay best; $17,690 Amazon | https://gpudojo.com/ (as of 2026-11-09 21:56 UTC) |
| RTX PRO 6000 Max-Q | No US retail found. EU from €13,699; tracker lowest average $21,789 (Sep) | https://gpupoet.com/gpu/learn/price/september-2026/nvidia-rtx-pro-6000-blackwell-max-q (Sep 2026); https://www.hardwaredealz.com/hardware/gpu/nvidia-96gb-gddr7-4x-dp-retail/preisvergleich.28234 (undated) |
| RTX PRO 6000 Server Edition | No retail price found (sold in OEM servers). Rents at $1.69-5.50/GPU-h | thundercompute link above (9 Nov 2026) |
| RTX PRO 6000 launch price, for reference | $8,565 | https://www.tomshardware.com/pc-components/gpus/nvidia-rtx-pro-6000-blackwell-gpu-is-listed-for-usd8-565-at-us-retailer-26-percent-more-expensive-than-the-last-gen-rtx-6000-ada (Mar 2025) |
| NVIDIA DGX Spark 128 GB, 4 TB | $6,950 list (raised 2 Oct 2026). 64 GB model from $4,999 via OEMs from 23 Oct | https://www.implicator.ai/nvidia-adds-64gb-dgx-spark-at-4-999-as-128gb-model-climbs-to-6-950/ (Oct 2026); https://openclawdc.com/blog/dgx-spark-price-every-gb10-box/ (13 Sep, updated 1 Nov 2026) |
| NVIDIA/PNY DGX Spark at Newegg | $5,399.99 in stock (before the 2 Oct rise) | openclawdc link (13 Sep 2026) |
| NVIDIA two-pack | $13,599 | openclawdc link (13 Sep 2026) |
| ASUS Ascent GX10, 1 TB | $5,999 ASUS US store, in stock | openclawdc link (26 Oct 2026) |
| ASUS Ascent GX10, 4 TB | $7,999 Newegg | openclawdc link (13 Sep 2026) |
| GIGABYTE AI TOP ATOM, 4 TB | $5,999.99 Newegg, in stock | openclawdc link (13 Sep 2026) |
| HP ZGX G1n, 2 TB | $5,449 Newegg, in stock | openclawdc link (13 Sep 2026) |
| HP ZGX Nano G1n, 2 TB | $5,699.99 Newegg | openclawdc link (13 Sep 2026) |
| Dell Pro Max with GB10, 4 TB | $8,224.39 dell.com | openclawdc link (13 Sep 2026) |
| Lenovo ThinkStation PGX | $5,849.99 (1 TB) / $7,299.99 (4 TB), out of stock | openclawdc link (13 Sep 2026) |
| MSI EdgeXpert, 4 TB | $6,822.71 Newegg | openclawdc link (13 Sep 2026) |
| Acer Veriton GN100, 2 TB | $5,942.02 Newegg | openclawdc link (13 Sep 2026) |
| RTX 5090 32 GB | FE $1,999 list, out of stock. Walmart GIGABYTE AORUS $3,340 (one-day listing). Market $6,500-9,400 | https://tech-insider.org/nvidia-rtx-50-prices-rise-november-2026-rtx-5090-3340/ (3 Nov 2026, prices of 2 Nov) |
| RTX 5090, tracker | $5,100 used eBay best, $7,000 Amazon | https://gpudojo.com/ (2026-11-09) |
| RTX 5090, tracker | eBay 3-lowest average $5,915; deals from $6,029 | https://gpupoet.com/gpu/learn/price/november-2026/nvidia-geforce-rtx-5090 (Nov 2026) |
| RTX 6000 Ada 48 GB | eBay 3-lowest average $10,714-10,721; 6-month typical $7,384 | https://gpupoet.com/gpu/learn/card/nvidia-rtx-6000-ada-generation (undated, spec audit 2 Sep 2026) |
| RTX A6000 48 GB (Ampere), used | $4,250 eBay, $4,480 Amazon. eBay median ask $5,087, middle half $4,477-5,180 | https://gpudojo.com/a6000 (9-10 Nov 2026) |
| A100 80 GB, used | $10,999 eBay best, $21,999 Amazon | https://gpudojo.com/ (2026-11-09) |
| H100 PCIe 80 GB | $35,999 eBay (30 Oct), $29,500 Newegg (9 Oct) | https://gpudojo.com/h100-pcie (30 Oct 2026) |
| AMD Instinct MI210 64 GB, used | $4,299 eBay | https://gpudojo.com/mi210 (10 Nov 2026) |
| AMD Radeon AI PRO R9700 32 GB | Launch $1,299; EU low €1,519 | https://gpuprix.com/eu/gpus/radeon-ai-pro-r9700 (mid-2026, no Nov data) |
| Strix Halo 128 GB: GMKtec EVO-X2 | $3,499.99 | https://openclawdc.com/blog/ryzen-ai-max-395-alternative-local-llm/ (listing dated 1 Oct 2026) |
| Strix Halo 128 GB: Framework Desktop | $3,449 | same page (Oct 2026) |
| Mac Studio M5 Ultra 96 GB, 1 TB | $5,499 | https://runtimewire.com/article/apple-mac-studio-m5-ultra-local-ai-price (Aug 2026) |
| Mac Studio M5 Ultra 256 GB, 1 TB | $10,799 (needs 80-core GPU +$1,300, memory +$4,000) | https://www.macrumors.com/guide/m5-max-vs-m5-ultra/ (2026) |
| Mac Studio M5 Ultra 512 GB, 1 TB | $22,299 (orders from 28 Oct) | https://www.ithinkdiff.com/512gb-mac-studio-m5-ultra-price-22299/ (Oct 2026) |
| Used RTX 3090 24 GB (for reference) | median ask $1,940 | https://gpudojo.com/rtx-3090 (9 Nov 2026) |
| Electricity | 18.2 ¢/kWh US residential 2026 average | https://www.eia.gov/outlooks/steo/report/elec_coal_renew.php (EIA STEO 2026) |

Cloud rates:

| Provider | H100 SXM | H100 PCIe | A100 80 GB | RTX PRO 6000 | Source and date |
|---|---|---|---|---|---|
| RunPod community / secure | $2.69 / $3.99 | $1.99 / $2.89 | $1.19-1.39 / $1.79 | $1.69 / $2.49 | https://www.runpod.io/pricing (read 10 Nov 2026) |
| Lambda, on-demand | $4.89 (1x) to $4.59 (8x) | $3.79 | $3.19 (8x HGX) | not listed | https://lambda.com/pricing (rates effective 16 Nov 2026) |
| Vast.ai median | | | | $1.72 | thundercompute link (9 Nov 2026) |

Hard prices were not readable directly at Newegg, B&H, CDW and NVIDIA's marketplace (they block automated reads or timed out). Those numbers come from dated trackers and press. Re-check the live listing before ordering.

## 2. The one table

Arithmetic used in every row:
- Decode tok/s, one stream (ESTIMATE) = memory bandwidth × 0.7 ÷ weight bytes. Weights: 8B at FP8/INT8 = 8 GB. 70B at 4-bit ≈ 40 GB (NF4/AWQ plus scales). The 0.7 factor is typical of vLLM/llama.cpp at batch 1. Batched judge serving runs far higher in aggregate, see section 3.
- 1B from scratch on 20B tokens (ESTIMATE): FLOPs = 6 × N × D = 6 × 1e9 × 2e10 = 1.2e20. Days = 1.2e20 ÷ (dense BF16 peak × 0.40 MFU × 86,400). 40% is a good small-model MFU with FlashAttention and torch.compile.
- QLoRA 70B memory (ESTIMATE): NF4 base ≈ 70e9 × 0.53 B ≈ 37 GB, plus LoRA r=16 with Adam ≈ 2-3 GB, plus activations with gradient checkpointing at seq 2K, batch 1 ≈ 4-8 GB. Total ≈ 45-48 GB. So 48 GB works only at short sequences. 80 GB and up is comfortable.
- Power cost (ESTIMATE): watts at full load × 730 h ÷ 1000 × $0.182. 1 kW all month = $133.

| Option | Price now | Memory | Bandwidth | Tensor compute | Stack | QLoRA 70B? | 8B tok/s (1 stream) | 70B 4-bit tok/s | 1B/20B-token run | Load power, $/month 24/7 | Noise |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RTX PRO 6000 WS 96 GB | $15,450-19,999 | 96 GB GDDR7 | 1,792 GB/s | 4,000 AI TOPS FP4 sparse (vendor). Derived dense: FP4 ~2,015, FP8 ~1,008, BF16 ~500 TFLOPS | CUDA, Linux and Windows | Yes, comfortable | 1792×0.7/8 ≈ 157 | 1792×0.7/40 ≈ 31 | 1.2e20/(500e12×0.4) = 6.9 days | card 600 W + host ~250 = 850 W → $113 | Open-air, moderate |
| RTX PRO 6000 Max-Q 96 GB | ~€13.7k+ (no US) | 96 GB | 1,792 GB/s | 3,511 AI TOPS FP4 sparse (vendor). BF16 ~439 derived | CUDA | Yes | ≈ 157 | ≈ 31 | 7.9 days | 300 W + 200 = 500 W → $66 | Blower, audible |
| DGX Spark / OEM GB10, 128 GB | $5,449 (HP) to $6,950 (NVIDIA) | 128 GB LPDDR5X unified | 273 GB/s | 1 PFLOP FP4 sparse (vendor). Derived dense FP8 ~250, BF16 ~125 TFLOPS | CUDA on ARM Linux (DGX OS). No Windows | Yes, comfortable | 273×0.7/8 ≈ 24 | 273×0.7/40 ≈ 4.8 | 1.2e20/(125e12×0.4) = 27.8 days | ~170-240 W → $23-32 | Quiet, small |
| 2x GB10 via ConnectX-7 (200 Gb/s) | ~$11k-13.9k | 256 GB | 2 × 273 GB/s | 2 × above | CUDA, NCCL over CX-7 | Yes | same as one | ~6-8 split over link | ~14-16 days with good scaling | ~$46-64 | Quiet |
| 2x RTX 5090 32 GB | $10,200-18,800 | 64 GB (2 × 32) | 2 × 1,792 GB/s | 3,352 AI TOPS FP4 sparse each (vendor). BF16 ~209 dense each with FP32 accumulate | CUDA, Linux and Windows | Yes via FSDP-QLoRA across 2 cards | ≈ 157 per card | TP2 over PCIe ≈ 35-45 | 1.2e20/(2×209e12×0.4) = 8.3 days | 2×575 + 250 = 1,400 W → $186 | Loud, hot |
| RTX 6000 Ada 48 GB | ~$7,400-10,700 | 48 GB GDDR6 | 960 GB/s | FP8 ~728 dense, BF16 ~364 dense | CUDA, Linux and Windows | Tight: seq ≤1-2K | 960×0.7/8 ≈ 84 | 960×0.7/40 ≈ 17 | 1.2e20/(364e12×0.4) = 9.5 days | 300 + 150 = 450 W → $60 | Blower, audible |
| RTX A6000 48 GB, used | $4,250-5,100 | 48 GB GDDR6 | 768 GB/s | No FP8 tensor. BF16 ~155 dense | CUDA, Linux and Windows | Tight: seq ≤1-2K | 768×0.7/8 ≈ 67 (W8A16 Marlin) | 768×0.7/40 ≈ 13 | 1.2e20/(155e12×0.4) = 22.4 days | 300 + 150 = 450 W → $60 | Blower, audible |
| A100 80 GB PCIe, used | $10,999+ | 80 GB HBM2e | 1,935 GB/s | No FP8. BF16 312 dense | CUDA, Linux | Yes | 1935×0.7/8 ≈ 169 (INT8 weight-only) | 1935×0.7/40 ≈ 34 | 1.2e20/(312e12×0.4) = 11.1 days | 300 + 200 = 500 W → $66 | Passive card: needs server fans, loud |
| H100 PCIe 80 GB | $29,500-35,999 | 80 GB HBM2e | 2,000 GB/s | FP8 1,513 dense, BF16 756 dense | CUDA, Linux | Yes | ≈ 175 | ≈ 35 | 4.6 days | 350 + 200 = 550 W → $73 | Passive, loud |
| AMD MI210 64 GB, used | $4,299 | 64 GB HBM2e | 1,638 GB/s | BF16/FP16 181 dense. No FP8 | ROCm, Linux only | Yes on memory. bitsandbytes ROCm works but is less proven | ≈ 143 | ≈ 29 | 1.2e20/(181e12×0.4) = 19 days | 300 + 200 = 500 W → $66 | Passive, loud |
| Radeon AI PRO R9700 32 GB | ~$1,300-1,800 | 32 GB GDDR6 | 640 GB/s | FP8 supported (RDNA4). FP16 ~96 dense (approx.) | ROCm on Linux, partial on Windows | No (one card) | 640×0.7/8 ≈ 56 | doesn't fit | ~36 days | 300 + 150 = 450 W → $60 | Blower |
| Strix Halo 128 GB (EVO-X2 / Framework) | $3,449-3,500 | 128 GB LPDDR5X, ~96-110 GB to GPU | 256 GB/s | ~59 TFLOPS FP16 (RDNA 3.5, 40 CU). No FP8 | ROCm/Vulkan, llama.cpp best. PyTorch training immature | Fits on memory, but slow and fragile toolchain | 256×0.7/8 ≈ 22 | 256×0.7/40 ≈ 4.5 | 1.2e20/(59e12×0.3) = 78 days | ~140-160 W → $19-21 | Moderate |
| Mac Studio M5 Ultra 96 GB | $5,499 | 96 GB unified | 1.2 TB/s (reported) | Apple does not publish tensor TFLOPS. No FP8/FP4 tensor path in MLX | MLX, llama.cpp. No CUDA (no vLLM, bitsandbytes, Unsloth CUDA kernels) | MLX QLoRA on 4-bit 70B fits (40 GB + activations). Training slow | 1200×0.7/8 ≈ 105 | 1200×0.7/40 ≈ 21 | Not computable from published specs. Our guess 20-60 days | ~200-300 W → $27-40 | Near silent |
| Mac Studio M5 Ultra 256 GB | $10,799 (over hard max) | 256 GB | 1.2 TB/s | same | MLX | Yes | ≈ 105 | ≈ 21 (70B 8-bit ≈ 12) | same | same | Near silent |
| Existing RTX 3080 10 GB (Armature) | owned | 10 GB | 760 GB/s | FP16 ~119 dense (FP16 acc), ~60 with FP32 acc | CUDA | No | 760×0.7/8 ≈ 66 (8B FP8 does not fit with KV. Use 4-bit: ≈ 110) | doesn't fit | 1B full AdamW needs ~16 GB, doesn't fit. 100-350M models do | 320 + 150 → $62 | Gaming card |
| Existing 48 GB Mac | owned | 48 GB | depends on chip (Pro 273, Max 400-546 GB/s) | — | MLX | No (70B 4-bit ≈ 40 GB leaves no room) | 34-48 | doesn't fit | slow | low | Quiet |

The dense BF16 numbers for the RTX PRO 6000 (~500), GB10 (~125) and the Max-Q (~439) are third-party derivations from NVIDIA's sparse FP4 figures, not datasheet lines (https://flopper.io/gpu/nvidia-rtx-pro-6000-blackwell-max-q-workstation-edition/spec-sheet.pdf , https://gpupoet.com/gpu/learn/card/nvidia-rtx-pro-6000-blackwell-workstation). The PRO 6000 bandwidth (1,792 GB/s) and 4,000 AI TOPS are datasheet lines (https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-6000-max-q/workstation-datasheet-blackwell-rtx-pro-6000-max-q-nvidia-us-5349650-web.pdf).

Reality check against published runs (from the Muse Glimmer note): Muse Glimmer 30B NVFP4 decodes at 58 tok/s on an RTX PRO 6000 and about 12 tok/s on a DGX Spark (LMSYS, Classmethod). Our formula gives 1792×0.7/25.4 ≈ 49 and 273×0.7/25.4 ≈ 7.5. The formula is conservative by about 20-60%, so treat the table as a floor.

## 3. Workload by workload

**8B judges at high throughput.** One stream is bandwidth-bound (table). Batched serving is compute-bound. Ceiling per card (ESTIMATE) = dense compute × 0.3 ÷ (2 × 8e9 FLOPs per token). A6000: 155e12 × 0.3 / 16e9 ≈ 2,900 tok/s. RTX 6000 Ada with FP8: 728e12 × 0.3 / 16e9 ≈ 13,600. GB10 with FP8: 250e12 × 0.3 / 16e9 ≈ 4,700, but its 273 GB/s also caps it: at batch 64 one weight read per step gives 273 × 0.7 / 8 × 64 ≈ 1,500 tok/s before KV reads. Several judges at once want discrete-GPU bandwidth. A 48 GB card holds several 8B judges at FP8 (8 GB each plus KV). This is the workload where owning beats renting: a rented L40S or 5090 costs $0.69-1.19/h, which is $500-870 a month at 24/7 (RunPod, 10 Nov 2026).

**QLoRA 3B-70B.** 3-14B already fits the 48 GB Mac (MLX) and the 3080 for ≤8B at short sequences. 30B (Muse Glimmer, Qwen-class) needs 24-36 GB. 70B needs ~45-48 GB at seq 1-2K and ~60-80 GB at 4-8K. A 48 GB card does 70B only with short sequences. GB10, Mac 96 GB and 80 GB+ cards do it comfortably. Speed: GB10's ~125 TFLOPS BF16 is close to an A6000's ~155, so a 70B QLoRA step runs at similar speed on both. GB10 wins on headroom, A6000 on cost.

**70B teacher for distillation.** Generating many tokens from a 70B wants bandwidth. Per stream: A6000 ≈ 13, RTX 6000 Ada ≈ 17, Mac M5 Ultra ≈ 21, GB10 ≈ 5 tok/s. Batched, a 48 GB card has little room left for KV after 40 GB of weights, so batch stays small. GB10 has room for a large batch but low bandwidth. For bulk teacher generation, renting an H100 for a weekend (FP8 70B at batch 64+, thousands of tok/s) is likely cheaper than any local box.

**1B from scratch on ~20B tokens.** 1.2e20 FLOPs. Rented H100 SXM: 1.2e20 / (989e12 × 0.4) = 3.0e5 s ≈ 84 GPU-hours ≈ $226 at RunPod community $2.69, $335 at RunPod secure $3.99, $411 at Lambda 1x $4.89. Locally this is 9.5 days (6000 Ada), 22 days (A6000), 28 days (GB10). A 100-350M model is 3-10x cheaper again and fits the 3080. Owning hardware does not pay for itself on this workload. Rent it.

**Muse Glimmer 30B.** Fits every option with 48 GB or more. FP8 (35 GB) runs on a 48 GB card. BF16 (62 GB) needs GB10, Mac 96 GB, or 80 GB+. QLoRA fits 48 GB.

## 4. What $7-10k buys in the cloud, same jobs

| Budget | H100 SXM hours | A100 80 GB hours |
|---|---|---|
| $7,500 | 2,788 (RunPod community $2.69) / 1,880 (RunPod secure $3.99) / 1,534 (Lambda 1x $4.89) | 6,303 (RunPod community $1.19) / 4,190 (secure $1.79) |
| $10,000 | 3,717 / 2,506 / 2,045 | 8,403 / 5,587 |

Per job (ESTIMATE): one 1B/20B-token run ≈ 84 H100-h ≈ $226-411. One 70B QLoRA pass over ~50M tokens at ~500 tok/s training throughput on one H100 ≈ 28 h ≈ $75-140. Bulk 70B teacher generation of 100M tokens at ~3,000 tok/s batched FP8 ≈ 9.3 h ≈ $25-45. Judges 24/7 on one rented H100 PCIe at $1.99-2.89 = $1,450-2,110 a month, so $7.5k lasts 3.5-5 months. Cloud wins clearly for burst training and bulk generation. Owned hardware wins for always-on judges, iteration loops and private data.

## 5. Armature: what to check (it decides the cheap path)

Open the side panel and read these off the parts. Software reports are unreliable for PSU details.
1. **PSU**: wattage and model off the label. The 3080 10 GB is a 320 W card and NVIDIA asked for a 750 W PSU, so Armature likely has 750-850 W. A 300 W card (A6000, RTX 6000 Ada, Max-Q) is a straight swap at that wattage. A 600 W RTX PRO 6000 Workstation or a 5090 needs 1,000-1,200 W, ideally ATX 3.1.
2. **Connectors**: count free PCIe 8-pin leads. RTX A6000 takes one 8-pin **EPS/CPU-style** plug (adapter from two PCIe 8-pins usually in the box). RTX 6000 Ada takes one 16-pin 12VHPWR (adapter in box). RTX PRO 6000 Workstation takes one 12V-2x6 at 600 W. Use a native 12V-2x6 cable from an ATX 3.1 PSU or the supplied adapter fully seated. No third-party angled adapters.
3. **Slot and lane**: which PCIe gen the top x16 slot runs (board manual, or GPU-Z "Bus interface"). PCIe 5.0 is not needed for any of these cards. Gen 4 x16 costs under a few percent for single-card inference and training. Gen 3 x16 is also fine for single-card work. It matters only for multi-GPU tensor parallel.
4. **Case length and width**: measure GPU clearance in mm. RTX PRO 6000 Workstation is about 304 mm long and dual-slot. A6000, RTX 6000 Ada and Max-Q are about 267 mm, dual-slot blowers.
5. **Airflow**: blower cards exhaust out the back and suit a closed case. The open-air PRO 6000 Workstation dumps 600 W into the case, so it needs at least two front intakes and one rear/top exhaust. Passive A100/H100/MI210 cards will overheat in a desktop case without a ducted high-static-pressure fan.
6. **System RAM and disk**: 64 GB RAM minimum for loading and quantising 70B, 128 GB better. NVMe space: a 70B BF16 download is ~140 GB, so plan 2 TB free.
7. **OS**: install Ubuntu 24.04 dual-boot, or at least WSL2. vLLM, bitsandbytes and Unsloth are first-class on Linux. On Windows they run through WSL2 with some loss and occasional driver friction.
8. **Two cards at once?** Keeping the 3080 next to a new 300 W card means ~620 W of GPU plus CPU, which needs ~1,000 W and two slots spaced at least three apart. Simpler to retire the 3080 or move it to a judge-only role in another box.

## 6. Recommendations

**At ~$7-8k, pick one:**

1. **Used RTX A6000 48 GB in Armature, plus ~$3k of cloud credit.** About $4,250-5,100 for the card (gpudojo, 9-10 Nov 2026), likely no PSU change. Fast CUDA on x86, works with vLLM, Unsloth and bitsandbytes on Linux. It serves several 8B judges at a time, runs 70B at 4-bit (~13 tok/s single stream), runs Muse Glimmer at FP8, and does 70B QLoRA at short sequences. The ~$3k of cloud covers the 1B pretraining runs and any long-sequence 70B QLoRA (roughly ten 1B runs, or 750-1,100 H100-hours). Best throughput per dollar today. Weak points: Ampere has no FP8 tensor cores (FP8 checkpoints still run as W8A16), it is used with no warranty, and the blower is loud under load.

2. **A GB10 box (HP ZGX G1n $5,449, ASUS Ascent GX10 $5,999, GIGABYTE AI TOP ATOM $5,999.99), plus ~$1.5-2.5k of cloud.** New with warranty, 128 GB, CUDA, quiet, ~$25/month in power. Comfortable 70B QLoRA at long sequences, BF16 Muse Glimmer, and 70B teacher at large batch. It is slow per stream (70B ≈ 5 tok/s, 8B ≈ 24) and the weakest of the CUDA options for high-throughput judges. It runs ARM Linux only. Choose this over option 1 if memory headroom and warranty matter more than judge throughput. Buy an OEM unit, not NVIDIA's own: same GB10 chip, $1,000-1,500 less than the $6,950 list.

The Mac Studio M5 Ultra 96 GB ($5,499) is the honorable mention. It has the best 70B decode speed in budget (~21 tok/s, 1.2 TB/s), runs silent, and fits our MLX work. It falls behind on CUDA tooling, batched serving and training speed.

**At $10k:**

**HP ZGX G1n or another OEM GB10 (~$5,449-5,999) plus a used RTX A6000 in Armature (~$4,250-4,500). Total about $9,700-10,500.** Two machines running in parallel cover each other's gaps. The GB10 takes 70B QLoRA at long sequences, the 70B teacher, BF16 LoRA of Muse Glimmer, and anything that needs >48 GB. The A6000 takes the always-on 8B judges, 30B FP8 inference, and small-model training. Cloud stays the plan for 1B pretraining. If the A6000 lands near the $5,087 median, the total runs a few hundred over $10k. In that case choose the $5,449 HP or pull the card price down with an eBay offer.

Runner-up at $10k: two used A6000s (~$8.5-10.2k) with an NVLink bridge in one Linux box. That gives 96 GB of pooled fast VRAM and is the fastest single host in budget. But it needs a ~1,200 W PSU, a board with two x16 slots three apart, and possibly a new case, which pushes it past $10k unless Armature's board and case already fit.

**Not recommended at today's prices:** RTX PRO 6000 (any edition, $15.5k+), 2x RTX 5090 ($10k-19k for 64 GB), used A100 80 GB ($11k+), H100 PCIe ($29.5k+), Mac 256/512 GB ($10.8k/$22.3k), a single 5090 at $5-7k (32 GB for the price of 48 GB used). The RTX PRO 6000 becomes the clear single-card answer if it falls back toward its $8.5-9.5k launch range. Worth a weekly price check.

## 7. Risks

- **Availability and price swings.** Prices moved 50-130% in 12 months. The DGX Spark rose $2,251 in two steps (Feb and 2 Oct 2026). Lock a price by ordering, not by watching. Third-party marketplace listings at 3-5x MSRP are common on 5090/PRO 6000. Buy only from first-party stores or the retailer itself ("sold by Newegg"), not marketplace sellers.
- **Warranty.** New GB10 OEM boxes carry the OEM warranty (HP/ASUS/GIGABYTE typically 1-3 years, check per SKU). Used pro cards usually have none. NVIDIA's pro warranty is tied to the original purchaser and does not transfer reliably.
- **Used-market traps.** Ex-mining or ex-datacentre cards with worn blower fans and dried thermal pads. "A6000" listings that are really the A6000-class A40 (passive, no display out, needs server airflow). China-shipped "open box" cards. Scams with stock photos. To defend: pay through eBay or PayPal protection, ask for a photo with the serial and a GPU-Z screenshot, run a 30-minute stress test plus a CUDA memtest (e.g. `gpu-burn` and `cuda_memtest`) within the return window, and check temps (blower card should hold under ~85 °C core).
- **Windows vs Linux.** Linux is first-class for vLLM, SGLang, bitsandbytes, Unsloth, FlashAttention and Transformer Engine. On Windows, use WSL2. Native Windows vLLM is not officially supported. DGX Spark/GB10 runs DGX OS (Ubuntu on ARM64) only. Some Python wheels lack aarch64 builds, so expect to compile a few packages from source. ROCm (MI210, R9700, Strix Halo) is Linux-first. Strix Halo PyTorch training support was still uneven in 2026. MLX is macOS only and has no bitsandbytes/vLLM equivalents (mlx-lm covers LoRA/QLoRA and serving).
- **Power and heat.** A 600 W card on an old PSU or a badly seated 12V-2x6 plug is a melted-connector risk. Blower cards at 300 W are loud in a small room. Passive datacentre cards cook in desktop cases.
- **Two-Spark pairing.** ConnectX-7 at 200 Gb/s is far slower than NVLink. Splitting one model across two Sparks adds memory, not speed. NVIDIA's two-pack ($13,599) costs more than two single OEM units plus a QSFP cable.
- **Our numbers.** Throughput figures are bandwidth and FLOP arithmetic, checked against two published Muse Glimmer runs (formula ran 20-60% low). The dense BF16 figures for Blackwell parts are derived, not datasheet lines. Measure our own judges on the hardware before sizing a fleet.
