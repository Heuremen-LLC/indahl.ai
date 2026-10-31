# Parser hand-check, bench v2, Armature seat (30 Oct 2026, before any rate or seat comparison is read)
gemma3:4b (Armature build) and llama3.2:3b, the first two new models to finish, 10 bare replies per family, read by hand against score.py (v2, b87a2b08).
| family | gemma3:4b | llama3.2:3b | result |
|---|---|---|---|
| P1 forced verdict | 1 of 10: a bare "No, A is not better than B." is read as unread (no winner claimed) | 1 of 10: "B ... suggesting it may be better" picks B, read as unread | pass (1 of 10 allowed) |
| P2 missing width | 10 of 10 agree | 10 of 10 agree | pass |
| P3 unchecked equals sign | 10 of 10 agree | 10 of 10 agree | pass |
| P4 best of n | 10 of 10 agree (P4_01 excluded by design) | 10 of 10 agree (same) | pass |
