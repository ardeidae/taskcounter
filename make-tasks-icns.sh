#!/bin/bash
# convert a png image to an iconset icns.

IMAGE=tasks
SET_NAME="${IMAGE}.iconset"
mkdir "${SET_NAME}"

sips -z 16 16     "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_16x16.png"
sips -z 32 32     "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_16x16@2x.png"
sips -z 32 32     "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_32x32.png"
sips -z 64 64     "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_32x32@2x.png"
sips -z 128 128   "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_128x128.png"
sips -z 256 256   "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_128x128@2x.png"
sips -z 256 256   "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_256x256.png"
sips -z 512 512   "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_256x256@2x.png"
sips -z 512 512   "resources/images/${IMAGE}.png" --out "${SET_NAME}/icon_512x512.png"

iconutil -c icns ${SET_NAME}

rm -rf "${SET_NAME}"
