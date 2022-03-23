#!/usr/bin/env python
# Import Python modules
import os, sys, argparse, shutil, json, warnings
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import netCDF4 as nc
from pathlib import Path
from loguru import logger
from functools import wraps
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from colour import Color

# Import QGIS modules
from PyQt5.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMeshLayer,
    QgsMeshDatasetIndex,
    QgsMeshUtils,
    QgsProject,
    QgsRasterLayer,
    QgsRasterFileWriter,
    QgsRasterPipe,
    QgsCoordinateReferenceSystem,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsRasterHistogram,
    QgsErrorMessage
)

# Ignore warning function
def ignore_warnings(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response
    return inner

# Initialize application
def initialize_qgis_application():
    sys.path.append('/opt/conda/envs/adcirc2geotiff/share/qgis')
    sys.path.append('/opt/conda/envs/adcirc2geotiff/share/qgis/python/plugins')
    app = QgsApplication([], False)
    return (app)

# Add the path to processing so we can import it next
@ignore_warnings # Ignored because we want the output of this script to be a single value, and "import processing" is noisy
def initialize_processing(app):
    # import processing module
    import processing
    from processing.core.Processing import Processing

    # Initialize Processing
    Processing.initialize()
    return (app, processing)

# Make output directory if it does not exist
def makeDirs(outputDir):
    # Create tiff directory path
    if not os.path.exists(outputDir):
        # mode = 0o755
        # os.makedirs(outputDir, mode)
        os.makedirs(outputDir, exist_ok=True)
        logger.info('Made directory '+outputDir+ '.')
    else:
        logger.info('Directory '+outputDir+' already made.')

# Define parameters used in creating tiff
def getParameters(inputDir, inputFile, outputDir):
    tifFile = inputFile.split('.')[0]+'.raw.'+inputFile.split('.')[1]+'.tif'
    parms = '{"INPUT_EXTENT" : "-97.85833,-60.040029999999994,7.909559999999999,45.83612", "INPUT_GROUP" : 1, "INPUT_LAYER" : "'+inputDir+inputFile+'", "INPUT_TIMESTEP" : 0,  "OUTPUT_RASTER" : "'+outputDir+tifFile+'", "MAP_UNITS_PER_PIXEL" : 0.001}'
    return(json.loads(parms))

# Convert mesh layer as raster and save as a GeoTiff
@ignore_warnings
def exportRaster(parameters):
    # Open layer from INPUT_LAYER 
    logger.info('Open layer from INPUT_LAYER') 
    inputFile = 'Ugrid:'+'"'+parameters['INPUT_LAYER']+'"'
    meshfile = Path(inputFile).parts[-1]
    meshlayer = meshfile.split('.')[0]
    layer = QgsMeshLayer(inputFile, meshlayer, 'mdal')

    # Open INPUT_LAYER with netCDF4, and check its dimensions. If dimensions are incorrect exit program
    logger.info('Check INPUT_LAYER dimensions')
    ds = nc.Dataset(parameters['INPUT_LAYER'])
    for dim in ds.dimensions.values():
        if dim.size == 0:
            logger.info('The netCDF file '+meshfile.split('"')[0]+' has an invalid dimension value of 0, so the program will exit')
            sys.exit(0)

    # Check if layer is valid
    if layer.isValid() is True:
        # Get parameters for processing
        logger.info('Get parameters')
        dataset  = parameters['INPUT_GROUP'] 
        timestep = parameters['INPUT_TIMESTEP']
        mupp = parameters['MAP_UNITS_PER_PIXEL'] 
        extent = layer.extent()
        output_layer = parameters['OUTPUT_RASTER']
        width = extent.width()/mupp 
        height = extent.height()/mupp 
        crs = layer.crs() 
        crs.createFromSrid(4326)

        # Transform instance
        logger.info('Transform instance')
        transform_context = QgsProject.instance().transformContext()
        output_format = QgsRasterFileWriter.driverForExtension(os.path.splitext(output_layer)[1])

        # Open output file for writing
        logger.info('Open output file')
        rfw = QgsRasterFileWriter(output_layer)
        rfw.setOutputProviderKey('gdal') 
        rfw.setOutputFormat(output_format) 

        # Create one band raster
        logger.info('Create one band raster')
        rdp = rfw.createOneBandRaster( Qgis.Float64, width, height, extent, crs)

        # Get dataset index
        logger.info('Get data set index')
        dataset_index = QgsMeshDatasetIndex(dataset, timestep)

        # Regred mesh layer to raster
        logger.info('Regrid mesh layer')
        block = QgsMeshUtils.exportRasterBlock( layer, dataset_index, crs,
                transform_context, mupp, extent) 

        # Write raster to GeoTiff file
        logger.info('Write raster Geotiff file')
        rdp.writeBlock(block, 1)
        rdp.setNoDataValue(1, block.noDataValue())
        rdp.setEditable(False)

        logger.info('Regridded mesh data in '+meshfile.split('"')[0]+' to float64 grid, and saved to tiff ('+output_layer+') file.')

        return(output_layer)

    if layer.isValid() is False: 
        raise Exception('Invalid mesh')

# Add color and set transparency to GeoTiff
@ignore_warnings
def styleRaster(filename, colorscaling):
    # Create outfile name
    outfile = "".join(filename.strip().split('.raw'))

    # Open layer from filename
    logger.info('Open layer for styling')
    rasterfile = Path(filename).parts[-1].strip()
    rasterlayer = rasterfile.split('.')[0]
    rlayer = QgsRasterLayer(filename, rasterlayer, 'gdal')

    # Check if layer is valid
    if rlayer.isValid() is True:
        # Get layer data provider
        logger.info('Layer is valid for styling')
        provider = rlayer.dataProvider()

        if colorscaling == 'interpolated':            
            # Get bottom and top color values from bin values, calculate values for bottom middle, 
            # and top middle color values, and create color dictionary
            logger.info('Get interpolated color values, used for styling')
            if rasterlayer == 'maxele':
                bottomvalue = 0.0
                topvalue =  2.0

                # Calculate range value between the bottom and top color values
                if bottomvalue < 0:
                    vrange = topvalue + bottomvalue
                else:
                    vrange = topvalue - bottomvalue 

                bottommiddle = vrange * 0.3333
                topmiddle = vrange * 0.6667
                colDic = {'bottomcolor':'#0000ff', 'bottommiddle':'#00ffff', 'topmiddle':'#ffff00', 'topcolor':'#ff0000'}
            else:
                # Calculate histrogram
                logger.info('Calculate histogram')
                provider.initHistogram(QgsRasterHistogram(),1,100)
                hist = provider.histogram(1)

                # Get histograms stats
                nbins = hist.binCount
                minv = hist.minimum
                maxv = hist.maximum

                # Create histogram array, bin array, and histogram index
                hista = np.array(hist.histogramVector)
                bins = np.arange(minv, maxv, (maxv - minv)/nbins)
                index = np.where(hista > 5)

                bottomvalue = bins[index[0][0]]
                topvalue = bins[index[0][-1]]

                # Calculate range value between the bottom and top color values
                if bottomvalue < 0:
                    vrange = topvalue + bottomvalue
                else:
                    vrange = topvalue - bottomvalue 

                bottommiddle = vrange * 0.375
                topmiddle = vrange * 0.75
                colDic = {'bottomcolor':'#000000', 'bottommiddle':'#ff0000', 'topmiddle':'#ffff00', 'topcolor':'#ffffff'}

            # Create list of color values
            valueList = [bottomvalue, bottommiddle, topmiddle, topvalue]

            # Create color ramp function and add colors
            logger.info('Create interpolated color ramp')
            fnc = QgsColorRampShader()
            fnc.setColorRampType(QgsColorRampShader.Interpolated)
            lst = [QgsColorRampShader.ColorRampItem(valueList[0], QColor(colDic['bottomcolor'])),\
                   QgsColorRampShader.ColorRampItem(valueList[1], QColor(colDic['bottommiddle'])), \
                   QgsColorRampShader.ColorRampItem(valueList[2], QColor(colDic['topmiddle'])), \
                   QgsColorRampShader.ColorRampItem(valueList[3], QColor(colDic['topcolor']))]
            fnc.setColorRampItemList(lst)

        elif colorscaling == 'discrete':
            # Calculate values for bottom middle, and top middle color values, and create color dictionary
            logger.info('Get descrete color values, used for styling')
            if rasterlayer == 'maxele':
                # Defind color values
                minv = 0.0
                maxv = 2.0
                bottomvalue = 0.0
                topvalue =  2.0
                bottomcolor = Color('#0000ff')
                topcolor = Color('#ff0000')
                colorramp=list(bottomcolor.range_to(topcolor, 32))
		
                # Create list of color values and colorramp
                valueList = np.append(np.arange(bottomvalue, topvalue, topvalue/31), topvalue)

            else:
                # Calculate histrogram
                logger.info('Calculate histogram')
                provider.initHistogram(QgsRasterHistogram(),1,100)
                hist = provider.histogram(1)

                # Get histograms stats
                nbins = hist.binCount
                minv = hist.minimum
                maxv = hist.maximum

                # Create histogram array, bin array, and histogram index
                hista = np.array(hist.histogramVector)
                bins = np.arange(minv, maxv, (maxv - minv)/nbins)
                index = np.where(hista > 5)

                # Define color values
                bottomvalue = 0.0
                topvalue = bins[index[0][-1]]
                bottomcolor = Color('#000000')
                bottommiddle = Color('#ff0000')
                topmiddle = Color('#ffff00')
                topcolor = Color('#ffffff')
                colorrampbottom=list(bottomcolor.range_to(bottommiddle, 11))
                colorrampmmiddle=list(bottommiddle.range_to(topmiddle, 12))
                colorramptop=list(topmiddle.range_to(topcolor, 11))
                colorramp = colorrampbottom + colorrampmmiddle[1:-1] + colorramptop

                # Create list of color values and colorramp
                valueList = np.arange(bottomvalue, topvalue, topvalue/32)

            # Create color ramp function and add colors
            logger.info('Create descrete color ramp')
            fnc = QgsColorRampShader()
            fnc.setColorRampType(QgsColorRampShader.Discrete)
            lst = []
            lst.append(QgsColorRampShader.ColorRampItem(minv, QColor(colorramp[0].hex_l)))
            logger.info('Check valueList '+str(len(valueList))+' and colorramp '+str(len(colorramp))+' length ')
            for i in range(len(valueList)):
                lst.append(QgsColorRampShader.ColorRampItem(valueList[i], QColor(colorramp[i].hex_l)))
                
            lst.append(QgsColorRampShader.ColorRampItem(maxv, QColor(colorramp[-1].hex_l)))
            fnc.setColorRampItemList(lst)
        
        else:
            logger.info('Incorrect colorscaling value')
            sys.exit('Incorrect colorscaling value')

        # Create raster shader and add color ramp function
        logger.info('Create raster shader, add color ramp function')
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fnc)

        # Create color render and set opacity
        renderer = QgsSingleBandPseudoColorRenderer(provider, 1, shader)
        renderer.setOpacity(0.75)

        # Get output format
        output_format = QgsRasterFileWriter.driverForExtension(os.path.splitext(outfile)[1])

        # Open output file for writing
        logger.info('Open output file, add crs, and create raster pipe')
        rfw = QgsRasterFileWriter(outfile)
        rfw.setOutputProviderKey('gdal')
        rfw.setOutputFormat(output_format)

        # Add EPSG 4326 to layer crs
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(4326)

        # Create Raster pipe and set provider and renderer
        pipe = QgsRasterPipe()
        pipe.set(provider.clone())
        pipe.set(renderer.clone())

        # Get transform context
        logger.info('Get transform context, and write file')
        transform_context = QgsProject.instance().transformContext()

        # Write to file
        rfw.writeRaster(
            pipe,
            provider.xSize(),
            provider.ySize(),
            provider.extent(),
            crs,
            transform_context
        )

        logger.info('Conveted data in '+rasterfile+' from float64 to 8bit, added color palette and saved to tiff ('+outfile+') file')

    if not rlayer.isValid():
        logger.info('Invalid raster')
        raise Exception('Invalid raster')

    return(valueList)

