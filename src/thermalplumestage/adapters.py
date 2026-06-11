"""JSON adapters and sample inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import CurrentForecast, DischargePoint, DischargeSpecs, EcologyThresholds, ForecastHour
from .validate import int_list, optional_bool, require_float, require_list, require_mapping, require_str, string_list


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8", newline="\n")


def parse_specs(data: Any) -> DischargeSpecs:
    root = require_mapping(data, "discharge specs")
    points = []
    for raw in require_list(root.get("discharge_points"), "discharge_points"):
        item = require_mapping(raw, "discharge point")
        coordinates = require_list(item.get("coordinates"), "coordinates")
        if len(coordinates) != 2:
            raise ValueError("coordinates must contain latitude and longitude")
        max_flow = require_float(item, "max_flow_m3_s", minimum=0.01)
        min_flow = require_float(item, "min_flow_m3_s", minimum=0.0)
        if min_flow > max_flow:
            raise ValueError("min_flow_m3_s cannot exceed max_flow_m3_s")
        points.append(
            DischargePoint(
                point_id=require_str(item, "point_id"),
                coordinates=(float(coordinates[0]), float(coordinates[1])),
                discharge_temp_c=require_float(item, "discharge_temp_c", minimum=-2.0, maximum=80.0),
                max_flow_m3_s=max_flow,
                min_flow_m3_s=min_flow,
                diffuser_efficiency=require_float(item, "diffuser_efficiency", minimum=0.05, maximum=1.0),
                mixing_depth_m=require_float(item, "mixing_depth_m", minimum=1.0),
                habitat_distance_m=require_float(item, "habitat_distance_m", minimum=1.0),
                allowed_hours=int_list(item.get("allowed_hours"), "allowed_hours"),
                evidence=string_list(item.get("evidence"), "evidence"),
            )
        )
    return DischargeSpecs(
        site_id=require_str(root, "site_id"),
        facility_name=require_str(root, "facility_name"),
        baseline_temp_c=require_float(root, "baseline_temp_c", minimum=-2.0, maximum=40.0),
        points=points,
    )


def parse_forecast(data: Any) -> CurrentForecast:
    root = require_mapping(data, "current forecast")
    hours = []
    for raw in require_list(root.get("forecast_hours"), "forecast_hours"):
        item = require_mapping(raw, "forecast hour")
        hours.append(
            ForecastHour(
                hour=int(require_float(item, "hour", minimum=0, maximum=23)),
                current_speed_m_s=require_float(item, "current_speed_m_s", minimum=0.0),
                direction_deg=require_float(item, "direction_deg", minimum=0.0, maximum=359.999),
                ambient_temp_c=require_float(item, "ambient_temp_c", minimum=-2.0, maximum=40.0),
                tide_state=require_str(item, "tide_state").lower(),
                stratification_index=require_float(item, "stratification_index", minimum=0.0, maximum=1.0),
                storm_watch=optional_bool(item, "storm_watch", False),
            )
        )
    return CurrentForecast(forecast_id=require_str(root, "forecast_id"), forecast_hours=hours)


def parse_thresholds(data: Any) -> EcologyThresholds:
    root = require_mapping(data, "ecology thresholds")
    return EcologyThresholds(
        max_delta_c_at_boundary=require_float(root, "max_delta_c_at_boundary", minimum=0.1),
        protected_radius_m=require_float(root, "protected_radius_m", minimum=10.0),
        max_exposure_hours=require_float(root, "max_exposure_hours", minimum=0.25),
        recovery_window_hours=require_float(root, "recovery_window_hours", minimum=0.0),
        sensitive_species=string_list(root.get("sensitive_species"), "sensitive_species"),
        critical_habitat=optional_bool(root, "critical_habitat", False),
    )


def load_case(specs_path: str | Path, forecast_path: str | Path, thresholds_path: str | Path) -> tuple[DischargeSpecs, CurrentForecast, EcologyThresholds]:
    return parse_specs(read_json(specs_path)), parse_forecast(read_json(forecast_path)), parse_thresholds(read_json(thresholds_path))


def sample_case() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    specs = {
        "site_id": "MGT-BASIN-07",
        "facility_name": "Mariner Geothermal Test Basin",
        "baseline_temp_c": 8.4,
        "discharge_points": [
            {
                "point_id": "OUTFALL-A",
                "coordinates": [35.1271, 129.1432],
                "discharge_temp_c": 22.5,
                "max_flow_m3_s": 5.8,
                "min_flow_m3_s": 0.6,
                "diffuser_efficiency": 0.78,
                "mixing_depth_m": 34,
                "habitat_distance_m": 620,
                "allowed_hours": [1, 2, 3, 4, 12, 13, 14, 15],
                "evidence": ["diffuser survey 2026-05", "ROV habitat map"],
            },
            {
                "point_id": "OUTFALL-B",
                "coordinates": [35.1192, 129.151],
                "discharge_temp_c": 18.8,
                "max_flow_m3_s": 3.4,
                "min_flow_m3_s": 0.4,
                "diffuser_efficiency": 0.61,
                "mixing_depth_m": 19,
                "habitat_distance_m": 430,
                "allowed_hours": [3, 4, 5, 15, 16],
                "evidence": ["temperature probe array"],
            },
        ],
    }
    forecast = {
        "forecast_id": "KHOA-20260611T0600Z",
        "forecast_hours": [
            {"hour": 1, "current_speed_m_s": 0.42, "direction_deg": 81, "ambient_temp_c": 8.2, "tide_state": "ebb", "stratification_index": 0.24},
            {"hour": 3, "current_speed_m_s": 0.63, "direction_deg": 92, "ambient_temp_c": 8.1, "tide_state": "ebb", "stratification_index": 0.18},
            {"hour": 5, "current_speed_m_s": 0.21, "direction_deg": 144, "ambient_temp_c": 8.5, "tide_state": "slack", "stratification_index": 0.56},
            {"hour": 12, "current_speed_m_s": 0.51, "direction_deg": 260, "ambient_temp_c": 8.9, "tide_state": "flood", "stratification_index": 0.31},
            {"hour": 15, "current_speed_m_s": 0.36, "direction_deg": 245, "ambient_temp_c": 9.0, "tide_state": "flood", "stratification_index": 0.41},
            {"hour": 20, "current_speed_m_s": 0.18, "direction_deg": 201, "ambient_temp_c": 8.7, "tide_state": "slack", "stratification_index": 0.72, "storm_watch": True},
        ],
    }
    thresholds = {
        "max_delta_c_at_boundary": 1.1,
        "protected_radius_m": 500,
        "max_exposure_hours": 2.5,
        "recovery_window_hours": 4,
        "sensitive_species": ["eelgrass bed", "abalone nursery"],
        "critical_habitat": True,
    }
    return specs, forecast, thresholds

