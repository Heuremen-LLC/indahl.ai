# HFSIZE: the size a Hugging Face model name states against the parameters its weight files hold. Plan, written before any model is compared.

## Claim read
Many model names state a size: Llama-3.1-8B, Qwen2.5-7B-Instruct, SmolLM2-135M. Stated: this model has about that many parameters. Record: the parameter count Hugging Face itself computes from the headers of the model's safetensors weight files (the safetensors total in the API).

## Population
The 1,000 most downloaded models by the Hugging Face API, sorted by downloads, read on one day (the date is stored). Unit: one repository. Repositories from the same organization are not independent, so the number of distinct organizations among the DISAGREE rows is reported beside the count.

## Read (fixed now)
API: https://huggingface.co/api/models, sorted by downloads, expanded with safetensors and tags, one request per page of 1,000.
Stated size: the name after the last slash, one size token matching a number (digits with an optional decimal part) followed directly by B, M or K (case-insensitive), not preceded by a letter, digit or period and not followed by a letter. B is 1e9, M is 1e6, K is 1e3. If the name holds two or more different size tokens, or a mixture-of-experts pattern (NxMB such as 8x7B, or an active-size token such as -A3B), the size is not a single stated figure and the repository is NOT_COMPARABLE.
Actual size: the safetensors total from the API. No total means NOT_COMPARABLE.
Packed or quantized repositories (name or tags containing awq, gptq, gguf, bnb, 4bit, 8bit, int4, int8, fp8, fp4, nvfp4, mxfp4, w4a16, w8a8, quantized) store several parameters per stored value, so the total is not a parameter count. They are NOT_COMPARABLE.
Classes: AGREE when actual divided by stated is between 0.70 and 1.35 inclusive. The band covers rounding of the name (a 7B that is 7.6B), tied or untied embeddings, and added vision or audio parts, and was fixed before the first read. DISAGREE outside the band. NOT_COMPARABLE as above.
Reported: counts by class, the share DISAGREE among AGREE plus DISAGREE with a Wilson 95% interval, why repositories were not comparable, and every DISAGREE row with the stated size, the actual total and the ratio.
Outcome against the claim that a name's size is the weights' size (zero disagreement): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 comparable repositories: CANNOT_TELL. Same thresholds as HFLICENSE and PKGLICENSE.
Re-read every 30 days.

## Hand check (fixed now)
Every DISAGREE row is opened by hand, the name, the card and the file list, before it is shown, and the reason written beside it (for example: the number in the name is a version, or the repository holds several checkpoints). A row where the reading, not the repository, was wrong is corrected by a dated addendum and the whole read is run again.

## Known-good
Planted pairs before each read: 7B with 7.24e9 AGREE, 7B with 7e10 DISAGREE, 7B with 7e8 DISAGREE, 135M with 1.345e8 AGREE, 7B with 4.9e9 AGREE (0.70 edge), 7B with 9.45e9 AGREE (1.35 edge), 7B with 9.5e9 DISAGREE, names with 8x7B, -A3B and two size tokens NOT_COMPARABLE, awq NOT_COMPARABLE. Token reading: Qwen2.5-7B-Instruct reads 7e9 (2.5 is not a size), all-MiniLM-L6-v2 reads no size, bge-m3 reads no size, SmolLM2-135M reads 1.35e8, gpt2-medium reads no size. Live: Qwen/Qwen2.5-7B-Instruct and HuggingFaceTB/SmolLM2-135M must read AGREE. Any wrong answer stops the pass.

## Not claimed
That the name is wrong where it disagrees: a name can state a family size and the repository can hold a different model. The quality of any model. Anything about repositories without safetensors weights.

## Addendum 1 (29 Oct, after the first read and its hand check, before anything was shown)
Two errors in the instrument, found by opening the 15 DISAGREE rows.
1. prism-ml/Bonsai-27B-mlx-1bit is a 1-bit packed repository. The packed list named 4bit and 8bit but not the other bit widths. The list now matches any single-digit bit width from 1 to 8 followed by "bit" as well as the names already listed.
2. ornith-ai/Ornith-1.0-9B and ornith-ai/Ornith-1.0-35B show a safetensors total of 1,469,680 and 664,944 while their own dtype breakdown in the same API response holds 9,409,813,744 and 35,107,181,936 BF16 parameters. The two numbers from Hugging Face disagree with each other, so the repository cannot be compared. The reader now sums the breakdown and, when the total differs from the sum, sets the repository to NOT_COMPARABLE with the reason "Hugging Face total does not match its own breakdown". These rows are counted and listed apart, since they are a finding about the API, not about the name.
The first read's numbers (133 agree, 15 disagree) are not used. The whole read is run again. The band, the thresholds and the outcome rule did not change.

## Note 1 (29 Oct, hand check of the second read, before anything was shown)
After addendum 1, 12 of 142 comparable repositories read DISAGREE. All 12 were opened by hand and none is a reading error. The reasons found fall in four kinds: a name that states the size of the model a draft checkpoint pairs with (3), a name that states one component (the language model, the non-embedding count, or in one row a context length) (4 including the context-length row), a repository whose weights hold several components while the name states one (5, two of them with the split not given in the card, and one with the configuration gated). No rule changed. The band is the one fixed before the first read, so rows at 1.366 to 1.382 stay DISAGREE.

## Note 2 (29 Oct, correcting the count in Note 1, before anything was shown)
Note 1 gave the kinds as 3, 4 and 5. Counted again from data/hand_checked.json the 12 rows are: a draft checkpoint whose name states the model it pairs with (3), a name that states one component, being the language model, the non-embedding count or a context length (3), a repository whose weights hold several components (5), and one row whose reason is not established because its configuration is gated (1). No row changed class.
