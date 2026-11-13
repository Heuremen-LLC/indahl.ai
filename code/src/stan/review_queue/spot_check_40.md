# Spot check: does the quote support the label?

Each row is a three-way grounded agreement. The quote exists in the text (code-checked). The question for a person is whether it supports the label, using the definition. Mark each row SUPPORTS, DOES_NOT_SUPPORT or UNSURE.

## Row 1, code F4, id ba461b3c70f2
Label: PRESENT (via crosstalk)
Quote: "We also provide numerical experiments and an experiment on a real device for the wave equation to demonstrate the validity of our proposed method."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Hamiltonian simulation for hyperbolic partial differential equations by scalable quantum circuits

Solving partial differential equations for extremely large-scale systems within a feasible computation time serves in accelerating engineering developments. Quantum computing algorithms, particularly the Hamiltonian simulations, present a potential and promising approach to achieve this purpose. Actually, there are several oracle-based Hamiltonian simulations with potential quantum speedup, but their detailed implementations and accordingly the detailed computational complexities are all unclear. This paper presents a method that enables us to explicitly implement the quantum circuit for Hamiltonian simulation; the key technique is the explicit gate construction of differential operators contained in the target partial differential equation discretized by the finite difference method. Moreover, we show that the space and time complexities of the constructed circuit are exponentially smaller than those of conventional classical algorithms. We also provide numerical experiments and an experiment on a real device for the wave equation to demonstrate the validity of our proposed method. Published by the American Physical Society 2024
Mark: 

## Row 2, code F2, id caa68f493f80
Label: PRESENT (via round1)
Quote: "achieves 31 to 61 percent higher success-per-oracle efficiency"
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Quantum Skip Gates: Coherently Conditioned Subroutines in Iterative Quantum Algorithms

The Quantum Skip Gate (QSG) is a unitary circuit primitive that coherently superposes the execution and omission of an expensive quantum subroutine based on the outcome of a cheaper preceding subroutine, without mid-circuit measurement or loss of coherence. By using a control qubit and an internal flag, QSG enables conditional quantum logic entirely within a unitary framework. We demonstrate QSG experimentally in a Grover-style search on IBM quantum hardware with four data qubits and three Grover iterations, where it reduces costly subroutine calls by 9 to 25 percent and achieves 31 to 61 percent higher success-per-oracle efficiency relative to a fixed-order baseline. Noise-model simulations further confirm and strengthen these gains, reaching improvements of up to 45 percent when using an optimized swap-out design. These results show that coherently conditioned subroutines provide practical resource management, significantly reducing runtime cost and noise accumulation in near-term quantum algorithms.
Mark: 

## Row 3, code F2, id 8b0c61ea84a6
Label: PRESENT (via round1)
Quote: "By encoding feature selection as a Quadratic Unconstrained Binary Optimization (QUBO)"
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Formulating Subgroup Discovery as a Quantum Optimization Problem for Network Security

While current network intrusion detection systems achieve satisfactory accuracy, they often lack explainability. Subgroup Discovery (SD) addresses this by building interpretable rules that characterize feature interactions associated with attack traffic. With large datasets, classical heuristic beam search methods struggle with exponentially scaling search spaces and can prune critical multi-feature interactions. This paper introduces a quantum-enhanced pipeline for SD applied to network intrusion detection using NSL-KDD, formulating SD as quantum optimization for the first time. By encoding feature selection as a Quadratic Unconstrained Binary Optimization (QUBO) and solving it via the Quantum Approximate Optimization Algorithm (QAOA) on IBM Quantum hardware (ibm_pittsburgh), the pipeline identifies subgroups of network features that discriminate normal from attack traffic. A least-squares regression QUBO formulation fits the Weighted Relative Accuracy (WRAcc) landscape over feature subsets, with surrogate sampling for larger QUBOs. Results are benchmarked against exhaustive enumeration and Beam Search using ratios for Hamiltonian quality and WRAcc. Hardware scaling experiments on ibm_pittsburgh (10-30 qubits) reveal that QAOA at depth p = 1 shows WRAcc ratios of 0.983 at 10 qubits, 0.971 at 15 qubits, 0.855 at 20 qubits, and 0.624 at 25 qubits, degrading to 0.039 at 30 qubits as circuit noise dominates, establishing an empirical NISQ scaling boundary. Results demonstrate that QAOA discovers subgroups competitive with classical heuristics and finds multi-feature interaction patterns that greedy Beam Search prunes, with QAOA-unique subgroups achieving up to 99.6% test precision. This work establishes a framework for quantum combinatorial optimization in cybersecurity and characterizes hardware scaling for NISQ devices.
Mark: 

## Row 4, code F7, id e4ec46831660
Label: PRESENT (via crosstalk)
Quote: "We also run the experiments on a non-shuttling, superconducting processor (IBM Torino)"
Definition: F7 Classical comparison available. A simple classical method on the same instances matches or exceeds the reported result.
Applies to: Any claim of speed or quality against a classical method, in any field. Claims about quantum or other novel hardware are the usual case.
Test: Choose the classical method before the comparison and name it. Run it on the same instances. Report its result with its interval and level. Read the classical result against the reported result as set out below.
PRESENT when: The comparison reads ABOVE or CONSISTENT in favour of the classical method. That is, the difference between the classical result and the reported result, with its interval, lies entirely above the negative of the margin named before the run.
ABSENT when: The comparison reads BELOW. The difference lies entirely below the negative of that margin.
CANNOT_TELL reasons: NOT_RELEASED: The instances are not released.; UNREADABLE: The instances or the reported result were released and cannot be read.; STRADDLES_EDGE: The interval of the difference overlaps the negative of the margin.; TOO_WIDE_TO_RESOLVE: The interval reaches both the null and the size that matters.; NO_INTERVAL_FORMABLE: No interval can be formed for the difference.
NOT_APPLICABLE when: The claim is not about speed or quality against a classical method.
Text: Circuit-Level Noise Estimation via Shuttling in Plaquette Circuits

We present a method for estimating QEC circuit-level noise levels assuming that only single-shot measurements are available (e.g. measurements are slow and performed in a zoned/parallel fashion), and that lower level quantum hardware calibration is not possible (e.g. cloud access) or not feasible (e.g. large scale computing). We develop and run surface code plaquette experiments using two syndrome qubit configurations: FRESH, involving fresh qubits for each plaquette repetition, and RECYCLE, reusing qubits. To validate our approach, we compile plaquettes to ion-trap (IonQ Aria1) native gate set and apply hardware-aware rewrite templates to reduce circuit depth and execution time. We also run the experiments on a non-shuttling, superconducting processor (IBM Torino). We estimate circuit-level noise rates from the resulting single-shot plaquette measurement statistics, and conclude numerically about the viability of low-depth QEC experiments.
Mark: 

## Row 5, code F6, id eac2be66aea7
Label: ABSENT (via crosstalk)
Quote: "Our results demonstrate that fundamental energetic properties of black-box quantum computers can be quantitatively accessed through operational time measurements"
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Energy Inference of Black-Box Quantum Computers Using Quantum Speed Limit

