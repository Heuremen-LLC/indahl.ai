# Spot check, 20 pairs (seed 1112, random.sample over judgments.jsonl order)

Judge was Claude Sonnet, one reader. A person should check these. Fill the last line of each entry.

## 1. 117e55b1a2f6 F5
Judgment: PARTLY
Quote: We observe a relative gain of up to ~ 34% in out-of-sample test scores for those models with access to quantum hardware-transformed data
Note used: [no per-code basis on List; recount found text] AUC 0.97 against about 0.63: +34 AUC points, not a relative gain (that would be about 54%)
Abstract: Enhanced fill probability estimates in institutional algorithmic bond trading using statistical learning algorithms with quantum computers

The estimation of fill probabilities for trade orders represents a key ingredient in the optimization of algorithmic trading strategies. It is bound by the complex dynamics of financial markets with inherent uncertainties, and the limitations of models aiming to learn from multivariate financial time series that often exhibit stochastic properties with hidden temporal patterns. In this paper, we focus on algorithmic responses to trade inquiries in the corporate bond market and investigate fill probability estimation errors of common machine learning models when given real production-scale intraday trade event data, transformed by a quantum algorithm running on IBM Heron processors, as well as on noiseless quantum simulators for comparison. We introduce a framework to embed these quantum-generated data transforms as a decoupled offline component that can be selectively queried by models in low-latency institutional trade optimization settings. A trade execution backtesting method is employed to evaluate the fill prediction performance of these models in relation to their input data. We observe a relative gain of up to ~ 34% in out-of-sample test scores for those models with access to quantum hardware-transformed data over those using the original trading data or transforms by noiseless quantum simulation. These empirical results suggest th
Person's judgment: 

## 2. 9feb1c4f3cda F6
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: Table XII caption gives 450 trials per cell for every row, while the two decomposition cells fit 167/205 and 85/93. The author confirmed both counts on 2 Nov 2026 and says Zenodo v1.8 will add an n column and a corrected caption (not yet read)
Abstract: UniMind: Calibration-Aware Scheduling and Placement for Quantum-Accelerated AI Middlewars

UniMind is a user-space middleware for quantum-accelerated AI workloads that scores, places, executes, and refreshes calibration data in a closed loop. This record contains the v7 manuscript in two editions (12-page full and 6-page compact), each as compiled PDF and LaTeX source. The paper is a measurement study of how a quantum runtime should maintain scheduling decisions when hardware calibration changes over time. We instrument a 156-qubit superconducting device (ibm_marrakesh) across three primary daily snapshots (D0-D2, 2026-08-29 to 08-31) plus 34 hourly calibration snapshots (2026-09-01 to 09-02, three backends: marrakesh, kingston, fez). Four findings: (1) calibration validity is temporally bounded and small (day-over-day rank correlation 0.579, top-10 Jaccard 0.25, stale top-3 pins 1.94-2.1x worse across 24-34 h; hourly top-3 margins ~1e-3 vs median |dC| = 0.0127); we formalize the Calibration Validity Horizon T_valid as a lower-bound design primitive. (2) Adaptive refresh (top-10 Jaccard   0.005, ~0.04 ms per scoring pass) dominates static and periodic policies at near-zero cost; a 144-threshold sweep places the default at the Pareto knee. (3) Refresh, not placement selection, dominates end-to-end reliability at the measured scale (+33/37 pp with fresh pins; pinned vs free is a bounded null, 70.0% vs 76.7%, Fisher p = 0.77, MDE ~ 32 pp). (4) Proxy-trained layout models do not 
Person's judgment: 

## 3. bc4d8a32f146 F6
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] From the printed means and SDs: ER-10 0.990 vs 0.981 (diff +0.009, unpaired z ~ +2.0). ER-20 0.992 vs 0.994 (diff -0.002, z ~ -0.5, reversed). RG-3 0.996 vs 0.991 (diff +0.005, z ~ +2.5). AR at iteration 10: ER-10 0.983 vs 0.968, ER-20 0.990 vs 0.987, RG-3 0.994 vs 0.991. Does not reproduce (sign reverses on ER-20 at convergence, every class lies inside ~2.5 sd, z is ours, unpaired, instances may be paired)
Abstract: Quantum Approximate Optimization via Noise-Directed Adaptive Warm-Starting

