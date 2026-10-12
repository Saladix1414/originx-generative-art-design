from oxgad.models.sd15_external_vae_plan import (
    APPROVAL_PHRASE,
    build_external_vae_download_plan,
    validate_external_vae_download_plan,
)


def test_external_vae_plan_matches_schema():
    value = build_external_vae_download_plan()
    validate_external_vae_download_plan(value)


def test_selects_official_small_fp16_vae():
    value = build_external_vae_download_plan()

    assert value["modelId"] == "OX-MODEL-002"
    assert value["componentId"] == "OX-MODEL-002-VAE-FP16-1"
    assert value["artifact"]["precision"] == "FP16"
    assert value["artifact"]["expectedSizeBytes"] == 167335342
    assert value["artifact"]["expectedSha256"] == (
        "sha256:"
        "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
        "29bb4d81890039d2aa16dd7c"
    )


def test_external_vae_requires_explicit_approval():
    value = build_external_vae_download_plan()

    assert value["approval"]["requiredPhrase"] == APPROVAL_PHRASE
    assert value["approval"]["present"] is False
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False


def test_preflight_and_retry_are_separate_gates():
    value = build_external_vae_download_plan()

    assert value["postDownload"]["singlePreflightRequired"] is True
    assert (
        value["postDownload"][
            "genesisRetryRequiresSeparateApproval"
        ]
        is True
    )
    assert value["governance"]["nextTokenAllowed"] is False