Cloud-based quantum computers do not provide users with access to hardware-level information such as the underlying Hamiltonians, which obstructs the characterization of their physical properties. We propose a method to infer the energy scales of gate Hamiltonians in such black-box quantum processors using only user-accessible data, by exploiting quantum speed limits. Specifically, we reinterpret the Margolus-Levitin and Mandelstam-Tamm bounds as estimators of the energy expectation value and variance, respectively, and relate them to the shortest time for the processor to orthogonalize a quantum state. This shortest gate time, expected to lie on the nanosecond scale, is inferred from job execution times measured in seconds by employing gate-time amplification. We apply the method to IBM's superconducting quantum processor and estimate the energy scales associated with single-, two-, and three-qubit gates. The order of estimated energy is consistent with typical drive energies in superconducting qubit systems, suggesting that current gate operations approach the quantum speed limit. Our results demonstrate that fundamental energetic properties of black-box quantum computers can be quantitatively accessed through operational time measurements, reflecting the conjugate relationship between time and energy imposed by the uncertainty principle.
Mark: 

## Row 6, code F2, id 38f479dac8d2
Label: PRESENT (via round1)
Quote: "CHSH Bell parameter S = 2.290 ± 0.010"
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Bell Nonlocality Across a Simulated Horizon: CHSH Violation in a Gate-Based Qubit-Truncated Pair-Creation Analog on NISQ Hardware

We report a gate-based quantum circuit that implements a qubit-truncated analog of pair creation, inspired by Hawking radiation phenomenology, and demonstrate certified Bell nonlocality on IBM Quantum hardware (ibm_fez, Heron R2, 156 qubits). Using a two-mode squeezing (TMS) gate mapping |00⟩ to cos(θ/2)|00⟩ + sin(θ/2)|11⟩, we generate entangled pairs across a designated ‘horizon’ position in a 20-qubit chain.Main results: CHSH Bell parameter S = 2.290 ± 0.010 (29.8σ shot-noise; >22σ conservative with systematics), entanglement witness W = 2.838 ± 0.004, and Bell-state fidelity F(|Φ⁺⟩) = 96%. Bootstrap resampling (10,000 iterations) confirms robustness (100% of samples violate classical bounds).Important caveat: this is a protocol demonstration for gravity-inspired entanglement certification on NISQ hardware, not a faithful simulation of Hawking radiation (no thermal spectrum / vacuum structure).
Mark: 

## Row 7, code F5, id e4ec46831660
Label: ABSENT (via crosstalk)
Quote: "We estimate circuit-level noise rates from the resulting single-shot plaquette measurement statistics"
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: Circuit-Level Noise Estimation via Shuttling in Plaquette Circuits

We present a method for estimating QEC circuit-level noise levels assuming that only single-shot measurements are available (e.g. measurements are slow and performed in a zoned/parallel fashion), and that lower level quantum hardware calibration is not possible (e.g. cloud access) or not feasible (e.g. large scale computing). We develop and run surface code plaquette experiments using two syndrome qubit configurations: FRESH, involving fresh qubits for each plaquette repetition, and RECYCLE, reusing qubits. To validate our approach, we compile plaquettes to ion-trap (IonQ Aria1) native gate set and apply hardware-aware rewrite templates to reduce circuit depth and execution time. We also run the experiments on a non-shuttling, superconducting processor (IBM Torino). We estimate circuit-level noise rates from the resulting single-shot plaquette measurement statistics, and conclude numerically about the viability of low-depth QEC experiments.
Mark: 

## Row 8, code F6, id a17c693d0945
Label: PRESENT (via crosstalk)
Quote: "identical-depth circuit"
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Differential Observation of Quantum Many-Body Scar Revivals in Trotterized PXP Dynamics on a Superconducting Processor

We report a pre-registered observation of quantum many-body scar revivals in the one-dimensional PXP model, executed as Trotterized digital quantum simulation on a 156-qubit superconducting processor (IBM ibm_fez). Preparing the Neel-ordered product states |Z2>, |Z3>, and |Z4> on N=12 qubits with periodic boundary conditions and evolving under a first-order Trotter decomposition of the PXP Hamiltonian, we measure the return probability P(t) at five times up to t = 4.8. The scarred state |Z2> shows a return probability of 0.0710 ± 0.0041 at t = 4.8, while the thermalizing control |Z4>, evolved through an identical-depth circuit, shows 0.0008 ± 0.0004. The differential signal constitutes a 17.2-sigma observation of selective revival, exceeding our pre-registered 3-sigma criterion. Because both states traverse identical circuit depths, hardware noise affects them equally and the difference isolates the physical scar signature.
Mark: 

## Row 9, code F2, id b3253cdd1e6a
Label: PRESENT (via crosstalk)
Quote: "The method relies on a graph representation of the embedding problem, where the optimal decoupling sequence can be efficiently calculated"
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Resource-Efficient Context-Aware Dynamical Decoupling Embedding for Arbitrary Large-Scale Quantum Algorithms

We introduce and implement GraphDD: an efficient method for real-time, circuit-specific, optimal embedding of dynamical decoupling (DD) into executable quantum algorithms. We demonstrate that for an arbitrary quantum circuit, GraphDD exactly refocuses both quasistatic single-qubit dephasing and crosstalk idling errors over the entire circuit, while using a minimal number of additional single-qubit gates embedded into idle periods. The method relies on a graph representation of the embedding problem, where the optimal decoupling sequence can be efficiently calculated using an algebraic computation that scales linearly with the number of idles. This allows optimal DD to be embedded during circuit compilation, without any calibration overhead, additional circuit execution, or numerical optimization. The method is generic and applicable to any arbitrary circuit; in compiler runtime the specific pulse-sequence solutions are tailored to the individual circuit, and consider a range of contextual information on circuit structure and device connectivity. We verify the ability of GraphDD to deliver enhanced circuit-level error suppression on 127-qubit IBM devices, showing that the optimal DD embedding resulting from GraphDD provides orders of magnitude improvements to measured circuit fidelities compared with standard embedding approaches available in Qiskit.
Mark: 

## Row 10, code F2, id d3e6c8ec9c54
Label: ABSENT (via crosstalk)
Quote: "The authors also show how quantum process tomography may be performed in a restless setting."
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Minimum Quantum Run-Time Characterization and Calibration via Restless Measurements with Dynamic Repetition Rates

Qubit calibration and characterization are important for attaining high-fidelity gates in quantum computing, but require a significant amount of time, which limits a device's ability to run useful quantum circuits. This study uses restless measurement, in which the qubits are never reset, to speed up characterization and calibration tasks. The authors also show how quantum process tomography may be performed in a restless setting. This approach reduces the footprint of characterization and calibration on quantum processors by quickly and faithfully executing the corresponding circuits.
Mark: 

## Row 11, code F6, id 1e6a907923ec
Label: ABSENT (via crosstalk)
Quote: "We expect the method to be generally applicable to open systems."
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Method for simulating open-system dynamics using midcircuit measurements on a quantum computer

We present a method for simulating the dynamics of an open electronic system on a quantum computer. This approach entails mid-circuit measurements and resets to simulate the addition or removal of electrons from the system. Our method provides a way to apply non-reversible operations to a quantum computer without the need for additional qubits. Using this method, we simulate the dynamics of an open electronic system consisting of a chain of electrons positioned between two conductive leads on the $ibm\_torino$ quantum computer. We expect the method to be generally applicable to open systems.
Mark: 

## Row 12, code F5, id 4ab47bcd9340
Label: PRESENT (via crosstalk)
Quote: "The behaviour arises in all released versions of the library (0.8.4 to 0.9.0)."
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: Impact of Data Loss in Postprocessing on Training and Inference of Quantum Neural Networks