Progress towards a quantum advantage using known heuristic methods for combinatorial optimization is impeded by hardware noise and limited qubit count. Here, we propose a noise-aware adaptive approach to quantum approximate optimization, Noise-Directed Adaptive Warm-Starting (ND-AWS), that builds on recent concepts such as Warm-Start QAOA and Noise-Directed Adaptive Remapping. By leveraging bitflip gauge transformations, our algorithm exploits amplitude-damping-like noise components. We experimentally implement high-performance quantum optimization ansätze on 100-qubit Ising Hamiltonians, showing that ND-AWS generally improves the performance over a non-gauge-transformed iterative Warm-Starting variant, at no additional circuit cost. This places our results among the highest-quality demonstrations of quantum optimization with similar ansätze at this scale. Crucially, the simplicity of the framework opens the door for future enhancements such as adaptive bias schedules, and integration with classical solvers.
Person's judgment: 

## 4. cff8f652ebba F7
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] Simulated annealing on one CPU core reaches the CPLEX optimum on all 8 unweighted Table 1 instances in about 0.1 s or less, against 7–8 min of QPU reported
Abstract: Integrated error-suppressed pipeline for quantum optimization of nontrivial binary combinatorial optimization problems on gate-model hardware at the 156-qubit scale

Abstract We introduce a novel hybrid quantum–classical variational optimization method for unconstrained binary combinatorial optimization problems on gate-model quantum computers, integrating a custom variational ansatz, staged feedback-based dual variational parameter update strategies, efficient parametric compilation, automated error suppression during hardware execution, and scalable O( n ) classical post-processing to correct for bitflip errors. Without this integrated approach, we show that standard circuit execution at scale produces output indistinguishable from random sampling, establishing the necessity of each pipeline component. We benchmark the method on IBM superconducting quantum computers for several optimization problems drawn from NP-hard problem classes, where the optimization is conducted on hardware with no use of classical simulation or prior knowledge of the solution. For Max-Cut on random regular graphs with topologies not matched to device connectivity, the method achieves approximation ratios (AR) of 100% for unweighted 3-regular graphs up to 156 nodes, weighted regular graphs up to 80 nodes, and weighted 7-regular graphs up 50 nodes. Applied to higher-order binary optimization, the method finds the ground state energy of 127- and 156-qubit spin-glass models matched to device topology w
Person's judgment: 

## 5. b4adf48f932c F5
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] Table I node-minutes give 33.8x and 25.3x per decade. The last step is not a test, since runs stop at a wall-clock limit and the paper does not say which did
Abstract: Closed-loop calculations of electronic structure on a quantum processor and a classical supercomputer at full scale

Quantum computers must operate in concert with classical computers to deliver on the promise of quantum advantage for practical problems. To achieve that, it is important to understand how quantum and classical computing can interact together, and how one can characterize the scalability and efficiency of hybrid quantum–classical workflows. So far, early experiments with quantum-centric supercomputing workflows have been limited in scale and complexity. Here, we use a Heron quantum processor deployed on premises with the entire supercomputer Fugaku to perform the largest computation of electronic structure involving quantum and classical high-performance computing. We design a closed-loop workflow between the quantum processors and 152,064 classical nodes of Fugaku, to approximate the electronic structure of chemistry models beyond the reach of exact diagonalization, with accuracy comparable to some all-classical approximation methods. Our work pushes the limits of the integration of quantum and classical high-performance computing, showcasing computational resource orchestration at the largest scale possible for current classical supercomputers.
Person's judgment: 

## 6. c620932a0f2f F4
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: hardware run dates, job ids, qubit layout, shots per randomisation under TREX, the definition of "-Hardware" versus "-Hardware-EM", the emulator's construction and whether it includes mitigation, per-run vectors for the emulators, QPU ...
Abstract: A 1-bit quantum filter for particle trajectory reconstruction

