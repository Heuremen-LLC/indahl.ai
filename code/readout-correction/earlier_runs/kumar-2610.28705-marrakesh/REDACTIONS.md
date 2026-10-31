# Redactions in this public copy

The files listed here differ from the files in our working folder. Only these kinds of strings were replaced or removed: name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local>. No number, rule, reading, job id or line of code logic was changed. The originals are kept and can be shown on request.

The hash files in this folder (CODE_*.sha256.text and PLAN_*.sha256.text) were written before any job and give the hashes of the original files. A file listed below therefore shows a different hash from the one in those lists. The sha256 of the original is given beside the sha256 of this public copy, so the original can be checked against the hash file when it is shown.

Not copied: the git folder of the working directory, its .gitignore (which listed circuits_kumar.qpy and the props files as ignored, so it would have hidden them from a repository), and the Python bytecode cache.

Not copied, by choice: the folder theirs/ (the author's own published paper text, code and result files, which are his and are listed on his arXiv page), the folder failed_A1_8299/ (the first A1 attempt that ended in an IBM-side error, with its record, job file and log) and results_kumar_VOID_20261024.text (the 24 October analysis file written from no data). ADDENDUM_KUMAR_resubmit.md.text, ADDENDUM_CANCELLED.md, PLAN_KUMAR.md.text and RESULT_KUMAR_MARRAKESH.md.text refer to these by name. The references are left as written.

Files in this folder that read the author's files in theirs/ (known_good.py, synth_kumar.py) need that folder to run. It can be fetched from his arXiv listing.

| file | replacements | kinds | sha256 of the original | sha256 of this public copy |
|---|---|---|---|---|
| ADDENDUM_CANCELLED.md | 4 | sentence about publishing or permission removed | e1d181975e588c1b2e7a5a3284363797af71a9c21b850fda2b905693e8ac3757 | e8e6f239408dae469159948e8b56bd3cf10dca62717a1eac75833420806aa5aa |
| PLAN_KUMAR.md.text | 4 | name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local> | 4c25d5402ff5a2a36f5c336bb2149b11ac8bd7fc261511555cf9d14d287e78e6 | dc00e8d983aac1e216a7f79dc41db98c648a724d8fb967251395c55b5fe72ced |
| fire_kumar.log | 2 | local paths replaced by relative paths or <local> | b8b4c0a135b197dbcbc5cc2342756e7b309d7482d1853f4e97273e16c72866e7 | 994335377092f34dae5da248d2e432f5de478f28a00bedfdbbee6f3f05b3a2fe |
| fire_kumar.py | 3 | name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local> | 8866bea4bfb9ec695f3511326fc7274fbffa76cbbd33bd6e9060ae0fba641323 | 6317e8862f346c00e886c04286bba5ab6cd706921379aa7247234cd0b8d2b731 |
| known_good.py | 1 | local paths replaced by relative paths or <local> | 28a14033fb130bf009c192cfab0b43401d31890cf4d5110e7c441da096ea45f5 | 19b9afb261f6e2266b4312d4de4f408e83fd785420b7d79d9999bd85829ae6ae |

Scan of the JSON data files in this folder for the same strings (our instance name, local paths, internal run labels, names): no hits, so none were edited.
