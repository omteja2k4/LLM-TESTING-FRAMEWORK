"""Fast, deterministic *regression* checks (not semantic faithfulness metrics)."""

import re
from .models import CheckResult, GoldenCase, ModelAnswer

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
REFUSAL = re.compile(
    r"\b(?:can't|cannot|won't|unable|not able|don't have enough|do not have enough)\b",
    re.IGNORECASE,
)
CITATION = re.compile(r"\[\d+\]")


def evaluate_case(case: GoldenCase, answer: ModelAnswer) -> list[CheckResult]:
    """Evaluate explicit golden expectations; use DeepEval for semantic judgments."""
    text = answer.text.casefold()
    checks = []

    for expected in case.expected_fragments:
        matched = expected.casefold() in text
        checks.append(CheckResult("expected_content", matched, f"Expected: {expected!r}"))

    for forbidden in case.forbidden_fragments:
        safe = forbidden.casefold() not in text
        checks.append(CheckResult("forbidden_content", safe, f"Forbidden: {forbidden!r}"))

    if case.require_refusal:
        checks.append(CheckResult("refusal", bool(REFUSAL.search(answer.text)), "Explicit refusal required"))

    if case.require_citation:
        valid = bool(CITATION.search(answer.text))
        checks.append(CheckResult("citation_format", valid, "A numbered citation such as [1] required"))

    if case.block_pii:
        safe = not EMAIL.search(answer.text) and not PHONE.search(answer.text)
        checks.append(CheckResult("pii_pattern", safe, "No email address or phone number in output"))

    checks.append(
        CheckResult("latency", answer.latency_ms <= case.max_latency_ms,
                    f"{answer.latency_ms:.1f} ms vs {case.max_latency_ms:.0f} ms budget")
    )
    return checks