Abstract The transition to the High-Luminosity Large Hadron Collider (HL-LHC) presents a computational challenge where particle reconstruction complexity may outpace classical computing resources. While quantum computing offers potential speedups, standard algorithms like Harrow-Hassidim-Lloyd (HHL) require prohibitive circuit depths for near-term hardware. Here, we introduce a 1-Bit Quantum Filter, a domain-specific adaptation of HHL that reformulates tracking from matrix inversion to binary ground-state filtering. By replacing high-precision phase estimation with a single-ancilla spectral threshold and exploiting the Hamiltonian’s sparsity, we achieve an asymptotic gate complexity of $${{\mathscr{O}}}(\sqrt{N}\log N)$$ O ( N log N ) , given Hamiltonian dimension N . We validate this approach on LHCb Monte Carlo events, demonstrating segment finding efficiency highly competitive with the classical state-of-the-art methods. Furthermore, we benchmark performance using the Quantinuum System Model H2 trapped-ion processor and IBM Heron R3 superconducting processor. This work establishes a quantum track reconstruction method capable of solving realistic event topologies on noise-free simulators and smaller tracking scenarios within the current constraints of the Noisy Intermediate Scale Quantum (NISQ) era. Remaining challenges toward a full end-to-end tracking solution include an efficient readout and Hamiltonian cons
Person's judgment: 

## 7. b907a4b7ec3e F6
Judgment: PARTLY
Quote: We present an empirical study of circuit-depth thresholds on IBM Quantum Heron-class hardware using 4- and 5-qubit GHZ-state preparation circuits
Note used: [no per-code basis on List; recount found text] Population printed as fidelity. 'GHZ fidelity' is defined as P(0...0) + P(1...1), the population only. GHZ fidelity is (P + C)/2 with C  83.7% decay are upper bounds on fidelity. Parity  is also Z-basis only.
Abstract: Empirical Noise-Adaptive Circuit-Depth Thresholds on IBM Quantum Heron-Class Devices

We present an empirical study of circuit-depth thresholds on IBM Quantum Heron-class hardware using 4- and 5-qubit GHZ-state preparation circuits with logical depths from 2 to 20. On ibm_torino, we observe qubit-count-dependent depth limits: 4-qubit circuits reach a fidelity plateau near 88% beyond depth 10, while 5-qubit circuits show continued decay from 89.4% to 83.7% over the same range. The observed fidelity at depth 20 substantially exceeds predictions from an independent gate-error model (88% vs. 61%), indicating coherent error effects and partial error cancellation not captured by simple accumulation models. These results provide hardware-specific depth bounds for near-term quantum circuits and support calibration-based depth selection over fixed heuristics. We recommend a maximum depth ≤ 10 for applications requiring >85% fidelity on this hardware.
Person's judgment: 

## 8. eeeb59274f80 F7
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] Their headline says 'up to 3-4× reduction in wall clock time when utilising four QPUs'. Their Table 2 gives 2.64x on four QPUs and 2.45x on a single QPU run in parallel. A simple classical method, simulated annealing, is printed by the authors themselves at 2.3 s with 213 optimal solutions, against 0 optimal solutions on Kingston.
Abstract: Towards High Performance Quantum Computing (HPQ): Parallelisation of the Hamiltonian Auto Decomposition Optimisation Framework (HADOF)

Practical applicability of quantum optimisation on near term devices is constrained by limited qubit counts and hardware noise, which restricts the scalability of quantum optimisation algorithms for combinatorial problems. The simulation of large quantum circuits is also difficult and constrained by memory requirement. The Hamiltonian Auto Decomposition Optimisation Framework (HADOF) addresses this by decomposing large QUBOs into smaller subproblems that can be solved iteratively on quantum or classical backends. This allows the scalability of quantum QUBO algorithms beyond device limits, as well as their simulation on classical devices. In this research, we extend the evaluation of HADOF by benchmarking on real IBM QPUs across sequential, single-QPU parallel, and multi-QPU parallel execution modes, advancing toward High Performance Quantum (HPQ) computing for combinatorial optimisation problems. Experimental results on IBM quantum hardware demonstrate up to 3-4x reduction in wall clock time when utilising four QPUs compared to sequential execution baseline, while maintaining comparable solution quality. Notably, even single QPU execution benefits from parallelised job orchestration and execution, yielding up to 3x speedup. Simulated results predict over 5x speed-up in parallel execution mode. We further validate the practical applicability o
Person's judgment: 

