# Redactions in this public copy

The files listed here differ from the files in our working folder. Only these kinds of strings were replaced or removed: name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local>. No number, rule, reading, job id or line of code logic was changed. The originals are kept and can be shown on request.

The hash files in this folder (CODE_*.sha256.text and PLAN_*.sha256.text) were written before any job and give the hashes of the original files. A file listed below therefore shows a different hash from the one in those lists. The sha256 of the original is given beside the sha256 of this public copy, so the original can be checked against the hash file when it is shown.

Not copied: the git folder of the working directory, and the Python bytecode cache.

Not copied, by choice: the folder theirs/ (the author's own published paper text, code and result files, which are his and are listed on his arXiv page). known_good.py and synth_kumar.py read it and need it to run. PLAN_KUMAR.md.text refers to it by name. The references are left as written.

| file | replacements | kinds | sha256 of the original | sha256 of this public copy |
|---|---|---|---|---|
| PLAN_KUMAR.md.text | 4 | name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local> | e0a17b1df9ff05a956e03042c5527dd6ae9f4622911d836454943598a031d84f | ef4900bae073885576b2c49f7f4024e85382255a6f4b0cd02aafc62bbe23ca76 |
| fire_kumar.py | 3 | name of our IBM Quantum instance replaced by <our IBM instance>; sentence about publishing or permission removed; local paths replaced by relative paths or <local> | 921acca09f8b7e8d310a598a7fa94456729384ca4b1eb18d1b0cfd3276d5cad1 | 2279a5453ac0e9f7f06abeb536752c9520358545c07719a207ae885057e294ec |
| known_good.py | 1 | local paths replaced by relative paths or <local> | 28a14033fb130bf009c192cfab0b43401d31890cf4d5110e7c441da096ea45f5 | 19b9afb261f6e2266b4312d4de4f408e83fd785420b7d79d9999bd85829ae6ae |

Scan of the JSON data files in this folder for the same strings (our instance name, local paths, internal run labels, names): no hits, so none were edited.

## Second pass, 31 Oct 2026
Further strings replaced in PLAN_KUMAR.md.text: names of other runs in our queue and an internal record path (no number, rule or logic changed). sha256 of this public copy now: 1e728428abd889495554739fadd845c80518ce983ee7608b2a51363c0507b97b

## Second pass, 31 Oct 2026 (b)
RESULT_KUMAR_KINGSTON.md.text: an internal note about our business records removed from one line (no number changed). sha256 now: 7c8acd198fb5937c803103f0503ada91f40af56aad688b125309a807ef7717e3
