from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import sys
import os
import geopandas as gpd

# Supply path to qgis install location (update this path if necessary)
qgis_path = r"C:\Program Files\QGIS 3.38.1\apps\qgis"
QgsApplication.setPrefixPath(qgis_path, True)

# Create a reference to the QgsApplication
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Add the path to Processing framework
sys.path.append(os.path.join(qgis_path, 'python', 'plugins'))

# Import and initialize Processing
import processing
from processing.core.Processing import Processing
Processing.initialize()

QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

print("QGIS version:", Qgis.QGIS_VERSION)
print("Processing algorithms:", len(QgsApplication.processingRegistry().algorithms()))

# Check if the algorithm exists and print its parameters
alg = QgsApplication.processingRegistry().algorithmById('native:dtmslopebasedfilter')
if alg:
    print("Algorithm found. Parameters:")
    for param in alg.parameterDefinitions():
        print(f"- {param.name()}: {param.description()}")
else:
    print("Algorithm 'native:dtmslopebasedfilter' not found")

try:
    # Create a QgsRasterLayer for input
    input_path = r"C:\Users\Copy\Desktop\koustav\Analytics Data\Analytics Data\DEM\DEM.tif"
    input_raster = QgsRasterLayer(input_path, 'input')
    if not input_raster.isValid():
        raise Exception("Invalid input raster")

    # Print debug information about the input raster
    print("Input raster info:")
    print(f"- Is valid: {input_raster.isValid()}")
    print(f"- CRS: {input_raster.crs().authid()}")
    print(f"- Width: {input_raster.width()}")
    print(f"- Height: {input_raster.height()}")
    print(f"- Bands: {input_raster.bandCount()}")

    # Specify output file paths
    output_ground_path = r'C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1output_dtm_filter_ground.tif'
    output_nonground_path = r'C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\output_dtm_filter_nonground.tif'

    # Create a feedback object
    feedback = QgsProcessingFeedback()

    # Run the algorithm
    result = processing.run("native:dtmslopebasedfilter", {
        'INPUT': input_raster,
        'BAND': 1,
        'RADIUS': 50,
        'TERRAIN_SLOPE': 1.5,
        'FILTER_MODIFICATION': 1,
        'STANDARD_DEVIATION': 0.001,
        'OUTPUT_GROUND': output_ground_path,
        'OUTPUT_NONGROUND': output_nonground_path
    }, feedback=feedback)

    print("DTM Filter Algorithm executed. Result:", result)

    # Check if output files were created
    for output_path in [output_ground_path, output_nonground_path]:
        if os.path.exists(output_path):
            print(f"Output file created successfully: {output_path}")
            output_raster = QgsRasterLayer(output_path, 'output')
            if output_raster.isValid():
                print("Output raster is valid")
                print(f"- CRS: {output_raster.crs().authid()}")
                print(f"- Width: {output_raster.width()}")
                print(f"- Height: {output_raster.height()}")
                print(f"- Bands: {output_raster.bandCount()}")
            else:
                print(f"Output raster is not valid: {output_path}")
        else:
            print(f"Output file was not created: {output_path}")

    ##(2)Polygonize
    alg = QgsApplication.processingRegistry().algorithmById('gdal:polygonize')
    if alg:
        print("\n\n#####POLYGONIZE#####\nAlgorithm found. Parameters:")
        for param in alg.parameterDefinitions():
            print(f"- {param.name()}: {param.description()}")
    else:
        print("Algorithm 'gdal:polygonize' not found")

    try:
        # Create a QgsRasterLayer for input
        input_path = r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1output_dtm_filter_ground.tif"
        input_raster = QgsRasterLayer(input_path, 'input')
        if not input_raster.isValid():
            raise Exception("Invalid input raster")

        # Print debug information about the input raster
        print("Input raster info:")
        print(f"- Is valid: {input_raster.isValid()}")
        print(f"- CRS: {input_raster.crs().authid()}")
        print(f"- Width: {input_raster.width()}")
        print(f"- Height: {input_raster.height()}")
        print(f"- Bands: {input_raster.bandCount()}")

        # Specify output file paths
        output_polygonize=r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1polygonize.gpkg"

        # Create a feedback object
        feedback = QgsProcessingFeedback()

        result = processing.run("gdal:polygonize", {
            'INPUT':input_raster,
            'BAND':1,
            'FIELD':'DN',
            'EIGHT_CONNECTEDNESS':False,
            'EXTRA':'',
            'OUTPUT':output_polygonize
        }, feedback=feedback)

        print("Polygonize was executed. Result:", result)

        # Check if output files were created
        
        if os.path.exists(output_polygonize):
            print(f"Output file created successfully: {output_polygonize}")
        else:
            print(f"Output file was not created")

        # DISSOLVE
        alg = QgsApplication.processingRegistry().algorithmById('native:dissolve')
        if alg:
            print("Algorithm found. Parameters:")
            for param in alg.parameterDefinitions():
                print(f"- {param.name()}: {param.description()}")
        else:
            print("Algorithm 'native:dissolve' not found")

        try:
            # Create a QgsRasterLayer for input
            dissolve_input_path = r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1polygonize.gpkg"
            input_vector = QgsVectorLayer(dissolve_input_path, 'input','ogr')
            if not input_vector.isValid():
                raise Exception("Invalid input vector cannot apply dissolve")

            # Print debug information about the input raster
            print("\n\n#####DISSOLVE#####\nInput Vector info:")
            print(f"- Is valid: {input_vector.isValid()}")
            print(f"- CRS: {input_vector.crs().authid()}")
            
            # Specify output file paths
            output_dissolve=r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1dissolve.gpkg"

            # Create a feedback object
            feedback = QgsProcessingFeedback()

            result_dissolve = processing.run("native:dissolve", {
                'INPUT':input_vector,
                'FIELD':[],
                'SEPARATE_DISJOINT':False,
                'OUTPUT':output_dissolve
            }, feedback=feedback)


            print("Dissolve was executed. Result:", result_dissolve)

            # Check if output files were created
            
            if os.path.exists(output_dissolve):
                print(f"Output file created successfully: {output_dissolve}")
            else:
                print(f"Output file was not created")

        except Exception as e:
            print("Error executing algorithm:", str(e))
            import traceback
            print(traceback.format_exc())

        ##(4)Simplify
        alg = QgsApplication.processingRegistry().algorithmById('native:simplifygeometries')
        if alg:
            print("Algorithm found. Parameters:")
            for param in alg.parameterDefinitions():
                print(f"- {param.name()}: {param.description()}")
        else:
            print("Algorithm 'native:simplifygeometries' not found")

        try:
            # Create a QgsRasterLayer for input
            simplify_input_path = r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1dissolve.gpkg"
            input_vector = QgsVectorLayer(simplify_input_path, 'input','ogr')
            if not input_vector.isValid():
                raise Exception("Invalid input vector cannot apply simplify")

            # Print debug information about the input raster
            print("\n\n#####SIMPLIFY#####\nInput Vector info:")
            print(f"- Is valid: {input_vector.isValid()}")
            print(f"- CRS: {input_vector.crs().authid()}")
            
            # Specify output file paths
            output_simplify=r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1simplify.gpkg"

            # Create a feedback object
            feedback = QgsProcessingFeedback()

            result_simplify = processing.run("native:simplifygeometries", {
                'INPUT':input_vector,
                'METHOD':0,
                'TOLERANCE':1,
                'OUTPUT':output_simplify
            }, feedback=feedback)



            print("Simplify was executed. Result:", result_simplify)

            # Check if output files were created
            
            if os.path.exists(output_simplify):
                print(f"Output file created successfully: {output_simplify}")
            else:
                print(f"Output file was not created")

        except Exception as e:
            print("Error executing algorithm:", str(e))
            import traceback
            print(traceback.format_exc())



        ##(4)Delete holes
        alg = QgsApplication.processingRegistry().algorithmById('native:deleteholes')
        if alg:
            print("Algorithm found. Parameters:")
            for param in alg.parameterDefinitions():
                print(f"- {param.name()}: {param.description()}")
        else:
            print("Algorithm 'native:deleteholes' not found")

        try:
            # Create a QgsRasterLayer for input
            deleteholes_input_path = r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1simplify.gpkg"
            input_vector = QgsVectorLayer(deleteholes_input_path, 'input','ogr')
            if not input_vector.isValid():
                raise Exception("Invalid input vector cannot apply deleteholes")

            # Print debug information about the input raster
            print("\n\n#####DELETEHOLES#####\nInput Vector info:")
            print(f"- Is valid: {input_vector.isValid()}")
            print(f"- CRS: {input_vector.crs().authid()}")
            
            # Specify output file paths
            output_deleteholes=r"C:\Users\Copy\Desktop\files_kp\DATA\Bench_detection\DEM1\code_result\1deleteholes.gpkg"

            # Create a feedback object
            feedback = QgsProcessingFeedback()

            result_deleteholes = processing.run("native:deleteholes", {
                'INPUT':input_vector,
                'MIN_AREA':100,
                'OUTPUT':output_deleteholes
            }, feedback=feedback)

            print("deleteholes was executed. Result:", result_deleteholes)

            # Check if output files were created
            
            if os.path.exists(output_deleteholes):
                print(f"Output file created successfully: {output_deleteholes}")
            else:
                print(f"Output file was not created")

        except Exception as e:
            print("Error executing algorithm:", str(e))
            import traceback
            print(traceback.format_exc())
    except Exception as e:
        print("Error executing algorithm:", str(e))
        import traceback
        print(traceback.format_exc())

except Exception as e:
    print("Error executing algorithm:", str(e))
    import traceback
    print(traceback.format_exc())

# Exit QGIS
qgs.exitQgis()