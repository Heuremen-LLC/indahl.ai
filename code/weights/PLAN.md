# WEIGHTS: does a model name keep the same weights? Plan, committed before the first read.

## The question
A Hugging Face repository name is a pointer. Anyone who pins a model by name expects the weight files behind it to stay the same. We read the weight files of the 1,000 most downloaded models and read them again on later passes. A model is SAME when its weight files are identical on two passes, CHANGED when a weight file was replaced, added or removed, GONE when the repository no longer resolves.

## Data
The Hugging Face API. The list of the 1,000 most downloaded models comes from the models endpoint sorted by downloads. For each model we read the file list of the main branch (the tree endpoint, root folder). A weight file is a file ending in .safetensors, .gguf, .pt, .pth or .onnx, or a .bin file whose name starts with pytorch_model. Each has a content hash (the LFS object id) recorded by Hugging Face. Per model we keep the set of (file name, content hash) for weight files, with the moment of the read.

## Rule (fixed now)
- A pass reads the current top 1,000 and also re-reads every model kept from earlier passes that has dropped out of the top 1,000, so no model leaves the record.
- Pair outcome per model, comparing a pass with the previous pass that read it: SAME, CHANGED, GONE. A read that fails for any other reason is UNREADABLE and is not scored; it is retried on the next pass and counted on the page.
- A model whose root has no weight files (they sit in subfolders, or the repository holds adapters only) is NOT_COMPARABLE and listed with that reason.
- Headline: among model pairs that are SAME or CHANGED, the share CHANGED, with a 95 percent Wilson interval. ABOVE if the lower end is above 1 percent. CONSISTENT if the upper end is below 1 percent. Otherwise CANNOT_TELL. One percent is the share we would call noticeable. It is set before any pass.
- GONE is counted and listed on its own, never folded into CHANGED or SAME.
- The first pass has nothing to compare with and returns NOTHING_RETURNED for the headline.
- Repeat passes every 720 ticks of the tick bus.

## Known-good, run before every pass
Planted file sets run through the comparison: identical sets must return SAME; one changed hash CHANGED; one file added CHANGED; one file removed CHANGED; the same files renamed with identical hashes must return CHANGED (a file name is part of the pointer); an empty set NOT_COMPARABLE; an absent repository GONE. Then a live check: the repository HuggingFaceTB/SmolLM2-135M read twice in a row must return SAME.

## Hand check
Every CHANGED model is listed only after it is in data/hand_checked.json with the file names and a note read from the repository's commit history. The count awaiting a hand check is on the page.

## Not claimed
Why a file changed. A repair, a conversion or a re-upload of the same numbers would all read CHANGED, because the hash changed. Weights in subfolders are not read. Gated repositories whose file lists need a login are UNREADABLE. The record starts today and says nothing about changes before it.
