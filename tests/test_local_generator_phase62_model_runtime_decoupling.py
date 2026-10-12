from oxgad.models.candidate import (
    MODEL_CANDIDATE_VERSION,
    build_model_candidate,
    validate_model_candidate,
)


def test_model_candidate_is_parametric():
    value = build_model_candidate(
        model_id="originx.test.candidate",
        name="OriginX Test Candidate",
        family="test-family",
        artifact_format="test-format",
        artifact_size_bytes=1024,
        artifact_sha256="sha256:" + ("a" * 64),
        runtime_family="ORIGINX_LOCAL_RUNTIME",
    )

    validate_model_candidate(value)

    assert value["candidateVersion"] == MODEL_CANDIDATE_VERSION
    assert value["modelId"] == "originx.test.candidate"
    assert value["runtimeCompatibility"]["runtimeFamily"] == (
        "ORIGINX_LOCAL_RUNTIME"
    )
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False
