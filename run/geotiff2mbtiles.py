#!/usr/bin/env python
import sys, os
from subprocess import Popen, PIPE

def geotiff2mbtiles(inputFile, zlstart, zlstop, cpu, outputDir):
    # Create mbtiles directory path
    #mbtilespath = dirPath.split('/')[0:-1]
    #mbtilespath.append(outputDir)
    #mbtilespath = "/".join(mbtilespath)
    if not os.path.exists(outputDir):
        mode = 0o755
        os.makedirs(outputDir, mode)

    gdal2mbtiles_cmd = '/repos/gdal2mbtiles/gdal2mbtiles.py'
    dirPath = "/".join(outputDir.split('/')[0:-1])+'/'
    tiff = dirPath+'tiff'+'/'+inputFile

    diffzl = int(zlstop) - int(zlstart)
    if diffzl != 0:
        zl = zlstart+'-'+zlstop
    elif diffzl == 0:
        zl = zlstart
    else:
        sys.exit('Incorrect zoom level')

    outputFile = ".".join(inputFile.split('.')[0:2])+'.'+zlstart+'.'+zlstop+'.mbtiles'
    mbtiles = outputDir+'/'+outputFile

    cmds_list = [
      ['python', gdal2mbtiles_cmd, tiff, '-z', zl, '--processes='+cpu, mbtiles]
    ]
    procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]

    for proc in procs_list:
        proc.wait()

inputFile = sys.argv[1]
zlstart = sys.argv[2]
zlstop = sys.argv[3]
cpu = sys.argv[4]
outputDir = sys.argv[5]
dirPath = "/".join(outputDir.split('/')[0:-1])+'/'

geotiff2mbtiles(inputFile, zlstart, zlstop, cpu, outputDir)
