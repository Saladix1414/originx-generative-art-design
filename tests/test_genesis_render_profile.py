from oxgad.genesis.render_profile import (
    APPROVAL_PHRASE,
    build_interruption_evidence,
    build_render_profile_2,
    build_token_0001_profile_2_gate,
)


def test_profile_2_is_conservative_and_single_token():
    value = build_render_profile_2()

    assert value["scope"]["tokenIds"] == [1]
    assert value["scope"]["batchSize"] == 1
    assert value["render"]["width"] == 384
    assert value["render"]["height"] == 384
    assert value["render"]["steps"] == 10
    assert value["render"]["sampler"] == "dpm++2m"
    assert value["render"]["scheduler"] == "karras"


def test_profile_2_uses_lossless_rgb8_png():
    output = build_render_profile_2()["output"]

    assert output["format"] == "PNG"
    assert output["bitsPerChannel"] == 8
    assert output["lossless"] is True
    assert output["canonical"] is False


def test_profile_2_preserves_canonical_identity_records():
    preservation = build_render_profile_2()[
        "identityPreservation"
    ]

    assert all(preservation.values())


def test_interruption_is_not_a_token_failure():
    value = build_interruption_evidence()

    assert value["state"] == "INTERRUPTED_BY_USER"
    assert value["observation"]["candidateImageProduced"] is False
    assert value["classification"]["tokenFailure"] is False
    assert value["governance"]["nextBatchAllowed"] is False


def test_new_gate_is_only_for_token_0001():
    value = build_token_0001_profile_2_gate()

    assert value["tokenId"] == 1
    assert value["limits"]["tokens"] == 1
    assert value["approval"]["requiredPhrase"] == APPROVAL_PHRASE
    assert value["approval"]["present"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["nextTokenAllowed"] is False
