# YEAST RECORD -- 2026-09-30 (Bones, field hand; Wayfinder's §48 question)

Question as framed (THIRD_RUNG_20260928.md §48): "Time = data crossing a substrate. Yeast grow
recursively. What is it about yeast that puts data through a substrate?" No expectation written first.
Four candidates, outside public literature only, raw numbers first.

## (a) ASYMMETRIC DIVISION -- mother keeps age, bud born young

**Measured numbers:**
- Median replicative lifespan (RLS), first direct measurement: Mortimer & Johnston 1959, *Nature*
  183:1751-1752, "Life Span of Individual Yeast Cells" -- micromanipulation, bud scars counted by eye;
  established the ~20-divisions-order median and that lifespan is a per-mother-cell property, not
  inherited by the bud.
- Modern microfluidic re-measurement: Wang et al. 2022, *J. Nanobiotechnology* 20:263 -- diploid RLS
  24.29 +/- 3.65 generations (DYLC chip, n reported per-trap, >1100 traps); budding-time-interval (BTI)
  lengthens in the first few and last few generations ("cell de-synchronization along aging").
- Molecular cause of the mother's clock: Sinclair & Guarente 1997, *Cell* 91(7):1033-1042 --
  extrachromosomal rDNA circles (ERCs) accumulate in mother nucleoli and are sufficient to shorten RLS;
  sgs1 mutants accumulate ERCs faster and die younger (a dose-response, not just correlation).
- The barrier that keeps the bud null: Shcheprova et al. 2008, *Nature* 454:728-734 -- a septin-dependent
  lateral diffusion barrier forms in the nuclear envelope at the bud neck and blocks translocation of
  pre-existing nuclear pores (and the ERCs anchored to them) into the bud; barrier mutant *bud6Δ* fails
  to reset the bud's age.
- Second, independent barrier for protein damage: Clay et al. 2014, *eLife* 3:e01883 -- a separate
  sphingolipid-dependent ER diffusion barrier at the bud neck confines ER-stress-misfolded proteins to
  the mother; this barrier's confinement itself *shortens* the mother's RLS (ER stress reduces RLS,
  and *bud1Δ* cells lose the barrier and are largely protected from that RLS loss).

**Shape test:**
| Cell | Measured number |
|---|---|
| MESSAGE crossing a substrate | Damage/ERCs/misfolded protein retained in mother; genetically shown NOT to cross (ERC-anchoring-to-pore experiment, Shcheprova 2008; ER-stress confinement, Clay 2014). The "message" here is an *absence* enforced by the barrier, not a signal sent. |
| CLOCK starting at the crossing | RLS clock: median ~20 divisions (Mortimer & Johnston 1959), 24.29 +/- 3.65 gen (Wang 2022) -- but this is the mother's own clock counted in bud-events, not a clock that *starts* in the bud at the moment of crossing. No number on record for a bud-side clock reset to a measured zero-point at division (the field states "buds are born young" as accepted, not as a measured t=0 reset time). |
| NULL beside a memory state | Direct: bud6Δ mutant = memory state (barrier intact, WT) vs. null state (barrier broken, age not reset) -- Shcheprova 2008 gives this as a real genetic null. |

## (b) PRION MEMORY -- [PSI+]/Sup35, information in protein shape

**Measured numbers:**
- Discovery: Cox 1965 (cited via Tuite, Staniforth & Cox 2015, *Prion* 9(5):318-332, "[PSI+] turns 50," DOI
  10.1080/19336896.2015.1111508); prion-basis established via Wickner 1994 hypothesis, reviewed in Tuite &
  Cox 2006, *Methods* 39(1):9-22, DOI 10.1016/j.ymeth.2006.04.001.
