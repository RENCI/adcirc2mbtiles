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

# tell conda what the shell is
RUN conda init bash

# make d directory for the repos and go there
RUN mkdir /repo
WORKDIR /repo

# get the repo
RUN git clone https://github.com/renci/adcirc2mbtiles.git

# define working directory
WORKDIR adcirc2mbtiles/build

# Create the environment, initialize conda in bash config files, and install repo:
RUN conda env create -f environment.yml

# change to the run directory                        
WORKDIR /repo/adcirc2mbtiles/run

# set the python path
ENV PYTHONPATH=/repo/adcirc2mbtiles

# set the location of the output directory
ENV RUNTIMEDIR=/stageDIR

ENTRYPOINT ["conda run -n adcirc2mbtiles python adcirc2geotiff.py"]

CMD ["maxele.63.nc", "tiff"]