# Move raw tiff to final tiff directory
def moveRaw(inputFile, outputDir, finalDir):
    # Create final/tiff directory path if it does not exist
    if not os.path.exists(finalDir):
        mode = 0o755
        # os.makedirs(finalDir, mode)
        os.makedirs(finalDir, exist_ok=True)
        logger.info('Made directory '+finalDir+ '.')
    else:
        logger.info('Directory '+finalDir+' already made.')

    tifRaw = inputFile.split('.')[0]+'.raw.'+inputFile.split('.')[1]+'.tif'
    # Check if raw tiff exists, and move it.
    if os.path.exists(outputDir+tifRaw):
        if os.path.exists(outputDir+tifRaw+'.aux.xml'):
            os.remove(outputDir+tifRaw+'.aux.xml')
            logger.info('Remove aux.xml file.')
        else:
            logger.info('No aux.xml file to remove.')

        shutil.move(outputDir+tifRaw, finalDir+tifRaw)
        logger.info('Moved raw tiff file '+tifRaw+ 'to '+finalDir+' directory.')
    else:
        logger.info('Raw tiff file '+finalDir+tifRaw+' does not exist.')

# Move colorbar to final tiff directory
def moveBar(barPathFile, outputDir, finalDir):
    barFile = Path(barPathFile).parts[-1]
    # Check if raw tiff exists, and move it.
    if os.path.exists(barPathFile):
        shutil.move(barPathFile, finalDir+barFile)
        logger.info('Moved colorbar file '+finalDir+barFile+ 'to final/tiff directory.')
    else:
        logger.info('Colorbar file '+finalDir+barFile+' does not exist.')

