from oxgad.genesis.fp16_vae_retry import (
    APPROVAL_PHRASE,
    build_external_vae_preflight_review,
    build_fp16_vae_genesis_retry_plan,
)


def test_external_vae_preflight_is_technically_passed():
    value = build_external_vae_preflight_review()

    assert value["state"] == "PASSED_EXTERNAL_VAE_COMPATIBILITY"
    assert value["visualReview"]["verticalBandingAbsent"] is True
    assert value["visualReview"]["artisticQualityEvaluated"] is False
    assert value["diagnosis"]["embeddedQ4VaeDefectConfirmed"] is True


def test_retry_preserves_identity_and_generation_parameters():
    value = build_fp16_vae_genesis_retry_plan()
    preserved = value["preserved"]

    assert value["tokenId"] == 1
    assert preserved["identityUnchanged"] is True
    assert preserved["dnaUnchanged"] is True
    assert preserved["runtimeSeed"] == 5770080363699867898
    assert preserved["width"] == 384
    assert preserved["height"] == 384
    assert preserved["steps"] == 10
    assert preserved["sampler"] == "dpm++2m"
    assert preserved["scheduler"] == "karras"


def test_retry_binds_verified_external_fp16_vae():
    binding = build_fp16_vae_genesis_retry_plan()[
        "externalVaeBinding"
    ]

    assert binding["precision"] == "FP16"
    assert binding["decodeMode"] == "NON_TILED"
    assert binding["sha256"] == (
        "sha256:"
        "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
        "29bb4d81890039d2aa16dd7c"
    )


def test_retry_requires_new_exact_approval():
    value = build_fp16_vae_genesis_retry_plan()

    assert value["approval"]["requiredPhrase"] == APPROVAL_PHRASE
    assert value["approval"]["present"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["nextTokenAllowed"] is False
