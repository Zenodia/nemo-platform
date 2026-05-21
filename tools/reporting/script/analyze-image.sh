#!/usr/bin/env bash

# Script to download an image and produce a report
# We are looking for image efficiency
# TODO, track layer drift between versions

set -ex

NAME=$1
IMAGE=$2

echo NAME=$NAME
echo IMAGE=$IMAGE

rm -rf image image.tgz analysis.json

# copy image down
time skopeo --override-os=linux --override-arch amd64 copy docker://$IMAGE dir:./image
time skopeo copy dir:./image docker-archive:./image.tgz
# generate report
time dive --ci -j analysis.json --source docker-archive ./image.tgz || true

# display report
echo "Analyzing $NAME"
jq ". += { name: \"$NAME\" }" < analysis.json > "$NAME.json" || true
time dive --ci --source docker-archive ./image.tgz
