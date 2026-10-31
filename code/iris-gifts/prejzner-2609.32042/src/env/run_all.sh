#!/bin/sh
# Runs every check in this folder. Zero GPU, no model calls, standard library only, isolated mode.
# usage: sh run_all.sh [PATH_TO_llama_chat_format.py]   (the optional file is llama-cpp-python v0.3.19, read as text)
set -e
cd "$(dirname "$0")"
python3 -I selftest.py
python3 -I constants_check.py
python3 -I acceptance.py
if [ -n "$1" ]; then python3 -I difftest_llcpp.py "$1"; fi
python3 -I render_prompts.py table
