# adcirc2mbtiles
Converts ADCIRC mesh data, in a NetCDF file to a MapBox tiles (mbtiles) file.

## Build
  cd build  
  docker build -t adcirc2mbtiles_image .

## Test Run
  To run in test mode first edit the Docker file removing the commenting out of the ENTRYPOINT and CMD:

      ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "adcirc2mbtiles"] 

      CMD ["python", "adcirc2geotiff.py", "--inputFile", "maxele.63.nc", "--outputDir", "/data/sj37392jdj28538/tiff"]

  Then to run default settings you must make an input directory () in your /directory/path/to/storage/ directory: 

    mkdir /directory/path/to/storage/input

  and put a maxele.63.nc file in it. Then run following command:

    docker run --volume /directory/path/to/storage/:/data/sj37392jdj28538 adcirc2mbtiles

  To use a different file, such as maxwvel.63.nc, you put that file in the input directory and run the following command:

    docker run --volume /directory/path/to/storage:/data/sj37392jdj28538 adcirc2mbtiles python adcirc2geotiff.py --inputFile maxwvel.63.nc --outputDir /data/sj37392jdj28538/tiff

  After producing a tiff image, you can create a mbtiles file by running the following command:

    docker run --volume /directory/path/to/storage:/data/sj37392jdj28538 adcirc2mbtiles python geotiff2mbtiles.py --inputFile maxwvel.63.tif --zlstart 0 --zlstop 9 --cpu 6 --outputDir /data/sj37392jdj28538/mbtiles 

   These methods will create exited containers, which you will need to remove after using. Below is an explanation of how to create a stand alone container, and run the commands above inside the container.

## Create Container

  Another way of testing is to create a stand alone container. An example of how to do this is shown below:

    docker run -ti --name adcirc2mbtiles --volume /directory/path/to/storage:/data/sj37392jdj28538 -d adcirc2mbtiles /bin/bash

  After the container has been created, you can access it using the following command:

    docker exec -it adcirc2mbtiles bash

  To create tiffs and mbtiles you must first activate the conda enviroment using the following command:

    conda activate adcirc2mbtiles

  Now you can run the command to create a tiff:

    python adcirc2geotiff.py --inputFile maxwvel.63.nc --outputDir /data/sj37392jdj28538/tiff

  and the command to create the mbtiles file:

    python geotiff2mbtiles.py --inputFile maxwvel.63.tif --zlstart 0 --zlstop 9 --cpu 6 --outputDir /data/sj37392jdj28538/mbtiles
 