## 9. 81b8b9ef5700 F4
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: run date, job id, layout (physical qubits), transpiled depth and CZ count, shots actually used ("we assume Nshots = 1024"), counts, data or code statement, calibration stamp for the medians ("at the time of the experiment"), how E is ...
Abstract: Geometric Measure of Entanglement of Rank-2 Mixed Multiqubit States and its Estimation on a Quantum Processor

The geometric measure of entanglement of mixed states is investigated based on its relation to spin correlations. We derive an analytical expression for the entanglement of rank-2 mixed states composed of arbitrary multiqubit pure states within a two-dimensional Hilbert subspace. The dependence of the entanglement of rank-2 mixed multiqubit states on the parameters characterizing arbitrary pure states in the mixture is studied both analytically and using quantum computing. For a particular class of mixed states, namely, equal-probability mixtures of an arbitrary multiqubit state and the Schrödinger cat state, we construct quantum protocols for detecting the geometric measure of entanglement based on its relation to spin correlations. We quantify the entanglement using both the AerSimulator and the ibm_marrakesh quantum computer. The effects of quantum-computing errors are also analyzed. The simulation results reproduce the analytical dependencies, while measurements on the quantum device demonstrate good agreement with theoretical predictions within estimated error bounds.
Person's judgment: 

## 10. fad148ca986b F6
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] Ratios rebuild. Run counts do not reconcile
Abstract: Hybrid Quantum-Classical Optimisation of Traveling Salesperson Problem

The Traveling Salesperson Problem (TSP) is a fundamental NP-hard optimisation challenge with widespread applications in logistics, operations research, and network design. While classical algorithms effectively solve small to medium-sized instances, they struggle with scalability due to exponential complexity. In this work, we present a hybrid quantum-classical approach that leverages IBM's Qiskit Runtime to integrate quantum optimisation techniques with classical machine learning methods, specifically K-Means clustering and Random Forest classifiers. These machine learning components aid in problem decomposition and noise mitigation, improving the quality of quantum solutions. Experimental results for TSP instances ranging from 4 to 8 cities reveal that the quantum-only approach produces solutions up to 21.7% worse than the classical baseline, while the hybrid method reduces this cost increase to 11.3% for 8 cities. This demonstrates that hybrid approaches improve solution quality compared to purely quantum methods but remain suboptimal compared to classical solvers. Despite current hardware limitations, these results highlight the potential of quantum-enhanced methods for combinatorial optimisation, paving the way for future advancements in scalable quantum computing frameworks.
Person's judgment: 

## 11. 5674aee2e2d1 F2
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: "The 70.7% difference in CX gate error is particularly striking, ... and it directly explains the large zero-shot KL divergence": a mean over couplers where 5 vs 9 unusable couplers make up 87% to 91% of the mean. Medians differ by -1.4%. ...
Abstract: Few-Shot Cross-Device Transfer for Quantum Noise Modeling on Real Hardware

In the noisy intermediate-scale quantum (NISQ) regime, quantum devices contain hardware-specific noise sources which restrict device-invariant error mitigation strategies. We explore transfer learning approaches to apply noise models learned on one quantum device to a different device with the help of a small amount of data. We create a real-hardware dataset from two IBM quantum devices, ibm_fez (source) and ibm_marrakesh (target), comprising 170 noisy and ideal circuit output distributions, with device calibration features added. We train a residual neural network on the source device to map noisy to ideal outcomes. The zero-shot transfer test shows a KL divergence of 1.6706 (up from 0.3014), establishing device specificity. With K = 20 fine-tuning samples, KL drops to 1.1924 (28.6% improvement over zero-shot), recovering 34.9% of the gap between zero-shot and in-domain KL. Ablation studies reveal that the major cause of mismatches across devices is CX gate error, followed by readout error. The results show quantum noise can be learned and fine-tuned with minimal samples, and provide a plausible approach to cross-device quantum error mitigation.
Person's judgment: 