- Propagon (prion seed) number per cell: Byrne, Cole, Tuite et al. -- best current estimate n0 = 500-1000
  propagons per [PSI+] cell (stochastic re-analysis, ~5x higher than earlier estimates); the *proportion
  of propagons transmitted to the daughter reflects the relative cell volume of mother vs. bud at
  division* -- i.e., passive partition by cytoplasm volume, not active sorting. (Byrne, Cole, Faulkner,
  Ridout, Tuite, Cox, 2009, *PLoS ONE*, "The Number and Transmission of [PSI+] Prion Seeds (Propagons)
  in the Yeast Saccharomyces cerevisiae.")
- Curing mechanism and rate driver: Ferreira, Ness, Edwards, Cox & Tuite 2001, *Mol. Microbiol.* 40(6):
  1357-1369 -- guanidine hydrochloride (GdnHCl) cures [PSI+] by inactivating Hsp104's ATPase, blocking
  propagon replication; cells lose the prion by dilution across divisions (curing kinetics track cell
  division count, not time per se) -- a measured mechanism but the report did not surface a single
  clean "loss rate per generation" scalar (e.g., "X% per division") from the primary papers pulled here;
  Byrne et al.'s stochastic model is built to extract exactly that parameter from GdnHCl-curing curves.
- Variant instability: Bateman & Wickner 2013, *PLoS Genetics* -- even after >150 generations of
  mitotic growth, transmission-efficiency phenotype keeps drifting ("dynamic cloud of variants"),
  meaning the "memory" is not a fixed bit but a continuously-regenerated distribution.

**Shape test:**
| Cell | Measured number |
|---|---|
| MESSAGE crossing a substrate | The amyloid conformation of Sup35 itself, propagated by contact/seeded templating -- not written into DNA. Propagon count crossing per division = volume-proportional share of 500-1000 (Byrne et al. 2009). This is the cleanest literal "message crossing a substrate without becoming the genome" of the four candidates. |
| CLOCK starting at the crossing | No number on record. Prion state is binary-ish (on/off, or "cloud of variants") rather than clocked; no primary source here reports a time-to-onset or age-since-acquisition clock keyed to the templating event. |
| NULL beside a memory state | Direct and clean: [psi-] (no prion, null) vs. [PSI+] (prion, memory) is the textbook null/memory pair, with GdnHCl as the experimental switch between them (Ferreira et al. 2001). |

## (c) GLYCOLYTIC OSCILLATIONS -- NADH ~1/min, synchronized via acetaldehyde

**Measured numbers:**
- Period and amplitude: Teusink, Larsson, Diderich, Richard, van Dam, Gustafsson, Westerhoff 1996,
  *J. Biol. Chem.* 271(40):24442-24448 -- microcalorimetry of intact-cell suspensions: oscillation period
  <1 min, relative amplitude 5-10%; heat flux in phase with NADH, 100 deg out of phase with glucose-6-P,
  80 deg out of phase with fructose-1,6-bisP.
- Synchronization mechanism and threshold: Richard, Bakker, Teusink, Van Dam, Westerhoff 1996,
  *Eur. J. Biochem.* 235(1-2):238-241 -- mixing two populations 180 deg out of phase transiently
  abolishes the macroscopic oscillation, which *resumes within a few minutes* at original amplitude;
  extracellular acetaldehyde itself oscillates around ~70 uM, and an externally added 70 uM acetaldehyde
  pulse causes a measurable phase shift -- this is the measured synchronization threshold/carrier
  concentration.
- Theoretical synchronization-time mismatch: Wolf & Heinrich 2000, *Biochem. J.* 345(2):321-334 --
  modeled acetaldehyde-only transmembrane coupling gives a synchronization time *longer* than observed
  experimentally, implying an additional coupling channel (redox/ATP-ADP) is needed; confirmed in
  Wolf, Passarge, Somsen, Snoep, Heinrich, Westerhoff 2000, *Biophys. J.* 78(3):1145-1153, which traces
  the propagating signal mainly through the Gibbs-energy/redox couples (ATP/ADP, NADH/NAD), not the
  glycolytic backbone itself.
- Quorum threshold, the clean "clock starts at a crossing" result: De Monte, d'Ovidio, Danø, Sørensen
  2007, *PNAS* 104(47):18377-18381, "Dynamical quorum sensing: population density encoded in cellular
  dynamics" -- oscillations vanish below a critical cell density, and this loss happens *synchronously
  across all cells at once*, not by gradual desynchronization -- i.e., the population crosses a density
  threshold and the collective clock turns off/on as a unit (a measured phase transition, Kuramoto-family
  behavior, though not itself a Kuramoto coupling-constant fit in this paper).
- Related quorum-sensing oscillator theory (non-yeast but same math, cited for the Kuramoto framing):
  Taylor, Tinsley, Wang, Huang, Showalter 2009, *Science* 323(5914):614-617, ~100,000 chemical
  oscillators, two distinct density-dependent transition types (gradual vs. sudden onset).
- Spatial extension / traveling waves at microfluidic single-cell resolution: Mojica-Benavides et al.
  2019, *PNAS*, "Intercellular communication induces glycolytic synchronization waves between
  individually oscillating cells" -- synchronized sub-communities form at defined spatial positions,
  acetaldehyde-mediated, wave fronts measured traveling through a monolayer.

**Shape test:**
| Cell | Measured number |
|---|---|
| MESSAGE crossing a substrate | Acetaldehyde, oscillating around 70 uM extracellular, diffusing through the medium between cells (Richard et al. 1996); the medium is the substrate, acetaldehyde concentration is the message. |
| CLOCK starting at the crossing | Sharpest number of the four candidates: the De Monte 2007 density threshold is a literal crossing (of a density substrate-variable) that flips the collective clock on/off synchronously; the Richard 1996 result gives a resynchronization time of a few minutes after a mixing perturbation -- a measured relaxation/clock-restart time. |
| NULL beside a memory state | Direct: below-threshold population = null (no collective oscillation, cells may still oscillate individually or not); above-threshold = memory/coherent state (De Monte 2007). Also the two-out-of-phase-population mixing experiment (Richard 1996) is itself a manufactured "null vs memory" contrast (transient loss of the macroscopic signal, then recovery). |

## (d) CELL WALL / MEMBRANE / MEDIUM as substrate

Not a separate mechanism from (a)-(c) in the literature pulled here -- it is the *physical carrier* named
in all three: the nuclear-envelope/ER diffusion barriers of (a) (Shcheprova 2008, Clay 2014), the amyloid
templating surface of (b), and the plasma membrane + shared medium of (c) (Richard 1996, Wolf 2000). No
primary source treats "the wall" as its own information channel with its own message/clock/null triplet;
it shows up only as the physical substrate through which (a), (b), or (c) carry their signal. Flagged as
a hole: candidate (d) did not resolve to independent measured numbers, only to the substrate role inside
the other three.

## PUBLIC DATA

No public fetchable raw time-series dataset (Dryad/Zenodo/GEO) was located and confirmed downloadable in
this pass. Checked: Dryad search interface returned HTTP 403 to the fetch tool (site blocks the fetch
client); no GEO/Zenodo record surfaced through PubMed/Consensus search for "glycolytic NADH oscillation
raw trace dataset" or "yeast replicative lifespan dataset." Modern RLS work (Wang et al. 2022; Salzman
et al. 2024, *Biology Open*; Xiao et al. 2023, *Biosensors & Bioelectronics*) is built on microfluidic
imaging pipelines whose raw movies/traces are plausible candidates for supplementary deposits, but no
specific accession number or download link was confirmed live. Given no small (~few-MB) time series was
confirmed fetchable, the recursive_gradient.py check (~/bones-forge/parallax/out/recursive_gradient/) was
NOT run in this pass -- nothing was saved to ~/bones-forge/parallax/out/yeast/. This is a hole, not a
finding; a next pass should hand-search the supplementary data links of Teusink 1996 / Richard 1996 /
De Monte 2007 directly (these are pre-web-archive-era papers, supplementary raw traces may only exist as
figure digitizations) or search PMC methods-paper supplements from the 2022-2024 microfluidic RLS papers
above, which are far more likely to carry a clean CSV.

