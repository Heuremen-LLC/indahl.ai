# indahl-triangulate

One question, three independent seats run blind, read item by item. The outcome is one of four (ABOVE, BELOW, CONSISTENT, CANNOT_TELL; or HOLDS, FAILS, SPLIT, CANNOT_TELL for yes/no questions), with what would decide it and a RECEIPT.md holding every seat's answer verbatim.

Heuremen LLC, https://indahl.ai. Source: https://github.com/Heuremen-LLC/indahl.ai/tree/main/claude-plugins/src/triangulate

## Services this plugin contacts

None. It runs inside your session. If the indahl.ai connector (indahl-data) is installed, a seat may read indahl.ai's public data through it.

Privacy: https://indahl.ai/privacy. Terms: https://indahl.ai/terms.

## Credits

Sage, the outside referee on our work, found on 14 Nov 2026 (her item #25) that this skill asked each seat for evidence but never checked it, and counted seats instead of evidence. The grounding rules (UNGROUNDED, SHARED_SOURCE, two grounded seats on independent evidence chains) are hers, applied at the lines she named.
