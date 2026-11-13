
## Note (30 Oct 2026, from the site pass)
After each run the rider starts tape_push.py in the background. It commits and pushes only code/tape in the public mirror, so that the leaf links on the page open soon after an entry is written and not at the next release. Nothing else in the mirror is committed. The push is skipped when the public repository holds newer commits, and the release script then pushes the folder with the rest. No rule changed.
