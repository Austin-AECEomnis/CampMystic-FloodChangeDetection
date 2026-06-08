# GDB Path Resolution: Feature Classes Under OneDrive

## What Happened

Scripted paths to the stable_reference feature class failed repeatedly with:

```
ERROR 000732: Dataset does not exist or is not supported
```

Paths attempted included:

```
C:\GIS_Projects\CampMystic_ChangeDetection\CampMystic_ChangeDetection.gdb\stable_reference
C:\GIS_Projects\GuadalupeCorridor_FloodAnalysis\GuadalupeCoridor_FloodAnalysis\stable_reference
C:\GIS_Projects\GuadalupeCorridor_FloodAnalysis\GuadalupeCoridor_FloodAnalysis.gdb\stable_reference
```

## Root Cause

The stable_reference feature class was digitized in a project opened from the
default ArcGIS Pro project location under OneDrive Documents, not from the
custom GIS_Projects working directory. The actual path was:

```
C:\Users\aaddi\OneDrive\Documents\ArcGIS\Projects\GuadalupeCoridor_FloodAnalysis\
GuadalupeCoridor_FloodAnalysis.gdb\stable_reference
```

Note the single-L spelling in `GuadalupeCoridor` (one 'r' instead of two in
Corridor). This is the geodatabase name as created and cannot be changed
without migrating all data to a new GDB.

## How to Find the Correct Path

When scripted paths fail, use the ArcGIS Pro layer Properties panel:

1. Right-click the layer in the Contents pane
2. Select Properties
3. Go to the Source tab
4. Copy the exact path shown

This is the path ArcPy requires. Do not reconstruct paths from memory,
folder names, or display names in the Contents pane.

## Additional Note on arcpy.sa.Sample Field Requirements

The Sample tool requires a numeric unique ID field. Text fields are not
accepted as the unique_id_field parameter and will return:

```
ERROR 000864: Unique ID field: The input is not within the defined domain.
ERROR 003911: The field is not of type SHORT | LONG | OBJECTID | BIGINTEGER
```

Always use OBJECTID as the unique_id_field. Map labels back to OID values
manually in the cursor query after sampling.

## Key Learning

Always verify feature class paths from the layer Source tab before
scripting. ArcGIS Pro project GDBs may live under OneDrive Documents or
other locations depending on how the project was originally created.
ArcPy references geodatabase names exactly as created, including any
spelling variations.
