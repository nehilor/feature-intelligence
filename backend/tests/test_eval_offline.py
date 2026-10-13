import json

import pytest
from evals.runners.offline import run_offline_evaluation
from evals.schemas.datasets import RelationshipDataset


def test_offline_eval_passes_with_frozen_fixtures() -> None:
    result = run_offline_evaluation()
    assert result.passed is True
    assert result.relationship["accuracy"] == 1.0
    assert result.relationship["macro_f1"] == 1.0
    assert result.theme["accuracy"] == 1.0
    assert result.structured_output["success_rate"] == 1.0


def test_invalid_dataset_fails_validation(tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"dataset_version": "x", "cases": []}), encoding="utf-8")
    with pytest.raises(Exception):
        RelationshipDataset.model_validate(json.loads(bad.read_text()))