## 12. b0f0db610d8b F1
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: IBM KCuF3 2603.15608: the classical MPS "set an upper bound on the accuracy", and the circuits were compiled from that same MPS, then graded against it
Abstract: Benchmarking quantum simulation with neutron-scattering experiments

Realistic simulation of quantum materials is a central goal of quantum computation. Although quantum processors have advanced rapidly in scale and fidelity, it has remained unclear whether pre-fault-tolerant devices can perform quantitatively reliable material simulations. We demonstrate that a superconducting quantum processor operating on up to 50 qubits can already produce meaningful, quantitative comparisons with inelastic neutron-scattering measurements of KCuF$_3$, a canonical realization of a gapless Luttinger liquid system with a strongly correlated ground state and a spectrum of emergent spinons. The quantum simulation is enabled by a quantum-classical workflow for computing dynamical structure factors (DSFs). The resulting spectra are benchmarked against experimental measurements using multiple metrics, highlighting the impact of circuit depth and circuit fidelity on simulation accuracy. Finally, we extend our simulations to a 1D XXZ Heisenberg model with next-nearest-neighbor (NNN) interactions and a strong anisotropy, producing a gapped excitation spectrum, which could be used to describe the CsCoX$_3$ compounds above the Néel temperature. Our results establish a framework for computing DSFs for quantum materials in classically challenging regimes of strong entanglement and long-range interactions, enabling quantum simulations that are directly testable against laboratory measurements.
Person's judgment: 

## 13. 0af882d5335f F3
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: "The policy transfers successfully" / "improves ... on all representative benchmarks": counts of positive cells with no width, one record per cell (n_records_same_key = 1 for the 16 Fig. 11 cells), no seed repeat
Abstract: TuniQ: Autotuning Compilation Passes for Quantum Workloads at Scale for Effectiveness and Efficiency

Quantum processors are being integrated into HPC ecosystems as co-processors, where compilation of quantum circuits into hardware-executable form determines both output fidelity and runtime. Current compilers use a fixed pass sequence and ignore the fact that optimal pass selection varies with circuit, hardware, and noise conditions. We present TuniQ, a reinforcement learning-based system that selects compilation passes at each pipeline stage, adapting to circuit, backend, and current noise profile. TuniQ introduces several novel design components like a dual-encoder for stage-aware representation, shaped rewards for cross-stage credit assignment, and dynamic action masking for valid compilation. Evaluated across diverse quantum workloads on multiple IBM Quantum Cloud processors, TuniQ improves fidelity and reduces compilation time over the state-of-the-art IBM Qiskit transpiler, generalizes across backends without retraining, and scales strongly to utility-scale circuits with growing advantage.
Person's judgment: 

## 14. b846af5ff863 F4
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: No circuits or counts released (24 Oct batch 13): NUS+Lanzhou 2610.22482 (on request), Sydney+IBM 2610.11658, Indiana+LBNL 2610.18482 || error bars on every hardware point (Fig 3a has none). N_circ. Shots. Run dates. Job ids. Layout as numbers (Fig S4 colour map only). ZNE scale factors, folding and extrapolation form. Whether each plotted point is raw or ZNE-corrected ...
Abstract: Exploring Quantum Phase Transitions Beyond Landau Theory on a Quantum Processor

Direct continuous quantum phase transitions between phases that break distinct symmetries challenge the conventional Landau-Ginzburg-Wilson paradigm and provide a framework for deconfined quantum criticality. Here, we investigate a Landau-forbidden ferromagnetic-to-valence-bond-solid (FM-VBS) transition in a frustrated one-dimensional spin chain using superconducting quantum processors. Combining matrix-product-state-assisted circuit preparation with quantum-hardware measurements, we resolve the suppression of long-range ferromagnetic correlations and the redistribution of competing-order fluctuations across the transition. Distance-resolved correlations and finite-size analyses reveal signatures consistent with critical behavior. We further extend our investigation to nonequilibrium dynamics, directly preparing dimerized states and tracking the evolution of VBS order and joint FM-VBS fluctuations under local unitary interactions. Our results establish a versatile quantum-hardware framework for probing competing orders, critical correlations, and many-body dynamics beyond conventional Landau theory.
Person's judgment: 

