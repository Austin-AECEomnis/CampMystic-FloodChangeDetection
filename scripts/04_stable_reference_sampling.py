"""
04_stable_reference_sampling.py
Camp Mystic Flood Change Detection -- Stable Reference Sampling and Threshold Derivation

Purpose:
    Derives the change detection threshold empirically from stable reference
    surfaces rather than applying a hardcoded value. This produces a threshold
    calibrated to the specific sensor pair, date combination, and landscape
    of this analysis.

    Workflow:
        1. Extract red band from both NAIP clipped and NOAA mosaic
        2. Compute absolute difference on red band across full extent
        3. Sample difference raster at stable reference polygons
        4. Compute noise floor statistics from confirmed stable surfaces
        5. Report suggested threshold (mean + 2 std dev)

    Reference surface requirements:
        Polygons must be over hard impervious surfaces confirmed visually
        identical in both pre and post imagery. Avoid: tree canopy, river
        channel, vegetation, areas with shadow variation between dates.
        Recommended: road sections, parking lots, concrete pads, rooftops
        with no adjacent trees.

    Critical: Validate reference surfaces against BOTH pre and post imagery
    before running this script. A surface that appears stable may have
    experienced real flood-related change (sediment deposition, scour).
    Contaminated reference polygons inflate the noise floor and produce
    an artificially high threshold that misses real change signal.

    For the Camp Mystic analysis, the tennis court appeared stable visually
    but was confirmed post-analysis as covered with flood-deposited sediment
    in the NOAA imagery. It was excluded from the noise floor and reclassified
    as a known-change validation point. See troubleshooting/
    04_reference_polygon_contamination.md for full documentation.

Environment:
    ArcGIS Pro arcgispro-py3 conda environment
    Run via ArcGIS Pro Python Window
    Requires: Spatial Analyst extension

Author: Austin Addington Berlin / AECE Omnis LLC
"""

import arcpy
from arcpy.sa import Abs, Raster
import numpy as np
import os

# -- Configuration -------------------------------------------------------------

NAIP_CLIPPED  = r"C:\GIS_Projects\CampMystic_ChangeDetection\naip_clipped.tif"
NOAA_MOSAIC   = r"C:\GIS_Projects\CampMystic_ChangeDetection\noaa_mosaic.tif"
STABLE_REF    = r"C:\Users\aaddi\OneDrive\Documents\ArcGIS\Projects\GuadalupeCoridor_FloodAnalysis\GuadalupeCoridor_FloodAnalysis.gdb\stable_reference"
SAMPLE_OUTPUT = r"C:\GIS_Projects\CampMystic_ChangeDetection\stable_sample.dbf"

# OID-to-label mapping for stable reference polygons.
# Update this dictionary if you re-digitize or reorder your reference polygons.
SURFACE_LABELS = {
    1: "road",
    2: "tennis_court",
    3: "asphalt_court"
}

# Surfaces to EXCLUDE from noise floor calculation.
# Any surface confirmed as having experienced real flood change must be excluded.
# The tennis court at Camp Mystic was covered with flood-deposited sediment
# and returns a signal value (27.09), not noise. It belongs in the known-change set.
EXCLUDED_FROM_NOISE_FLOOR = {"tennis_court"}

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# -- Main ----------------------------------------------------------------------

def main():

    # -- Step 1: Extract red band and compute difference -----------------------

    print("Extracting red band (Band 1) from NAIP and NOAA...")
    naip_red = arcpy.ia.ExtractBand(NAIP_CLIPPED, [1])
    noaa_red = arcpy.ia.ExtractBand(NOAA_MOSAIC,  [1])

    print("Computing absolute difference raster on red band...")
    diff_red = Abs(Raster(naip_red) - Raster(noaa_red))
    print("  Difference raster computed (visible in Pro map if added to Contents)")
    print()

    # -- Step 2: Sample difference raster at stable reference polygons ---------

    print("Sampling difference raster at stable reference polygons...")
    arcpy.sa.Sample(
        in_rasters=diff_red,
        in_location_data=STABLE_REF,
        out_table=SAMPLE_OUTPUT,
        resampling_type="BILINEAR",
        unique_id_field="OBJECTID"    # Must be numeric; text fields not accepted by Sample tool
    )
    print(f"  Sample output: {SAMPLE_OUTPUT}")
    print()

    # -- Step 3: Identify value field in DBF output ----------------------------

    # DBF field name for the difference raster values is auto-generated
    # and will not be a human-readable name. Find it dynamically.
    all_fields = [f.name for f in arcpy.ListFields(SAMPLE_OUTPUT)]
    value_field = None
    skip_fields = {"OID", "LOCATIONID", "X", "Y"}
    for f in all_fields:
        if f.upper() not in skip_fields:
            ftype = arcpy.ListFields(SAMPLE_OUTPUT, f)[0].type
            if ftype in ("Double", "Single", "Float"):
                value_field = f
                break

    if not value_field:
        print("ERROR: Could not identify value field in sample output.")
        print(f"Fields found: {all_fields}")
        return

    print(f"Value field identified: {value_field}")
    print()

    # -- Step 4: Read sample values and compute statistics ---------------------

    print("Sample values by surface:")
    all_values    = []
    stable_values = []

    with arcpy.da.SearchCursor(SAMPLE_OUTPUT, ["LOCATIONID", value_field]) as cursor:
        for row in cursor:
            oid      = row[0]
            val      = row[1]
            label    = SURFACE_LABELS.get(oid, f"OID_{oid}")
            excluded = label in EXCLUDED_FROM_NOISE_FLOOR
            flag     = " [EXCLUDED -- known change]" if excluded else ""
            print(f"  {label:<20} diff value: {round(val, 4)}{flag}")
            all_values.append((label, val))
            if not excluded and val is not None:
                stable_values.append(val)

    print()

    if len(stable_values) < 2:
        print("WARNING: Fewer than 2 stable reference values. Threshold may not be reliable.")
        print("Add more stable reference polygons and rerun.")
        return

    stable_arr = np.array(stable_values)
    mean_val   = round(float(np.mean(stable_arr)), 2)
    std_val    = round(float(np.std(stable_arr)),  2)
    p95_val    = round(float(np.percentile(stable_arr, 95)), 2)
    threshold  = round(mean_val + 2 * std_val, 2)

    stable_labels = [l for l, v in all_values if l not in EXCLUDED_FROM_NOISE_FLOOR]

    print("Noise floor statistics (stable surfaces only):")
    print(f"  Surfaces used:       {stable_labels}")
    print(f"  Mean difference:     {mean_val}")
    print(f"  Std deviation:       {std_val}")
    print(f"  95th percentile:     {p95_val}")
    print(f"  Mean + 2 std dev:    {threshold}")
    print(f"  Suggested threshold: {threshold}")
    print()
    print("Copy the suggested threshold value into 05_band_subtraction_zonal_stats.py")
    print("as the THRESHOLD variable before running the next script.")


if __name__ == "__main__":
    main()