As quantum hardware scales to larger devices, the classical software layers that interface with it must evolve in step. Postprocessing routines developed and tested primarily in simulator settings can encode assumptions that no longer hold on utility-scale devices, leading to data loss that can be difficult to detect from high-level model outputs alone. We present a case study of \texttt{SamplerQNN}, the sampling-based quantum neural network class in the Qiskit Machine Learning library. Here, the postprocessing method applies a filter that assumes measurement bit-strings are in virtual qubit space. On our quantum hardware runs, where bit-strings span over 100 physical qubits, this filter led to the loss of 85 to 99.6\% of valid measurement shots, depending on the transpiler's qubit placement. The resulting probability vector is unnormalised, allowing distorted prediction and loss values to propagate through the model without an API-level warning. We demonstrate the impact across five experiments on two IBM backends: for inference, accuracy drops from 0.94 to 0.39 on the same raw measurements; for training, the loss signal is compressed by 22 to 27$\times$, substantially reducing the sensitivity of the optimiser to the objective landscape. The behaviour arises in all released versions of the library (0.8.4 to 0.9.0). We implemented a layout-based marginalisation fix, merged into the GitHub codebase as Pull Request \#1041, that makes \texttt{SamplerQNN} postprocessing forward-compatible with current and upcoming hardware.
Mark: 

## Row 13, code F4, id 7f97fb132c0b
Label: PRESENT (via crosstalk)
Quote: "This methodology is illustrated by examining the ground states of the XY model with a magnetic field in the z-direction in one dimension."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Determining Ground-State Phase Diagrams on Quantum Computers via a Generalized Application of Adiabatic State Preparation

Quantum phase transitions materialize as level crossings in the ground-state energy when the parameters of the Hamiltonian are varied. The resulting ground-state phase diagrams are straightforward to determine by exact diagonalization on classical computers, but are challenging on quantum computers because of the accuracy needed and the near degeneracy of the competing states close to the level crossings. On the other hand, classical computers are limited to small system sizes, which quantum computers may help overcome. In this work, we use a local adiabatic ramp for state preparation to allow us to directly compute ground-state phase diagrams on a quantum computer via time evolution. This methodology is illustrated by examining the ground states of the XY model with a magnetic field in the z-direction in one dimension. We are able to calculate an accurate phase diagram on both two- and three-site systems using IBM quantum machines.
Mark: 

## Row 14, code F4, id 792e5f9bddb7
Label: PRESENT (via crosstalk)
Quote: "We study quantum conditional entropy production, which quantifies the irreversibility of system-environment evolution from the perspective of a third system, called the reference."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Conditional entropy production and quantum fluctuation theorem of dissipative information: Theory and experiments

We study quantum conditional entropy production, which quantifies the irreversibility of system-environment evolution from the perspective of a third system, called the reference. The reference is initially correlated with the system. We show that the quantum unconditional entropy production with respect to the system is less than the conditional entropy production with respect to the reference, where the latter includes a reference-induced dissipative information. The dissipative information pinpoints the distributive correlation established between the environment and the reference, even though they do not interact directly. When reaching the thermal equilibrium, the system-environment evolution has a zero unconditional entropy production. However, one can still have a nonzero conditional entropy production with respect to the reference, which characterizes the informational nonequilibrium of the system-environment evolution in the view point of the reference. The additional contribution to the conditional entropy production, the dissipative information, characterizes a minimal thermodynamic cost that the system pays for maintaining the correlation with the reference. Positive dissipative information also characterizes potential work waste. We prove that both types of entropy production and the dissipative information follow quantum fluctuation theorems when a two-point measurement is applied. We verify the quantum fluctuation theorem for the dissipative information experimentally on IBM quantum computers. We also present examples based on the qubit collisional model and demonstrate universal nonzero dissipative information in the qubit Maxwell's demon protocol.
Mark: 

## Row 15, code F5, id 81d658e6acc4
Label: ABSENT (via crosstalk)
Quote: "We validate our simulated results with hardware demonstrations on a graph with 67 nodes."
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: Imaginary Hamiltonian variational Ansatz for combinatorial optimization problems

Obtaining exact solutions to combinatorial optimization problems using classical computing is computationally expensive. The current tenet in the field is that quantum computers can address these problems more efficiently. While promising algorithms require fault-tolerant quantum hardware, variational algorithms have emerged as viable candidates for near-term devices. The success of these algorithms hinges on multiple factors, with the design of the Ansatz being of the utmost importance. It is known that popular approaches such as the quantum approximate optimization algorithm (QAOA) and quantum annealing suffer from adiabatic bottlenecks, which lead to either larger circuit depth or evolution time. On the other hand, the evolution time of imaginary-time evolution is bounded by the inverse energy gap of the Hamiltonian, which is constant for most noncritical physical systems. In this work we propose an imaginary Hamiltonian variational Ansatz ($i\mathrm{HVA}$) inspired by quantum imaginary-time evolution to solve the MaxCut problem. We introduce a tree arrangement of the parametrized quantum gates, enabling the exact solution of arbitrary tree graphs using the one-round $i\mathrm{HVA}$. For randomly generated $D$-regular graphs, we numerically demonstrate that the $i\mathrm{HVA}$ solves the MaxCut problem with a small constant number of rounds and sublinear depth, outperforming the QAOA, which requires rounds increasing with the graph size. Furthermore, our Ansatz solves the MaxCut problem exactly for graphs with up to 24 nodes and $D\ensuremath{\le}5$, whereas only approximate solutions can be derived by the classical near-optimal Goemans-Williamson algorithm. We validate our simulated results with hardware demonstrations on a graph with 67 nodes.
Mark: 

## Row 16, code F2, id 9f769b3f25e2
Label: ABSENT (via crosstalk)
Quote: "The results are obtained on real hardware and complemented by simulations."
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Parallelizing Quantum-Classical Workloads: Profiling the Impact of Splitting Techniques

Quantum computers are the next evolution of computing hardware. Quantum devices are being exposed through the same familiar cloud platforms used for classical computers, and enabling seamless execution of hybrid applications that combine quantum and classical components. Quantum devices vary in features, e.g., number of qubits, quantum volume, CLOPS, noise profile, queuing delays and resource cost. So, it may be useful to split hybrid workloads with either large quantum circuits or a large number of quantum circuits, into smaller units. In this paper, we profile two workload splitting techniques on IBM's Quantum Cloud: (1) Circuit parallelization, to split one large circuit into multiple smaller ones, and (2) Data parallelization to split a large number of circuits that run on one device to smaller batches of circuits that run on concurrently on multiple devices. These can improve the utilization of heterogeneous quantum hardware, but involve trade-offs. We evaluate these techniques on two key algorithmic classes: Variational Quantum Eigensolver (VQE) and Quantum Support Vector Machine (QSVM), and measure the impact on quality of the result, circuit execution times, quantum resource usage, and processing overheads, relative to a baseline without such parallelization. The results are obtained on real hardware and complemented by simulations. We see that (1) VQE with circuit cutting is ~ 39% better in ground state estimation than the uncut version, and (2) QSVM that combines data parallelization with a reduced feature set yields upto 3 ×improvement in quantum workload execution time and reduces quantum resource use by 3 ×, while providing comparable accuracy. Error mitigation can improve the accuracy by ≈ 7% and reduce resource footprint by ≈4% compared to the best case among the considered scenarios.
Mark: 

## Row 17, code F1, id 090eb1cacc3e
Label: PRESENT (via crosstalk)
Quote: "This experiment simulates the kicked transverse field Ising model with far-from-Clifford parameters on an IBM Heron device."
Definition: F1 Self-built reference. Results are compared with a reference built from the same setup or from IBM’s stated figures.
Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
Test: Find the reference the result is compared with. Read how it was built.
PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
CANNOT_TELL reasons: METHOD_UNSTATED: The paper does not say how the reference was built.; NOT_RELEASED: The reference or the figures it was built from are named but not released.; UNREADABLE: The reference was released and cannot be read.
NOT_APPLICABLE when: The claim compares its result with no reference.
Text: Reliable high-accuracy error mitigation for utility-scale quantum circuits

