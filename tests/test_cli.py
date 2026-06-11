import json

from thermalplumestage.cli import main


def test_cli_sample_and_run_json(tmp_path):
    specs = tmp_path / "discharge_specs.json"
    forecast = tmp_path / "current_forecast.json"
    ecology = tmp_path / "ecology_thresholds.json"
    output = tmp_path / "report.json"

    assert main(["sample", "-d", str(specs), "-f", str(forecast), "-e", str(ecology)]) == 0
    assert main(["run", "-d", str(specs), "-f", str(forecast), "-e", str(ecology), "--full", "-o", str(output)]) == 0

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["boundary"]["cross_model_certified"] is False
    assert data["summary"]["overall_status"] in {"stage_release", "mitigate_before_release", "halt_release"}
    assert data["windows"]


def test_cli_markdown_contains_threshold_table(tmp_path):
    specs = tmp_path / "discharge_specs.json"
    forecast = tmp_path / "current_forecast.json"
    ecology = tmp_path / "ecology_thresholds.json"
    output = tmp_path / "report.md"

    main(["sample", "-d", str(specs), "-f", str(forecast), "-e", str(ecology)])
    assert main(["run", "-d", str(specs), "-f", str(forecast), "-e", str(ecology), "--markdown", "-o", str(output)]) == 0

    text = output.read_text(encoding="utf-8")
    assert "Valve Timing and Dilution Schedule" in text
    assert "cross_model_certified=false" in text

