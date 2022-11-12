#!/bin/bash
# update ts files

# path to this script
SCRIPT_PATH="$( cd "$(dirname "$0")" || exit 2; pwd -P )"

hash pyrcc5 2> /dev/null || { echo >&2 "pyrcc5 not found, aborting."; exit 1; }

pyrcc5 -o "${SCRIPT_PATH}/taskcounter/resources.py" "${SCRIPT_PATH}/resources.qrc"