Error mitigation is essential for unlocking the full potential of quantum algorithms and accelerating the timeline toward quantum advantage. As quantum hardware progresses to push the boundaries of classical simulation, efficient and robust error mitigation methods are becoming increasingly important for producing accurate and reliable outputs. However, existing error-mitigation approaches face a fundamental tradeoff between practical performance and reliability: heuristic methods such as zero-noise extrapolation (ZNE) enjoy faster runtime but lack accuracy guarantees, while rigorous techniques such as probabilistic error cancellation (PEC) provide unbiased estimates at prohibitive computational cost. We introduce a characterization-based, rigorously-grounded quantum error mitigation and error suppression framework (QESEM) that resolves this tradeoff by leveraging the accuracy guarantees of quasi-probabilistic mitigation with dramatically reduced overhead. We explain the innovative methods underlying QESEM and demonstrate its capabilities in the largest utility-scale error mitigation experiment based on an unbiased method. This experiment simulates the kicked transverse field Ising model with far-from-Clifford parameters on an IBM Heron device. We further validate QESEM's versatility across arbitrary quantum circuits and devices through high-accuracy error-mitigated molecular VQE circuits executed on IBM Heron and IonQ trapped-ion devices. Compared with multiple variants of the widely used zero-noise extrapolation method, QESEM consistently achieves higher accuracy while avoiding the prohibitive runtime overhead associated with PEC. These results mark a significant step forward in accuracy and reliability for running quantum circuits on current devices across diverse applications. Finally, we provide projections of QESEM's performance on near-term devices toward quantum advantage.
Mark: 

## Row 18, code F4, id 72706fd9794c
Label: PRESENT (via crosstalk)
Quote: "The proposed QPUF circuit logic has been deployed on IBM quantum systems and simulators for validation"
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: QPUF: Quantum Physical Unclonable Functions for Security-by-Design of Industrial Internet-of-Things

This research investigates the integration of quantum hardware-assisted security into critical applications, including the Industrial Internet-of-Things (IIoT), Smart Grid, and Smart Transportation. The Quantum Physical Unclonable Functions (QPUF) architecture has emerged as a robust security paradigm, harnessing the inherent randomness of quantum hardware to generate unique and tamper-resistant cryptographic fingerprints. This work explores the potential of Quantum Computing for Security-by-Design (SbD) in the Industrial Internet-of-Things (IIoT), aiming to establish security as a fundamental and inherent feature. SbD in Quantum Computing focuses on ensuring the security and privacy of Quantum computing applications by leveraging the fundamental principles of quantum mechanics, which underpin the quantum computing infrastructure. This research presents a scalable and sustainable security framework for the trusted attestation of smart industrial entities in Quantum Industrial Internet-of-Things (QIoT) applications within Industry 4.0. Central to this approach is the QPUF, which leverages quantum mechanical principles to generate unique, tamper-resistant fingerprints. The proposed QPUF circuit logic has been deployed on IBM quantum systems and simulators for validation. The experimental results demonstrate the enhanced randomness and an intra-hamming distance of approximately 50% on the IBM quantum hardware, along with improved reliability despite varying error rates, coherence, and decoherence times. Furthermore, the circuit achieved 100% reliability on Google’s Cirq simulator and 95% reliability on IBM’s quantum simulator, highlighting the QPUF’s potential in advancing quantum-centric security solutions.
Mark: 

## Row 19, code F1, id 5669ebfbfe7b
Label: PRESENT (via round1)
Quote: "The ceiling is a property of the map-data pair at a stated bandwidth, not of the classical table alone."
Definition: F1 Self-built reference. Results are compared with a reference built from the same setup or from IBM’s stated figures.
Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
Test: Find the reference the result is compared with. Read how it was built.
PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
CANNOT_TELL reasons: METHOD_UNSTATED: The paper does not say how the reference was built.; NOT_RELEASED: The reference or the figures it was built from are named but not released.; UNREADABLE: The reference was released and cannot be read.
NOT_APPLICABLE when: The claim compares its result with no reference.
Text: Fractal dimension predicts quantum kernel collapse in angle-encoded data

Angle-encoded quantum kernels on tabular data collapse when the feature map is wider than the intrinsic dimension of the data. We propose the correlation fractal dimension D2 as an a priori qubit budget: encode D2 coordinates chosen by FD-ASE instead of the PCA-95% width or all E attributes. On nine data sets and a statevector simulator (n= 32), a one-layer ZZ fidelity kernel at q=D2 stays geometrically alive while the same kernel at the PCA-95% width has already collapsed. The budget is map-dependent: product-state and IQP maps overshoot it; a second ZZ layer undershoots it. Packed dense-angle and re-uploading encodings still live at the fractal q, but not when PCA-95% features are stacked onto those qubits. Shrinking the angle bandwidth moves the ZZ knee later; stretching it kills the kernel earlier. On IBM Quantum (ibm_fez, 256 shots, n=8) the one-layer ZZ kernel at the fractal width matches the exact kernel (MAE 0.021); past that width both hardware and simulator have collapsed. The ceiling is a property of the map-data pair at a stated bandwidth, not of the classical table alone.
Mark: 

## Row 20, code F2, id 85d159217c32
Label: PRESENT (via crosstalk)
Quote: "Our architecture extracts molecular torsions from relative phases in statevector simulations."
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Logarithmic-scale variational quantum eigensolver for off-lattice protein structure prediction in continuous torsional angle space

Classical and current quantum approaches to protein structure prediction (QPSP) face limitations, notably massive qubit requirements restricting near-term models to simplistic on-lattice simulations. We propose a logarithmic-scale variational quantum eigensolver (VQE) that reduces qubit requirements for N torsional degrees of freedom to O(log2N), enabling off-lattice, all-atom simulations. Our architecture extracts molecular torsions from relative phases in statevector simulations. On quantum hardware, a decoder maps the empirical cumulative distribution function (CDF) from basis-state probabilities to bounded torsional variables. These feed a classical algorithm to build heavy-atom coordinates. We use an EfficientSU2 ansatz and multi-stage relaxation to mitigate barren plateaus. Structures are evaluated via a custom hybrid quantum-classical Hamiltonian, alongside Rosetta and OpenMM benchmarks. Evaluation on chignolin and Trp-cage yielded native-like conformations. Chignolin reached a 0.623 Å Cα RMSD in retained snapshots and 1.199 Å in final models; Trp-cage achieved a 2.501 Å RMSD among snapshots (3.512 Å in final models). Execution on IBM processors (ibm_cleveland, ibm_miami) successfully recovered native-like structures with a best RMSD of 1.758 Å. The custom energy function performed best overall, though energy-ranking imbalances persisted across sampled landscapes for all functions. This introduces the first all-atom, continuous-space quantum algorithm for QPSP. By converting physical qubit constraints into circuit depth constraints, it proves high-resolution prediction is feasible with exponentially fewer qubits. Despite current limits like computational overhead and energy function sensitivity, it establishes a scalable foundation for hybrid quantum biophysics.
Mark: 

## Row 21, code F4, id 9edf432b337f
Label: PRESENT (via crosstalk)
Quote: "We measure the benefits of a pulse-efficient circuit transpilation with process tomography"
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Pulse-efficient circuit transpilation for quantum applications on cross-resonance-based hardware

