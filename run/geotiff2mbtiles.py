#!/usr/bin/env python
import sys, os
from subprocess import Popen, PIPE

def geotiff2mbtiles(dirPath, inputFile, zlstart, zlstop, cpu, outputDIR):
    # Create mbtiles directory path
    mbtilespath = dirPath.split('/')[0:-1]
    mbtilespath.append(outputDIR)
    mbtilespath = "/".join(mbtilespath)
    if not os.path.exists(mbtilespath):
        mode = 0o755
        os.makedirs(mbtilespath, mode)

    gdal2mbtiles_cmd = '/repos/gdal2mbtiles/gdal2mbtiles.py'
    tiff = dirPath+'tiff'+'/'+inputFile

    diffzl = int(zlstop) - int(zlstart)
    if diffzl != 0:
        zl = zlstart+'-'+zlstop
    elif diffzl == 0:
        zl = zlstart
    else:
        sys.exit('Incorrect zoom level')

    outputFile = ".".join(inputFile.split('.')[0:2])+'.'+zlstart+'.'+zlstop+'.mbtiles'
    mbtiles = mbtilespath+'/'+outputFile

    cmds_list = [
      ['python', gdal2mbtiles_cmd, tiff, '-z', zl, '--processes='+cpu, mbtiles]
    ]
    procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]

    for proc in procs_list:
        proc.wait()

dirPath = '/stageDIR/'
inputFile = sys.argv[1]
zlstart = sys.argv[2]
zlstop = sys.argv[3]
cpu = sys.argv[4]
outputDIR = sys.argv[5]

geotiff2mbtiles(dirPath, inputFile, zlstart, zlstop, cpu, outputDIR)
