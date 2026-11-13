# The Horn re-read — power_4080.csv segment by segment
2026-09-30, Bones (field hand, laptop-side analysis). Raw data untouched at
`ctrai@laptop:/home/ctrai/horn/20260928_091702/`. Script:
`~/bones-forge/the-horn/reread/horn_analysis.py`, run on the laptop
(single process, light); outputs pulled back as small JSON summaries in the
same directory. Nothing on the Mac's live system was touched.

## Timeline used (EDT, from field_notes.txt)
- 09:17:06 recorder starts (home)
- ~10:37:00 (assumed) last clearly-home window ends / transit begins — NO
  hard marker exists for "left home" or "in car"; this split is a guess,
  flagged below, not a measured boundary.
- 10:57:30 site start, by the chain-link fence, **raining, laptop under an
  umbrella**
- 11:11:25 rain stopped, antenna up toward the sky, **uncovered**, still
  outside the fence
- 11:17:17 (message timestamp) walked through a gap in the fence, stood
  directly beneath the horn on both sides "for a while" — wet gear, soaked
  feet, throughout
- 11:23:15 yodel recorded at the horn
- 11:24:17 tower photo — attention shifts to the boresight tower / excavator
- 12:00:49 recorder stops

Six segments were cut from these anchors: HOME, CAR_GUESS, SITE_RAIN_UMBRELLA,
SITE_DRY_UNCOVERED_OUTSIDE_FENCE, UNDER_HORN_INSIDE_FENCE, and
POST_HORN_OBSERVATION (tower/construction watching). That's the three-way
split (home/car/site) with the site arm itself split into the three
conditions Wayfinder named — rain+umbrella, dry+uncovered+outside-fence,
wet+inside-fence-under-horn — each treated as its own object, not a repeat
of the same test.

## 1. Raw segment numbers (narrowband 4070-4090 MHz, `db_4070_4090`)

| Segment | duration | n | mean dB | median dB | sd | narrow−wide gap |
|---|---|---|---|---|---|---|
| HOME | 4794 s | 14291 | −43.14 | −44.73 | 4.20 | +0.84 |
| CAR_GUESS | 1230 s | 3655 | −46.48 | −46.68 | 1.19 | −0.05 |
| SITE_RAIN_UMBRELLA | 835 s | 2471 | −46.49 | −46.53 | 0.53 | +0.02 |
| SITE_DRY_UNCOVERED_OUTSIDE_FENCE | 352 s | 1056 | **−47.32** | −47.37 | 0.54 | −0.07 |
| UNDER_HORN_INSIDE_FENCE | 420 s | 1243 | −46.65 | −46.43 | 0.80 | −0.03 |
| POST_HORN_OBSERVATION | 2192 s | 6507 | −43.34 | −45.65 | 4.60 | −0.35 |

"narrow−wide gap" = mean(4070-4090) − mean(4000-4160); positive means the
tight 20 MHz window (which holds our own 4080.0000 MHz comb line) reads
louder than the surrounding 160 MHz average.

**What survived:** the quietest stretch of the whole day was NOT under the
horn — it was the 352 s right before he crossed the fence: rain stopped,
antenna up, uncovered, still standing outside the fence (−47.32 dB mean).
Under the horn itself, through the fence, wet, was a close second-quietest
(−46.65 dB) but about 0.7 dB louder than the dry-uncovered-outside-fence
stretch, and slightly louder even than the rain+umbrella stretch's median.
Home and the post-horn tower-watching period are both loud and volatile (sd
4.2–4.6 dB) — the two quiet-instrument-behavior periods bookend the loud
ones almost symmetrically. Car transit (guessed boundary) sits close to the
rain+umbrella level, both far quieter than home.