We show a pulse-efficient circuit transpilation framework for noisy quantum hardware. This is achieved by scaling cross-resonance pulses and exposing each pulse as a gate to remove redundant single-qubit operations with the transpiler. Crucially, no additional calibration is needed to yield better results than a CNOT-based transpilation. This pulse-efficient circuit transpilation therefore enables a better usage of the finite coherence time without requiring knowledge of pulse-level details from the user. As demonstration, we realize a continuous family of cross-resonance-based gates for SU(4) by leveraging Cartan's decomposition. We measure the benefits of a pulse-efficient circuit transpilation with process tomography and observe up to a 50% error reduction in the fidelity of ${R}_{ZZ}(\ensuremath{\theta})$ and arbitrary SU(4) gates on IBM Quantum devices. We apply this framework for quantum applications by running circuits of the quantum approximate optimization algorithm applied to MAXCUT. For an 11-qubit nonhardware native graph, our methodology reduces the overall schedule duration by up to 52% and errors by up to 38%.
Mark: 

## Row 22, code F5, id 6da9b992c251
Label: ABSENT (via crosstalk)
Quote: "fidelities and entropies are reconstructed directly from raw IBM and Rigetti outputs;"
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: Coherence Stability in Deep Single-Qubit Circuits Outside the Regime Predicted by Standard Decoherence Models

Coherence measurements as high as 0.9995 on IBM hardware and 0.975 on Rigetti—persisting even at extreme single-qubit depths up to 2048 H–S–H blocks—define an empirical outlier far beyond anything predicted by standard decoherence models. This stability emerges precisely where contemporary theory expects rapid collapse toward mixed states, yet the circuits remain sharply ordered and depth-insensitive. This behavior is empirically and mathematically congruent with the two-parameter unified Kālīon Field, a scalar–tensor framework shown to resolve the Hubble tension, reproduce the MOND acceleration law, unify dark-sector phenomenology, reduce quantum entropy, preserve coherence under non-unital evolution, constrain vacuum curvature, and organize gravitational–informational dynamics within a single coupled structure. The paper presents the anomaly independently of interpretation: fidelities and entropies are reconstructed directly from raw IBM and Rigetti outputs; the full dataset shows no monotonic decay toward the p₀ = 0.5 baseline; and the significance relative to a mixed-state null is extreme. The alignment with the Kālīon predictions is documented but not presupposed. All raw data, circuit reconstructions, and analysis scripts accompany this Zenodo deposit for full replication and scrutiny.
Mark: 

## Row 23, code F6, id 792e5f9bddb7
Label: PRESENT (via crosstalk)
Quote: "We verify the quantum fluctuation theorem for the dissipative information experimentally on IBM quantum computers."
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Conditional entropy production and quantum fluctuation theorem of dissipative information: Theory and experiments

We study quantum conditional entropy production, which quantifies the irreversibility of system-environment evolution from the perspective of a third system, called the reference. The reference is initially correlated with the system. We show that the quantum unconditional entropy production with respect to the system is less than the conditional entropy production with respect to the reference, where the latter includes a reference-induced dissipative information. The dissipative information pinpoints the distributive correlation established between the environment and the reference, even though they do not interact directly. When reaching the thermal equilibrium, the system-environment evolution has a zero unconditional entropy production. However, one can still have a nonzero conditional entropy production with respect to the reference, which characterizes the informational nonequilibrium of the system-environment evolution in the view point of the reference. The additional contribution to the conditional entropy production, the dissipative information, characterizes a minimal thermodynamic cost that the system pays for maintaining the correlation with the reference. Positive dissipative information also characterizes potential work waste. We prove that both types of entropy production and the dissipative information follow quantum fluctuation theorems when a two-point measurement is applied. We verify the quantum fluctuation theorem for the dissipative information experimentally on IBM quantum computers. We also present examples based on the qubit collisional model and demonstrate universal nonzero dissipative information in the qubit Maxwell's demon protocol.
Mark: 

## Row 24, code F4, id 9a797da9bd1e
Label: PRESENT (via crosstalk)
Quote: "We present examples of this implementation on sample models using Qiskit and test them using both quantum simulators and IBM Quantum hardware."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: A Bayesian-network-based quantum procedure for failure risk analysis

Abstract Studying the propagation of failure probabilities in interconnected systems such as electrical distribution networks is traditionally performed by means of Monte Carlo simulations. In this paper, we propose a procedure for creating a model of the system on a quantum computer using a restricted representation of Bayesian networks. We present examples of this implementation on sample models using Qiskit and test them using both quantum simulators and IBM Quantum hardware. The results show a correlation in the precision of the results when considering the number of Monte Carlo iterations alongside the sum of shots in a single quantum circuit execution.
Mark: 

## Row 25, code F5, id fe974d100fdb
Label: ABSENT (via crosstalk)
Quote: "Experimental results demonstrate that our approach consistently maintains high fidelity across all jobs while significantly enhancing system throughput."
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: QuSplit: achieving both high fidelity and throughput via job splitting on noisy quantum computers

Abstract With the progression into the quantum utility era, computing is shifting toward quantum-centric architectures, where multiple quantum processors collaborate with classical computing resources. Platforms such as IBM Quantum and Amazon Braket exemplify this trend, enabling access to diverse quantum backends. However, efficient resource management remains a challenge, as quantum processors are highly susceptible to noise, which significantly impacts computation fidelity. Additionally, the heterogeneous noise characteristics across different processors add further complexity to scheduling and resource allocation. Existing scheduling strategies typically focus on mapping and scheduling jobs to these heterogeneous backends, which leads to some jobs suffering extremely low fidelity. Targeting quantum optimization jobs (e.g., VQC, VQE, QAOA) — among the most promising quantum applications in the NISQ era — we hypothesize that executing the later stages of a job on a high-fidelity quantum processor can significantly improve overall fidelity. To verify this, we use VQE as a case study and develop a Genetic Algorithm-based scheduling framework that incorporates job splitting to optimize fidelity and throughput. Experimental results demonstrate that our approach consistently maintains high fidelity across all jobs while significantly enhancing system throughput. Furthermore, the proposed algorithm exhibits excellent scalability in handling an increasing number of quantum processors and larger workloads, making it a robust and practical solution for emerging quantum computing platforms. To further substantiate its effectiveness, we conduct experiments on a real quantum processor, IBM Strasbourg, which confirm that job splitting improves fidelity and reduces the number of iterations required for convergence.
Mark: 

## Row 26, code F6, id 9d0e807315b2
Label: ABSENT (via crosstalk)
Quote: "An explicit demonstration for Z_{2} gauge theory is presented including exploratory tests using the ibm_perth device."
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Improved Hamiltonians for Quantum Simulations of Gauge Theories

Quantum simulations of lattice gauge theories for the foreseeable future will be hampered by limited resources. The historical success of improved lattice actions in classical simulations strongly suggests that Hamiltonians with improved discretization errors will reduce quantum resources, i.e., require ≳2^{d} fewer qubits in quantum simulations for lattices with d-spatial dimensions. In this work, we consider O(a^{2})-improved Hamiltonians for pure gauge theories and design the corresponding quantum circuits for its real-time evolution in terms of primitive gates. An explicit demonstration for Z_{2} gauge theory is presented including exploratory tests using the ibm_perth device.
Mark: 

## Row 27, code F6, id 88113b1c4420
Label: ABSENT (via crosstalk)
Quote: "We study the Quantum Zeno Effect (QZE) on a single qubit on IBM Quantum Experience devices under the effect of multiple measurements."
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Observation of the quantum Zeno effect on a NISQ device

