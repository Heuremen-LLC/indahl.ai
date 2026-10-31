# Faults/Guards bench v2, Mac seat, for models first run on Armature (plan committed before any reply on this seat; 30 Oct 2026)
Purpose: a second seat for the cross-machine check. Armature ran bench v2 on these models (faultsbench2_armature); the Mac seat ran only phi4-mini of
them. Same items, arms, settings, gates and scorer as faultsbench2/PLAN_v2.md (byte copies, CODE.sha256); run.py is faultsbench2/run.py unchanged
(our seat 127.0.0.1:11500).
Models: llama3.2:3b, qwen2.5:1.5b, granite4.1:3b, ministral-3:3b. Their weights digests on Armature equal the registry's today (dde5aa3fc5ff,
183715c43589, 662b0626cd58, 910e4bf4e233); the Mac copies are checked equal to those before any reply.
Readings: per model, the seat comparison of faultsbench_armature/PLAN.md (identical-reply share per arm; per family paired bare fault-rate difference,
bootstrap 2,000, 95%; outside 0 = seat-dependent). Seats never pooled. Parser hand-check before anything is printed. Nothing goes on a page until the
ledger has it and he says so. One GPU job at a time (queued in iris_index/queue.json).
