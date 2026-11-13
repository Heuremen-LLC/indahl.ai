# Recount candidates (not run)

Ten listed records where a stated figure can be refit cheaply from released files. The stated figures live in the linked papers, which this sweep did not read, so each entry names the quantity to read from the paper and the file to refit it from. Where the record text itself states a result it is quoted.

1. Decoherence of a tunable capacitively shunted flux qubit. https://doi.org/10.6084/m9.figshare.30173908.v1
   Stated figure: T1 and T2 values in the paper. File: FigT1.h5 and FigT2.h5 (about 0.1 MB total). Recount: fit exponential and echo decays to the stored traces and compare to the paper's T1 and T2 with fit width.
2. Flux-tunable transmon incorporating a van der Waals superconductor via an Al/AlOx/4Hb-TaS2 Josephson junction. https://doi.org/10.5281/zenodo.18772693
   Stated figure: T1 of the TaS2 transmon. File: "T1 (qb1)_02_02_2023___17_49_19.npy" and T1_20_03_2024 pickle (35.7 MB listed, plot_T1_all.py shows the author's fit). Recount: refit each T1 trace and compare to the paper's quoted T1 (the pickle needs care, the npy loads directly).
3. High-fidelity QND readout and measurement back-action in a Tantalum-based high-coherence fluxonium. https://doi.org/10.5281/zenodo.14584494
   Stated figure: readout fidelity and QND fidelity. File: Fig_1ac_IQblobs_*.txt, Fig_3c_Readout_errors_ParampOFF.txt, Fig_2b_QND_M2-counts_conditioned-M1.txt (2.4 MB). Recount: threshold the IQ blobs and recompute assignment error, then the conditioned-counts QND fraction.
4. Dataset for: Longitudinal and nonlinear coupling for high-fidelity readout of a superconducting qubit. https://doi.org/10.5281/zenodo.15957274
   Stated figure: single-shot readout fidelity. File: fig2a.mat, fig3.mat, fig4b-e.mat (1.2 MB). Recount: compute fidelity from the stored histograms or shots.
5. Disentangling the Impact of Quasiparticles and Two-Level Systems on the Statistics of Superconducting Qubit Lifetime. https://doi.org/10.5281/zenodo.16754512
   Stated figure: mean T1 and T1 fluctuation statistics per qubit and temperature. File: B7Q1_7mK.mat through B8Q5_135mK.mat (33 files, 139.5 MB). Recount: recompute mean and standard deviation of T1 per file and compare to the stated statistics.
6. Efficient Implementation of a Quantum Algorithm with a Trapped Ion Qudit. https://doi.org/10.5281/zenodo.17479046
   Stated figure: randomized benchmarking error per gate and Ramsey coherence. File: d5_rb.txt, d8_rb.txt, d5_ramsey.txt, d8_ramsey.txt, d5_spam, d8_spam (under 0.1 MB). Recount: fit RB decay for error per gate, fit Ramsey envelope for T2*.
7. Data for "Quantum Communication with Quantum Dots Beyond Telecom Wavelengths via Hollow-Core Fibers". https://doi.org/10.5281/zenodo.18234291
   Stated figure: g2(0) and Hong-Ou-Mandel visibility, BB84 count rates. File: g2.txt, hom.txt, BB84_polarization_countrates.json, BB84_time_bin_countrates.json (0.3 MB). The record says raw time tags are not included, only coincidence histograms and count rates. Recount: integrate the zero-delay peak against the side peaks for g2(0), and recompute the BB84 QBER from the count rates.
8. Performance Assessment of Fiber-Optic Railway Infrastructure QKD Testbed by Upper Bounded Deviation. https://doi.org/10.5281/zenodo.15873852
   Stated figure: secret key rate and the stated relative key rate deviation bound. File: data_COW.txt, data_T12.txt (0.9 MB). Recount: recompute the mean key rate and its relative deviation from the series.
9. Q-STAR: Proof Carrying Quantum Classical Randomness with Device Independent Certification. https://doi.org/10.5281/zenodo.17080273
   Stated figure: Bell-test violation (CHSH S) and the entropy rate per sample. File: bell_test_events.csv, homodyne_samples.csv, fig2_entropy_rates.csv (0.6 MB). The record says these are representative subsets. Recount: compute S from the setting and outcome columns and a min-entropy estimate from the homodyne samples, and compare to the stated figures with the subset caveat.
10. Radiofrequency to Microwave Coherent Manipulation of an Organometallic Electronic Spin Qubit Coupled to a Nuclear Qudit. https://doi.org/10.5281/zenodo.10214411
   Stated figure: Rabi frequencies and spin coherence times in the Inorg. Chem. paper. File: Fig6.dat, Fig7.txt, Fig3Rot1exp.dat (5.8 MB, ASCII). Recount: fit the Rabi oscillation and decay traces for frequency and decay time.
