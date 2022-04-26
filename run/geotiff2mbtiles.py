#!/usr/bin/env python
# Import Python modules
import sys, os, argparse, shutil
from pathlib import Path
from loguru import logger
from subprocess import Popen, PIPE

# This function takes a tiff file and converts it to an mbtiles file, based on inputs
def geotiff2mbtiles(inputFile, zlstart, zlstop, cpu, inputDir, outputDir, finalDir):
    # Create mbtiles directory path
    if not os.path.exists(outputDir):
        #mode = 0o755
        #os.makedirs(outputDir, mode)
        os.makedirs(outputDir, exist_ok=True)
        logger.info('Made directory '+Path(outputDir).parts[-1]+ '.')
    else:
        logger.info('Directory '+Path(outputDir).parts[-1]+' already made.')

    # Define gdal2mbtiles command, and directory paths
    gdal2mbtiles_cmd = '/home/nru/repos/gdal2mbtiles/gdal2mbtiles.py'

    # Combine start and stop zooms to be able to run in gdal2mbtiles command 
    diffzl = int(zlstop) - int(zlstart)
    if diffzl != 0:
        zl = zlstart+'-'+zlstop
    elif diffzl == 0:
        zl = zlstart
    else:
        logger.info('Incorrect zoom level')
        sys.exit('Incorrect zoom level')

    # Define output file name
    outputFile = ".".join(inputFile.split('.')[0:2])+'.'+zlstart+'.'+zlstop+'.mbtiles'

    # Check if output file exist, and remove it if it does exist
    if os.path.exists(outputDir+outputFile):
        os.remove(outputDir+outputFile)
        logger.info('Removed old mbtiles file '+outputDir+outputFile+'.')
        logger.info('Mbtiles path '+outputDir+outputFile+'.')
    else:
        logger.info('Mbtiles path '+outputDir+outputFile+'.')

    # Define command and run it
    cmds_list = [
      ['python', gdal2mbtiles_cmd, inputDir+inputFile, '-z', zl, '--processes='+cpu, outputDir+outputFile]
    ]
    procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]

    for proc in procs_list:
        proc.wait()

    logger.info('Created mbtiles file '+outputFile+' from tiff file '+inputFile+'.')

    # Create final directory path
    if not os.path.exists(finalDir):
        # mode = 0o755
        # os.makedirs(finalDir, mode)
        os.makedirs(finalDir, exist_ok=True)
        logger.info('Made directory '+Path(finalDir).parts[-1]+ '.')
    else:
        logger.info('Directory '+Path(finalDir).parts[-1]+' already made.')

    # Move mbtiles file to findal mbtiles directory
    shutil.move(outputDir+outputFile, finalDir+outputFile)
    logger.info('Moved mbtiles file to '+Path(finalDir).parts[-1]+' directory.')

@logger.catch
def main(args):
    # get input variables from args
    inputFile = args.inputFile 
    zlstart = args.zlstart
    zlstop = args.zlstop
    cpu = args.cpu
    inputDir = os.path.join(args.inputDir, '')
    outputDir = os.path.join(args.outputDir, '')
    finalDir = os.path.join(args.finalDir, '')

    # Remove old logger and start new one
    logger.remove()
    log_path = os.path.join(os.getenv('LOG_PATH', os.path.join(os.path.dirname(__file__), 'logs')), '')
    logger.add(log_path+'geotiff2mbtiles.log', level='DEBUG')

    # Check if input file exist, and then run geotiff2mbtiles function
    if os.path.exists(inputDir+inputFile):
        # When error exit program
        logger.add(lambda _: sys.exit(0), level="ERROR")

        logger.info('Create mbtiles file, with zoom levels '+zlstart+' to '+zlstop+', from '+inputFile.strip()+' tiff file '+inputFile+' using '+cpu+' CPUs.')

        geotiff2mbtiles(inputFile, zlstart, zlstop, cpu, inputDir, outputDir, finalDir)

    else:
        logger.info(inputDir+inputFile+' does not exist')
        if inputFile.starstswith("swan"):
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Argument which requires a parameter (eg. -d test)
    parser.add_argument("--inputFile", help="Input file name", action="store", dest="inputFile", required=True)
    parser.add_argument("--zlstart", help="Start zoom level", action="store", dest="zlstart", required=True)
    parser.add_argument("--zlstop", help="Stop zoom level", action="store", dest="zlstop", required=True)
    parser.add_argument("--cpu", help="Number of CPUs to use", action="store", dest="cpu", required=True)
    parser.add_argument("--inputDIR", "--inputDir", help="Input directory path", action="store", dest="inputDir", required=True)
    parser.add_argument("--outputDIR", "--outputDir", help="Output directory path", action="store", dest="outputDir", required=True)
    parser.add_argument("--finalDIR", "--finalDir", help="Final directory path", action="store", dest="finalDir", required=True)

    args = parser.parse_args()
    main(args)

