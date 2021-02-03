# adcirc2mbtiles
Converts ADCIRC mesh data, in a NetCDF file to a MapBox tiles (mbtiles) file.

## Build
  cd build  
  docker build -t adcirc2mbtiles_image .

## Test Run
  To run in test mode first edit the Docker file removing the commenting out of the ENTRYPOINT and CMD:

      ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "adcirc2mbtiles"] 

      CMD ["python", "adcirc2geotiff.py", "maxele.63.nc", "/data/sj37392jdj28538/tiff"]

  Then to run default settings you must make an input directory () in your /directory/path/to/storage/ directory: 

    mkdir /directory/path/to/storage/input

  and put a maxele.63.nc file in it. Then run following command:

    docker run --volume /directory/path/to/storage/:/data/sj37392jdj28538 adcirc2mbtiles_image

  To use a different file, such as maxwvel.63.nc, you put that file in the input directory and run the following command:

    docker run --volume /directory/path/to/storage:/data/sj37392jdj28538 adcirc2mbtiles_image python adcirc2geotiff.py maxwvel.63.nc tiff

  After producing a tiff image, you can create a mbtiles file by running the following command:

    docker run --volume /directory/path/to/storage:/data/sj37392jdj28538 adcirc2mbtiles_image python geotiff2mbtiles.py maxele.63.tif 0 9 6 mbtiles


