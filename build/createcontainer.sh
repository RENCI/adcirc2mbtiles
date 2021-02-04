#!/bin/bash
# setup specific to apsviz-maps
docker run -ti --name adcirc2mbtiles \
  --volume /d/dvols/apzviz:/data/sj37392jdj28538 \
  -d jmpmcmanus/adcirc2mbtiles /bin/bash 
