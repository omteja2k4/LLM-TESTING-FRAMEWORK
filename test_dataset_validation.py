import json
import pytest
from ai_quality.goldens import load_cases


def test_duplicate_ids_are_rejected(tmp_path):
    row = {"case_id": "x", "category": "factual", "question": "Q?", "context": ["Fact"]}
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([row, row]), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        load_cases(path)


def test_empty_context_is_rejected(tmp_path):
    row = {"case_id": "x", "category": "factual", "question": "Q?", "context": []}
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([row]), encoding="utf-8")
    with pytest.raises(ValueError, match="empty evidence"):
        load_cases(path)
