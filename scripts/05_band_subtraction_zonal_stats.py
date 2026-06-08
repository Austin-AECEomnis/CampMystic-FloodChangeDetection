"""
05_band_subtraction_zonal_stats.py
Camp Mystic Flood Change Detection -- Band Subtraction, Threshold, and Zonal Statistics

Purpose:
    Executes the full Tier 2 change detection pipeline from aligned mosaics
    to per-structure change scores joined to terrain risk attributes.

    Pipeline:
        1. Extract RGB bands (1, 2, 3) from both NAIP clipped and NOAA mosaic
        2. Compute absolute difference per band
        3. Average three band differences into single mean change magnitude raster
        4. Apply threshold: pixels above threshold retain value, pixels below set to 0
        5. Save change detection raster
        6. Clip structure centroids to Camp Mystic boundary
        7. Buffer structures by 3 meters
        8. Run ZonalStatisticsAsTable against buffered structures
        9. Join MEAN, MAX, STD, COUNT fields back to structure layer

    Threshold note:
        Set THRESHOLD to the value produced by 04_stable_reference_sampling.py.
        Default value 19.88 is the empirically derived threshold from the
        Camp Mystic analysis (road + asphalt court stable surfaces, June 2022
        to July 2025 sensor pair). Recalibrate for different sensor pairs or
        date combinations.

    Buffer note:
        Running Zonal Statistics against point centroids returns COUNT=1 per
        structure (single pixel per zone) with STD=0 across all structures.
        A 3-meter buffer captures approximately 50-60 pixels per structure at
        0.6m resolution, providing a meaningful statistical sample per zone.

Environment:
    ArcGIS Pro arcgispro-py3 conda environment
    Run via ArcGIS Pro Python Window
    Requires: Spatial Analyst extension

Author: Austin Addington Berlin / AECE Omnis LLC
"""

import arcpy
from arcpy.sa import Abs, Raster, Con
import os

# -- Configuration -------------------------------------------------------------

NAIP_CLIPPED      = r"C:\GIS_Projects\CampMystic_ChangeDetection\naip_clipped.tif"
NOAA_MOSAIC       = r"C:\GIS_Projects\CampMystic_ChangeDetection\noaa_mosaic.tif"
CHANGE_OUTPUT     = r"C:\GIS_Projects\CampMystic_ChangeDetection\change_detection.tif"

STRUCTURES_FULL   = r"C:\GIS_Projects\KendallCounty_FloodAnalysis\KendallCounty_FloodAnalysis.gdb\Auto_High_Risk_107_Structures"
CAMP_MYSTIC_BOUND = r"C:\GIS_Projects\KendallCounty_FloodAnalysis\KendallCounty_FloodAnalysis.gdb\CampMystic_Boundary"
STRUCTURES_SUBSET = r"C:\GIS_Projects\CampMystic_ChangeDetection\CampMystic_Structures.shp"
STRUCTURES_BUFFER = r"C:\GIS_Projects\CampMystic_ChangeDetection\CampMystic_Structures_Buffer.shp"
ZONAL_OUTPUT      = r"C:\GIS_Projects\CampMystic_ChangeDetection\zonal_stats_buffered.dbf"

# Empirically derived threshold from 04_stable_reference_sampling.py.
# Recalibrate this value for different sensor pairs or date combinations.
THRESHOLD = 19.88

# Buffer distance for structure zones.
# Single centroid point = 1 pixel = no statistical distribution.
# 3 meters captures ~50-60 pixels per structure at 0.6m resolution.
BUFFER_DISTANCE = "3 Meters"

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# -- Main ----------------------------------------------------------------------

