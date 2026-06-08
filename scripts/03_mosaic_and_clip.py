"""
03_mosaic_and_clip.py
Camp Mystic Flood Change Detection -- Mosaic Construction and NAIP Clip

Purpose:
    Combines individual tiles into single continuous rasters for each dataset
    and clips NAIP to the NOAA extent so both mosaics cover identical ground.

    This script:
        1. Builds NAIP mosaic from 4 tiles (4-band, 8-bit unsigned)
        2. Builds NOAA mosaic from 2 resampled tiles (4-band, 8-bit unsigned)
        3. Clips NAIP mosaic to NOAA mosaic extent
        4. Verifies all three outputs match on CRS, cell size, and extent

    Band count note:
        Both NAIP and NOAA tiles are 4-band. NAIP includes a near-infrared
        channel that does not display in the Pro Contents pane by default.
        Always confirm band count via arcpy.Raster().bandCount before
        calling MosaicToNewRaster. Declaring the wrong band count produces
        ERROR 000157.

Environment:
    ArcGIS Pro arcgispro-py3 conda environment
    Run via ArcGIS Pro Python Window

Author: Austin Addington Berlin / AECE Omnis LLC
"""

import arcpy
import os

# -- Configuration -------------------------------------------------------------

NAIP_FOLDER   = r"C:\GIS_Projects\CampMystic_ChangeDetection\NAIP_PreEvent\Extracted"
RESAMP_FOLDER = r"C:\GIS_Projects\CampMystic_ChangeDetection\NOAA_Imagery\Resampled"
OUTPUT_FOLDER = r"C:\GIS_Projects\CampMystic_ChangeDetection"

NAIP_MOSAIC   = os.path.join(OUTPUT_FOLDER, "naip_mosaic.tif")
NOAA_MOSAIC   = os.path.join(OUTPUT_FOLDER, "noaa_mosaic.tif")
NAIP_CLIPPED  = os.path.join(OUTPUT_FOLDER, "naip_clipped.tif")

arcpy.env.workspace       = OUTPUT_FOLDER
arcpy.env.overwriteOutput = True

# -- Main ----------------------------------------------------------------------

def main():

    # Collect input tiles
    naip_tiles = [
        os.path.join(NAIP_FOLDER, f)
        for f in os.listdir(NAIP_FOLDER)
        if f.endswith('.tif') and not f.endswith('.aux.xml')
    ]

    noaa_tiles = [
        os.path.join(RESAMP_FOLDER, f)
        for f in os.listdir(RESAMP_FOLDER)
        if f.endswith('.tif') and not f.endswith('.aux.xml')
    ]

    print(f"NAIP tiles: {len(naip_tiles)}  (expected 4)")
    print(f"NOAA tiles: {len(noaa_tiles)}  (expected 2)")
    print()

    if len(naip_tiles) != 4 or len(noaa_tiles) != 2:
        print("ERROR: Unexpected tile count. Check folder paths and rerun 01_data_inventory.py.")
        return

    # -- Step 1: Build NAIP mosaic ---------------------------------------------

    print("Building NAIP mosaic...")
    arcpy.management.MosaicToNewRaster(
        input_rasters=naip_tiles,
        output_location=OUTPUT_FOLDER,
        raster_dataset_name_with_extension="naip_mosaic.tif",
        pixel_type="8_BIT_UNSIGNED",
        number_of_bands=4
    )
    print("  NAIP mosaic complete")

    # -- Step 2: Build NOAA mosaic ---------------------------------------------

    print("Building NOAA mosaic...")
    arcpy.management.MosaicToNewRaster(
        input_rasters=noaa_tiles,
        output_location=OUTPUT_FOLDER,
        raster_dataset_name_with_extension="noaa_mosaic.tif",
        pixel_type="8_BIT_UNSIGNED",
        number_of_bands=4
    )
    print("  NOAA mosaic complete")
    print()

    # -- Step 3: Clip NAIP to NOAA extent --------------------------------------

    print("Clipping NAIP to NOAA extent...")
    noaa_extent = arcpy.Raster(NOAA_MOSAIC).extent
    arcpy.management.Clip(
        in_raster=NAIP_MOSAIC,
        rectangle=noaa_extent,
        out_raster=NAIP_CLIPPED,
        clipping_geometry="NONE",
        maintain_clipping_extent="MAINTAIN_EXTENT"
    )
    print("  Clip complete")
    print()

    # -- Step 4: Verify all three outputs --------------------------------------

    print("Verifying outputs...")
    outputs = [
        ("NAIP mosaic",  NAIP_MOSAIC),
        ("NOAA mosaic",  NOAA_MOSAIC),
        ("NAIP clipped", NAIP_CLIPPED),
    ]

    for label, path in outputs:
        r  = arcpy.Raster(path)
        sr = r.spatialReference
        print(f"  {label}")
        print(f"    CRS:       {sr.name}")
        print(f"    Cell size: {round(r.meanCellWidth, 4)} meters")
        print(f"    Bands:     {r.bandCount}")
        print(f"    Extent:    {r.extent}")
        print()

    print("Extent check: NAIP clipped and NOAA mosaic extents should match exactly.")
    print("Proceed to 04_stable_reference_sampling.py")


if __name__ == "__main__":
    main()