## 15. d0b570e43454 F6
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: [no per-code basis on List; recount found text] A binomial estimate has variance ~ 1/nu and standard deviation ~ nu^(-1/2). The text assigns the nu^(-1/2) scaling to the variance (and to the covariance matrix elements). Does not reproduce (statement slip, text vs textbook).
Abstract: Separate and efficient characterization of state-preparation and measurement errors using single-qubit operations

Abstract In many platforms, errors from state-preparation and measurement (SPAM) dominate over single-qubit gate errors. To inform further hardware improvements and the development of more effective SPAM mitigation strategies, it is necessary to separately characterize the error contributions from SP and measurement (M). Here, we show how to construct a protocol that can efficiently and separately characterize the SP and M error parameters by using only high-fidelity single-qubit gates and repeated single-qubit measurements without reset. The measurements are assumed to be non-destructive and M errors are taken to be (spatially and temporally) uncorrelated and classical. Notably, the circuit depth of the protocol is independent of system size, and the target parameters may be characterized to a precision that is only limited by the number of experimental repetitions. We employ our protocol for the parallel characterization of SPAM errors on multiple qubits in the IBM quantum platform devices, where we find SP infidelities up to 6.57% and readout assignment errors up to 19.1%. Using numerical simulations, we also demonstrate how measurement-error mitigation that does not properly account for SP errors generally leads to a biased estimate of measured observable expectation values.
Person's judgment: 

## 16. fe8bcc8fa411 F2
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: (a) text against own figure: Sec 6.3 "This small study reproduces the direction and tail pattern seen in simulation" and Sec 3 A2 "shows that the same failure pattern can arise from ordinary device behavior, without deliberate injection". ...
Abstract: When Error Mitigation Makes Things Worse: Budget-Aware Evaluation, Extrapolation Failure, and the Calibration Trust Boundary

Error mitigation is expected to turn noisy quantum measurements into more useful estimates. We show that it can instead amplify error. Under control-offset miscalibration, the evaluated unconstrained zero-noise extrapolation (ZNE) estimators are worse than no mitigation on 38-63% of simulated instances and produce extreme tail errors. A small IBM Heron study finds worsening on 80-88% of 18 instances across two depths, with mean error 3.0-4.1 times the raw error. In simulation, the median changes little, so median-only monitoring misses the failures. We then compare methods at the same online shot budget per evaluation and report offline training cost separately. After that cost is amortized, a budget-conditioned neural corrector occupies the low-budget end of the simulated accuracy-cost frontier and falls back to the raw estimate when an ensemble disagrees; its hardware transfer remains unsuccessful. Finally, we treat provider-reported calibration as an input that is not bound to the execution-time device state. A white-box projected-gradient stress test on this metadata increases the corrector's error 8.1 times within the feature ranges used for training and evades the disagreement monitor on half of the worsened cases. Together, the results connect budget-aware evaluation, tail risk, and calibration integrity in near-term quantum learning pipelines.
Person's judgment: 

## 17. 6c813c240f0d F1
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: Istanbul Gelisim 2605.13109: tolerance eps = 0.04 set from FakeFez (a stored snapshot). Their own honest ibm_fez run (worst 0.074) fails it
Abstract: QCIVET: A Quantum--Classical Pipeline Integrity Framework with Contract-Based Subtype Verification and Hash-Chained Audit Traces

