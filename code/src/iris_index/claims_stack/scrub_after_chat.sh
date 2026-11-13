#!/bin/bash
# 29 Oct (ROUND_S1.md addendum 3): the old-name file rename, written to run when the round ends, now runs when the BBH chat queue job ends.
until [ -f ~/bones-forge/iris_index/queue_s1-bbh-chat.log ] && grep -q "S1B DONE" ~/bones-forge/iris_index/queue_s1-bbh-chat.log; do sleep 120; done
exec bash ~/bones-forge/tools/scrub_name_iris.sh 99999999
