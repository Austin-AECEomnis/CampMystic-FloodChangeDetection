"""
02_noaa_reproject_resample.py
Camp Mystic Flood Change Detection -- NOAA Reprojection and Resampling

Purpose:
    NOAA emergency imagery is delivered in GCS WGS 1984 (geographic, degree
    units). NAIP imagery is in NAD83 UTM Zone 14N (projected, meter units).
    Pixel-level band subtraction requires both datasets to be in the same
    coordinate system and at the same cell size.

    This script:
        1. Reprojects NOAA tiles from WGS84 to NAD83 UTM Zone 14N (EPSG 26914)
        2. Resamples reprojected NOAA tiles from ~0.14m to 0.6m to match NAIP

    Resampling direction note:
        NOAA native resolution after reprojection is approximately 0.14 meters.
        NAIP resolution is 0.6 meters. Resampling is always performed toward
        the coarser resolution. Resampling NAIP down to 0.14m would create
        false precision -- detail that was never captured at acquisition.
        The honest working resolution for this analysis is 0.6 meters.

Environment:
    ArcGIS Pro arcgispro-py3 conda environment
    Run via ArcGIS Pro Python Window

Author: Austin Addington Berlin / AECE Omnis LLC
"""

import arcpy
import os

# -- Configuration -------------------------------------------------------------

NOAA_FOLDER   = r"C:\GIS_Projects\CampMystic_ChangeDetection\NOAA_Imagery"
PROJ_FOLDER   = r"C:\GIS_Projects\CampMystic_ChangeDetection\NOAA_Imagery\Projected"
RESAMP_FOLDER = r"C:\GIS_Projects\CampMystic_ChangeDetection\NOAA_Imagery\Resampled"

TARGET_EPSG   = 26914    # NAD83 UTM Zone 14N
TARGET_CELL   = "0.6"    # meters, matching NAIP

arcpy.env.overwriteOutput = True

# -- Main ----------------------------------------------------------------------

def main():

    # Create output folders if they do not exist
    os.makedirs(PROJ_FOLDER, exist_ok=True)
    os.makedirs(RESAMP_FOLDER, exist_ok=True)

    # Collect original NOAA tiles
    noaa_tiles = [
        os.path.join(NOAA_FOLDER, f)
        for f in os.listdir(NOAA_FOLDER)
        if f.endswith('.tif') and not f.endswith('.aux.xml')
    ]

    if len(noaa_tiles) == 0:
        print("ERROR: No NOAA tiles found. Check NOAA_FOLDER path.")
        return

    print(f"NOAA tiles to process: {len(noaa_tiles)}")
    print()

    # -- Step 1: Reproject -----------------------------------------------------

    target_sr = arcpy.SpatialReference(TARGET_EPSG)
    projected_tiles = []

    print("Step 1: Reprojecting NOAA tiles to NAD83 UTM Zone 14N...")
    for tile in noaa_tiles:
        filename = os.path.basename(tile).replace(".tif", "_utm.tif")
        output = os.path.join(PROJ_FOLDER, filename)
        print(f"  Reprojecting {os.path.basename(tile)}...")
        arcpy.management.ProjectRaster(
            in_raster=tile,
            out_raster=output,
            out_coor_system=target_sr,
            resampling_type="BILINEAR"
        )
        projected_tiles.append(output)
        print(f"  Done: {filename}")

    print()

    # -- Verify reprojection ---------------------------------------------------

    print("Verifying reprojected tiles...")
    for tile in projected_tiles:
        r = arcpy.Raster(tile)
        sr = r.spatialReference
        print(f"  {os.path.basename(tile)}")
        print(f"    CRS:       {sr.name}")
        print(f"    Cell size: {round(r.meanCellWidth, 4)} meters")
        print(f"    Bands:     {r.bandCount}")
    print()

    # -- Step 2: Resample ------------------------------------------------------

    resampled_tiles = []

    print("Step 2: Resampling reprojected NOAA tiles to 0.6m...")
    for tile in projected_tiles:
        filename = os.path.basename(tile).replace("_utm.tif", "_utm_06m.tif")
        output = os.path.join(RESAMP_FOLDER, filename)
        print(f"  Resampling {os.path.basename(tile)}...")
        arcpy.management.Resample(
            in_raster=tile,
            out_raster=output,
            cell_size=TARGET_CELL,
            resampling_type="BILINEAR"
        )
        resampled_tiles.append(output)
        print(f"  Done: {filename}")

    print()

    # -- Verify resampled output -----------------------------------------------

    print("Verifying resampled tiles...")
    all_pass = True
    for tile in resampled_tiles:
        r = arcpy.Raster(tile)
        sr = r.spatialReference
        cell_ok = round(r.meanCellWidth, 1) == 0.6
        crs_ok  = "UTM_Zone_14N" in sr.name
        band_ok = r.bandCount == 4
        type_ok = r.pixelType == "U8"
        status  = "OK" if all([cell_ok, crs_ok, band_ok, type_ok]) else "FAIL"
        if not all([cell_ok, crs_ok, band_ok, type_ok]):
            all_pass = False
        print(f"  [{status}] {os.path.basename(tile)}")
        print(f"    CRS: {sr.name} | Cell: {round(r.meanCellWidth, 4)}m | Bands: {r.bandCount} | Type: {r.pixelType}")

    print()
    if all_pass:
        print("All checks passed. Proceed to 03_mosaic_and_clip.py")
    else:
        print("One or more checks failed. Review output above before proceeding.")


if __name__ == "__main__":
    main()
