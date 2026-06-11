"""Markdown rendering."""

from __future__ import annotations

from .models import ThermalReport


def render_markdown(report: ThermalReport) -> str:
    data = report.to_dict()
    lines = [
        f"# ThermalPlume Stage Report: {report.site_id}",
        "",
        f"- Facility: {report.facility_name}",
        f"- Forecast: {report.forecast_id}",
        f"- Overall status: `{data['summary']['overall_status']}`",
        f"- `cross_model_certified={str(report.boundary['cross_model_certified']).lower()}`",
        f"- `production_promotion_required={str(report.boundary['production_promotion_required']).lower()}`",
        "",
        "## Best Release Hours",
    ]
    best = data["summary"]["best_release_hours"]
    if best:
        for item in best:
            lines.append(f"- {item['point_id']} hour {item['hour']}: {item['flow_m3_s']} m3/s")
    else:
        lines.append("- No within-threshold release hour selected.")
    lines.extend(["", "## Valve Timing and Dilution Schedule", ""])
    lines.append("| point | hour | flow m3/s | valve | boundary delta C | radius m | status |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for item in data["windows"]:
        lines.append(
            f"| {item['point_id']} | {item['hour']} | {item['recommended_flow_m3_s']} | "
            f"{item['valve_fraction']} | {item['boundary_delta_c']} | {item['dilution_radius_m']} | {item['status']} |"
        )
    lines.extend(["", "## Ecological Threshold Report", ""])
    lines.append(f"- Threshold: {data['summary']['ecology_threshold_c']} C at protected boundary")
    lines.append(f"- Halt windows: {data['summary']['halt_windows']}")
    lines.append(f"- Mitigation windows: {data['summary']['mitigation_windows']}")
    lines.append(f"- Critical habitat: {str(data['summary']['critical_habitat']).lower()}")
    lines.append(f"- Sensitive species: {', '.join(data['summary']['sensitive_species']) or 'none'}")
    lines.extend(["", "## Boundary", ""])
    for key, value in report.boundary.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"

