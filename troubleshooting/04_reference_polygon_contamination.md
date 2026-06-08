# Reference Polygon Contamination: Tennis Court Sediment Deposition

## What Happened

Three stable reference polygons were digitized over surfaces visually
confirmed as unchanged between the June 2022 NAIP and July 2025 NOAA imagery:

- Road segment (Camp Mystic Way Rd)
- Tennis court
- Asphalt court

Initial sampling returned:

| Surface | Red Band Diff Value |
|---------|-------------------|
| road | 13.16 |
| tennis_court | 27.09 |
| asphalt_court | 17.64 |

The tennis court value at 27.09 was significantly higher than the road and
asphalt court values. Initial noise floor calculation including all three
surfaces produced a threshold of 30.91 (mean + 2 std dev).

## Root Cause

Post-analysis review of the NOAA imagery confirmed the tennis court surface
was covered with flood-deposited sediment after the July 4 water recession.
The court underwent real surface change between the two acquisition dates.
A difference value of 27.09 is not noise — it is signal from actual
flood-related surface alteration.

Including a contaminated surface in the noise floor calculation artificially
inflated the mean and standard deviation, pushing the threshold 11 points
higher than warranted. A threshold of 30.91 would have missed real change
signal in the 20 to 30 range.

## Resolution

Remove the tennis court from the noise floor calculation entirely.
Recalculate using road and asphalt court only:

| Metric | Value |
|--------|-------|
| Mean difference | 15.40 |
| Std deviation | 2.24 |
| 95th percentile | 17.41 |
| Mean + 2 std dev | **19.88 (applied threshold)** |

The tennis court value of 27.09 now serves as a known-change validation
point. It sits 7 points above the corrected threshold, confirming that
real flood-deposited surface change produces values clearly above the
noise ceiling. This validates the threshold separation between stable
and changed surfaces.

## Validation Significance

This correction is analytically important and portfolio-significant.
The threshold derivation is now:

- Calibrated to the specific sensor pair and date combination
- Validated by a known-change ground truth point on the same imagery
- Defensible: the methodology caught its own contamination through
  domain knowledge and corrected it explicitly

## Key Learning

Reference polygons for noise floor derivation must be validated against
BOTH pre and post imagery before sampling. Visual similarity in the pre-event
image alone is not sufficient. Ground knowledge of what happened at each
surface between acquisition dates is required to detect contamination.
A surface that looks stable may have experienced real flood-related change.
