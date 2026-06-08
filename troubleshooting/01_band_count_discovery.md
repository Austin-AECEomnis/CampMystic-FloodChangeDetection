# Band Count Discovery: NAIP and NOAA 4-Band vs. 3-Band

## What Happened

NAIP tiles downloaded from EarthExplorer appeared as 3-band RGB in the
ArcGIS Pro Contents pane. Based on this visual, the initial MosaicToNewRaster
call declared `number_of_bands=3`. The tool returned:

```
ERROR 000157: Input and target dataset should have the same number of bands
Failed to execute (MosaicToNewRaster)
```

A diagnostic check using `arcpy.Raster().bandCount` confirmed all four NAIP
tiles are actually 4-band. The fourth band is near-infrared (NIR).
The same finding applied to NOAA tiles. Both datasets confirmed 4-band.

## Why It Happens

ArcGIS Pro defaults to rendering bands 1-2-3 as RGB. The NIR band sits in
the dataset silently and does not participate in the default visual rendering.
There is no visual indicator in the Contents pane that a fourth band exists.

## Diagnostic Script

Run this before building any mosaic to confirm band counts:

```python
import arcpy
import os

folder = r"C:\GIS_Projects\CampMystic_ChangeDetection\NAIP_PreEvent\Extracted"
tiles = [os.path.join(folder, f) for f in os.listdir(folder)
         if f.endswith('.tif') and not f.endswith('.aux.xml')]

for tile in tiles:
    r = arcpy.Raster(tile)
    print(f"{os.path.basename(tile)}: {r.bandCount} bands, {r.pixelType}")
```

## Resolution

Set `number_of_bands=4` in all MosaicToNewRaster calls for both NAIP and NOAA.
Only bands 1, 2, and 3 (RGB) are used in the band subtraction analysis. The NIR
band is present in the mosaics but not referenced in the change detection script.

## Key Learning

Never assume band count from the Contents pane visual. Always verify with
`arcpy.Raster().bandCount` before building mosaics or declaring pixel types.