Abstract We study the Quantum Zeno Effect (QZE) on a single qubit on IBM Quantum Experience devices under the effect of multiple measurements. We consider two possible cases: the Rabi evolution and the free decay. SPAM error mitigations have also been applied. In both cases we observe the occurrence of the QZE as an increasing of the survival probability with the number of measurements.
Mark: 

## Row 28, code F4, id 4b94c0a57546
Label: PRESENT (via crosstalk)
Quote: "We discuss how to leverage these bounds for different algorithms and demonstrate our findings through experiments on real quantum computers involving up to 127 qubits."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Provable bounds for noise-free expectation values computed from noisy samples

Quantum computing has emerged as a powerful computational paradigm capable of solving problems beyond the reach of classical computers. However, today’s quantum computers are noisy, posing challenges to obtaining accurate results. Here, we explore the impact of noise on quantum computing, focusing on the challenges in sampling bit strings from noisy quantum computers and the implications for optimization and machine learning. We formally quantify the sampling overhead to extract good samples from noisy quantum computers and relate it to the layer fidelity, a metric to determine the performance of noisy quantum processors. Further, we show how this allows us to use the conditional value at risk of noisy samples to determine provable bounds on noise-free expectation values. We discuss how to leverage these bounds for different algorithms and demonstrate our findings through experiments on real quantum computers involving up to 127 qubits. The results show strong alignment with theoretical predictions. In this study, the authors investigate the impact of noise on quantum computing with a focus on the challenges in sampling bit strings from noisy quantum computers, which has implications for optimization and machine learning.
Mark: 

## Row 29, code F4, id 286741ceed0c
Label: PRESENT (via round1)
Quote: "the present work marks an important milestone towards achieving utility-scale quantum computation"
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Dynamical mean field theory for real materials on a quantum computer

Quantum computers (QC) could harbor the potential to significantly advance materials simulations, particularly at the atomistic scale involving strongly correlated fermionic systems, where an accurate description of quantum many-body effects scales unfavorably with size. While a full-scale treatment of condensed matter systems with currently available noisy quantum computers remains elusive, quantum embedding schemes like dynamical mean-field theory (DMFT) allow the mapping of an effective, reduced subspace Hamiltonian to available devices to improve the accuracy of ab initio calculations such as density functional theory (DFT). Here, we report on the development of a hybrid quantum-classical DFT + DMFT simulation framework which relies on a quantum impurity solver based on the Lehmann representation of the impurity Green’s function. Hardware experiments with up to 14 qubits on the IBM Quantum system are conducted, using advanced error mitigation methods and a novel calibration scheme for an improved zero-noise extrapolation to effectively reduce adverse effects from inherent noise on current quantum devices. We showcase the utility of our quantum DFT + DMFT workflow by assessing the correlation effects on the electronic structure of a real material, Ca 2 CuO 2 Cl 2 , which is mapped to an effective single-band Hubbard Hamiltonian and the subsequently derived Anderson impurity model solved with up to 6 bath sites on available quantum hardware. Further, we carefully benchmark our quantum results with respect to exact reference solutions and experimental spectroscopy measurements. While challenges remain to scale our approach to larger, multi-orbital and multi-site systems with more bath sites, the present work marks an important milestone towards achieving utility-scale quantum computation in materials simulation.
Mark: 

## Row 30, code F2, id 22079849cc4b
Label: ABSENT (via crosstalk)
Quote: "Weighted Jaccard similarity indicates that twins constructed from downloadable calibration CSV data often achieved the closest agreement with hardware"
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Evaluating Calibration-Based Digital Twins for IBM Quantum Hardware Simulation

We evaluate calibration-based digital twins for IBM Quantum hardware, aiming to reproduce hardware measurement outcomes on classical simulators. We present a workflow that builds twins from downloadable calibration CSV files by mapping coherence times, gate and readout error rates, and operation durations to thermal-relaxation, depolarizing, and readout error channels, while reconstructing a directed coupling map to restore connectivity constraints during transpilation. We compare four twin variants (CSV-built, backend-derived simulator, backend-derived noise model, and fake-backend snapshots) under a common execution and validation protocol. Experiments on two IBM QPUs, ibm_brisbane and ibm_sherbrooke, use randomized five-qubit circuits of depths 10, 20, and 30 across four optimization levels. Weighted Jaccard similarity indicates that twins constructed from downloadable calibration CSV data often achieved the closest agreement with hardware, while backend-derived twins provided competitive and practical baselines. The results further show that agreement depends on both the target device and the transpilation settings, underscoring the need to validate digital twins for the specific execution setup rather than assuming transferability across devices.
Mark: 

## Row 31, code F5, id ede67b06a2ed
Label: ABSENT (via crosstalk)
Quote: "Numerical results show that our theoretical error bounds for CPFs match or outperform the empirical error scaling of standard product formulas for these systems."
Definition: F5 Number recomputes differently. A printed number does not follow from the paper’s own data or arithmetic.
Applies to: Any claim that prints a number that follows from data or arithmetic.
Test: Recompute the number from what the paper released. Round the recomputed value to the printed precision and compare it with the printed value.
PRESENT when: The rounded recomputed value is not equal to the printed value.
ABSENT when: The rounded recomputed value is equal to the printed value.
CANNOT_TELL reasons: NOT_RELEASED: The data or readings needed for the recomputation are not released. Also record QIA-F4 Present.; UNREADABLE: The data were released and cannot be read.; METHOD_UNSTATED: The paper does not state the computation well enough to repeat it.
NOT_APPLICABLE when: The claim prints no number that follows from data or arithmetic.
Text: Faster Algorithmic Quantum and Classical Simulations by Corrected Product Formulas

Hamiltonian simulation using product formulas is arguably the most straightforward and practical approach for algorithmic simulation of a quantum system’s dynamics on a quantum computer. Here we present corrected product formulas (CPFs), a variation of product formulas achieved by injecting auxiliary terms called correctors into standard product formulas. We establish several correctors that improve the accuracy of standard product formulas by orders of magnitude when simulating Hamiltonians comprised of two exactly simulatable partitions, a common structure of lattice Hamiltonians. Importantly, injecting these correctors increases the overall simulation cost by only a small additive or multiplicative factor. We show that correctors are particularly advantageous for perturbed systems, where one partition has a relatively small norm compared to the other, as they allow the small norm to be utilized as an additional parameter for controlling the simulation error. We demonstrate the performance of CPFs by numerical simulations for several lattice Hamiltonians. Numerical results show that our theoretical error bounds for CPFs match or outperform the empirical error scaling of standard product formulas for these systems. We also demonstrate improvements offered by CPFs by implementing small-size systems on actual quantum hardware, as well as on noisy and noiseless quantum simulators. CPFs could be a valuable algorithmic tool for early fault-tolerant quantum computers with limited computing resources. As for standard product formulas, CPFs could also be used for simulations on a classical computer.
Mark: 

## Row 32, code F6, id 9d4ab99aa33f
Label: ABSENT (via crosstalk)
Quote: "Quantum computing offers an alternative paradigm for addressing combinatorial optimization problems compared to classical computing."
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Quantum-enhanced Markov Chain Monte Carlo for Combinatorial Optimization

Quantum computing offers an alternative paradigm for addressing combinatorial optimization problems compared to classical computing. Despite recent hardware improvements, the execution of empirical quantum optimization experiments at scales known to be hard for state-of-the-art classical solvers is not yet in reach. In this work, we offer a different way to approach combinatorial optimization with near-term quantum computing. Motivated by the promising results observed in using quantum-enhanced Markov chain Monte Carlo (QeMCMC) for approximating complicated probability distributions, we combine ideas of sampling from the device with QeMCMC together with warm-starting and parallel tempering, in the context of combinatorial optimization. We demonstrate empirically that our algorithm recovers the global optima for instances of the Maximum Independent Set problem (MIS) up to 117 decision variables using 117 qubits on IBM quantum hardware. We show early evidence of a scaling advantage of our algorithm compared to similar classical methods for the chosen instances of MIS. MIS is practically relevant across domains like financial services and molecular biology, and, in some cases, already difficult to solve to optimality classically with only a few hundred decision variables.
Mark: 

