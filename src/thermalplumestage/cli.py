"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .adapters import load_case, sample_case, write_json
from .planner import build_report
from .report import render_markdown


def _cmd_sample(args: argparse.Namespace) -> int:
    specs, forecast, thresholds = sample_case()
    write_json(args.discharge_output, specs)
    write_json(args.forecast_output, forecast)
    write_json(args.ecology_output, thresholds)
    print(f"wrote {args.discharge_output}")
    print(f"wrote {args.forecast_output}")
    print(f"wrote {args.ecology_output}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    specs, forecast, thresholds = load_case(args.discharge, args.forecast, args.ecology)
    report = build_report(specs, forecast, thresholds)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.markdown:
        output.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    else:
        write_json(output, report.to_dict() if args.full else report.compact_dict())
    print(f"wrote {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thermalplumestage")
    sub = parser.add_subparsers(dest="command", required=True)

    sample = sub.add_parser("sample", help="write sample discharge, forecast, and ecology inputs")
    sample.add_argument("-d", "--discharge-output", default="examples/discharge_specs.json")
    sample.add_argument("-f", "--forecast-output", default="examples/current_forecast.json")
    sample.add_argument("-e", "--ecology-output", default="examples/ecology_thresholds.json")
    sample.set_defaults(func=_cmd_sample)

    run = sub.add_parser("run", help="plan marine thermal-discharge dispersion")
    run.add_argument("-d", "--discharge", required=True, help="discharge specs JSON")
    run.add_argument("-f", "--forecast", required=True, help="current forecast JSON")
    run.add_argument("-e", "--ecology", required=True, help="ecology thresholds JSON")
    run.add_argument("-o", "--output", required=True)
    run.add_argument("--full", action="store_true", help="write full JSON")
    run.add_argument("--markdown", action="store_true", help="write Markdown")
    run.set_defaults(func=_cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))