Hybrid quantum--classical pipelines increasingly support applications such as drug discovery, fraud detection, and cloud quantum processing unit (QPU) auditing, yet existing integrity-verification methods remain largely classical and fail to capture quantum-stage behaviour. We propose QCIVET, a contract-based integrity-verification framework that models a hybrid pipeline as a sequence of stages with explicit specifications and audits it at both syntactic and semantic levels. Syntactic integrity is enforced through a hash-chained audit trail with optional external anchoring, while semantic integrity at quantum stages is verified using a calibrated observable-deviation test grounded in the behavioural-subtyping discipline of Liskov and Wing. We prove soundness under the diamond-norm distance between quantum channels, conditional completeness for informationally complete observable families, and compositionality under inheritance chains. We further identify a class of Z-only-sneaky overrides that evade weak single-Pauli contracts but are exposed by multi-Pauli contracts. The framework is evaluated under calibration-derived noise models from IBM Quantum Eagle r3 and Heron r2 processors, and the subtype-separation protocol is validated end-to-end on a real ibm_fez (Heron r2) processor. QCIVET is instantiated on three representative applications: variati
Person's judgment: 

## 18. d921c3b9554c F4
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: run dates
Abstract: Hardware-Verified Shor-Based ECDLP Key Recovery from 4-Bit to 18-Bit on IBM Quantum Systems

We report hardware-verified ECDLP private key recovery up to 18 bits (n = 130,579) — the largest on record — extending prior public demonstrations at 6-bit (Tippeconnic, September 2025) on IBM ibm_torino. Using Shor-based period finding on IBM Quantum superconducting processors, we present 14 successful hardware runs spanning subgroup orders from n = 7 to n = 130,579. Every recovered private key was classically verified by confirming d·G = Q on the curve y² = x³ + 7. The central technical contribution is a carry-ripple (CDKM) modular arithmetic oracle that achieves near-unity routing overhead on IBM's heavy-hex qubit topology, enabling hardware execution at circuit depths exceeding 300,000 layers on 77-qubit circuits. A fifteenth hardware run (8-bit, QFT-based oracle) produced no recoveries and is reported for completeness. All IBM job IDs are provided for independent audit.
Person's judgment: 

## 19. 2f87917f7c39 F4
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: run dates not printed || no circuits or counts released
Abstract: Scalable Hardware Maturity Probe for Quantum Accelerators via Harmonic Analysis of QAOA

As quantum processors begin operating as tightly coupled accelerators inside high-performance computing (HPC) facilities, dependable and reproducible behaviour becomes a gating requirement for scientific and industrial workloads. We present a hardware-maturity probe that quantifies a device's reliability by testing whether it can repeatedly reproduce the provably global optima of single-layer Quantum Approximate Optimization Algorithm (QAOA) circuits. Using harmonic-analysis techniques, we derive closed-form upper bounds on the number of stationary points in the p=1 QAOA cost landscape for broad classes of combinatorial-optimization problems. The bounds yield an exhaustive yet low-overhead grid-sampling scheme whose outcomes are analytically verifiable. The probe integrates reliability-engineering notions-run-to-failure statistics, confidence-interval estimation, and reproducibility testing-into a single, application-centric benchmark. The proposed method links analytic guarantees to empirical performance and supplies a standardised dependability metric for hybrid quantum-HPC (QHPC) workflows.
Person's judgment: 

## 20. 7bbe789b0d83 F3
Judgment: NOT_IN_ABSTRACT
Quote: None
Note used: "validating the correctness of our theory": accuracy percentages with no interval, no count of repeats for Fig. 3 (no error bars, Figs 4 and 6 have 20 runs), and no stated definition of "experimentally observed" shots or depth
Abstract: How Many Shots Does It Take? A Noise-Aware Quantum Resource Allocation Framework

Any algorithm execution on quantum computers requires several repeated and costly executions (known as shots) to obtain reliable results. In this work, we propose a closed-form accurate analytical expression to determine optimal number of shots required for reliable execution of any algorithm on a quantum computer. We also present a theoretically grounded technique to distribute fixed shot budget across different partitions in a quantum circuit minimizing the total error. Our proposed analytical model helps to reduce the shots associated with reliable execution of quantum algorithms by about 58\% compared to current practice, in turn reducing the energy consumption by upto 62\%. Furthermore, our proposed optimal shot allocation technique across different partitions reduces total error by up to 73\% compared to conventional approaches.
Person's judgment: 

