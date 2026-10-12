from oxgad.genesis.identity import (
    GENESIS_BATCH_ID,
    GENESIS_MAXIMUM_SUPPLY,
    build_genesis_batch_identities,
    build_genesis_identity,
)


def test_genesis_batch_identity():
    values = build_genesis_batch_identities()

    assert GENESIS_BATCH_ID == "GENESIS-BATCH-0001"
    assert GENESIS_MAXIMUM_SUPPLY == 1000
    assert len(values) == 10
    assert [item["tokenId"] for item in values] == list(
        range(1, 11)
    )
    assert [item["serial"] for item in values] == [
        f"#{value:04d}" for value in range(1, 11)
    ]


def test_genesis_identity_classification():
    value = build_genesis_identity(1)

    assert value["tier"] == "LEGENDARY"
    assert value["cohort"] == "GENESIS"
    assert value["era"] == "PRIMORDIAL ORIGIN"
    assert value["structureProfileEra"] == "Ascended Origin"
    assert value["generationTheme"] == (
        "Genesis / Primordial Origin"
    )


def test_names_dna_and_seeds_are_unique():
    values = build_genesis_batch_identities()

    assert len({item["canonicalName"] for item in values}) == 10
    assert len({item["dnaHash"] for item in values}) == 10
    assert len({item["seed"] for item in values}) == 10


def test_genesis_generation_is_deterministic():
    first = build_genesis_batch_identities()
    second = build_genesis_batch_identities()

    assert first == second


def test_model_binding_is_fixed():
    value = build_genesis_identity(1)["modelBinding"]

    assert value["modelId"] == "OX-MODEL-002"
    assert value["productionAlias"] == "OX-GENESIS-MODEL-1"
    assert value["modelHash"] == (
        "sha256:"
        "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
        "fe0fa9af6c64c4829022261f"
    )
