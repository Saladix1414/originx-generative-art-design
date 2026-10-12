from oxgad.models.production_candidate import (
    build_z_image_production_candidate,
    validate_production_model_candidate,
)


def test_z_image_candidate_is_pending_gate():
    value = build_z_image_production_candidate()
    validate_production_model_candidate(value)

    assert value["modelId"] == "OX-MODEL-001"
    assert value["productionAlias"] == "OX-GENESIS-MODEL-1"
    assert value["format"] == "GGUF"
    assert value["quantization"] == "Q4_0"
    assert value["license"] == "Apache-2.0"
    assert value["selectionState"] == (
        "CANDIDATE_PENDING_10_TOKEN_GATE"
    )
    assert value["benchmarkGate"]["requiredTokens"] == 10
    assert value["benchmarkGate"]["passed"] is False
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["canonicalizationAllowed"] is False
