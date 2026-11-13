# The 7 missed twins, read by hand (Bones, 12 Nov 2026)

Source: results/contamination_wall.json (missed_twins), data/twins.json (twin records), data/gold_items.json, results/missed_twins_check.json, data/fulltext_coverage.json, ceiling_ft/text/.

The positive control flagged 105 of 112 real twins (journal 51 of 51, Zenodo versions 54 of 61). These are the 7 it missed.

## Are they real twins?

All 7 are. Each is another version DOI in the same Zenodo concept family as its gold item, with the same author.

| Twin DOI | Gold id (split) | What the twin is |
|---|---|---|
| zenodo.19812235 | b3dab6a62172 (dev) | Same paper, same title, earlier version |
| zenodo.18165162 | 08c4a2608cbe (dev) | Same project, retitled version ("Holographic Information Recovery and 93.69-Sigma Causal Reversal"), rewritten abstract |
| zenodo.19473977 | 9862f0571c06 (dev) | The "Engineering Emergence, The Foundation" version, which is the List study itself |
| zenodo.19473978 | 9862f0571c06 (dev) | German-language early version (QITE on 156 qubits). A translated twin, the first one found |
| zenodo.23246373 | c8464231d15c (dev) | Quantum Anchor V1.2 ledger version |
| zenodo.22072152 | c71467663457 (test) | "Complete Programm (Parts I to XX)", which is the List study itself |
| zenodo.22072153 | c71467663457 (test) | First successor deposit (one-shot Hebbian plasticity) |

## Did any reach the pool or slices?

No known twin did. For all 7, the best title match in the pool plus slices is at most 0.21 Jaccard, and no pool or slice record carries the twin DOI (results/missed_twins_check.json). Nothing labelled as silver duplicates these gold items.

## Why the matcher missed them

In 6 of the 7, the matcher was right and the gold record was wrong. Gold's title and abstract came from OpenAlex. For these Zenodo concept DOIs, OpenAlex returned a different version from the one the recount read:

- b3dab6a62172: gold text is a different paper, "Gauss–Kuzmin Deviation as a Cross-Domain Performance Predictor". The List study and the twin are "Localisation-Unlocalisation Duality".
- 9862f0571c06: gold text is the early QITE version. The List study is "Engineering Emergence, The Foundation".
- c8464231d15c: gold text is "Methodological Obstacles, API Deprecations, and Empirical Null-Results". The List study is "Quantum Anchor Protocol".
- c71467663457: gold text is "Parts I to V". The List study is "Complete Programm (Parts I to XX)".

So the matcher compared the twin with the wrong gold text and correctly found no match. 1 of the 7 is a true content miss: 08c4a2608cbe, where the version was retitled and its abstract rewritten, and gold has no author list, so the author signal could not fire.

Read this way, the matcher's recall on Zenodo versions is under-read: 54 of 55 counting only twins whose gold text is the right version, against 54 of 61 as reported. Translation recall is no longer untested-for-lack-of-data: zenodo.19473978 is a German twin, but its miss comes from the gold-side drift, so it still says nothing about translation recall.

## Version drift across all gold

A scan of all 43 non-arXiv gold items, comparing the List study title with the fetched title, found 5 where the OpenAlex text is another version or another paper:

| Gold id | Split | Codes | Full text (the linked record's PDF) |
|---|---|---|---|
| b3dab6a62172 | dev | F2 F3 F4 | Right version (LUD, v5.0) |
| 9862f0571c06 | dev | F5 | The 90-page bundle that contains the Foundation sections (ends at section 40, "This Document as Foundation") |
| c8464231d15c | dev | F5 | Not fetched (no PDF in the record) |
| ebc0dd772d38 | dev | none | The PDF is named "Variational Quantum Regression…" but its text is titled "Quantum Kernel-Based Cancer Atlas". The author's file drifted, not our fetch |
| c71467663457 | test | none | 71-page dissertation, the linked record |

e18aca5c62c3 and 6aecacfbca78 also score low, but only because the List label is short. The paper is the same.

What this means:
- Abstract lane (closed): 5 of 197 gold items were labelled on another version's abstract. b3dab6a62172 was labelled on a different paper.
- Full-text lane (running now): text comes from the linked record's own PDF, so it matches the recount for b3dab6a62172 and 9862f0571c06. ebc0dd772d38 carries no flags and enters only as an unflagged pair. c8464231d15c and c71467663457 have no dev full text.
- This goes into Sage's break 7 item "record the version against the version the recount read". It applies to Zenodo concept DOIs as well as arXiv.


## Corrected wording (Sage, 12 Nov 20:15)
Corrected Zenodo-version recall: 54 of 55, counting only twins whose gold text is the right version (54 of 61 as reported). 6 of the 7 misses come from version drift on the gold side. The wall's claim is "no known twin in the pool", not "no twin".
