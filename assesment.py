'''
This is for cliping a raster image and creating NDVI using python
'''
from os import path
import rasterio as rio
import geojson
from rasterio.crs import CRS
from rasterio.mask import mask

# image and data path
image = 'T11SLU_20200925T183121_4Band_clip.tif'
bounds_json = 'bounds.geojson'

def raster_clip(image,bounds_json, output, proj=4326):
    '''
    Desc: This method is used to clip/subset raster image and save in folder
    Args:
    image-satellite image path
    bounds_json-boundary JSON file 
    output-output file name
    proj(optional)-projection parameter  
    
    '''
    try:
        # checking the file if exists 
        if path.isfile(bounds_json): 
            # open the boundary json  
            with open(bounds_json) as f:    
                bounds = geojson.load(f)
            # create features from the provided geometry                
            features = [feature["geometry"] for feature in bounds['features']]
            coords = []
            if len(features) >0:
                for ftr in features:
                    if ftr['type'] == "Polygon":
                        coords.append(ftr)
                if len(coords)>0:
                    if path.isfile(image):
                        with rio.open(image) as src:    
                            # clip the raster with the polygon using the features variable 
                            out_image, out_transform = mask(src, coords, crop=True)
                            out_meta = src.meta.copy() 
                            #update the metadata with new dimensions                   
                            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform,
                            "crs": CRS.from_epsg(proj)   
                            }) 
                            # creating ouput file name                               
                            if ".tif" not in output:
                                clip_image = output+".tif"
                            
                            with rio.open(clip_image, "w", **out_meta) as dest:                        
                                dest.write(out_image)
                            #Call NDVI 
                            create_ndvi(clip_image)
                            print("Clip and NDVI created successfully")
                    else:
                        print("Please check the image file; it's not available in the folder")
        else:
            print("Please check the JSON file; its not available")
    except Exception as ex:
        print(ex)

def create_ndvi(clip_image):
    '''
    Tis method is to create NDVI from the clipped image
    Args: 
    clip_image-clipped image    
    '''
    try:

        with rio.open(clip_image) as src:
            # Load red and NIR bands- band order BGRN   
            band_red = src.read(3)
            band_nir = src.read(4)
            # Calculate NDVI
            ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)    
            
            # Set spatial characteristics of the output object to mirror the input
            kwargs = src.meta
            kwargs.update(
                dtype=rio.float32,
                count=1
                )
            split_name = clip_image.split(".")
            ndvi_image = split_name[0]+"_ndvi.tif"
        # Create the NDVI file
        with rio.open(ndvi_image, 'w', **kwargs) as dst:
            dst.write_band(1, ndvi.astype(rio.float32))
    except Exception as ex:
        print(ex)
raster_clip(image,bounds_json,"output")
#raster_clip(image,bounds_json,"output",proj=3857)
