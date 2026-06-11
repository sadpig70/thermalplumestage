# ThermalPlume Stage Report: MGT-BASIN-07

- Facility: Mariner Geothermal Test Basin
- Forecast: KHOA-20260611T0600Z
- Overall status: `stage_release`
- `cross_model_certified=false`
- `production_promotion_required=true`

## Best Release Hours
- OUTFALL-A hour 3: 0.6229 m3/s
- OUTFALL-B hour 3: 0.4773 m3/s

## Valve Timing and Dilution Schedule

| point | hour | flow m3/s | valve | boundary delta C | radius m | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| OUTFALL-A | 3 | 0.6229 | 0.1074 | 0.9306 | 170.45 | within_threshold |
| OUTFALL-B | 3 | 0.4773 | 0.1404 | 0.9306 | 187.39 | within_threshold |
| OUTFALL-A | 12 | 0.6 | 0.0807 | 1.1933 | 205.04 | mitigate |
| OUTFALL-A | 1 | 0.6 | 0.0699 | 1.3767 | 221.93 | mitigate |
| OUTFALL-B | 15 | 0.4 | 0.0726 | 1.5071 | 287.01 | halt |
| OUTFALL-A | 15 | 0.6 | 0.0543 | 1.7732 | 271.41 | halt |
| OUTFALL-B | 5 | 0.4 | 0.0137 | 5.7708 | 880.53 | halt |

## Ecological Threshold Report

- Threshold: 1.1 C at protected boundary
- Halt windows: 3
- Mitigation windows: 2
- Critical habitat: true
- Sensitive species: eelgrass bed, abalone nursery

## Boundary

- `source_round`: `SA-EVX-20260611-001`
- `source_artifact`: `.sa-evx/rounds/SA-EVX-20260611-001/final_integrated_idea.md`
- `source_candidate`: `ThermalPlume Stage`
- `cross_model_certified`: `False`
- `production_promotion_required`: `True`
