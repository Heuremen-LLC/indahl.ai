# The check block: specification

Heuremen LLC. Tools: readcheck.py, readcheck_hook.py, install_hook.sh, test_gate.sh (this folder).

An entry is a dated section in a CHECKS.md file beside the reading it covers:

```
## 2026-11-01 14:05 what the reading is
packs: L,P
- I: holds: <what was checked>
- II: fixed: <what was wrong and what changed>
- L6: cannot tell: <why it cannot be decided here>
- P1: n/a: <why the line does not apply>
```

Every core field and every field of each named pack must be answered. An answer starts with holds:, fixed:, caught:, n/a: or
cannot tell:, followed by at least a short sentence. Entries are appended, never edited after they are committed.
The field names skip IV on purpose.

## The core

Required in every entry, in every domain. "holds: <what you checked>" is a legal answer. A blank is not.

**I. THE NONE.** Was the comparison built BEFORE the reading, like for like (same averaging, count, search freedom, moment)? Is the
denominator built from the numerator: does the gate that decides which items count contain the thing being counted (an exclusion that
depends on the effect, a readability filter that one arm fails more often)? Count what the gate drops, by arm.

**II. THE GAP.** Did a net, a mean, a median or a "consistent" zero out a difference that was the reading? Count item by item
(flips in each direction) before you net, and compare against the REPEAT FLOOR of the same setup. A spread between runs is a reading,
not noise to average away.

**III. THE SIGN.** Did a per-cell verdict fold the sign? When several cells each read "consistent", do their signs agree? Is the
effect a product or a sum? Magnitudes and signed values never in one sentence without saying which.

**V. THE RULER.** Name the ruler before the number, and run two side by side when they can disagree: value with width, an exact test on
discordant pairs, the split (S = what every run shares, such as the repeat floor, and P = what moves with the change under test), and a
bound (CONSISTENT is a bound, so print it).

**VI. FOUR OUTCOMES, BOTH ALTERNATIVES.** ABOVE / BELOW / CONSISTENT / CANNOT_TELL, never folded. Test BOTH live alternatives (zero
AND the size that would matter): if the interval reaches both, it is CANNOT_TELL on the question that matters, whatever the label says.

**R. THE RECORD.** Every count, date, time and version read from the file, job record or log, never from memory. A reading defined
after the data says so.

## Pack L: language-model evaluations, model claims, benches

1. **Parser read in full before any rate.** 10 replies per label. More than 10% of the read replies mis-parsed (2 of 10) means that label is
   CANNOT_TELL (parser).
2. **No rate seen before the parser read.** Look at progress lines only until the replies have been read.
3. **The setup is a carrier.** Harness, prompt format, chat template, extraction rule, shots, max tokens, stop sequences: name both
   sides' setup. If the other side's differs or is unnamed, a value outside the interval reads CANNOT_TELL with its direction beside it.
   Test the rebuttal by running their setup where it is public.
4. **Repeat floor per machine before any across-machine, backend or seed claim**, and item flips counted, not only net rates. Record
   server version, build, parallel slots and flags at run time, on every machine.
5. **Recount from the released files first**, with keys matched exactly.
6. **The setup answering for the model.** JSON mode, think flags, truncation at the length limit, echoed input, refusals: count
   unread and dropped items BY REASON, per arm.
7. **A gold set reviewed by a labeller cannot score that labeller.** A judge's validity is per contrast, not per judge.
8. **Paired, not unpaired. Seed width, not point wins. Position swaps against their copy floor. Batch size as a carrier.**
9. **The prompt must not contain the answer.**
10. **A pinned name is not pinned behaviour.** Backend fingerprint, server, GPU and host are carriers. Same-host repeats are the known-good.
11. **Datasets and tools age.** A pinned dataset or URL that no longer loads is substituted only with row counts checked and a note
    written before any result.
12. **A referee or labeller from the same model family as the model under test is not an outside seat.** Say so wherever one is used.

## Pack P: public copy (pages, papers, emails, READMEs, lists)

1. **Quotes are verbatim**, checked against the source text. A paraphrase never sits inside quotation marks.
2. **Every figure says where it lives**: paper text, a table or figure, released data, arithmetic on printed values, a translation, and
   which version.
3. **Setting labels match the source.**
4. **No cause named where only a rule-out was measured**, and "we name no mechanism" must be true of the whole text.
5. **Every interval says what it is** (95%? 99%? standard error?).
6. **A summary line is no stronger than the committed reading.**
7. **The source first, the page after, one release path, verified on the live page.**
8. **Check the rendered page, not just the feed**: every script the page loads answers 200 and the section fills.
9. **Style rules are written down and checked like any other line.**
10. **A reading defined after the data is labelled so** (papers and pages).
