from pathlib import Path

from oxgad.genesis.batch import (
    build_genesis_batch_plan,
    validate_genesis_batch_plan,
    write_genesis_batch_contracts,
)


def test_batch_plan_has_exactly_ten_sequential_tokens():
    value = build_genesis_batch_plan()

    validate_genesis_batch_plan(value)
    assert value["batchId"] == "GENESIS-BATCH-0001"
    assert [item["tokenId"] for item in value["tokens"]] == (
        list(range(1, 11))
    )


def test_batch_is_prepare_only_and_sequential():
    value = build_genesis_batch_plan()
    policy = value["executionPolicy"]

    assert policy["mode"] == "SEQUENTIAL"
    assert policy["batchSize"] == 1
    assert policy["stopOnFailure"] is True
    assert policy["nextBatchAutomatic"] is False
    assert policy["executionAllowed"] is False
    assert all(
        item["state"] == "PREPARED_NOT_EXECUTED"
        for item in value["tokens"]
    )


def test_prompts_and_candidate_paths_are_unique():
    tokens = build_genesis_batch_plan()["tokens"]

    assert len({item["positivePrompt"] for item in tokens}) == 10
    assert len({item["candidatePath"] for item in tokens}) == 10
    assert all(item["canonical"] is False for item in tokens)


def test_model_hash_is_fixed():
    value = build_genesis_batch_plan()

    assert value["model"]["modelHash"] == (
        "sha256:"
        "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
        "fe0fa9af6c64c4829022261f"
    )


def test_contract_writer(tmp_path: Path):
    plan = write_genesis_batch_contracts(tmp_path)

    assert (tmp_path / "batch-plan.json").is_file()
    assert plan["tokensRequested"] == 10

    for token_id in range(1, 11):
        root = (
            tmp_path
            / f"token-{token_id:04d}"
            / "contracts"
        )
        assert (root / "identity.json").is_file()
        assert (root / "lore.json").is_file()
        assert (root / "art-spec.json").is_file()
        assert (root / "render-plan.json").is_file()
        assert (root / "runtime-binding.json").is_file()
