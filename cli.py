"""Command-line interface for local runs and GitHub Actions."""

import argparse
import json
from pathlib import Path
from .clients import FixtureClient, GeminiClient
from .goldens import load_cases
from .runner import run_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate golden AI QA cases")
    parser.add_argument("--provider", choices=["fixture", "gemini"], default="fixture")
    parser.add_argument("--dataset", default="datasets/goldens.json")
    parser.add_argument("--fixtures", default="datasets/fixture_responses.json")
    parser.add_argument("--output", default="reports/evaluation.json")
    args = parser.parse_args()

    cases = load_cases(args.dataset)
    client = FixtureClient(args.fixtures) if args.provider == "fixture" else GeminiClient()
    report = run_suite(cases, client)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Provider: {args.provider}")
    print(f"Cases: {report['summary']['passed_cases']}/{report['summary']['total_cases']} passed")
    print(f"Report: {output}")
    return 0 if report["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