def main():

    # -- Step 1: Extract RGB bands ---------------------------------------------

    print("Extracting RGB bands from NAIP and NOAA mosaics...")
    naip_r = Raster(arcpy.ia.ExtractBand(NAIP_CLIPPED, [1]))
    naip_g = Raster(arcpy.ia.ExtractBand(NAIP_CLIPPED, [2]))
    naip_b = Raster(arcpy.ia.ExtractBand(NAIP_CLIPPED, [3]))

    noaa_r = Raster(arcpy.ia.ExtractBand(NOAA_MOSAIC, [1]))
    noaa_g = Raster(arcpy.ia.ExtractBand(NOAA_MOSAIC, [2]))
    noaa_b = Raster(arcpy.ia.ExtractBand(NOAA_MOSAIC, [3]))
    print("  Bands extracted")

    # -- Step 2: Compute absolute difference per band --------------------------

    print("Computing absolute band differences...")
    diff_r = Abs(naip_r - noaa_r)
    diff_g = Abs(naip_g - noaa_g)
    diff_b = Abs(naip_b - noaa_b)
    print("  Band differences computed")

    # -- Step 3: Average into single change magnitude raster ------------------

    print("Computing mean change magnitude raster...")
    diff_mean = (diff_r + diff_g + diff_b) / 3
    print("  Mean difference raster computed")

    # -- Step 4: Apply threshold -----------------------------------------------

    print(f"Applying threshold: {THRESHOLD}...")
    change_raster = Con(diff_mean > THRESHOLD, diff_mean, 0)
    change_raster.save(CHANGE_OUTPUT)
    print(f"  Change raster saved: {CHANGE_OUTPUT}")
    print()

    # -- Step 5: Clip structures to Camp Mystic boundary ----------------------

    print("Clipping structures to Camp Mystic boundary...")
    arcpy.analysis.Clip(
        in_features=STRUCTURES_FULL,
        clip_features=CAMP_MYSTIC_BOUND,
        out_feature_class=STRUCTURES_SUBSET
    )
    count = arcpy.management.GetCount(STRUCTURES_SUBSET)[0]
    print(f"  Structures within boundary: {count}")
    print()

    # -- Step 6: Buffer structures ---------------------------------------------

    print(f"Buffering structures by {BUFFER_DISTANCE}...")
    arcpy.analysis.Buffer(
        in_features=STRUCTURES_SUBSET,
        out_feature_class=STRUCTURES_BUFFER,
        buffer_distance_or_field=BUFFER_DISTANCE,
        dissolve_option="NONE"
    )
    print(f"  Buffer complete: {arcpy.management.GetCount(STRUCTURES_BUFFER)[0]} features")
    print()

    # -- Step 7: Zonal Statistics ----------------------------------------------

    print("Running Zonal Statistics against buffered structures...")
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=STRUCTURES_BUFFER,
        zone_field="BUILD_ID",
        in_value_raster=CHANGE_OUTPUT,
        out_table=ZONAL_OUTPUT,
        statistics_type="ALL"
    )
    print(f"  Zonal Statistics complete: {ZONAL_OUTPUT}")
    print()

    # -- Step 8: Join change scores to structure layer ------------------------

    print("Joining change scores to structure layer...")
    arcpy.management.JoinField(
        in_data=STRUCTURES_SUBSET,
        in_field="BUILD_ID",
        join_table=ZONAL_OUTPUT,
        join_field="BUILD_ID",
        fields=["MEAN", "MAX", "STD", "COUNT"]
    )
    print("  Join complete")
    print()

    # -- Step 9: Print results table -------------------------------------------

    print("Change scores by structure (3m buffer):")
    print(f"  {'BUILD_ID':<15} {'MEAN':>8} {'MAX':>8} {'STD':>8} {'COUNT':>8} {'SLOPE_VAL':>10} {'FLOWACC_VA':>11}")
    print("  " + "-" * 66)

    with arcpy.da.SearchCursor(
        STRUCTURES_SUBSET,
        ["BUILD_ID", "MEAN", "MAX", "STD", "COUNT", "SLOPE_VAL", "FLOWACC_VA"]
    ) as cursor:
        for row in cursor:
            above = " *" if row[1] and row[1] > THRESHOLD else ""
            print(
                f"  {str(row[0]):<15}"
                f" {round(row[1], 2):>8}"
                f" {round(row[2], 2):>8}"
                f" {round(row[3], 2):>8}"
                f" {int(row[4]):>8}"
                f" {round(row[5], 2):>10}"
                f" {round(row[6], 2):>11}"
                f"{above}"
            )

    print()
    print(f"  * = mean change score above threshold ({THRESHOLD})")
    print()
    print("Analysis complete. Final layer: CampMystic_Structures.shp")
    print("Load in ArcGIS Pro and symbolize by MEAN field to visualize change scores.")


if __name__ == "__main__":
    main()
