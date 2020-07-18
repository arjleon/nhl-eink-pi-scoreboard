#!/bin/bash
# Get directory of script and attempt to update git and run python script against venv
DIR=$(dirname "$0")
(cd "$DIR" || exit; git pull; ./venv/bin/python main.py)