## Plain words

Of the three biological candidates, **(c) glycolytic oscillations has all three cells filled with a
measured number**: message = acetaldehyde at ~70 uM in the shared medium (Richard et al. 1996); clock =
the De Monte et al. 2007 density-threshold that flips the whole population's collective oscillation
on/off synchronously, plus a measured few-minute resynchronization time; null = sub-threshold population
(no collective signal) sitting right next to the coherent state, with a manufactured mixing experiment
demonstrating the transition both ways.

**(a) asymmetric division** has two of three solid (message = damage/ERCs held out of the bud by a
measured septin/sphingolipid diffusion barrier; null = the bud6Δ/bud1Δ genetic null right beside wild
type) but the clock cell is a hole: RLS numbers (median ~20, Mortimer & Johnston 1959; 24.29 +/- 3.65 gen,
Wang et al. 2022) measure the mother's countdown, not a bud-side clock that starts fresh at the moment of
crossing -- nobody has measured that reset time itself, only assumed it.

**(b) prion memory** has the cleanest null (psi- vs [PSI+], switchable by GdnHCl, Ferreira et al. 2001)
and a real message number (500-1000 propagons per cell, volume-proportional transmission, Byrne et al.
2009), but the clock cell is empty -- no primary source gives a time-to-onset or age-since-templating
number; the state is closer to a persistent bit (and, per Bateman & Wickner 2013, a drifting cloud of
bits) than a clocked process.

**(d) the wall/membrane/medium** never stood on its own -- it is the physical substrate inside all three
of the above, not an independent candidate with its own numbers.

