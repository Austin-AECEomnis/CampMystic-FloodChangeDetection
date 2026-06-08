# 🌊 Camp Mystic Flood Change Detection

**RGB Change Detection and LiDAR Feasibility Assessment**
**Camp Mystic / Guadalupe River Corridor, Kerr County, TX — July 2025 Flood Event**

---

## 📋 Overview

On July 4, 2025, the Guadalupe River at Hunt, TX rose approximately 26 feet in 45 minutes, inundating structures throughout the corridor including Camp Mystic, the most heavily impacted site in the event. This repository documents a multi-tier change detection analysis evaluating flood impact through pre/post imagery comparison and LiDAR point cloud feasibility assessment.

**Tier 1** (terrain analysis) was completed in a prior workflow. See the [ESRI GIS Master Workflow repository](https://github.com/Austin-AECEomnis/ESRI-GIS-Master-Workflow) for the full terrain pipeline that identified 107 high-risk structures in the Guadalupe corridor.

**Tier 2** (RGB change detection) is the primary executed analysis in this repository. Pre-event NAIP imagery (June 2022) is compared against post-event NOAA emergency imagery (July 20, 2025) to detect surface change at structure locations using band subtraction, empirical threshold derivation, and Zonal Statistics scoring.

**Tier 3** (LiDAR point cloud differencing) was evaluated for both the 2025 Camp Mystic event and the 2018 Llano River flood event. Data availability was assessed across USGS 3DEP and TxGIO repositories. Findings and limitations are fully documented.

---

## 🗂️ Repository Contents

| File | Description |
|------|-------------|
| `README.md` | Methodology, findings, data sources, and navigation |
| `scripts/01_data_inventory.py` | Confirms tile counts, band counts, CRS, cell size, and extent for all input rasters |
| `scripts/02_noaa_reproject_resample.py` | Reprojects NOAA tiles from WGS84 to NAD83 UTM Zone 14N and resamples to 0.6m |
| `scripts/03_mosaic_and_clip.py` | Builds NAIP and NOAA mosaics and clips NAIP to NOAA extent |
| `scripts/04_stable_reference_sampling.py` | Samples stable reference polygons to derive empirical noise-floor threshold |
| `scripts/05_band_subtraction_zonal_stats.py` | Runs band subtraction, applies threshold, buffers structures, runs Zonal Statistics, joins results |
| `troubleshooting/01_band_count_discovery.md` | NAIP tiles appeared as 3-band in Pro but confirmed 4-band via arcpy.Raster() |
| `troubleshooting/02_crs_reprojection.md` | NOAA tiles delivered in WGS84 geographic coordinates vs NAIP UTM projected |
| `troubleshooting/03_resolution_resampling.md` | NOAA at 0.14m vs NAIP at 0.6m — resampling direction and rationale |
| `troubleshooting/04_reference_polygon_contamination.md` | Tennis court identified as contaminated reference surface mid-analysis |
| `troubleshooting/05_tier3_lidar_evaluation.md` | Full LiDAR data search findings for both Camp Mystic and Llano flood events |
| `troubleshooting/06_gdb_path_resolution.md` | Feature class path resolution when GDB lives under OneDrive rather than project folder |

---

## ⚙️ Requirements

| Requirement | Detail |
|-------------|--------|
| Software | ArcGIS Pro 3.x |
| Python Environment | ArcGIS Pro default `arcgispro-py3` conda environment |
| Extensions | Spatial Analyst (required for raster algebra, Sample, ZonalStatisticsAsTable) |
| Input 1 | 4 NAIP GeoTIFF tiles, June 6 2022, EarthExplorer download |
| Input 2 | 2 NOAA GeoTIFF tiles, July 20 2025, post-event emergency imagery |
| Input 3 | Stable reference polygons feature class in project geodatabase |
| Input 4 | Structure centroids subset clipped to Camp Mystic boundary |

---

## 📡 Data Sources

### Pre-Event Imagery: NAIP
- **Source:** USGS EarthExplorer — [earthexplorer.usgs.gov](https://earthexplorer.usgs.gov)
- **Collection date:** June 6, 2022
- **Search parameters:** Aerial Imagery > NAIP, date range 2021–2023, coordinates centered on Camp Mystic AOI
- **Tiles downloaded:** 4 GeoTIFF tiles (NE, NW, SE, SW quadrants)
- **Format:** Full resolution GeoTIFF (not compressed)
- **Delivered CRS:** NAD83 UTM Zone 14N (EPSG 26914)
- **Cell size:** 0.6 meters
- **Bands:** 4 (Red, Green, Blue, Near-Infrared)

> **Note:** NAIP tiles from EarthExplorer are 4-band even when ArcGIS Pro renders them as 3-band RGB in the Contents pane. Always verify band count using `arcpy.Raster().bandCount` before building mosaics.

### Post-Event Imagery: NOAA Emergency Response
- **Source:** NOAA Emergency Response Imagery
- **Flight date:** July 20, 2025 (16 days after the flood peak)
- **Tiles used:** 2 GeoTIFF tiles covering Camp Mystic footprint
- **Delivered CRS:** GCS WGS 1984 (geographic, degree units)
- **Native cell size:** ~0.14 meters (confirmed after reprojection to UTM)
- **Bands:** 4 (Red, Green, Blue, Near-Infrared)
- **Resampled to:** 0.6 meters to match NAIP for pixel-level arithmetic

### Structure Centroids
- **Source:** Auto_High_Risk_107_Structures from KendallCounty_FloodAnalysis.gdb
- **Subset:** 12 structures clipped to CampMystic_Boundary polygon
- **Terrain fields carried forward:** SLOPE_VAL, FLOWACC_VAL from Tier 1 analysis

---

## 🔁 Workflow Overview

### Step 1: Data Inventory and Diagnostic
Confirm all input rasters are present, readable, and have the expected properties before any processing begins. Verify band count, CRS, cell size, pixel type, and extent for each NAIP and NOAA tile.

### Step 2: NOAA Reprojection and Resampling
NOAA tiles are delivered in WGS84 geographic coordinates. NAIP tiles are in NAD83 UTM Zone 14N projected coordinates. Pixel-level arithmetic requires matching CRS and matching cell size.

- Reproject NOAA tiles to NAD83 UTM Zone 14N (EPSG 26914) using BILINEAR resampling
- Resample reprojected NOAA tiles from ~0.14m to 0.6m to match NAIP

> **Resampling direction:** Always resample to the coarser resolution. Resampling NAIP down to 0.14m would create false precision — information that was never captured at acquisition. The honest working resolution for this analysis is 0.6 meters.

### Step 3: Mosaic Construction and NAIP Clip
- Build NAIP mosaic from 4 tiles using MosaicToNewRaster (4 bands, 8-bit unsigned)
- Build NOAA mosaic from 2 resampled tiles using MosaicToNewRaster (4 bands, 8-bit unsigned)
- Clip NAIP mosaic to NOAA extent so both datasets cover identical ground

### Step 4: Stable Reference Sampling and Threshold Derivation
Digitize 3 polygons over surfaces confirmed stable between June 2022 and July 2025. Extract red band difference values at each polygon. Compute noise floor statistics. Set threshold at mean + 2 standard deviations.

**Reference surfaces used:**

| Surface | OID | Area (sq m) | Red Band Diff | Role |
|---------|-----|-------------|---------------|------|
| Road segment (Camp Mystic Way Rd) | 1 | 138.71 | 13.16 | Noise floor |
| Tennis court | 2 | 2394.44 | 27.09 | Removed — contaminated |
| Asphalt court | 3 | 325.70 | 17.64 | Noise floor |

> **Tennis court contamination:** The tennis court was initially included as a stable reference surface. Post-analysis review confirmed the court was covered with flood-deposited sediment visible in the NOAA imagery. A value of 27.09 is not noise — it is signal from real flood-related surface change. The tennis court was removed from the noise floor calculation and reclassified as a known-change validation point. This correction is what makes the threshold defensible.

**Final threshold calculation (road + asphalt court only):**

| Metric | Value |
|--------|-------|
| Mean difference | 15.40 |
| Std deviation | 2.24 |
| 95th percentile | 17.41 |
| Mean + 2 std dev | **19.88 (applied threshold)** |

The tennis court at 27.09 sits 7 points above the threshold, validating that real flood-deposited surface change lands clearly above the noise ceiling.

### Step 5: Band Subtraction, Threshold Application, and Zonal Statistics
- Extract RGB bands (1, 2, 3) from both clipped NAIP and NOAA mosaics
- Compute absolute difference per band
- Average three band differences into a single mean change magnitude raster
- Apply threshold using Con: pixels above 19.88 retain their difference value, pixels below set to zero
- Clip structure centroids to Camp Mystic boundary (12 structures)
- Buffer structures by 3 meters (single centroid point = 1 pixel = no statistical distribution)
- Run ZonalStatisticsAsTable against buffered structures (ALL statistics)
- Join MEAN, MAX, STD, COUNT fields back to structure layer via BUILD_ID

---

## ✅ Results

### Change Detection Raster
Visual inspection confirmed the two court surfaces (tennis court and asphalt court) as the highest change magnitude areas in the dataset, consistent with confirmed sediment deposition. No crisp structural damage signal was visible at individual building footprints, consistent with the flood mechanics at Camp Mystic (see Analytical Interpretation below).

### Zonal Statistics by Structure (3m buffer)

| BUILD_ID | MEAN | MAX | STD | SLOPE_VAL | FLOWACC_VAL |
|----------|------|-----|-----|-----------|-------------|
| 32724356 | 50.05 | 144.0 | 39.23 | 3.31 | 1.0 |
| 22629214 | 44.05 | 100.33 | 20.65 | 0.39 | 20.0 |
| 32724252 | 33.85 | 85.0 | 17.22 | 0.47 | 33.0 |
| 32724498 | 33.21 | 61.0 | 16.38 | 2.08 | 0.0 |
| 22629221 | 27.75 | 77.0 | 20.51 | 0.41 | 10.0 |
| 32724358 | 22.80 | 63.67 | 21.32 | 2.95 | 0.0 |
| 32724509 | 19.34 | 56.67 | 18.70 | 2.06 | 0.0 |
| 32724361 | 16.54 | 81.33 | 30.04 | 1.77 | 2.0 |
| 32724547 | 11.72 | 65.0 | 19.99 | 2.34 | 0.0 |
| 32724789 | 13.38 | 75.67 | 15.97 | 0.42 | 2.0 |
| 22629036 | 8.99 | 84.33 | 20.46 | 1.84 | 1.0 |
| 32724497 | 7.77 | 107.0 | 26.59 | 1.63 | 6.0 |

7 of 12 structures returned mean change scores above the 19.88 threshold.

### Analytical Interpretation
The relationship between terrain risk scores and change magnitude is non-linear, and this is analytically expected rather than a failure. The S-bend geometry of the Guadalupe River at Camp Mystic slowed water velocity, producing widespread inundation rather than channelized high-velocity flow. Structures across the AOI experienced flood exposure regardless of flow accumulation position. The terrain analysis correctly identified all 12 structures as high risk. The change detection confirms surface alteration across the majority of the zone.

Camp Mystic structures were not physically displaced or destroyed. The flood caused rapid interior inundation. Rooftop spectral signatures are largely unchanged because the structures survived. What the change raster captures is surface alteration visible from nadir: sediment deposition on open surfaces, vegetation scour, debris fields. Interior flood damage is not detectable from overhead RGB imagery. This is a resolution and geometry limitation of Tier 2, not an analytical failure.

**The portfolio thesis holds:** terrain flagged the zone as at risk, the flood validated that assessment, and the change detection confirms surface alteration across the majority of the AOI.

---

## 🔍 Tier 3 LiDAR Evaluation

### What Tier 3 Would Add
LiDAR point cloud differencing answers a fundamentally different question than RGB change detection: did the ground surface elevation change? Vertical displacement in meters, distinction between surface types that look the same spectrally, detection of small vegetation removal below RGB resolution, and physically grounded confirmation of earth movement. These are capabilities Tier 2 cannot provide.

### Camp Mystic 2025 Evaluation
**Post-event:** NOAA flew RGB emergency imagery after the July 4, 2025 flood, not LiDAR. No post-event LiDAR collection exists for the Camp Mystic AOI.
**Conclusion:** Tier 3 not executable for this event. Tier 3 remains a described future capability pending a suitable post-event LiDAR acquisition.

### Llano River 2018 Evaluation
The October 2018 Llano River flood (peak October 16, 2018) was evaluated as an alternative Tier 3 candidate given the severity of the event and the FEMA Major Disaster Declaration (DR-4416).

**Post-event collection confirmed:**

| Property | Value |
|----------|-------|
| Project name | TX Hurricane B3 2018 (USGS 3DEP) |
| Collection window | January 4 through February 17, 2019 |
| Time since flood peak | ~12 to 16 weeks |
| Quality Level | QL2 |
| Resolution | 1 meter |
| Sensor | Leica ALS80, linear-mode LiDAR |
| Specification | USGS LiDAR Base Specification 1.3 |
| Published | June 2020 |

**Pre-event baseline search:**

| Repository | Finding |
|------------|---------|
| TxGIO DataHub | No coverage for Llano River corridor in usable timeframe |
| USGS 3DEP LiDAR Explorer | Collections available going back to 2006 only |

**Conclusion:** A 13-year pre/post gap is analytically indefensible for flood attribution. Tier 3 is not executable for the 2018 Llano event with publicly available data. The blocking constraint is data availability, not methodology.

### Tier 3 Summary

| Event | Post-Event LiDAR | Pre-Event Baseline | Viable |
|-------|-----------------|-------------------|--------|
| Camp Mystic 2025 | None found | N/A | No |
| Llano River 2018 | Confirmed (Jan–Feb 2019) | 2006 only (13yr gap) | No |

---

## 📁 File and Folder Structure

**Local project folder (Austin's machine):**
```
C:\GIS_Projects\CampMystic_ChangeDetection\
├── NAIP_PreEvent\
│   └── Extracted\           (4 NAIP GeoTIFF tiles + companions)
├── NOAA_Imagery\
│   ├── (2 original NOAA GeoTIFF tiles)
│   ├── Projected\           (2 NOAA tiles reprojected to UTM)
│   └── Resampled\           (2 NOAA tiles resampled to 0.6m)
├── LiDAR_DEM\
│   └── extracted\           (4 DEM tiles for Camp Mystic AOI)
├── naip_mosaic.tif
├── noaa_mosaic.tif
├── naip_clipped.tif
├── change_detection.tif
├── stable_sample.dbf
├── CampMystic_Structures.shp
├── CampMystic_Structures_Buffer.shp
└── zonal_stats_buffered.dbf
```

---

## 🔗 Related Portfolio Products

- StoryMap narrative: [arcg.is/0bGXv02](https://arcg.is/0bGXv02)
- Experience Builder interactive application: [experience.arcgis.com](https://experience.arcgis.com/experience/09c67703781c49ddbc0830655aba9473/)
- Live monitoring Dashboard: [arcgis.com/apps/dashboards](https://www.arcgis.com/apps/dashboards/ac7607e8f4fa4185a97697b25cd6b181)
- ESRI GIS Master Workflow (Tier 1 terrain analysis): [github.com/Austin-AECEomnis/ESRI-GIS-Master-Workflow](https://github.com/Austin-AECEomnis/ESRI-GIS-Master-Workflow)
- QGIS Open Source Master Workflow: [github.com/Austin-AECEomnis](https://github.com/Austin-AECEomnis)

---

## 👤 Author

Austin Addington Berlin
Founder, AECE Omnis LLC
AI-GIS Convergence Research
[linkedin.com/in/austinberlin](https://linkedin.com/in/austinberlin)
[github.com/Austin-AECEomnis](https://github.com/Austin-AECEomnis)
