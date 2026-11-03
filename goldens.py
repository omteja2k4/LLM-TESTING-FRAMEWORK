"""Read human-labeled regression cases from a JSON file."""

import json
from pathlib import Path
from .models import GoldenCase


def load_cases(path: str | Path) -> list[GoldenCase]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("Dataset must be a non-empty JSON list")

    cases = []
    seen = set()
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("Each golden case must be a JSON object")
        case = GoldenCase(**row)
        if not case.case_id.strip() or not case.question.strip():
            raise ValueError("Cases need non-empty case_id and question")
        if case.case_id in seen:
            raise ValueError(f"Duplicate case ID: {case.case_id}")
        if not case.context or any(not x.strip() for x in case.context):
            raise ValueError(f"Case {case.case_id} has empty evidence context")
        if case.max_latency_ms <= 0:
            raise ValueError("max_latency_ms must be positive")
        seen.add(case.case_id)
        cases.append(case)
    return cases
