import jsonschema
import pytest

from oxgad.models.sd15_production_candidate import (
    build_sd15_production_candidate,
    validate_sd15_production_candidate,
)


def test_sd15_candidate_identity_and_role():
    value = build_sd15_production_candidate()

    assert value["modelId"] == "OX-MODEL-002"
    assert value["modelName"] == "Stable Diffusion 1.5"
    assert value["quantization"] == "Q4_0"
    assert value["role"] == "PRIMARY_LOCAL_BASE_MODEL"
    assert value["productionAlias"] == "OX-GENESIS-MODEL-1"
    assert value["status"] == (
        "CANDIDATE_FOR_FINAL_LOCAL_PRODUCTION"
    )


def test_sd15_artifact_is_content_bound():
    artifact = build_sd15_production_candidate()["artifact"]

    assert artifact["format"] == "GGUF"
    assert artifact["expectedSizeBytes"] == 1566768416
    assert artifact["expectedSha256"] == (
        "sha256:"
        "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
        "fe0fa9af6c64c4829022261f"
    )


def test_sd15_license_is_recorded_exactly():
    source = build_sd15_production_candidate()["source"]

    assert source["license"] == "CreativeML OpenRAIL-M"
    assert source["gated"] is False


def test_sd15_artistic_identity_remains_originx():
    authority = build_sd15_production_candidate()[
        "artisticAuthority"
    ]

    assert authority["baseModelDefinesIdentity"] is False
    assert "OriginX Art Grammar" in authority["governedBy"]
    assert "Quality Engine" in authority["governedBy"]


def test_candidate_grants_no_download_or_execution():
    value = build_sd15_production_candidate()

    assert value["download"]["approvalPresent"] is False
    assert all(
        flag is False
        for flag in value["governance"].values()
    )


def test_candidate_cannot_be_declared_final():
    value = build_sd15_production_candidate()
    value["status"] = "FINAL_LOCAL_PRODUCTION_MODEL"

    with pytest.raises(jsonschema.ValidationError):
        validate_sd15_production_candidate(value)