## Row 33, code F1, id 3baae47d0f0e
Label: PRESENT (via round1)
Quote: "We achieve this by using higher precision quantum estimates of the eigenvalues relevant to the linear system, and a new classical step to guide the eigenvalue inversion part of Hybrid HHL."
Definition: F1 Self-built reference. Results are compared with a reference built from the same setup or from IBM’s stated figures.
Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
Test: Find the reference the result is compared with. Read how it was built.
PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
CANNOT_TELL reasons: METHOD_UNSTATED: The paper does not say how the reference was built.; NOT_RELEASED: The reference or the figures it was built from are named but not released.; UNREADABLE: The reference was released and cannot be read.
NOT_APPLICABLE when: The claim compares its result with no reference.
Text: An Enhanced Hybrid HHL Algorithm

We present a classical enhancement to improve the accuracy of the Hybrid variant (Hybrid HHL) of the quantum algorithm for solving linear systems of equations proposed by Harrow, Hassidim, and Lloyd (HHL). We achieve this by using higher precision quantum estimates of the eigenvalues relevant to the linear system, and a new classical step to guide the eigenvalue inversion part of Hybrid HHL. We show that eigenvalue estimates with just two extra bits of precision result in tighter error bounds for our Enhanced Hybrid HHL compared to HHL. Our enhancement reduces the error of Hybrid HHL by an average of 57 percent on an ideal quantum processor for a representative sample of 2x2 systems. On IBM Torino and IonQ Aria-1 hardware, we see that the error of Enhanced Hybrid HHL is on average 13 percent and 20 percent (respectively) less than that of HHL for the same set of systems.
Mark: 

## Row 34, code F1, id 9600cf747afa
Label: PRESENT (via crosstalk)
Quote: "Quantum annealing is implemented in adiabatic hardware such as D-Wave, and QAOA is implemented in gate-based hardware such as IBM."
Definition: F1 Self-built reference. Results are compared with a reference built from the same setup or from IBM’s stated figures.
Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
Test: Find the reference the result is compared with. Read how it was built.
PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
CANNOT_TELL reasons: METHOD_UNSTATED: The paper does not say how the reference was built.; NOT_RELEASED: The reference or the figures it was built from are named but not released.; UNREADABLE: The reference was released and cannot be read.
NOT_APPLICABLE when: The claim compares its result with no reference.
Text: Quantum Computing Approaches for Mission Covering Optimization

Quantum computing has the potential to revolutionize the way hard computational problems are solved in terms of speed and accuracy. Quantum hardware is an active area of research and different hardware platforms are being developed. Quantum algorithms target each hardware implementation and bring advantages to specific applications. The focus of this paper is to compare how well quantum annealing techniques and the QAOA models constrained optimization problems. As a use case, a constrained optimization problem called mission covering optimization is used. Quantum annealing is implemented in adiabatic hardware such as D-Wave, and QAOA is implemented in gate-based hardware such as IBM. This effort provides results in terms of cost, timing, constraints held, and qubits used.
Mark: 

## Row 35, code F6, id 8a788a8f7296
Label: PRESENT (via crosstalk)
Quote: "quantum vault not only protects both user and bank symmetrically"
Definition: F6 Text differs from own table. The text, abstract or caption differs from the paper’s own table, figure or files.
Applies to: Any claim whose text refers to a table, figure or file.
Test: Set each number or statement in the text, abstract and captions beside the table, figure or file it comes from.
PRESENT when: A statement or number in the text differs from the table, figure or file it refers to.
ABSENT when: Every checked statement and number agrees with its table, figure or file.
CANNOT_TELL reasons: NOT_RELEASED: The table, figure or file is not released.; UNREADABLE: The table, figure or file was released and cannot be read.
NOT_APPLICABLE when: The claim has no table, figure or file beside its text.
Text: Quantum Vault: Symmetric No-Cloning Protection for Token Issuer and User (Benchmarked on IBMQ)

Quantum tokens are underlying primitives for quantum money and network proposals, which leverage the no-cloning theorem to realize unforgeable authentication. A relevant but overlooked type of attack to such architectures is one in which a hacker steals the classical side information about the token states from the issuing agent (e.g., a bank), enabling the forgery of fake tokens without violating the no-cloning theorem. Our proposal addresses this threat by removing the classical side information about the token states, where instead a copy of the token is stored at the bank, i.e. a quantum vault. This copy can be accessed by anyone to perform authentication, consuming the token pair in the process. We benchmark the protocol and identify quality parameters within a hardware agnostic framework employing IBMQ processors, such that the protocol is applicable to arbitrary quantum platforms. By comparing the efficiency with which genuine tokens are produced and authenticated against a possible estimate-and-forge attack, we quantify the security of the protocol. We achieve probabilities lower than $10^{-4}$ for false-negative errors (Type 1) and $10^{-10}$ for successful attacks (Type 2) when considering quantum bills composed of 200 tokens, even in the worst performing processor and most conservative uncertainty estimate. The quantum vault not only protects both user and bank symmetrically with the same quantum principles, but provides a step towards public key authentication, since any untrusted party can have access granted by the bank to the tokens' authentication interface without being able to clone them. Besides this bank-mediated form of publicly accessible verifiability, our proposal achieves traceability and revocability, since the bank retains the vault copy of the tokens.
Mark: 

## Row 36, code F4, id d4788a437e5a
Label: PRESENT (via crosstalk)
Quote: "Experiments are conducted on both simulators and quantum devices for Variational Quantum Eigensolver (VQE) tasks to envaluate our methods."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: NAPA: Intermediate-Level Variational Native-Pulse Ansatz for Variational Quantum Algorithms

Variational quantum algorithms (VQAs) have demonstrated great potentials in the Noisy Intermediate Scale Quantum (NISQ) era. In the workflow of VQA, the parameters of ansatz are iteratively updated to approximate the desired quantum states. We have seen various efforts to draft better ansatz with less gates. Some works consider the physical meaning of the underlying circuits, while others adopt the ideas of neural architecture search (NAS) for ansatz generator. However, these designs do not exploit the full advantages of VQAs. Because most techniques target gate ansatz, and the parameters are usually rotation angles of the gates. In quantum computers, the gate ansatz will eventually be transformed into control signals such as microwave pulses on superconducting qubits. These control pulses need elaborate calibrations to minimize the errors such as over-rotation and under-rotation. In the case of VQAs, this procedure will introduce redundancy, but the variational properties of VQAs can naturally handle problems of over-rotation and under-rotation by updating the amplitude and frequency parameters. Therefore, we propose NAPA, a native-pulse ansatz generator framework for VQAs. We generate native-pulse ansatz with trainable parameters for amplitudes and frequencies. In our proposed NAPA, we are tuning parametric pulses, which are natively supported on NISQ computers. Given the limited availability of gradient-based optimizers for pulse-level quantum programs, we choose to deploy non-gradient optimizers in our framework. To constrain the number of parameters sent to the optimizer, we adopt a progressive way to generate our nativepulse ansatz. Experiments are conducted on both simulators and quantum devices for Variational Quantum Eigensolver (VQE) tasks to envaluate our methods. When adopted on NISQ machines, NAPA obtained improved the performance with decreased latency by an average of 86%. NAPA is able to achieve 96.482% and 99.336% accuracy for VQE tasks on H2 and HeH+ respectively. An average accuracy of 97.27% is achieved for medium-size quantum chemistry tasks on CO2, H2O, and NaH. NAPA also demonstrates advantages on quantum optimization tasks even with considerable noises in NISQ machines.
Mark: 

