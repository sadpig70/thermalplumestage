# PGF Design: ThermalPlume Stage

## Gantree

- Goal: marine thermal-discharge dispersion planner
  - Input: discharge specs
  - Input: current forecast
  - Input: ecology thresholds
  - Transform: compute thermal boundary delta by outfall/hour
  - Transform: reduce valve fraction under ecological threshold
  - Output: JSON and Markdown valve timing, dilution schedule, threshold report

## PPR

```
AI_LOAD(discharge_specs,current_forecast,ecology_thresholds)
  -> AI_VALIDATE(required_fields, physical_ranges)
  -> AI_ESTIMATE(thermal_load, dispersion_factor, boundary_delta)
  -> AI_DECIDE(valve_fraction, status, evidence_gap)
  -> AI_RENDER(json_report, markdown_report)
```

## Boundary

- `source_round=SA-EVX-20260611-001`
- `source_candidate=ThermalPlume Stage`
- `cross_model_certified=false`
- `production_promotion_required=true`

