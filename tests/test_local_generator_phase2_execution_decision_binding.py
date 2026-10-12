import jsonschema

from oxgad.forge import (
    build_execution_decision,
    execution_decision_hash,
    validate_execution_decision,
)


def _forge_contract():
    return {
        "forgeVersion": "OX-LOCAL-FORGE-1",
        "source": {
            "renderPlanVersion": "OX-RENDER-1",
            "renderPlanHash": "sha256:" + "a" * 64,
        },
        "hardware": {
            "profileVersion": "OX-HARDWARE-PROFILE-1",
            "requestedTarget": "LOCAL_CPP",
            "capability": "UNKNOWN",
        },
        "model": {
            "bindingState": "UNBOUND",
        },
        "execution": {
            "policy": "LOCAL_FIRST",
            "mode": "PREPARE_ONLY",
            "authorizationState": "BLOCKED",
            "executionAllowed": False,
        },
        "output": {
            "mediaGenerationAllowed": False,
            "canonicalArtworkAllowed": False,
        },
    }


def test_execution_decision_denies_prepare_only_forge_contract():
    decision = build_execution_decision(
        _forge_contract()
    )

    assert decision["decision"] == "DENY"
    assert decision["backendInvocationAllowed"] is False
    assert decision["requestedTarget"] == "LOCAL_CPP"
    assert decision["capability"] == "UNKNOWN"

    assert decision["reasonCodes"] == [
        "AUTHORIZATION_BLOCKED",
        "CANONICAL_ARTWORK_NOT_ALLOWED",
        "EXECUTION_NOT_ALLOWED",
        "HARDWARE_CAPABILITY_NOT_CONFIRMED",
        "MEDIA_GENERATION_NOT_ALLOWED",
        "MODEL_UNBOUND",
    ]


def test_execution_decision_validates_against_schema():
    decision = build_execution_decision(
        _forge_contract()
    )

    assert validate_execution_decision(
        decision
    ) == decision


def test_execution_decision_hash_is_stable():
    first = build_execution_decision(
        _forge_contract()
    )
    second = build_execution_decision(
        _forge_contract()
    )

    assert execution_decision_hash(first) == execution_decision_hash(second)


def test_execution_decision_rejects_execution_allowance():
    decision = build_execution_decision(
        _forge_contract()
    )
    decision["backendInvocationAllowed"] = True

    try:
        validate_execution_decision(
            decision
        )
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Execution decision allowed backend invocation."
        )
