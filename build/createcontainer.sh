#!/bin/bash
# setup specific to apsviz-maps
version=$1;

docker run -ti --name adcirc2mbtiles_$version \
  --volume /d/dvols/apzviz:/data/sj37392jdj28538 \
  -d adcirc2mbtiles:$version /bin/bash 
