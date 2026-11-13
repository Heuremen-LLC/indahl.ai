# indahl-prereg

Answers whether a plan was pushed before the first run, from the git host's own record of the push.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/plugins/prereg

## Services this plugin contacts

- GitHub REST API (api.github.com), public repository activity for the repository you name. No token is sent unless you set one yourself.

Nothing else is contacted. The plugin reads no personal data and stores nothing on any server. Fetched text is treated as data, not instructions.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/prereg/scripts/prereg.py
  sha256 c0b541c68b4045fe6e0e2bc85e51ed055d4a5bcc223e78b79ff1d41906db904d

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