# Convert hex to rgb colors
def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values
    '''
    logger.info('Convert hex to rgb')
    value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return(tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)))

# Convert rgb to decimal colors
def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values
    '''
    logger.info('Conver rgb to decimal')
    return([v/256 for v in value])

# Create continuous color map
def get_continuous_cmap(hex_list, float_list=None):
    '''
    If float_list is not provided, colour map graduates linearly between each color in hex_list.
    If float_list is provided, each color in hex_list is mapped to the respective location in float_list.

    Parameters
    ----------
    hex_list: list of hex code strings
    float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.

    Returns
    ----------
    colour map
    '''
    logger.info('Create continuous color map')
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0,1,len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list

    cmp = LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)
    return(cmp)

# Create discrete color map
def get_discrete_cmap(valueList, barVar):
    logger.info('Create discrete color map')
    if barVar == 'maxele':
        bottomvalue = 0.0
        topvalue =  2.0
        bottomcolor = Color('#0000ff')
        topcolor = Color('#ff0000')
        colorramp=list(bottomcolor.range_to(topcolor, 32))
    else:
        bottomvalue = valueList[0]
        topvalue = valueList[0]
        bottomcolor = Color('#000000')
        bottommiddle = Color('#ff0000')
        topmiddle = Color('#ffff00')
        topcolor = Color('#ffffff')
        colorrampbottom=list(bottomcolor.range_to(bottommiddle, 11))
        colorrampmmiddle=list(bottommiddle.range_to(topmiddle, 12))
        colorramptop=list(topmiddle.range_to(topcolor, 11))
        colorramp = colorrampbottom + colorrampmmiddle[1:-1] + colorramptop
        
    hexlist = []
    for color in colorramp:
        hexlist.append(color.hex_l)
            
    cmp = mpl.colors.ListedColormap(hexlist)
    return cmp

