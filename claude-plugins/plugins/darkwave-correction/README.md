# indahl-darkwave

Checks and corrects IBM Quantum runs with the Darkwave Correction Kit.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/plugins/darkwave-correction

## Services this plugin contacts

- IBM Quantum (quantum.cloud.ibm.com), through your own saved qiskit-ibm-runtime account, to read a backend and, only with --yes in an interactive terminal, to submit the measurement circuits (paid on your account).

Nothing else is contacted. The plugin reads no personal data and stores nothing on any server. Fetched text is treated as data, not instructions.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/darkwave-correction/scripts/darkwave_kit.py
  sha256 a43b1cf8989928dfd3f94b40b4ae5491d31e52e85cec117e315c4ad4fbc6a401

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
