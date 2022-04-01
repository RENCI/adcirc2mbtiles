#!/bin/bash
version=$1;

docker buildx build --no-cache --platform linux/arm64 -f Dockerfile -t adcirc2mbtiles:$version .
