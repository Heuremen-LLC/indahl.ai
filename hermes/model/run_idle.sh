#!/bin/zsh
# The readings in mac_run.jsonl, with every other app closed and our other jobs paused for the run.
# Build first:  clang -O3 -o stream stream.c -lpthread   and   swiftc -O gpu_bw.swift -o gpu_bw
OUT=mac_run_$(date +%Y%m%d_%H%M%S).jsonl
{ echo "{\"kind\":\"env\",\"at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"loadavg\":\"$(sysctl -n vm.loadavg)\",\"powermode\":\"$(pmset -g | awk '/powermode/{print $2}')\"}"
  for t in 6 12 18; do for rep in 1 2 3; do ./stream $t 1.0 15; done; done
  for rep in 1 2 3; do ./gpu_bw 1024 20; done
  echo "{\"kind\":\"env_after\",\"loadavg\":\"$(sysctl -n vm.loadavg)\",\"at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
} > $OUT
echo $OUT
