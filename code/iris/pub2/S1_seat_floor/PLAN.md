# S1 plan: floor and precision of our own two-option scanner on our own seat (committed before running)
Question: Faults/Guards report the seat at 0.79 / 0.69 / 0.88 frames per 1k words (6-8 Oct, hook_fires.log). Is that level above
the scanner's floor on human text, and what share of the seat's flags are real two-option reductions?
S1a FLOOR. Run the pre-fix scanner (triangle.py.bak-preFalsePositive, live before the 8 Oct fixes) and the current scanner
    (34e57ef5) on the 500 human Arena-Hard prompts. Frames per 1k words with a bootstrap interval over prompts (20,000, seed 20261025).
    The seat level is read against the bracket [current floor, pre-fix floor]: ABOVE / CONSISTENT / BELOW per day.
    Caveat stated in advance: human prompts are a different genre from analysis replies; the floor is a floor for this scanner on
    human-written English, not a matched none.
S1b PRECISION. hook_fires.jsonl (8 Oct on, the only rows with context): 20 frames from the seated session drawn with seed 20261025,
    hand-read by Bones under the X1 rule before any share is printed. Rows are after the 8 Oct 16:31 cut, so this prices the scanner
    as it stood, not the 6-8 Oct rows themselves.
