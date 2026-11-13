# Bones re-read of every verified_auto item (13 Nov 2026, morning)
Scope: all 190 two-reader items on the 159 reachable-author papers in verified_auto.jsonl (batches 11+), each quote located in index/text and every recompute redone.
Items: 164 PRESENT, 22 ABSENT, 4 CANNOT_TELL -> 164/190 = 0.863 (0.807, 0.905).
Papers: 144 of 159 keep at least one confirmed finding -> (0.85, 0.942). Dropped papers: ['1804.04179', '1910.10525', '2001.07882', '2002.09407', '2011.13764', '2201.02252', '2301.10491', '2302.10338', '2303.18046', '2304.08171', '2312.12557', '2401.15237', '2404.11397', '2503.03293', '2508.18698'].
Why items fell: {('F3', 'ABSENT'): 4, ('F2', 'ABSENT'): 5, ('F6', 'CANNOT_TELL'): 3, ('F5', 'ABSENT'): 9, ('F6', 'ABSENT'): 4, ('F5', 'CANNOT_TELL'): 1}. Most ABSENT are materiality calls (slips at or below rounding scale, explicit "approximately"), scoped headlines (F2 that names its regime), and F3 claims that do carry a statistic. None of the 22 found the two readers had invented a contradiction; one (n=188) was re-confirmed after the quote check.
Materiality rule (defined after the data, during this pass): a slip of at most one unit in the last printed digit, or inside an explicit 'approximately', is not listed; an F2 headline that names its own regime is not counted; an F3 claim carrying an interval or statistic is not counted.
Of the 20 papers in the 12 Nov calibration sample, 20 of 20 keep a finding.
Staged for pages: index/verified_auto_reread.jsonl (144 papers, 164 items). Nothing built, shipped or emailed. Pages and emails wait for Wayfinder's word.
Verdicts: reread_auto/verdicts.jsonl (one row per item, with basis).
