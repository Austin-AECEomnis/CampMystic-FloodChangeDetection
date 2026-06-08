# CRS Mismatch: NOAA WGS84 Geographic vs. NAIP UTM Projected

## What Happened

After confirming tile counts and band counts, a CRS diagnostic revealed that
NAIP and NOAA tiles were in different coordinate systems:

- NAIP: `NAD_1983_UTM_Zone_14N` — Projected, meter units, cell size 0.6
- NOAA: `GCS_WGS_1984` — Geographic, degree units, cell size ~0.0000013

The NOAA cell size in scientific notation (1.3489113117375975e-06) was the
immediate signal that the dataset was in geographic coordinates. A cell size
expressed in degrees rather than meters is not directly comparable to a
projected raster measured in meters.

## Why It Matters

Pixel-level band subtraction requires both datasets to occupy exactly the
same spatial grid. Subtracting a pixel at geographic coordinates from a pixel
at projected coordinates produces spatial misalignment. Even with on-the-fly
projection in ArcGIS Pro providing correct visual rendering, geoprocessing
tools operate on the raw coordinate values. The datasets must share a CRS
before any raster arithmetic is performed.

## Resolution

Reproject NOAA tiles to NAD83 UTM Zone 14N (EPSG 26914) using ProjectRaster
with BILINEAR resampling. BILINEAR is correct for continuous imagery data.
NEAREST NEIGHBOR is appropriate for categorical or classified data only.

Reproject NOAA to match NAIP, not the other way around. UTM Zone 14N is the
better working projection: meter-based units, appropriate for this part of
Texas, and consistent with all other project data.

## Verification

After reprojection, confirm CRS and cell size:

```python
import arcpy

r = arcpy.Raster(r"C:\path\to\reprojected_tile.tif")
print(r.spatialReference.name)   # NAD_1983_UTM_Zone_14N
print(r.meanCellWidth)           # ~0.14 meters after reprojection
```

## Key Learning

A raster cell size returned in scientific notation is the immediate diagnostic
signal for geographic (degree-unit) coordinates. Always check CRS before any
pixel-level operation.
