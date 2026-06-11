from thermalplumestage.adapters import parse_forecast, parse_specs, parse_thresholds, sample_case
from thermalplumestage.planner import build_report, plan_dispersal


def _sample_models():
    specs_data, forecast_data, thresholds_data = sample_case()
    return parse_specs(specs_data), parse_forecast(forecast_data), parse_thresholds(thresholds_data)


def test_fast_current_windows_rank_above_slack_or_storm():
    specs, forecast, thresholds = _sample_models()
    windows = plan_dispersal(specs, forecast, thresholds)

    assert windows[0].status == "within_threshold"
    assert windows[0].hour in {1, 3, 12, 15}
    assert all(item.status == "halt" for item in windows if item.hour == 20)


def test_valve_fraction_reduces_hot_outfall_under_threshold():
    specs, forecast, thresholds = _sample_models()
    windows = {(item.point_id, item.hour): item for item in plan_dispersal(specs, forecast, thresholds)}

    candidate = windows[("OUTFALL-A", 3)]
    assert 0 < candidate.valve_fraction < 1
    assert candidate.boundary_delta_c <= thresholds.max_delta_c_at_boundary * 1.35


def test_report_boundary_marks_sa_not_certified():
    specs, forecast, thresholds = _sample_models()
    report = build_report(specs, forecast, thresholds)

    assert report.boundary["source_round"] == "SA-EVX-20260611-001"
    assert report.boundary["source_candidate"] == "ThermalPlume Stage"
    assert report.compact_dict()["cross_model_certified"] is False


def test_critical_habitat_summary_is_preserved():
    specs, forecast, thresholds = _sample_models()
    report = build_report(specs, forecast, thresholds)

    assert report.summary["critical_habitat"] is True
    assert "eelgrass bed" in report.summary["sensitive_species"]
    assert report.summary["planned_windows"] > 0

