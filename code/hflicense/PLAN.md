# HFLICENSE: the license a Hugging Face repository states against the license file it carries. Plan, written before any repository is compared.

## Claim read
A model or dataset repository on Hugging Face states its license in its card (the license tag). The repository can also carry a license file. Stated: the repository is under license X. Record: the license file in the repository says Y.

## Population
The 500 most downloaded models and the 500 most downloaded datasets, by the Hugging Face API sorted by downloads, read on one day (the date is stored). Unit: one repository.

## Read (fixed now)
Hugging Face API (https://huggingface.co/api/models and /api/datasets, sorted by downloads, full listing with the file names), one request per 0.4 seconds, user agent naming this site.
Stated license: the license tag of the repository (license:NAME). The family of a tag is taken from the name: mit, apache, bsd, isc, gpl (with version when given), lgpl, agpl, mpl, cc0, the Creative Commons family with its qualifiers kept (cc-by, cc-by-sa, cc-by-nc, cc-by-nc-sa, cc-by-nd, cc-by-nc-nd), unlicense. Tags other, unknown, openrail, llama, gemma and any other custom or named-model license are OTHER.
Record: the first root file named LICENSE, LICENSE.md, LICENSE.txt, LICENSE-*, LICENCE or COPYING, fetched in full up to 30 kilobytes. Its family is read from its text: MIT (permission is hereby granted, free of charge), Apache-2.0 (Apache License, Version 2.0), BSD (redistribution and use in source and binary forms), ISC, GPL-2.0 or GPL-3.0 (GNU General Public License with its version), LGPL, AGPL, MPL-2.0, CC0, a Creative Commons text with its qualifiers (noncommercial, sharealike, noderivatives read from the text), Unlicense; anything else OTHER.
Classes: AGREE (same family; GPL with no version agrees with either GPL version), DISAGREE (both sides named and the families differ), NOT_COMPARABLE (no stated license tag, no license file in the repository root, a gated repository whose file cannot be read, or either side OTHER).
Reported: counts by class, separately for models and datasets; the share DISAGREE among AGREE plus DISAGREE with a Wilson 95% interval; the share of repositories with a stated license and no license file (descriptive, no outcome); and every DISAGREE row with both sides.
Outcome against the claim that the stated license is the file's license (zero disagreement): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 comparable repositories in a group: CANNOT_TELL. Same thresholds as PKGLICENSE.
Re-read every 30 days.

## Hand check (fixed now)
Every DISAGREE row is opened by hand, the tag and the file, before it is shown, and the reason written beside it. A row where the reading, not the repository, was wrong is corrected by a dated addendum and the whole read is run again.

## Known-good
The reading runs on planted pairs before each read, as in PKGLICENSE, plus planted file texts for each family (the full MIT, Apache-2.0, BSD-3-Clause and CC BY 4.0 texts must read as themselves, a custom text must read OTHER). Live: microsoft/phi-2 must read AGREE (mit tag, MIT file) and Qwen/Qwen2.5-7B-Instruct must read AGREE (apache-2.0 tag, Apache-2.0 file). Both were opened by hand on 29 Oct 2026 before this plan was committed. Any wrong answer stops the pass.

## Not claimed
Which side is right. That a license file in the root governs every file in the repository. Anything about a gated repository whose file cannot be read.

## Addendum 1 (29 Oct, on the first gate run, before any repository was read)
The planted full GPL-3.0 text read as AGPL, because the body of the GPL-3.0 mentions the GNU Affero General Public License (its section 13). The reading of the GNU licenses now uses the title in the first 400 characters of the file: Affero, Lesser General Public License, or General Public License with its version. Other families are read from the whole text as before. The gate (planted full texts for MIT, Apache-2.0, BSD-3-Clause, CC BY 4.0, CC BY-NC 4.0 and GPL-3.0) now must all pass. No rule, threshold or outcome changed.