**Band-specificity:** every site sub-segment's narrow−wide gap is small
(≤0.07 dB) and sits inside sample noise — meaning whatever makes the site
quieter than home is broadband, hitting the tight 4070-4090 window and the
160 MHz window equally. It is NOT a comb-line-specific effect. The one gap
that stands out is HOME's +0.84 dB, i.e. at home the tight window runs
noticeably louder relative to its surroundings than anywhere else all day.
Given ~120 samples/segment worth of averaging behind each mean, that 0.84 dB
gap is well outside its own noise, so it's a real, reproducible feature of
being at home specifically, not the horn — worth someone checking what's on
frequency near 4080-4090 MHz at the house (this dataset can't say what).

**Confound check (battery/USB sag):** a broadband level shift (equal in
narrow and wide bands) is exactly what battery or USB-power sag would look
like. That's what's seen across every site segment. It is consistent with a
sag/gain confound as much as with a physical quiet spot; the data alone
cannot separate "the antenna moved off Wi-Fi/cell clutter" from "the laptop
got colder/lower-power on the battery outdoors in the rain." Noted, not
resolved.

## 2. Continuous trace (30 s bins), site arrival through teardown

Held: the trace confirms the drop is IN THE CONTINUOUS SIGNAL, not only in
the discrete 17 clips analyzed earlier. It dips ~1 dB on arrival (10:57:30),
dips further and stabilizes lowest around 11:11–11:15 (antenna up,
uncovered), stays quiet through 11:17–11:20 (under horn), then a step back
up to home-loud levels begins almost immediately at 11:20:30 (still inside
the under-horn window by clock time) and the trace becomes wildly volatile
(swinging −32 to −46 dB, tens of dB jumps second to second) from about
11:39 onward through the stop at 12:00:49 — this is the construction/tower
period (excavator on site, decommissioning underway per field notes), not a
quiet zone at all. Full trace: `reread/horn_trace_30s.json`.

## 3. Antenna sky/ground flip check (10 s bins, 11:11–11:24)

No clean ~60 s square wave. There is real oscillation on a ~40–80 s scale
between a quiet plateau (~−47.6 dB) and a louder plateau (~−46.8 dB)
between 11:11:40 and 11:17:50 — consistent with, but not proof of, the
described "~1 min sky / ~1 min ground" Y-factor moves; the recorder carries
no flip-time log to confirm which plateau is which orientation. File:
`reread/horn_flip_10s.json`.

## 4. The 20 MHz comb line (4080.0000 MHz) across the 17 wideband sweeps

Tried as a location witness: extracted the 4080–4081 MHz 1 MHz bin from each
of the 17 full sweeps. Result: −42.9 to −73.1 dB, no consistent pattern by
location (site/horn sweeps land both among the loudest and quietest values;
e.g. 11:18 sweep −60.8 dB but 11:28 sweep −44.9 dB, both at/near the horn).
**Did not survive as a witness at this resolution** — 1 MHz bins, one
0.5 s-long sweep per 10-minute mark, and the comb line's own report that it
"sits on the HackRF's DC notch at exact tuning" (Biblioteca 9/28) together
make this too coarse and self-interfering to read as a heartbeat here. Would
need a proper FFT off the raw IQ captures to say anything real about the
comb line's location-dependence. File: `reread/horn_comb_by_sweep.json`.

## 5. Wideband absence check (home sweep 09:17 vs horn-window sweep 11:18)

Median noise floor is nearly identical, home −45.64 dB vs horn −45.52 dB
(0.12 dB apart) — so the overall floor doesn't move, only which discrete
signals poke above it. 179 one-MHz bins were clearly present at home and
gone at the horn (mostly scattered through 0–1000 MHz); 261 bins were
present at the horn and gone at home. This reads as ordinary
location-dependent line-of-sight to different broadcast/land-mobile
transmitters — a textbook explanation, noted and not pursued further. File:
`reread/horn_wideband_diff.json`.

## 6. Reverberation / periodicity check (post-horn teardown segment)

Autocorrelation of the narrowband trace decays smoothly from 0.79 at lag 1
(~0.3 s) with no secondary peak out to lag 60 (~20 s) — no periodic echo
structure found, just strong short-range correlation from the segment's
large, slow, irregular swings (construction-site RF, not a repeating
signal). File: `reread/horn_autocorr.json`.

## Number of tries (look-elsewhere)
Six named segment means/medians (one family), one narrow-vs-wide gap check
per segment (folded into #1), one flip-pattern check, one comb-line-by-sweep
check, one wideband presence/absence check, one autocorrelation check — **6
distinct tests** run against this re-read. Of those: the segment-mean drop
(broadband, present in the continuous trace) held; the comb-line-as-witness
did not survive (too coarse); the flip pattern is suggestive, unconfirmed;
wideband absence is mundane and expected; autocorrelation found nothing.

## Open / next
- The HOME_only narrow-band excess (+0.84 dB) is the one number here that
  doesn't fit its own background — worth a five-minute check at the house
  (what's near 4080-4090 MHz there) before reading anything into the horn
  itself.
- CAR_GUESS boundaries are a guess, not a marker — if an actual departure
  time exists (phone location history, garage door log, whatever), redo
  that split properly.
- The comb line needs the raw IQ files (17 x 100 MB, already on the laptop)
  and a real FFT, not the coarse hackrf_sweep bins, to say anything honest
  about whether it shifts at the horn.

## HOME CHECK, 2026-09-30 ~15:50Z (Wayfinder's hands: antenna unscrewed, then back on; Bones: two 60 s runs of hackrf_sweep 4070-4090, 100 kHz bins, ~800 sweeps each)
- Overall median: antenna -72.5 dB, no antenna -72.45 dB. Identical.
- 4080.0 bin vs band median: antenna -0.06, no antenna +0.06. 4075-4085 mean vs median: 0.00 / +0.01. Flat both ways.
- Strongest with antenna: 4071.0 at +0.66 (edge bin). Nothing at 4080 in either condition.
- Reading: the telescopic antenna makes NO difference at 4 GHz -- the HackRF's own noise is the whole reading up here, with or without it.
  The 9/28 home "+0.84 dB at 4080" is not reproduced today by this method. Caveat: 9/28 used horn_field.py's power_4080 capture at a
  fixed gain during the field recorder run; today used hackrf_sweep defaults. Different ruler. Null recorded with its neighbor:
  the 9/28 number came from the same session that found the 20 MHz clock comb sitting on the DC notch at exact tuning.
- CORRECTION ~16:05Z: the first "antenna on" minute was likely taken with the antenna still OFF (Wayfinder: "I put the antenna back on
  since you didn't really answer"). Real antenna-on minute (antenna2.csv): median -72.47 (no-antenna -72.45); 4080.0 bin +0.15 vs
  +0.06; 4079-4081 mean +0.07 vs 0.00; strongest bin 4078.2 at +0.70. Same verdict: the antenna adds ~0.1 dB of nothing at 4 GHz.
- ~16:15Z THE 0.3, TESTED (Wayfinder: "0.3 across the band -- the null is the time differential written off"). The 4080 bin inside each
  minute, 1600 sweeps in time order: per-sweep sd 5.9 / 5.6 dB; lag-1 autocorrelation 0.00 / -0.03 (shuffle 95th 0.04); lag-10 ~0;
  drift 0.55 / -0.08 dB per minute (inside noise). WHITE. The two runs differ by 0.28 dB at 4080 with z = 1.4 (se 0.15 each).
  Arithmetic: 5.9 / sqrt(1600) = 0.15; two of those differ by ~0.2. The 0.3 is what two one-minute averages of this radio's own noise
  disagree by. Null with its neighbor: no time structure was found at 1-second to 1-minute scales in this record. Not a time differential
  here; the ruler's resolution, measured.
- ~16:25Z RECURSIVE GRADIENT (THIRD_RUNG 41) on the same 4080 series, memories 0.5/0.1/0.02, 200 shuffles each: forward-minus-backward
  mean inside the shuffle band at every memory in both runs (e.g. antenna, memory 0.02: +0.14, band -0.43..+0.41); fraction forward >
  backward 0.48-0.51. No later-affects-earlier structure in this radio's own noise at 4 GHz. Tool saved: parallax/out/recursive_gradient/.
