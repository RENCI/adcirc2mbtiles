# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

##############
# Docker file for the creation of the adcirc geotiffs and mbtiles files.
#
# to create image: docker build -t adcirc2mbtiles:latest .
# to push image:
#       docker tag adcirc2mbtiles:latest renciorg/adcirc2mbtiles:latest
#       docker push renciorg/adcirc2mbtiles:latest
##############
# need at least 103 GB to process to tiffs. This includes 102 GB for the tiffs, and 1 GB for the netCDF files.
# need an additional 2 GB for the mbtiles files, for a total of 105 GB. Round off to 110 GB for good luck.
# need 28+ GB for the final color tiffs, and 70+ GB for the raw tiffs. The raw tiffs will be deleted after 
# they have been used to produce the color tiffs. We plan to save the color tiffs as well as the mbtiles.
# to process one maxele.63.nc file to tiff, I will need 52+ MB for the netCDF file, 14+ GB for the raw tiff
# file and 7 GB for the color tiff file, for a total of 22 GB.
# set the base image
##############
FROM continuumio/miniconda3

# author
MAINTAINER Jim McManus

# extra metadata
LABEL version="1.0"
LABEL description="adcirc2mbtiles image with Dockerfile."

# update sources list, and install basic apps, one per line for better caching
RUN apt-get clean && apt-get --allow-releaseinfo-change update &&\
    apt-get install -qy vim \
    libgl1 \
    libgl1-mesa-dev \
    aria2

# update conda and set the download channel
RUN conda update conda && \
    conda config --add channels conda-forge

# create a non-root user
RUN useradd -m -d /home/nru -u 1000 nru

# create a needed dir
RUN mkdir /home/nru/app
WORKDIR /home/nru/app

# Create the environment, initialize conda in bash config files, and install repos:
COPY environment.yml .
RUN conda env create -f environment.yml

# make a directory for the repos and go there
RUN mkdir /home/nru/repos
WORKDIR /home/nru/repos

# get the repos
RUN git clone https://github.com/renci/adcirc2mbtiles.git &&\
    git clone https://github.com/pchynoweth/gdal2mbtiles.git

# this dir was expected by the running pod. this will insure that it isnt defaulted to something else
RUN mkdir -p /home/nru/.config/matplotlib

# change to the run directory
WORKDIR /home/nru/repos/adcirc2mbtiles/run

# make sure everything is read/write
RUN chmod 777 -R /home/nru

# switch to the non-root user
USER nru

# set the python path
ENV PYTHONPATH=/home/nru/repos/adcirc2mbtiles

# tell conda what the shell is
RUN conda init bash

