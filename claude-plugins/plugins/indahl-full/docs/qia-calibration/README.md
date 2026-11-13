# indahl-qia-calibration

Checks an IBM Quantum result against the calibration record it ran under, with the QIA Research Package check (qia_check.py, standard library) and the same-job T1/T2 check.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/plugins/qia-calibration

## Services this plugin contacts

- IBM Quantum (quantum.cloud.ibm.com), only when you ask it to pull a backend's calibration or run the T1/T2 check, through your own saved qiskit-ibm-runtime account. Nothing is submitted without your explicit yes.
- indahl.ai (https://indahl.ai/qia/audit.json), a public read of our flagged-qubit list for the T1/T2 check.

Nothing else is contacted. The plugin reads no personal data and stores nothing on any server. Fetched text is treated as data, not instructions.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

Refereed before release by Sage, the outside referee at Heuremen LLC (13 Nov 2026): every fix from her review was applied before this version shipped.
