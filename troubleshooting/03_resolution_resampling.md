# Resolution Mismatch: NOAA 0.14m vs. NAIP 0.6m

## What Happened

After reprojecting NOAA tiles to UTM Zone 14N, the cell size confirmed as
approximately 0.14 meters. NAIP cell size is 0.6 meters. These are
significantly different resolutions and cannot be used directly in
pixel-level band subtraction without resampling to a common grid.

## Resampling Direction

**Resample NOAA up to 0.6m. Do not resample NAIP down to 0.14m.**

Resampling NAIP to 0.14m resolution would create false precision. NAIP was
collected at 0.6m. No amount of resampling produces information that was not
captured at acquisition. Downsampling introduces interpolated values between
real measurements, which corrupts the pixel arithmetic.

The honest working resolution for this analysis is 0.6 meters, set by the
coarser of the two input datasets.

## Implementation

```python
arcpy.management.Resample(
    in_raster=projected_tile,
    out_raster=output_path,
    cell_size="0.6",
    resampling_type="BILINEAR"
)
```

BILINEAR resampling is correct for continuous imagery. It produces a weighted
average of surrounding pixel values, appropriate for the smooth gradients in
aerial imagery.

## Verified Output

After resampling, all checks confirmed:

| Property | Value |
|----------|-------|
| Cell size | 0.6000000000000114 meters (floating point artifact, effectively 0.6) |
| CRS | NAD_1983_UTM_Zone_14N |
| Bands | 4 |
| Pixel type | U8 |

All properties now match NAIP for pixel-level arithmetic.

## Key Learning

When harmonizing two rasters with different cell sizes, always resample
toward the coarser resolution. The analytical resolution ceiling is set by
the coarser input dataset, regardless of what the finer dataset could
theoretically provide.
