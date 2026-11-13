# Spot-check marking page (12 Nov 2026)
Page: https://claude.ai/artifact/NGhWNQv9bxiNYZNUaYSmt1 (private, db + user).
Sets: A = pre-registered 40 (seed 4242), B = ceiling 20 (seed 1112), C = 20 teacher-PRESENT train rows (seed 1113, not in A).
Built by scripts/build_marks_page.py -> items.json; page = page_head.html + items + page_tail.html.
Marks live in the artifact db, collection "marks", doc id "<set>-<nn>", field mark = yes | no | ct. Read with ArtifactData list.
