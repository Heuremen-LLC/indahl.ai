# Base model, Job A: a second reading defined after the replies were read (31 Oct 2026 ~17:55 EDT, before any YO output)
The plan scores Job A from strict JSON. Reading a sample of the base model's replies in full showed most are not valid JSON: the stale
list is written with unquoted labels (q16 instead of 16), and the zero list is filled with placeholder fields ("q16:field").
Strict (the plan's rule): 0.048, 288 of 400 replies not valid JSON. Lenient (defined after the data: labels like q16 read as 16, q16:field
read as 16:field): 0.220, stale list found in 399 of 400. Both are far below flag-nothing (0.716). The comparison rule for YO stays the
plan's strict rule. The lenient reading is shown beside the strict one on the page, labelled as defined after the data. Code: posthoc_base_a.py.
