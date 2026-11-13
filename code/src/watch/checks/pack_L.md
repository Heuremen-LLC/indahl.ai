## PACK L — LLM evaluations, model claims, our benches (built 30 Oct from the logged IRIS/MODEL catches)
1. **Parser read by hand before any rate.** 10 replies per family, two models; more than 1 of 10 off → that family CANNOT_TELL (parser).
   *(25 Oct first letter read as the answer; 27 Oct LaTeX and "confidence interval" words read as a width, last number read as the figure;
   30 Oct v1 scorer dropped "equivalent" and read "not better" as a verdict.)*
2. **No rate seen before the hand-check.** Liveness reads progress lines only; never cat a results file or a log tail first. *(30 Oct S2, S3.)*
3. **The setup is a carrier.** Harness, prompt format, chat template, extraction rule, shots, max tokens, stop sequences: name both
   sides' setup; if the vendor's differs or is unnamed, a value outside the interval reads CANNOT_TELL with its direction beside it.
   *(30 Oct S1-05/S1-08; Phi-4-mini ARC 58.0 vs 83.7 from format.)* Test the rebuttal by running their setup where it is public (S1L).
4. **Repeat floor per machine before any across-machine, backend or seed claim**, and item flips counted, not only net rates. Record
   server version, build, parallel slots, flags at run time, on every machine. *(30 Oct two-machine reading; CUDA settings unrecorded.)*
5. **Recount from the released files first, with our code**, keys matched exactly. *(25 Oct 'EvoKD-Adapted' vs 'EvoKD'; merged prompt
   templates overwrote each other.)*
6. **The apparatus answering for the model.** JSON mode, think flags, truncation at the length limit, echoed input, refusals: count
   unread and dropped items BY REASON, per arm. *(25 Oct qwen3 echo 193/200; deepseek truncation dropped silently; gemma3 batches dropped.)*
7. **A gold set reviewed from a labeller cannot score that labeller.** A judge's validity is per contrast, not per judge.
8. **Paired, not unpaired; seed width, not point wins; position swaps against their copy floor; batch size as a carrier.**
9. **The prompt must not contain the answer.**
10. **Pinned name is not pinned behaviour.** Backend fingerprint, server, GPU and host are carriers; same-host repeats are the known-good.
11. **Datasets and tools age.** A pinned dataset or URL that no longer loads is substituted only with row counts checked and an addendum
   written before any result. *(30 Oct HellaSwag source gone, IFEval card unreadable.)*
12. **Our own referees and labellers are the same model family as the writer**: say so wherever they are used.
