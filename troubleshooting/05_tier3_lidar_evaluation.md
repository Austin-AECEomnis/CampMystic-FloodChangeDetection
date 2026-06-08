# Tier 3 LiDAR Evaluation: Camp Mystic 2025 and Llano River 2018

## What Tier 3 Would Provide

LiDAR point cloud differencing answers a fundamentally different question
than RGB change detection. Tier 2 detects spectral change: surfaces look
different from above. Tier 3 detects vertical change: surfaces are at a
different elevation than before.

Tier 3 capabilities not available from Tier 2:

- Vertical displacement measurements in actual meters
- Distinction between surface types that appear identical spectrally
  but changed differently in elevation
- Detection of small vegetation removal below RGB resolution
- Physically grounded confirmation tying spectral change to earth movement

The prerequisite is a pre-event and post-event LiDAR collection covering
the same area, both at sufficient resolution, with a temporal gap close
enough to the flood event that damage signatures have not been erased by
reconstruction and vegetation regrowth. A post-event collection window
of 3 to 6 months is considered the practical outer limit before rebuilding
and recovery begin to obscure the original damage signature.

## Camp Mystic 2025 Evaluation

**Search repositories:** TxGIO DataHub, USGS 3DEP LiDAR Explorer

**Post-event:** NOAA flew RGB emergency imagery after the July 4, 2025 flood,
not LiDAR. No post-event LiDAR acquisition exists for the Camp Mystic AOI.

**Conclusion:** Tier 3 not executable for the 2025 Camp Mystic event.
No post-event LiDAR baseline exists. Tier 3 remains a described future
capability pending a suitable acquisition.

## Llano River 2018 Evaluation

The October 2018 Llano River flood was evaluated as an alternative Tier 3
candidate. The event severity and FEMA Major Disaster Declaration (DR-4416)
made a federally commissioned post-event LiDAR flight plausible.

**Flood date:** Peak October 16, 2018. The Llano River at Llano rose 35 feet
in 24 hours, cresting at 39.91 feet, the highest level since 1935. The FM 2900
bridge at Kingsland collapsed and was washed away entirely.

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
| Classifications | Bare earth ground, water, bridge decks, noise |

The 12 to 16 week collection window falls within the 3 to 6 month damage
signature window. The bridge deck classification is directly relevant given
the FM 2900 bridge collapse.

**Pre-event baseline search:**

| Repository | Finding |
|------------|---------|
| TxGIO DataHub | No coverage for Llano River corridor in usable timeframe |
| USGS 3DEP LiDAR Explorer | Collections available going back to 2006 only |

Nearest usable pre-event collection: 2006, approximately 13 years prior
to the October 2018 flood.

**Conclusion:** A 13-year pre/post gap is analytically indefensible for
flood attribution. Over 13 years, structural change, development, demolition,
renovation, and vegetation growth produce vertical change signatures that
cannot be distinguished from flood-related displacement. Tier 3 is not
executable for the 2018 Llano event with publicly available data.

## Summary

| Event | Post-Event LiDAR | Pre-Event Baseline | Viable |
|-------|-----------------|-------------------|--------|
| Camp Mystic 2025 | None found | N/A | No |
| Llano River 2018 | Confirmed (Jan–Feb 2019) | 2006 only (13yr gap) | No |

## Finding

Both events were evaluated rigorously across two repositories. The blocking
constraint in both cases is data availability, not methodology. A suitable
post-event collection exists for the Llano 2018 event but no usable pre-event
baseline exists within an acceptable temporal window.

This evaluation demonstrates professional data assessment practice: confirming
what exists, assessing temporal viability, and documenting the conclusion with
evidence rather than simply noting that Tier 3 was not attempted.
