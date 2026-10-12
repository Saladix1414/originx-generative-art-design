import jsonschema
import pytest

from oxgad.models.model_operational_status import (
    MODEL_OPERATIONAL_STATUS_VERSION,
    build_z_image_reference_model_status,
    validate_model_operational_status,
)


def test_z_image_is_benchmarked_reference():
    value = build_z_image_reference_model_status()

    assert value["statusVersion"] == (
        MODEL_OPERATIONAL_STATUS_VERSION
    )
    assert value["modelId"] == "OX-MODEL-001"
    assert value["role"] == "REFERENCE_MODEL"
    assert value["status"] == "BENCHMARKED"
    assert value["localProductionStatus"] == (
        "NOT_SUITABLE_ON_CURRENT_DEVICE"
    )


def test_historical_registration_is_preserved():
    value = build_z_image_reference_model_status()
    historical = value["historicalRegistration"]

    assert historical["previousRole"] == (
        "PRIMARY_LOCAL_BASE_MODEL"
    )
    assert historical["previousProductionAlias"] == (
        "OX-GENESIS-MODEL-1"
    )
    assert historical["preserved"] is True


def test_artifacts_and_provenance_are_preserved():
    value = build_z_image_reference_model_status()

    assert value["artifacts"]["preserved"] is True
    assert value["artifacts"]["deletionAllowed"] is False
    assert all(value["provenance"].values())


def test_status_grants_no_runtime_authority():
    value = build_z_image_reference_model_status()

    assert all(
        flag is False
        for flag in value["governance"].values()
    )


def test_primary_role_is_rejected():
    value = build_z_image_reference_model_status()
    value["role"] = "PRIMARY_LOCAL_BASE_MODEL"

    with pytest.raises(jsonschema.ValidationError):
        validate_model_operational_status(value)
