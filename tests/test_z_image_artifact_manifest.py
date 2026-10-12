from oxgad.models.z_image_artifacts import (
    build_z_image_artifact_manifest,
)


def test_z_image_artifacts_are_expected_but_not_observed():
    value = build_z_image_artifact_manifest()

    assert value["modelId"] == "OX-MODEL-001"
    assert value["state"] == "EXPECTED_NOT_OBSERVED"
    assert len(value["artifacts"]) == 3
    assert value["totalExpectedSizeBytes"] == 6348318966
    assert all(not item["observed"] for item in value["artifacts"])
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False


def test_qwen_is_only_a_text_encoder_dependency():
    value = build_z_image_artifact_manifest()
    qwen = value["artifacts"][1]

    assert qwen["role"] == "TEXT_ENCODER_DEPENDENCY"
    assert value["modelId"] == "OX-MODEL-001"
