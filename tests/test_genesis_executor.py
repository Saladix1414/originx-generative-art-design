from pathlib import Path

from oxgad.genesis.batch import build_genesis_batch_plan
from oxgad.genesis.executor import png_evidence


def test_executor_commands_use_signed_seeds():
    plan = build_genesis_batch_plan()

    for token in plan["tokens"]:
        assert 0 <= token["seed"] <= 9223372036854775807


def test_executor_is_scoped_to_first_batch():
    plan = build_genesis_batch_plan()

    assert plan["batchId"] == "GENESIS-BATCH-0001"
    assert len(plan["tokens"]) == 10
    assert plan["executionPolicy"]["nextBatchAutomatic"] is False


def test_png_evidence_rejects_non_png(tmp_path: Path):
    path = tmp_path / "invalid.png"
    path.write_bytes(b"not-a-png")

    try:
        png_evidence(path)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid PNG was accepted.")