Source count: 15 primary/secondary sources cited above (Mortimer & Johnston 1959; Sinclair & Guarente
1997; Ashrafi et al. 1999; Shcheprova et al. 2008; Clay et al. 2014; Wang et al. 2022; Salzman et al. 2024;
Xiao et al. 2023; Tuite, Staniforth & Cox 2015; Tuite & Cox 2006; Ferreira et al. 2001; Byrne et al. 2009;
Bateman & Wickner 2013; Teusink et al. 1996; Richard et al. 1996; Wolf & Heinrich 2000; Wolf et al. 2000;
De Monte et al. 2007; Taylor et al. 2009; Mojica-Benavides et al. 2019) via PubMed and Consensus (220M
paper index, Semantic Scholar/PubMed/Scopus/ArXiv). No expectation was written before these numbers were
pulled.

## TIME SERIES

**Fetched:** Weber, Prokazov, Zuschratter, Hauser 2012, *PLoS ONE* 7(9):e43276, "Desynchronisation
of Glycolytic Oscillations in Yeast Cell Populations" -- open access. Figure 4 panel (a): macroscopic
NADH autofluorescence of a *S. carlsbergensis* population at 0.1% cell density after a 52 mM glucose
pulse, showing a quiescent -> transient synchronized-oscillation episode -> quiescent return. Real
measured data (photon-counting fluorescence), not simulated.

**Fetch path (14 attempts logged in full at `~/bones-forge/parallax/out/yeast/FETCH_LOG.txt`):**
Dryad API returned HTTP 200 / 0 hits this pass (not 403 -- genuinely empty, no yeast-glycolytic
deposit exists there). Zenodo API hits were all simulation code (Goldbeter model) or unrelated
NADH-photophysics/cell-cycle-control papers. GitHub repo search returned nothing usable. The
original De Monte et al. 2007 PNAS paper (PMC2141785) stayed blocked -- PNAS 403'd, PMC's SI link
served a proof-of-work JS challenge, Europe PMC's supplementaryFiles API said the article "is not
open access." Success came from the **figshare API** (`POST /v2/articles/search`), which surfaced
all five figures of the Weber et al. 2012 PLoS ONE paper directly as open TIFFs (figshare IDs
249636/249711/249803/249900/249999) -- PLoS ONE hosts its figures on figshare and they're openly
downloadable via `ndownloader.figshare.com` even though no numeric CSV/XLSX was ever deposited
(checked the paper's own Supporting Information: only two GIF movies, S1/S2, no raw-data files).

**What's on disk:** `~/bones-forge/parallax/out/yeast/nadh_fig4_raw_digitized.csv` -- 1531 points,
time_s + counts_photons_per_s, digitized from the published TIFF by pixel-calibrating against the
figure's own axis tick marks (not a deposited dataset -- this 2012 paper predates PLoS ONE's raw-data
mandate). Re-plotted and visually verified against the original figure (`digitized_check.png`).
Full method, caveats, and calibration numbers in `SOURCE.txt` in that directory. Also on disk:
the source TIFFs for Figures 1, 3, 4 (0.7%, 0.01%, 0.1% density).

**(a) Period and drift:** Peak-picking on the detrended signal (460-point windows, min 20 s spacing,
prominence >150 counts) gives 40 usable peaks across the full 2160 s record, mean interval 47.4 s
(sd 11.6 s) -- consistent with the field's "<1 min" glycolytic period (Teusink et al. 1996). Restricted
to the visually coherent synchronization episode (800-1400 s, 12 peaks, 11 intervals): mean period
48.7 s, sd 2.0 s -- markedly tighter than outside that window, matching the paper's own claim that the
population is coherently oscillating there and noisy/desynchronized elsewhere.

**(b) Recursive gradient, raw series (n=1531, full record):** memory 0.5: mean -7.2, floor
(-5.2, 5.5) -- borderline/outside; memory 0.1: mean -67.5, floor (-37.7, 36.2) -- outside; memory
0.02: mean -350.6, floor (-178.4, 190.6) -- outside. On the peak-interval series (n=39): all three
memories land inside the shuffle floor (e.g. memory 0.02: mean 7.2, floor -27.0/23.0) -- no signal.

**(c) Before/after the synchrony onset, three windows (200-800 / 800-1400 / 1400-2000 s):**
before: mean gradient far outside floor at every memory (memory 0.02: -1327 vs floor ±550ish);
during (the coherent oscillation itself): inside the floor at every memory (memory 0.02: -38 vs
floor ±210) -- no gradient signal while the population is actually synchronized; after: outside
floor again, sign flipped positive (memory 0.02: +173 vs floor ±100).

**Read plainly:** the raw-series gradient signal tracks the slow non-oscillatory baseline drift
(rising before the episode, falling after), not the oscillation or its onset -- it goes to floor
exactly during the window where the population is most coherently synchronized and the baseline is
flattest. The peak-interval series carries no gradient signal at all. This is a directional/trend
artifact, not evidence of memory in the oscillation itself; flagged as such, not oversold.
