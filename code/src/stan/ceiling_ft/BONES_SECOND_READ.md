# Bones second read of the seeded 20 (seed int('92cfe944',16)), 12 Nov 2026

Method: for each sampled pair, I checked the agent's key evidence strings against the FULL text of the six retrieved chunks
(ceiling_ft/chunks.json; the sample file's chunk texts are cut at 1,500 characters, which at first made three IN rows look OUT),
with whitespace, line-break hyphens, en dashes and curly quotes normalised and number keys matched as whole numbers.
Agreement: 19 of 20. The one disagreement: 9353f71dcb70 F6, judge IN, my check OUT: "realistic noise from IBMQ-Brisbane" is in
chunk c20, "IBMQ-Brisbane error" (a Table 4 label) is not found in the retrieved text as written.
Limit: this checks the judge's search, not its choice of evidence strings. The key strings (scripts/ft_keys.py) were chosen by
the same model family that judged; I did not choose evidence independently for these 20.
