from oxgad.genesis.technical_retry import (
    RETRY_APPROVAL_PHRASE,
    build_candidate_rejection,
    build_technical_retry_plan,
)


def test_candidate_is_rejected_for_critical_artifacts():
    value = build_candidate_rejection()

    assert value["state"] == "REJECTED_TECHNICAL_ARTIFACT"
    assert value["evidence"]["verticalBandingCritical"] is True
    assert value["decision"]["qualityGatePassed"] is False
    assert value["decision"]["canonicalApproved"] is False
    assert value["decision"]["upscaleAllowed"] is False


def test_rejection_does_not_fail_identity():
    preservation = build_candidate_rejection()[
        "identityPreservation"
    ]

    assert preservation["tokenIdentityFailed"] is False
    assert preservation["identityUnchanged"] is True
    assert preservation["dnaUnchanged"] is True
    assert preservation["resonanceUnchanged"] is True
    assert preservation["glyphUnchanged"] is True
    assert preservation["artSpecUnchanged"] is True
    assert preservation["seedUnchanged"] is True


def test_retry_changes_only_vae_decode_mode():
    value = build_technical_retry_plan()

    assert value["tokenId"] == 1
    assert value["classification"]["creativeReroll"] is False
    assert value["classification"]["modelSubstitution"] is False
    assert value["singleChange"]["retryMode"] == "NON_TILED"
    assert value["preserved"]["runtimeSeed"] == 5770080363699867898


def test_retry_requires_new_exact_approval():
    value = build_technical_retry_plan()

    assert value["approval"]["requiredPhrase"] == (
        RETRY_APPROVAL_PHRASE
    )
    assert value["approval"]["present"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["nextTokenAllowed"] is False
