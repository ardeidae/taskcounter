#!/bin/bash
# update ts files

# path to this script
SCRIPT_PATH="$( cd "$(dirname "$0")" || exit 2; pwd -P )"

hash pylupdate5 2> /dev/null || { echo >&2 "pylupdate5 not found, aborting."; exit 1; }

pylupdate5 $(find "${SCRIPT_PATH}/taskcounter" -type f -name '*.py') -ts "${SCRIPT_PATH}/resources/lang/fr_FR.ts"
pylupdate5 $(find "${SCRIPT_PATH}/taskcounter" -type f -name '*.py') -ts "${SCRIPT_PATH}/resources/lang/en_US.ts"
