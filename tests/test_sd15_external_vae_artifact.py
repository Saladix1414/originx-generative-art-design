from oxgad.models.sd15_external_vae_artifact import (
    load_external_vae_artifact,
    validate_external_vae_artifact,
)


def test_external_vae_receipt_is_valid():
    value = load_external_vae_artifact()
    validate_external_vae_artifact(value)

    assert value["modelId"] == "OX-MODEL-002"
    assert value["componentId"] == "OX-MODEL-002-VAE-FP16-1"
    assert value["state"] == "ACQUIRED_AND_VERIFIED"
    assert value["artifact"]["sizeBytes"] == 167335342
    assert value["artifact"]["sha256"] == (
        "sha256:"
        "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
        "29bb4d81890039d2aa16dd7c"
    )


def test_acquisition_grants_no_execution():
    governance = load_external_vae_artifact()["governance"]

    assert governance["downloadCompleted"] is True
    assert governance["executionAllowed"] is False
    assert governance["preflightRequired"] is True
    assert governance["genesisRetryAllowed"] is False
    assert governance["nextTokenAllowed"] is False
