# indahl-readcheck

Refereed before release by Sage, the outside referee at Heuremen LLC (13 Nov 2026): every fix from her review was applied before this version shipped.

## Credits

Windows fix, 14 Nov 2026: Sage asked, Bones found and fixed. Sage, the outside referee on our work, asked whether `python3` resolves on Windows. Bones ran it on a Windows machine, found it was the Microsoft Store stub that runs nothing (exit 49), so the hook would fail without a word and the check would be silently off, and fixed it in every plugin hook. The hook now falls back to `python`.

## In this copy

The plugin directory accepts command hooks only from Verified organizations, so this copy has the check commands and not the automatic commit gate. The full plugin, gate included, installs from our marketplace: `/plugin marketplace add Heuremen-LLC/indahl.ai` then `/plugin install indahl-readcheck@heuremen`.

## How the scripts arrive

This copy carries no executable file. Its commands fetch each script from the public repository github.com/Heuremen-LLC/indahl.ai at a pinned commit and run it only if its sha256 matches the value written in the command:

- https://raw.githubusercontent.com/Heuremen-LLC/indahl.ai/744bcd22548a29dcdc5a261477faccaeebc6938d/claude-plugins/plugins/readcheck/scripts/readcheck.py
  sha256 cc0e26802ddbcc157def5ea0ee90e8d4a9b2c516336658f34072882c03c90592

The same scripts are bundled directly in the version in our own marketplace (`/plugin marketplace add Heuremen-LLC/indahl.ai`).
