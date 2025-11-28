def proccess_metashape():
    import Metashape
import os, sys, time

project_path =  "Project.psx"
photos_folder = "n/"
ortho_folder =  "out/mosaic.png"

# Find files function
def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

# Create Project and Chunk
doc = Metashape.Document()
doc.save(path=project_path)
chunk = doc.addChunk()

# Photos import
photos = find_files(photos_folder, [".jpg", ".jpeg", ".tif", ".tiff"])
chunk.addPhotos(photos)
doc.save()

# match photos
chunk.matchPhotos(keypoint_limit = 40000, tiepoint_limit = 10000, generic_preselection = True, reference_preselection = True)
doc.save()

# Align cameras
chunk.alignCameras()
doc.save()

# Build Depth Maps
chunk.buildDepthMaps(downscale = 2, filter_mode = Metashape.MildFiltering)
doc.save()

# Build Model
chunk.buildModel()
doc.save()

# Build DEM
chunk.buildDem(source_data=Metashape.DepthMapsData)
doc.save()

# Build Orthomosaic
chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
doc.save()

# Export Orthomosaique (missing reprojection to EPSG 2154)
chunk.exportRaster(ortho_folder, source_data = Metashape.OrthomosaicData)
doc.save()

# Quit Metashape
Metashape.app.quit()
#exit()