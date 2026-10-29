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

## Addendum 2 (29 Oct, after the first read and its hand check, before anything was shown)
Two errors in the instrument, found because the results looked wrong before they were believed.
1. All 3 model disagreements were Creative Commons files read as CC0. The standard Creative Commons legal text ends with a notice that the text of the Creative Commons public licenses is dedicated to the public domain under the CC0 Public Domain Dedication, and the reader took that phrase anywhere in the file as the license. The Creative Commons family is now read from the title region, the first 600 characters (CC0 only when CC0 or "Zero" with "Universal" appears there; otherwise Attribution with its NonCommercial, ShareAlike and NoDerivatives qualifiers read from the same region). The gate gains planted tests: the full CC BY 4.0, CC BY-NC-SA 4.0 and CC0 1.0 texts, the CC BY 4.0 text with the trailer appended, and a short custom license stating the weights are under CC BY-NC 4.0.
2. All 330 datasets with a stated license read "no license file". The list endpoint returns no file names for datasets. The file names are now taken from the per-dataset endpoint when the list entry has none, one extra request per repository.
The first read's numbers (82 models agree, 350 models and 330 datasets with no license file) are not used. The whole read is run again. No rule, threshold or outcome changed.

## Addendum 3 (29 Oct, after the second read, before anything was shown)
The second read found no DISAGREE rows. Checking what the plan's NOT_COMPARABLE rule was hiding turned up two things.
1. One repository read a license file that was an image (huggingface/documentation-images, file license_other_example.png): the file-name matcher accepts any name starting with LICENSE. The matcher now accepts only names with no extension or the extensions .md, .txt and .rst. The whole read is run again.
2. Two descriptive rows are added, each with no outcome and counted apart from the main test: repositories whose tag names a standard license and whose file reads as a custom or unnamed text (for example Qwen/Qwen2.5-VL-7B-Instruct-AWQ: tag apache-2.0, file the Qwen License Agreement), and repositories whose tag is other or a custom name and whose file reads as a standard license (8 models in the second read). Every repository in the first group is opened by hand before it is listed. The main test, its classes and its thresholds are unchanged.

## Addendum 4 (29 Oct, after the third read and the hand check of the two mismatch rows, before anything was shown)
Fhrozen/FSD50k: tag cc-by-4.0; its LICENSE-DATASET.md says "FSD50K as a whole is released under license: Attribution 4.0 International (CC BY 4.0)". By hand the file agrees with the tag. The reader called it a custom text because its title region does not contain the words "Creative Commons" (only a creativecommons.org link), so it was filed with the mismatch rows. The Creative Commons reading in the title region now also accepts "Attribution" followed by a version number (for example 4.0 International), and a CC BY notation, with the same qualifiers. The gate gains the planted FSD50K sentence. The other mismatch row, Qwen/Qwen2.5-VL-7B-Instruct-AWQ (tag apache-2.0, file the Qwen License Agreement), was opened by hand and is a genuine difference. The whole read is run again. No rule, threshold or outcome changed.

## Addendum 5 (29 Oct, from the internal audit)
1. A call for a repository's file list that failed, or came back empty because the request failed, was scored as no license file in the repository root. That is the largest class on the page (352 models, 295 datasets). A failed call is now its own class, NOT_COMPARABLE with the reason file list could not be read. Every stored row of the no license file class is read again once, and a row whose list now shows a license file is scored on it.
2. The code accepts a license file name with a numeric tail and a card-data license fallback that addendum 3 does not list. Both stay as coded and are stated here.
3. Stated and not fixed: the OTHER family merges a genuinely custom license with a text the reader did not recognise, which kept the hand-verified Qwen AWQ tag and file difference outside the main test (it is listed in the descriptive group). Only DISAGREE rows are opened by hand, so a whole-text match for Apache, MIT or BSD on the AGREE side has no hand check. Repositories that copy one license text are priced as separate units.

## Addendum 6 (29 Oct, from the internal audit, before the next read)
The OTHER family merged three different things. The tag side is now split in the summary into: blank or the word other, unknown or none; a named custom license (llama, gemma, openrail, falcon, deepseek, qwen, any name with license or agreement); and anything else the reader did not recognise. The counts are for models and datasets, and a third count shows how many of those also read OTHER on the file side. No classification changed, all of them stay NOT_COMPARABLE, and no outcome moves. The split only shows what the residual contains. The same split for PKGLICENSE is stated and not yet built.

Note 1 to addendum 6 (29 Oct, hand read of the split). The 27 tags in the unrecognised group are real named licenses the reader has no family for: odc-by 22, cdla-permissive-2.0 1, cdla-sharing-1.0 1, openmdw-1.1 1, apple-amlr 1, cc 1. They are not custom terms. Adding families for them would change which rows are compared, and it needs the file-text side to recognise the same names, so it is a rule change for a later addendum with a new read, not done here.


## Addendum on cadence (29 Oct)
The repeat cadence is now every 66 ticks of the tick bus, about 6.4 hours, so that a change at the source shows within hours. The earlier cadence was a default chosen when the corner was built. Nothing else changes; each pass keeps the same read, the same politeness pauses and the same known-good checks.
