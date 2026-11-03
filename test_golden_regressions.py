"""Reproducible baseline tests; all fixture responses are synthetic."""

from pathlib import Path
import pytest
from ai_quality.clients import FixtureClient
from ai_quality.goldens import load_cases
from ai_quality.runner import run_suite

ROOT = Path(__file__).resolve().parents[1]
CASES = load_cases(ROOT / "datasets/goldens.json")
FIXTURES = ROOT / "datasets/fixture_responses.json"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.case_id)
def test_fixture_goldens(case):
    result = run_suite([case], FixtureClient(FIXTURES))
    assert result["summary"]["failed_cases"] == 0, result["results"]


def test_report_has_summary_and_all_cases():
    report = run_suite(CASES, FixtureClient(FIXTURES))
    assert report["summary"]["total_cases"] == len(CASES)
    assert report["summary"]["passed_cases"] == len(CASES)
    assert len(report["results"]) == len(CASES)
    assert report["summary"]["p95_latency_ms"] is not None


def test_missing_fixture_is_reported_without_abort(tmp_path):
    fixture = tmp_path / "missing.json"
    fixture.write_text("{}", encoding="utf-8")
    report = run_suite(CASES[:2], FixtureClient(fixture))
    assert report["summary"]["failed_cases"] == 2
    assert all(result["error"] is not None for result in report["results"])
