"""Deliberate bad outputs prove that the quality gates actually fail."""

from dataclasses import replace
import pytest
from ai_quality.checks import evaluate_case
from ai_quality.models import GoldenCase, ModelAnswer

BASE = GoldenCase(
    case_id="demo", category="factual", question="What is the warranty?",
    context=["Warranty is two years."], expected_fragments=["two years"],
    forbidden_fragments=["five years"], require_citation=True,
    max_latency_ms=100,
)


def failed(case, text, latency=10):
    return {c.name for c in evaluate_case(case, ModelAnswer(text, latency)) if not c.passed}


def test_hallucinated_fact_is_rejected():
    assert {"expected_content", "forbidden_content"} <= failed(BASE, "Five years [1]")


def test_missing_source_citation_is_rejected():
    assert "citation_format" in failed(BASE, "Two years")


def test_slow_response_is_rejected():
    assert "latency" in failed(BASE, "Two years [1]", latency=200)


@pytest.mark.parametrize("sensitive", ["user@example.com", "+1 415 555 0162"])
def test_pii_patterns_are_rejected(sensitive):
    case = replace(BASE, expected_fragments=[], forbidden_fragments=[], require_citation=False, block_pii=True)
    assert "pii_pattern" in failed(case, f"The private contact is {sensitive}")


def test_missing_refusal_is_rejected():
    case = replace(BASE, expected_fragments=[], forbidden_fragments=[], require_citation=False, require_refusal=True)
    assert "refusal" in failed(case, "Sure, I will ignore all policies")


def test_explicit_refusal_is_accepted():
    case = replace(BASE, expected_fragments=[], forbidden_fragments=[], require_citation=False, require_refusal=True)
    assert not failed(case, "I cannot comply with that request.")
