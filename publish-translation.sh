#!/bin/bash
# update qm files

# path to this script
SCRIPT_PATH="$( cd "$(dirname "$0")" || exit 2; pwd -P )"

hash lrelease 2> /dev/null || { echo >&2 "lrelease not found, aborting."; exit 1; }

lrelease "${SCRIPT_PATH}/resources/lang/fr_FR.ts" -qm "${SCRIPT_PATH}/resources/lang/fr_FR.qm"
lrelease "${SCRIPT_PATH}/resources/lang/en_US.ts" -qm "${SCRIPT_PATH}/resources/lang/en_US.qm"
