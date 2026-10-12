from oxgad.models.sd15_download_plan import (
    SD15_DOWNLOAD_APPROVAL_PHRASE,
    build_sd15_authorized_download_plan,
    validate_sd15_authorized_download_plan,
)


def test_sd15_download_plan_identity():
    value = build_sd15_authorized_download_plan()

    validate_sd15_authorized_download_plan(value)
    assert value["modelId"] == "OX-MODEL-002"
    assert value["selectedPath"] == "AUTHORIZED_DOWNLOAD"
    assert value["state"] == "PENDING_EXPLICIT_APPROVAL"


def test_sd15_download_artifact_is_exact():
    artifact = build_sd15_authorized_download_plan()[
        "artifact"
    ]

    assert artifact["expectedSizeBytes"] == 1566768416
    assert artifact["expectedSha256"] == (
        "sha256:"
        "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
        "fe0fa9af6c64c4829022261f"
    )
    assert artifact["quantization"] == "Q4_0"


def test_sd15_download_requires_exact_approval():
    value = build_sd15_authorized_download_plan()

    assert value["approval"]["required"] is True
    assert value["approval"]["present"] is False
    assert value["approval"]["requiredPhrase"] == (
        SD15_DOWNLOAD_APPROVAL_PHRASE
    )


def test_plan_grants_no_download_or_execution():
    value = build_sd15_authorized_download_plan()

    assert all(
        flag is False
        for flag in value["governance"].values()
    )


def test_download_does_not_authorize_benchmark():
    post = build_sd15_authorized_download_plan()[
        "postDownload"
    ]

    assert post["runtimeExecutionAllowed"] is False
    assert post["automaticBenchmarkAllowed"] is False
    assert post["singlePreflightApprovalRequired"] is True
