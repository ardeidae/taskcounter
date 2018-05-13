#!/bin/bash
# convert a png image to an iconset icns.

# path to this script
SCRIPT_PATH="$( cd "$(dirname "$0")" || exit 2; pwd -P )"

IMAGE=tasks
SET_NAME="${IMAGE}.iconset"
mkdir "${SCRIPT_PATH}/../${SET_NAME}"

sips -z 16 16     "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_16x16.png"
sips -z 32 32     "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_16x16@2x.png"
sips -z 32 32     "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_32x32.png"
sips -z 64 64     "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_32x32@2x.png"
sips -z 128 128   "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_128x128.png"
sips -z 256 256   "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_128x128@2x.png"
sips -z 256 256   "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_256x256.png"
sips -z 512 512   "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_256x256@2x.png"
sips -z 512 512   "${SCRIPT_PATH}/../resources/images/${IMAGE}.png" --out "${SCRIPT_PATH}/../${SET_NAME}/icon_512x512.png"

iconutil -c icns "${SCRIPT_PATH}/../${SET_NAME}"

rm -rf "${SCRIPT_PATH}/../${SET_NAME}"
