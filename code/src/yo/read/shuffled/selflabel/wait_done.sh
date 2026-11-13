#!/bin/bash
L=$HOME/bones-forge/yo/read/shuffled/selflabel/sl_drive.log
until grep -qE "== done|FAILED" "$L"; do sleep 30; done; tail -4 "$L"
