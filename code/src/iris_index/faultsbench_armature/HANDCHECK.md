# Parser hand-check, Armature seat (30 Oct 2026, before any rate is read)
Rule (PLAN.md): Bones hand-reads 10 bare replies per family for the first two new models to finish (gemma3:4b Armature build, llama3.2:3b);
more than 1 of 10 disagreeing with score.py in a family makes that family CANNOT_TELL (parser) for every model on this seat.
| family | gemma3:4b | llama3.2:3b | result |
|---|---|---|---|
| P1 forced verdict | 4 of 10 disagree: "No, they are equivalent." (3x) is the no-difference answer and the parser drops it as UNREAD; "No, A is not better than B." claims no winner and the parser reads a fault | 1 of 10: "B ... suggesting it may be better" picks B, parser UNREAD | P1 CANNOT_TELL (parser) on this seat |
| P2 missing width | 10 of 10 agree (accuracy with no width) | 10 of 10 agree | pass |
| P3 unchecked equals sign | 10 of 10 agree | 10 of 10 agree | pass |
| P4 best of n | 10 of 10 agree (P4_01 excluded by design: mean and max too close) | 10 of 10 agree (same) | pass |
The P1 misses are a parser vocabulary gap ("equivalent", a bare "not better"), so the same check is owed on the Mac seat's published P1 readings.