## Row 37, code F3, id 101309cfb11f
Label: ABSENT (via crosstalk)
Quote: "It collects the full tables (S1–S16), figures (S1–S12)"
Definition: F3 Reading without a width. A bounded reading is stated as yes or no, without an interval.
Applies to: Any claim with a bounded reading. A reading is bounded when the claim compares it with a figure, a threshold or a band.
Test: Find each bounded reading. Check whether it is stated with an interval and the level of that interval.
PRESENT when: A bounded reading is stated as yes or no with no interval.
ABSENT when: Each bounded reading carries an interval and its level.
CANNOT_TELL reasons: NOT_RELEASED: The counts needed to form an interval are not released.; UNREADABLE: The counts were released and cannot be read.
NOT_APPLICABLE when: The claim has no bounded reading.
Text: Supplementary material for "Qanela: From Cross-Platform Evidence to a Portable Quantum Assembly Language"

Supplementary material for the article Qanela: From Cross-Platform Evidence to a Portable Quantum Assembly Language (I. Vargas-Chacón, J. Carvajal-Godínez, E. Rivera-Alvarado), submitted to ACM Transactions on Quantum Computing. It collects the full tables (S1–S16), figures (S1–S12), the language grammar and the QPE program listings (S1–S2), the per-job records of the IBM Quantum hardware studies, and the conformance suite that the article cites as supplementary Tables, Figures and Listings. Every table and figure is derived from a JSON file in the two deposited repositories: the language artifact qanela-qal (doi:10.5281/zenodo.23623544, where this document is also kept as supplement/ at commit 6c0aec2) and the profiling study qanela (doi:10.5281/zenodo.23623430).
Mark: 

## Row 38, code F1, id abe62f3274f8
Label: PRESENT (via crosstalk)
Quote: "In this Letter, power narrowing is demonstrated for a class of powers-of-Lorentzian pulse shapes on the IBM Quantum processor ibmq_manila."
Definition: F1 Self-built reference. Results are compared with a reference built from the same setup or from IBM’s stated figures.
Applies to: Any claim that compares a result with a stated reference or with a vendor or device figure.
Test: Find the reference the result is compared with. Read how it was built.
PRESENT when: The reference was built from the same setup as the result, or from the vendor’s stated figures.
ABSENT when: The reference comes from a separate source named in the paper and was not built from the setup or the stated figures.
CANNOT_TELL reasons: METHOD_UNSTATED: The paper does not say how the reference was built.; NOT_RELEASED: The reference or the figures it was built from are named but not released.; UNREADABLE: The reference was released and cannot be read.
NOT_APPLICABLE when: The claim compares its result with no reference.
Text: Defying Conventional Wisdom in Spectroscopy: Power Narrowing on IBM Quantum

Power broadening-the broadening of the spectral line profile of a two-state quantum transition as the amplitude of the driving field increases-is a well-known and thoroughly examined phenomenon in spectroscopy. It typically occurs in continuous-wave driving when the intensity of the radiation field increases beyond the saturation intensity of the transition. In pulsed-field excitation, linear power broadening occurs for a pulse of rectangular temporal shape. Pulses with smooth shapes are known to exhibit much less power broadening, e.g., logarithmic for a Gaussian pulse shape. It has been predicted, but never experimentally verified, that pulse shapes which vanish in time as ∼|t|^{-λ} should exhibit the opposite effect-power narrowing-in which the postpulse transition line width decreases as the amplitude of the driving pulse increases. In this Letter, power narrowing is demonstrated for a class of powers-of-Lorentzian pulse shapes on the IBM Quantum processor ibmq_manila. Reduction of the line width by a factor of over 10 is observed when increasing the pulse area from π to 7π, in a complete reversal of the power broadening paradigm. Moreover, thorough study is conducted on the truncation of the pulse wings which introduces a (small) power-broadened term which prevents power narrowing from reaching extreme values. In the absence of other power broadening mechanisms, Lorentzian pulses truncated at sufficiently small values can achieve as narrow line profiles as desired.
Mark: 

## Row 39, code F4, id 34149f113c21
Label: PRESENT (via crosstalk)
Quote: "We experimentally demonstrate quantum randomness processing based on Bell-basis measurements of two identical input quoins prepared on IBM superconducting hardware."
Definition: F4 Reading not released. A reading needed to recompute the claim is not in the paper or its files: run dates, counts, circuits or intervals.
Applies to: Any claim that can be recomputed. The item circuits applies to claims about quantum circuits only and does not count as missing for other claims.
Test: List the readings the claim depends on. Check each one against the paper and its files. If the method is not stated well enough to name the readings, record Present with a note that the readings could not be listed.
PRESENT when: At least one needed reading is missing from the paper and its files, or the method is not stated well enough to name the needed readings. In the second case the note says so.
ABSENT when: Every needed reading is in the paper or its files.
CANNOT_TELL reasons: UNREADABLE: A released file that may hold a needed reading cannot be read.
NOT_APPLICABLE when: The claim depends on no reading. Such a claim is outside this standard.
Text: Experimental quantum Bernoulli factories via Bell-basis measurements

Randomness processing in the Bernoulli factory framework provides a concrete setting in which quantum resources can outperform classical ones. We experimentally demonstrate quantum randomness processing based on Bell-basis measurements of two identical input quoins prepared on IBM superconducting hardware. Using only the measurement outcomes (and no external classical randomness source), we realize the classically inconstructible Bernoulli doubling primitive f(p)=2p, and, as intermediate outputs from the same Bell-measurement statistics, an exact fair coin f(p)=1/2 and the classically inconstructible function f(p)=4p(1−p). We benchmark the measured output biases against ideal predictions and discuss the impact of device noise. Our results establish a simple resource-efficient experimental primitive for quantum-to-classical randomness processing and support the viability of quantum Bernoulli factories for quantum-enhanced stochastic simulation and sampling tasks.
Mark: 

## Row 40, code F2, id 1e6a907923ec
Label: PRESENT (via crosstalk)
Quote: "Our method provides a way to apply non-reversible operations to a quantum computer without the need for additional qubits."
Definition: F2 Selected result. The headline figure is a selected value: a maximum over rows, a best case, or a projection.
Applies to: Any claim that states a headline figure.
Test: Find the headline figure. Trace it to the rows it came from. Check whether it is a maximum, a best case or a projection.
PRESENT when: The headline figure is a maximum over rows, a best case, or a projection.
ABSENT when: The headline figure is a summary over all rows with the row count printed, or a single pre-named row.
CANNOT_TELL reasons: NOT_RELEASED: The rows the figure came from are not released.; UNREADABLE: The rows were released and cannot be read.
NOT_APPLICABLE when: The claim states no headline figure.
Text: Method for simulating open-system dynamics using midcircuit measurements on a quantum computer

We present a method for simulating the dynamics of an open electronic system on a quantum computer. This approach entails mid-circuit measurements and resets to simulate the addition or removal of electrons from the system. Our method provides a way to apply non-reversible operations to a quantum computer without the need for additional qubits. Using this method, we simulate the dynamics of an open electronic system consisting of a chain of electrons positioned between two conductive leads on the $ibm\_torino$ quantum computer. We expect the method to be generally applicable to open systems.
Mark: 
