#!/bin/bash
version=$1;

docker build -t adcirc2mbtiles:$version .
