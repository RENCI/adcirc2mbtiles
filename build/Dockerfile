# need at least 103 GB to process to tiffs. This includes 102 GB for the tiffs, and 1 GB for the netCDF files.
# need an additional 2 GB for the mbtiles files, for a total of 105 GB. Round off to 110 GB for good luck.
# need 28+ GB for the final color tiffs, and 70+ GB for the raw tiffs. The raw tiffs will be deleted after 
# they have been used to produce the color tiffs. We plan to save the color tiffs as well as the mbtiles.
# to process one maxele.63.nc file to tiff, I will need 52+ MB for the netCDF file, 14+ GB for the raw tiff
# file and 7 GB for the color tiff file, for a total of 22 GB.
# set the base image
FROM continuumio/anaconda3

# author
MAINTAINER Jim McManus

# extra metadata
LABEL version="1.0"
LABEL description="adcirc2mbtiles image with Dockerfile."

# update sources list, and install basic apps, one per line for better caching
RUN apt-get clean && apt-get update &&\
    apt-get install -qy nano \
    libgl1 \
    libgl1-mesa-dev \
    vim \
    aria2

# update conda and set the download channel
RUN conda update conda && \
    conda config --add channels conda-forge

WORKDIR /app

# Create the environment, initialize conda in bash config files, and install repos:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "adcirc2mbtiles", "/bin/bash", "-c"]

# make d directory for the repos and go there
RUN mkdir /repos
WORKDIR /repos

# get the repos
RUN git clone https://github.com/renci/adcirc2mbtiles.git &&\
    git clone https://github.com/pchynoweth/gdal2mbtiles.git

# change to the run directory                        
WORKDIR /repos/adcirc2mbtiles/run

# set the python path
ENV PYTHONPATH=/repos/adcirc2mbtiles

#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "adcirc2mbtiles"]

#CMD ["python", "adcirc2geotiff.py", "--inputFile", "maxele.63.nc", "--outputDir", "/data/sj37392jdj28538/tiff"]
