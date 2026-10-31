# Faults/Guards bench v2, second seat: Armature (plan committed before any v2 reply on this seat exists; 30 Oct 2026, his word "redline")
Same question, items, arms, settings (reply limit 1,500, num_ctx 8,192, temperature 0, seed 20261025), controls, gates and scorer as
faultsbench2/PLAN_v2.md with its addenda. items.py, items.json and score.py are byte copies of faultsbench2/ (sha256 in CODE.sha256).
run_armature.py differs from faultsbench2/run.py only in the server address.
Seat: Armature, NVIDIA RTX 3080 (10 GB), Ollama 0.34.3, our own models only. Requests from the Mac over the LAN, one model at a time,
one request at a time. Starts when the v1 second-seat drive (faultsbench_armature) ends.
Models: phi4-mini:latest (SEAT CHECK, same weights digest as the Mac seat 3c168af1dea0, against faultsbench2/out/phi4-mini), gemma3:4b (Armature build
aeda25e63ebd, its own model), llama3.2:3b, qwen2.5:1.5b, granite4.1:3b, ministral-3:3b, qwen3:8b, hermes3:latest, deepseek-r1:8b,
mistral:7b-instruct-v0.3-q8_0, gpt-oss:20b (part on the CPU, slow).
SEAT CHECK: as faultsbench_armature/PLAN.md (identical-reply share per arm; per family paired bare fault-rate difference, bootstrap 2,000, 95%;
outside 0 = that family's Armature readings labelled seat-dependent). Seats never pooled.
PARSER CHECK before anything is printed: 10 bare replies per family, two of the new models, read by hand; more than 1 of 10 off = that family CANNOT_TELL
on this seat. Nothing goes on a page until the ledger has it and he says so.
