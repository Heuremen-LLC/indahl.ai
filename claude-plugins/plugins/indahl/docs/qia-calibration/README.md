# indahl-qia-calibration

Checks an IBM Quantum result against the calibration record it ran under, with the QIA Research Package check (qia_check.py, standard library) and the same-job T1/T2 check.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/plugins/qia-calibration

## Services this plugin contacts

- IBM Quantum (quantum.cloud.ibm.com), only when you ask it to pull a backend's calibration or run the T1/T2 check, through your own saved qiskit-ibm-runtime account. Nothing is submitted without your explicit yes.
- indahl.ai (https://indahl.ai/qia/audit.json), a public read of our flagged-qubit list for the T1/T2 check.

Nothing else is contacted. The plugin reads no personal data and stores nothing on any server. Fetched text is treated as data, not instructions.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

Refereed before release by Sage, the outside referee at Heuremen LLC (13 Nov 2026): every fix from her review was applied before this version shipped.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/qia-calibration/scripts/qia_check.py
  sha256 f7354879f19e47d2aac76a15951e125b2a3ce102e0af97aa9f1f75a6c81b7ede
- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/qia-calibration/t1t2/run_check.py
  sha256 16571a2f3f75b8336d08b5815540e59eefc5d1da88f0669572279e7f1f2f016a

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