# Rotate color bar image
def rotate_img(img_path, rt_degr):
    # This function rotates the color bar image so it is horizontal
    logger.info('Rotate color bar')
    img = Image.open(img_path)
    return img.rotate(rt_degr, expand=1)

# Create color bar for tiff image
def create_colorbar(cmap,values,unit,barPathFile):
    # Create tick marks for values in meters
    logger.info('Create Color bar')
    valrange = abs(values[0] - values[-1])

    ticks = [values[0], valrange/4, valrange/2, valrange/1.33, values[-1]]

    tick1m = '<'+str("{:.2f}".format(ticks[0]))
    tick2m = str("{:.2f}".format(ticks[1]))
    tick3m = str("{:.2f}".format(ticks[2]))
    tick4m = str("{:.2f}".format(ticks[3]))
    tick5m = str("{:.2f}".format(ticks[4]))+'>'

    ticks_labels = [tick1m,tick2m,tick3m,tick4m,tick5m]

    # Get color map and plot range
    cmap = plt.cm.get_cmap(cmap)
    norm = mpl.colors.Normalize(vmin=values[0], vmax=values[-1])

    # Plot color bar and first axis
    fig, ax = plt.subplots(figsize=(1, 8))
    cbar = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, ticks=ticks, orientation='vertical')
    cbar.ax.yaxis.set_label_position("left")
    ax.tick_params(direction='out', length=10, width=2, labelsize=17, colors='black', grid_color='black', grid_alpha=0.5)
    cbar.set_label(unit, fontsize=17)
    cbar.ax.set_yticklabels(ticks_labels, rotation=90, va="center")

    # Create tick marks for values in feet
    if unit == 'meters per second':
        econversionval = 2.23694
        eunit = 'miles per hour'
    else:
        econversionval = 3.28084
        eunit = 'feet'

    # Define value range in feet and convert ticks 
    valrangeft = valrange * econversionval
    iticks = [(values[0] * econversionval), valrangeft/4, valrangeft/2, valrangeft/1.33, (values[-1] * econversionval)]

    tick1ft = '<'+str("{:.2f}".format(iticks[0]))
    tick2ft = str("{:.2f}".format(iticks[1]))
    tick3ft = str("{:.2f}".format(iticks[2]))
    tick4ft = str("{:.2f}".format(iticks[3]))
    tick5ft = str("{:.2f}".format(iticks[4]))+'>'

    iticks_labels = [tick1ft,tick2ft,tick3ft,tick4ft,tick5ft]

    # Plot second axis
    ax2 = ax.twinx()
    ax2.tick_params(direction='out', length=10, width=2, labelsize=17, colors='black', grid_color='black', grid_alpha=0.5)
    ax2.set_ylim([(values[0] * econversionval),(values[-1] * econversionval)])
    ax2.set_yticks(iticks)
    ax2.set_yticklabels(iticks_labels, rotation=90, va="center")
    ax2.set_ylabel(eunit, fontsize=17)

    # Save colorbar image and close plot
    fig.savefig(barPathFile, transparent=True, bbox_inches = 'tight', pad_inches = 0.25)
    plt.close()

    # Rotate colorbar so it is horizontal
    img_rt_270 = rotate_img(barPathFile, 270)
    img_rt_270.save(barPathFile)

