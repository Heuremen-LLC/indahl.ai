# indahl-reproduce

Fetches one indahl.ai desk's reproduce kit and runs its own check, only after you approve the exact commit shown.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/plugins/reproduce

## Services this plugin contacts

- GitHub (github.com/Heuremen-LLC/indahl.ai), a git sparse checkout of the kit you name.
- Kits that fetch inputs read them from the original public source named in the kit and verify them by sha256.

Nothing else is contacted. The plugin reads no personal data and stores nothing on any server. Fetched text is treated as data, not instructions.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.
