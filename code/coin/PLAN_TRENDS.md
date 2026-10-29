# COIN trends: pool shares over time and batch payouts (28 Oct 2026, his word)
Written and committed before any trend or payout series was computed.

## What is read
Ravencoin block records already collected (first payout address and coinbase tag per block, newest blocks appended on every round), and for payouts, the transactions inside each block, read forward from the chain. The explorer's per-address history is not in time order, so payouts are found by scanning blocks and keeping every transaction whose inputs all come from one watched address and that has 20 or more outputs. Watched addresses are the ten most frequent first payout addresses in the window.

## Pool shares over time (the share-move test)
Six hour buckets, UTC. For each of the ten addresses and the six most frequent coinbase tags, the share of blocks in the bucket against a baseline p, the same series' share over the preceding seven days (or all earlier data in the window, stated, while fewer than seven days exist). z = (bucket share - p) / sqrt(p (1 - p) / n), n the blocks in the bucket. A move is |z| of 3 or more. Blocks are random draws, so some flags are expected from chance: expected flags = tests x 0.0027. Both are published for each series. Outcome per series: ABOVE if observed flags exceed expected plus two square roots of expected, CONSISTENT if not, CANNOT_TELL while fewer than 14 days are held. Concentration is also tracked per bucket as the share of the top address and of the top three.

## Batch payouts
For each watched address: the payouts found (time, outputs, total RVN), the median and spread of the gap between payouts, the median outputs and total, how many distinct recipient addresses, and how much of its payout volume went to its five largest recipients. Across watched addresses: recipients shared by more than one, and any payout from one watched address to another. Addresses are shown as the chain records them with the coinbase tag where the same address signs blocks. Nothing here says who holds an address.

## Not done
No price, profit, return or forecast. No statement about intent or ownership. A pattern that fits several causes is stated as a pattern.

## Output
A Trends section on the COIN page, live. Every printed figure follows the page's existing practice for live panels. The collector and analysis scripts go in the public repository.

## Addendum 1 (28 Oct, before any series: the linkage test, his hypothesis)
His word: two of the large pools were operated by the same party. The chain can show shared infrastructure, never identity, so the test is written as a comparison against a floor.
For every pair of watched addresses: the overlap of their payout recipient sets (Jaccard, and the share of each one's payout volume that goes to recipients also paid by the other), whether either pays the other, and whether their blocks follow each other more or less often than chance (successive blocks by the pair against the count expected from their shares). The floor is the same quantities over all other pairs. A pair is called ABOVE the floor if its recipient overlap is above the largest overlap seen among the other pairs that share no direct payment and its volume share is above the 95th percentile of the other pairs. CONSISTENT with the floor if not. CANNOT_TELL while fewer than 30 payout batches are held for either address. Recipients that are exchanges or miners using several pools produce overlap without a common operator, so an ABOVE reading is reported as shared recipients, and the page says that is all it is. Pairs are named by their addresses and coinbase tags as the chain records them.

## Addendum 2 (28 Oct, before any series: the floor moves outside the pool set, his correction)
Pools on one chain are not unrelated: miners move between pools and exchanges pay several of them, so overlap among the pairs in the same set cannot serve as the floor. The threshold for the linkage test now comes from a control chain, and the statistic is calibrated on it before it is read on Ravencoin.
Control: Bitcoin pools, where operator relationships are documented in public. Positive control: AntPool and BTC.com, which Bitmain documents as its own. Negative controls: pairs of pools documented as separate companies (Foundry USA, F2Pool, ViaBTC, Luxor, SpiderPool among them). The same quantities are computed the same way: recipient overlap of payout batches (Jaccard and volume share) and successive-block excess, from the same block scan of the same kind of window.
Known-good gate: the statistic must flag the positive control and must not flag any negative pair. If it fails either, the Ravencoin linkage reading is CANNOT_TELL and the page says the instrument failed its gate. The ABOVE threshold on Ravencoin is the largest overlap seen among the negative control pairs, not any figure from the Ravencoin set. The Ravencoin internal pair overlaps are still shown as descriptive context, never as the floor.
Sources: the pool addresses are taken from mempool.space's pool list as published there, with the page and date recorded. If those addresses cannot be read, the control is not built and the reading is CANNOT_TELL.
