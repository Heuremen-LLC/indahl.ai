#!/bin/bash
# 29 Oct, his word: COIN back transactions over time. 30 days of blocks (43,200) then the transactions of those blocks. Resumable.
cd ~/bones-forge/coin_index
python3 -I rvn_history.py 4555233 4598432 > history.log 2>&1
python3 -I rvn_txs.py > history_txs.log 2>&1
echo done > history.DONE
