"""Thermal plume dispersion planning logic."""

from __future__ import annotations

from .models import BOUNDARY, CurrentForecast, DischargePoint, DischargeSpecs, EcologyThresholds, ForecastHour, ThermalReport, ValveWindow


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _tide_factor(tide_state: str) -> float:
    return {
        "ebb": 1.12,
        "flood": 1.05,
        "slack": 0.54,
        "neap": 0.72,
        "spring": 1.18,
    }.get(tide_state.lower(), 0.84)


def _dispersion_factor(point: DischargePoint, hour: ForecastHour) -> float:
    current = max(hour.current_speed_m_s, 0.02)
    mixing = 1.0 + min(point.mixing_depth_m, 80.0) / 52.0
    stratification_penalty = 1.0 - (hour.stratification_index * 0.46)
    return max(0.06, current * point.diffuser_efficiency * mixing * stratification_penalty * _tide_factor(hour.tide_state))


def _boundary_delta(point: DischargePoint, hour: ForecastHour, threshold: EcologyThresholds, flow_m3_s: float) -> float:
    thermal_gradient = max(0.0, point.discharge_temp_c - hour.ambient_temp_c)
    heat_load = thermal_gradient * flow_m3_s
    distance = max(point.habitat_distance_m, threshold.protected_radius_m)
    dilution_mass = _dispersion_factor(point, hour) * (distance / 88.0 + 4.5)
    return heat_load / max(dilution_mass, 0.01)


def _dilution_radius(point: DischargePoint, hour: ForecastHour, flow_m3_s: float) -> float:
    plume_push = (flow_m3_s * max(point.discharge_temp_c - hour.ambient_temp_c, 0.0)) ** 0.5
    return 70.0 + plume_push * 28.0 / max(_dispersion_factor(point, hour), 0.05)


def _allowed(point: DischargePoint, hour: ForecastHour) -> bool:
    return not point.allowed_hours or hour.hour in point.allowed_hours


def _window_status(delta: float, thresholds: EcologyThresholds, hour: ForecastHour, evidence_gaps: list[str]) -> str:
    if hour.storm_watch:
        return "halt"
    if delta <= thresholds.max_delta_c_at_boundary and not evidence_gaps:
        return "within_threshold"
    if delta <= thresholds.max_delta_c_at_boundary * 1.35:
        return "mitigate"
    return "halt"


def _exposure_credit(status: str, thresholds: EcologyThresholds) -> float:
    if status == "within_threshold":
        return min(1.0, thresholds.max_exposure_hours / 2.0)
    if status == "mitigate":
        return min(0.5, thresholds.max_exposure_hours / 4.0)
    return 0.0


def plan_dispersal(specs: DischargeSpecs, forecast: CurrentForecast, thresholds: EcologyThresholds) -> list[ValveWindow]:
    windows: list[ValveWindow] = []
    for point in specs.points:
        for hour in forecast.forecast_hours:
            if not _allowed(point, hour):
                continue
            full_delta = _boundary_delta(point, hour, thresholds, point.max_flow_m3_s)
            target_fraction = thresholds.max_delta_c_at_boundary / max(full_delta, 0.001)
            if thresholds.critical_habitat:
                target_fraction *= 0.9
            if thresholds.sensitive_species:
                target_fraction *= 0.94
            if hour.tide_state == "slack":
                target_fraction *= 0.72
            if hour.storm_watch:
                target_fraction = 0.0
            valve_fraction = _clamp(target_fraction, 0.0, 1.0)
            recommended_flow = max(point.min_flow_m3_s if valve_fraction > 0 else 0.0, point.max_flow_m3_s * valve_fraction)
            if valve_fraction == 0.0:
                recommended_flow = 0.0
            delta = _boundary_delta(point, hour, thresholds, recommended_flow)
            evidence_gaps = []
            if not point.evidence:
                evidence_gaps.append("missing diffuser or habitat survey evidence")
            if hour.current_speed_m_s < 0.25:
                evidence_gaps.append("weak current forecast")
            if hour.stratification_index >= 0.65:
                evidence_gaps.append("strong stratification forecast")
            rationale = [
                f"current={hour.current_speed_m_s:.2f}m/s tide={hour.tide_state}",
                f"ambient={hour.ambient_temp_c:.1f}C discharge={point.discharge_temp_c:.1f}C",
                f"protected_radius={thresholds.protected_radius_m:.0f}m habitat_distance={point.habitat_distance_m:.0f}m",
            ]
            status = _window_status(delta, thresholds, hour, evidence_gaps)
            windows.append(
                ValveWindow(
                    point_id=point.point_id,
                    hour=hour.hour,
                    recommended_flow_m3_s=recommended_flow,
                    valve_fraction=valve_fraction,
                    boundary_delta_c=delta,
                    dilution_radius_m=_dilution_radius(point, hour, recommended_flow),
                    exposure_credit_hours=_exposure_credit(status, thresholds),
                    status=status,
                    rationale=rationale,
                    evidence_gaps=evidence_gaps,
                )
            )
    return sorted(windows, key=lambda item: ({"within_threshold": 0, "mitigate": 1, "halt": 2}[item.status], item.boundary_delta_c, item.hour, item.point_id))


def _overall_status(windows: list[ValveWindow]) -> str:
    if not windows:
        return "no_release_window"
    if any(item.status == "within_threshold" for item in windows):
        return "stage_release"
    if any(item.status == "mitigate" for item in windows):
        return "mitigate_before_release"
    return "halt_release"


def build_report(specs: DischargeSpecs, forecast: CurrentForecast, thresholds: EcologyThresholds) -> ThermalReport:
    windows = plan_dispersal(specs, forecast, thresholds)
    best = [item for item in windows if item.status == "within_threshold"][:4]
    max_delta = max((item.boundary_delta_c for item in windows), default=0.0)
    halt_count = sum(1 for item in windows if item.status == "halt")
    summary = {
        "overall_status": _overall_status(windows),
        "best_release_hours": [{"point_id": item.point_id, "hour": item.hour, "flow_m3_s": round(item.recommended_flow_m3_s, 4)} for item in best],
        "halt_windows": halt_count,
        "mitigation_windows": sum(1 for item in windows if item.status == "mitigate"),
        "planned_windows": len(windows),
        "max_boundary_delta_c": round(max_delta, 4),
        "ecology_threshold_c": thresholds.max_delta_c_at_boundary,
        "critical_habitat": thresholds.critical_habitat,
        "sensitive_species": thresholds.sensitive_species,
        "differentiation": "physical marine thermal-discharge dispersion control, not heat monetization or bio-release quarantine",
    }
    return ThermalReport(
        site_id=specs.site_id,
        facility_name=specs.facility_name,
        forecast_id=forecast.forecast_id,
        windows=windows,
        summary=summary,
        boundary=dict(BOUNDARY),
    )

