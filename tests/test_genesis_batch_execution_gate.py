from oxgad.genesis.execution_gate import (
    GENESIS_BATCH_EXECUTION_APPROVAL_PHRASE,
    build_genesis_batch_execution_gate,
    validate_genesis_batch_execution_gate,
)


def test_gate_is_scoped_to_first_batch():
    value = build_genesis_batch_execution_gate()

    validate_genesis_batch_execution_gate(value)
    assert value["batchId"] == "GENESIS-BATCH-0001"
    assert value["range"] == "#0001-#0010"
    assert value["limits"]["tokens"] == 10
    assert value["limits"]["batchSize"] == 1


def test_gate_requires_exact_phrase():
    value = build_genesis_batch_execution_gate()

    assert value["approval"]["requiredPhrase"] == (
        GENESIS_BATCH_EXECUTION_APPROVAL_PHRASE
    )
    assert value["approval"]["present"] is False


def test_gate_stops_on_failure_and_thermal_limit():
    conditions = build_genesis_batch_execution_gate()[
        "stopConditions"
    ]

    assert "TOKEN_FAILURE" in conditions
    assert "THERMAL_LIMIT" in conditions
    assert "DEVICE_RESTART" in conditions


def test_gate_grants_no_authority_by_itself():
    governance = build_genesis_batch_execution_gate()[
        "governance"
    ]

    assert all(flag is False for flag in governance.values())
