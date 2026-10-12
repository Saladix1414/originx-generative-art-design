from oxgad.forge.sd15_runtime_preflight_plan import (
    SD15_RUNTIME_PREFLIGHT_APPROVAL_PHRASE,
    build_sd15_runtime_preflight_plan,
    validate_sd15_runtime_preflight_plan,
)


def test_sd15_preflight_is_small_and_conservative():
    value = build_sd15_runtime_preflight_plan()
    request = value["request"]

    validate_sd15_runtime_preflight_plan(value)
    assert request["width"] == 256
    assert request["height"] == 256
    assert request["steps"] == 1
    assert request["batchSize"] == 1
    assert request["threads"] == 4
    assert request["paramsBackend"] == "disk"
    assert request["mmap"] is True
    assert request["vaeTiling"] is True


def test_sd15_preflight_requires_exact_approval():
    value = build_sd15_runtime_preflight_plan()

    assert value["approval"]["present"] is False
    assert value["approval"]["requiredPhrase"] == (
        SD15_RUNTIME_PREFLIGHT_APPROVAL_PHRASE
    )


def test_preflight_is_not_token_benchmark():
    value = build_sd15_runtime_preflight_plan()

    assert value["purpose"] == "SINGLE_RUNTIME_PREFLIGHT"
    assert value["governance"][
        "benchmarkTokensAllowed"
    ] is False


def test_preflight_plan_grants_no_execution():
    value = build_sd15_runtime_preflight_plan()

    assert all(
        flag is False
        for flag in value["governance"].values()
    )
