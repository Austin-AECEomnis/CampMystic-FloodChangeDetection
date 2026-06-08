"""
01_data_inventory.py
Camp Mystic Flood Change Detection -- Data Inventory and Diagnostic

Purpose:
    Confirm all input rasters are present, readable, and have the expected
    properties before any processing begins. Checks band count, CRS, cell
    size, pixel type, and extent for all NAIP and NOAA tiles.

    Run this script first. Do not proceed to subsequent steps until all
    checks pass.

Environment:
    ArcGIS Pro arcgispro-py3 conda environment
    Run via ArcGIS Pro Python Window

Author: Austin Addington Berlin / AECE Omnis LLC
"""

import arcpy
import os

# -- Configuration -------------------------------------------------------------

NAIP_FOLDER = r"C:\GIS_Projects\CampMystic_ChangeDetection\NAIP_PreEvent\Extracted"
NOAA_FOLDER = r"C:\GIS_Projects\CampMystic_ChangeDetection\NOAA_Imagery"

# -- Inventory Function --------------------------------------------------------

def inventory_raster(path):
    """
    Print diagnostic properties of a raster dataset.

    Args:
        path (str): Full path to the raster file.
    """
    r = arcpy.Raster(path)
    sr = r.spatialReference
    print(f"  File:       {os.path.basename(path)}")
    print(f"  CRS:        {sr.name}")
    print(f"  Type:       {sr.type}")
    print(f"  Units:      {sr.linearUnitName if sr.type == 'Projected' else sr.angularUnitName}")
    print(f"  Cell size:  {round(r.meanCellWidth, 6)}")
    print(f"  Bands:      {r.bandCount}")
    print(f"  Pixel type: {r.pixelType}")
    print(f"  Extent:     {r.extent}")
    print()


# -- Main ----------------------------------------------------------------------

def main():

    # Collect NAIP tiles
    naip_tiles = [
        os.path.join(NAIP_FOLDER, f)
        for f in os.listdir(NAIP_FOLDER)
        if f.endswith('.tif') and not f.endswith('.aux.xml')
    ]

    # Collect NOAA tiles (originals only, not reprojected/resampled subfolders)
    noaa_tiles = [
        os.path.join(NOAA_FOLDER, f)
        for f in os.listdir(NOAA_FOLDER)
        if f.endswith('.tif') and not f.endswith('.aux.xml')
    ]

    print(f"NAIP tiles found: {len(naip_tiles)}")
    print("Expected: 4\n")
    for tile in naip_tiles:
        inventory_raster(tile)

    print(f"NOAA tiles found: {len(noaa_tiles)}")
    print("Expected: 2\n")
    for tile in noaa_tiles:
        inventory_raster(tile)

    # Summary check
    print("-" * 60)
    print("SUMMARY")
    print(f"  NAIP count: {len(naip_tiles)} {'OK' if len(naip_tiles) == 4 else 'ERROR - Expected 4'}")
    print(f"  NOAA count: {len(noaa_tiles)} {'OK' if len(noaa_tiles) == 2 else 'ERROR - Expected 2'}")
    print()
    print("Review CRS output above.")
    print("NAIP should be: NAD_1983_UTM_Zone_14N (Projected, Meter)")
    print("NOAA should be: GCS_WGS_1984 (Geographic, Degree)")
    print("If NOAA shows Projected/Meter it may already be reprojected.")
    print("Proceed to 02_noaa_reproject_resample.py")


if __name__ == "__main__":
    main()
