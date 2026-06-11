# ThermalPlume Stage Project Report

## Decision

Materialize `ThermalPlume Stage` as a stdlib-only Python MVP named `thermalplumestage`.

## Provenance

- Source round: `SA-EVX-20260611-001`
- Source artifact: `.sa-evx/rounds/SA-EVX-20260611-001/final_integrated_idea.md`
- Source candidate: `ThermalPlume Stage`
- `cross_model_certified=false`
- `production_promotion_required=true`

## MVP Contract

Inputs:

- `discharge_specs.json`
- `current_forecast.json`
- `ecology_thresholds.json`

Outputs:

- valve timing by outfall and hour
- spatial dilution schedule by plume radius and boundary delta
- ecological threshold report with halt/mitigate/stage-release decisions

## Derivative Check

The candidate is distinct from implemented heat and energy projects:

- `wastestack`: heat monetization and site finance, not marine plume dispersion.
- `powerroam`: compute workload dispatch to power conditions, not thermal outfall control.
- `coldmkh`: cold-capacity clearing, not environmental threshold staging.
- `lazarettostage`: bio-release quarantine, not physical heat release.
- `forgequarantine`: physical component crypto exposure, unrelated to marine ecology.

## Verification

Planned commands:

```bash
python -m pytest -q
python -m thermalplumestage sample -d examples/discharge_specs.json -f examples/current_forecast.json -e examples/ecology_thresholds.json
python -m thermalplumestage run -d examples/discharge_specs.json -f examples/current_forecast.json -e examples/ecology_thresholds.json --full -o examples/thermalplume_report.json
python -m thermalplumestage run -d examples/discharge_specs.json -f examples/current_forecast.json -e examples/ecology_thresholds.json --markdown -o examples/thermalplume_report.md
```

Result: passed.

- `python -m pytest -q` -> 6 passed
- CLI sample generation -> passed
- CLI full JSON report -> passed
- CLI Markdown report -> passed
- SVG XML parse -> passed
