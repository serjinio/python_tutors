#!/bin/bash
# Startup script

script_dir="$(cd "$0"; pwd)"
export PYTHONPATH="$script_dir"

echo "set PYTHONPATH to: $PYTHONPATH"
python app.py