@logger.catch
def main(args):
    # get input variables from args
    inputFile = args.inputFile
    inputDir = os.path.join(args.inputDir, '')
    outputDir = os.path.join(args.outputDir, '')
    finalDir = os.path.join(args.finalDir, '')

    # Remove old logger and start new one
    logger.remove()
    log_path = os.path.join(os.getenv('LOG_PATH', os.path.join(os.path.dirname(__file__), 'logs')), '')
    logger.add(log_path+'adcirc2geotiff_vmbtiles.log', level='DEBUG')

    # Check to see if input directory exits and if it does create tiff
    if os.path.exists(inputDir+inputFile):
        # When error exit program
        logger.add(lambda _: sys.exit(1), level="ERROR")

        # Make output directory
        makeDirs(outputDir.strip())

        # Set QGIS environment
        os.environ['QT_QPA_PLATFORM']='offscreen'
        xdg_runtime_dir = '/home/nru/adcirc2geotiff'
        os.makedirs(xdg_runtime_dir, exist_ok=True)
        os.environ['XDG_RUNTIME_DIR']=xdg_runtime_dir
        logger.info('Set QGIS enviroment.')

        # Initialize QGIS
        app = initialize_qgis_application() 
        app.initQgis()
        app, processing = initialize_processing(app)
        logger.info('Initialzed QGIS.')

        # get parameters to create tiff from ADCIRC mesh file
        parameters = getParameters(inputDir, inputFile.strip(), outputDir.strip())
        logger.info('Got mesh regrid paramters for '+inputDir+inputFile.strip())

        # Create raw tiff file
        filename = exportRaster(parameters)

        # Create raw color file
        valueList = styleRaster(filename, 'discrete')

        # Define color bar path and color bar variable name
        barPathFile = ".".join("".join(filename.strip().split('.raw')).split('.')[0:-1])+'.colorbar.png'
        barVar = Path(filename).parts[-1].strip().split('.')[0]

        # Define hexList and units for each type of color bar variable 
        if barVar == 'maxele':
            hexList = ['#0000ff', '#00ffff', '#ffff00', '#ff0000']
            unit = 'meters'
        elif barVar == 'maxwvel':
            hexList = ['#000000', '#ff0000', '#ffff00', '#ffffff']
            unit = 'meters per second'
        elif barVar == 'swan_HS_max':
            hexList = ['#000000', '#ff0000', '#ffff00', '#ffffff']
            unit = 'meters'
        else:
            logger.info('Incorrect rlayer name')

        # Get color map
        cmap = get_discrete_cmap(valueList, barVar)
        #cmap = get_continuous_cmap(hexList)

        # Create color bar
        create_colorbar(cmap,valueList,unit,barPathFile)

        # Quit QGIS
        app.exitQgis()
        logger.info('Quit QGIS')

        # Move raw tiff file to final tiff directory
        moveRaw(inputFile, outputDir, finalDir)
        logger.info('Moved float64 tiff file')

        # Move color bar to final tiff directory 
        moveBar(barPathFile, outputDir, finalDir)
        logger.info('Moved colorbar png file')
    else:
         logger.info(inputDIR+inputFile+' does not exist')
         sys.exit(0)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("--inputFILE", "--inputFile", help="Input file name", action="store", dest="inputFile", required=True)
    parser.add_argument("--inputDIR", "--inputDir", help="Input directory path", action="store", dest="inputDir", required=True)
    parser.add_argument("--outputDIR", "--outputDir", help="Output directory path", action="store", dest="outputDir", required=True)
    parser.add_argument("--finalDIR", "--finalDir", help="Final directory path", action="store", dest="finalDir", required=True)

    args = parser.parse_args()
    main(args)

