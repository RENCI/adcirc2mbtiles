# adcirc2mbtiles
Converts ADCIRC mesh data, in a NetCDF file to a MapBox tiles (mbtiles) file.

## Build
  cd build  
  docker build -t adcirc2mbtiles_image .

## Create Container

  To create a stand alone container for testing use the command shown below:

    docker run -ti --name adcirc2mbtiles --volume /directory/path/to/storage:/data/sj37392jdj28538 -d adcirc2mbtiles /bin/bash

  After the container has been created, you can access it using the following command:

    docker exec -it adcirc2mbtiles bash

  To create tiffs and mbtiles you must first activate the conda enviroment using the following command:

    conda activate adcirc2mbtiles

  Now you can run the command to create a tiff:

    python adcirc2geotiff.py --inputFile maxwvel.63.nc --outputDir /data/sj37392jdj28538/tiff

  and the command to create the mbtiles file:

    python geotiff2mbtiles.py --inputFile maxwvel.63.tif --zlstart 0 --zlstop 9 --cpu 6 --outputDir /data/sj37392jdj28538/mbtiles

## Running in Kubernetes

When running the container in Kubernetes the command line for adcirc2geotiff.py would be:

    conda run -n adcirc2mbtiles python adcirc2geotiff.py --inputFile maxwvel.63.nc --outputDir /xxxx/xxxxxxxxxx/tiff

And to run geotiff2mbtiles.py the command line would be:

    conda run -n adcirc2mbtiles python geotiff2mbtiles.py --inputFile maxwvel.63.tif --zlstart 0 --zlstop 9 --cpu 6 --outputDir /xxxx/xxxxxxxxxx/mbtiles

Where /xxxx/xxxxxxxxxx would be a specified directory path.
 
