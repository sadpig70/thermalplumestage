"""Data models for marine thermal-discharge planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BOUNDARY = {
    "source_round": "SA-EVX-20260611-001",
    "source_artifact": ".sa-evx/rounds/SA-EVX-20260611-001/final_integrated_idea.md",
    "source_candidate": "ThermalPlume Stage",
    "cross_model_certified": False,
    "production_promotion_required": True,
}


@dataclass(frozen=True)
class DischargePoint:
    point_id: str
    coordinates: tuple[float, float]
    discharge_temp_c: float
    max_flow_m3_s: float
    min_flow_m3_s: float
    diffuser_efficiency: float
    mixing_depth_m: float
    habitat_distance_m: float
    allowed_hours: list[int] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DischargeSpecs:
    site_id: str
    facility_name: str
    baseline_temp_c: float
    points: list[DischargePoint]


@dataclass(frozen=True)
class ForecastHour:
    hour: int
    current_speed_m_s: float
    direction_deg: float
    ambient_temp_c: float
    tide_state: str
    stratification_index: float
    storm_watch: bool = False


@dataclass(frozen=True)
class CurrentForecast:
    forecast_id: str
    forecast_hours: list[ForecastHour]


@dataclass(frozen=True)
class EcologyThresholds:
    max_delta_c_at_boundary: float
    protected_radius_m: float
    max_exposure_hours: float
    recovery_window_hours: float
    sensitive_species: list[str]
    critical_habitat: bool = False


@dataclass(frozen=True)
class ValveWindow:
    point_id: str
    hour: int
    recommended_flow_m3_s: float
    valve_fraction: float
    boundary_delta_c: float
    dilution_radius_m: float
    exposure_credit_hours: float
    status: str
    rationale: list[str]
    evidence_gaps: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "point_id": self.point_id,
            "hour": self.hour,
            "recommended_flow_m3_s": round(self.recommended_flow_m3_s, 4),
            "valve_fraction": round(self.valve_fraction, 4),
            "boundary_delta_c": round(self.boundary_delta_c, 4),
            "dilution_radius_m": round(self.dilution_radius_m, 2),
            "exposure_credit_hours": round(self.exposure_credit_hours, 3),
            "status": self.status,
            "rationale": self.rationale,
            "evidence_gaps": self.evidence_gaps,
        }


@dataclass(frozen=True)
class ThermalReport:
    site_id: str
    facility_name: str
    forecast_id: str
    windows: list[ValveWindow]
    summary: dict[str, Any]
    boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "site_id": self.site_id,
            "facility_name": self.facility_name,
            "forecast_id": self.forecast_id,
            "summary": self.summary,
            "windows": [item.to_dict() for item in self.windows],
            "boundary": self.boundary,
        }

    def compact_dict(self) -> dict[str, Any]:
        return {
            "site_id": self.site_id,
            "forecast_id": self.forecast_id,
            "overall_status": self.summary["overall_status"],
            "best_release_hours": self.summary["best_release_hours"],
            "halt_windows": self.summary["halt_windows"],
            "max_boundary_delta_c": self.summary["max_boundary_delta_c"],
            "cross_model_certified": self.boundary["cross_model_certified"],
            "production_promotion_required": self.boundary["production_promotion_required"],
        }

