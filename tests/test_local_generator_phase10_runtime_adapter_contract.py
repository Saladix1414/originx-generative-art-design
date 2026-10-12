import json
from pathlib import Path

import jsonschema

from oxgad.forge import (
    build_declared_runtime_adapter,
    runtime_adapter_hash,
    validate_runtime_adapter,
)


SCHEMA = Path("schemas/ox-runtime-adapter-1.schema.json")


def test_runtime_adapter_schema_is_valid_draft_2020_12():
    schema = json.loads(
        SCHEMA.read_text()
    )

    jsonschema.Draft202012Validator.check_schema(
        schema
    )


def test_runtime_adapter_is_declared_only_by_default():
    adapter = build_declared_runtime_adapter()

    assert adapter["adapterVersion"] == "OX-RUNTIME-ADAPTER-1"
    assert adapter["target"] == "LOCAL_CPP"
    assert adapter["runtime"]["family"] == "stable-diffusion.cpp"
    assert adapter["runtime"]["executablePath"] is None
    assert adapter["interfaceMode"] == "DECLARED_ONLY"

    assert adapter["capabilities"] == {
        "modelExecutionImplemented": False,
        "mediaGenerationImplemented": False,
        "commandConstructionImplemented": False,
    }

    assert adapter["governance"] == {
        "directInvocationAllowed": False,
        "backendInvocationAllowed": False,
        "requiresExecutionDecision": True,
        "requiresModelBinding": True,
        "requiresCandidateProvenance": True,
    }


def test_runtime_adapter_validates_against_schema():
    adapter = build_declared_runtime_adapter()

    assert validate_runtime_adapter(
        adapter
    ) == adapter


def test_runtime_adapter_rejects_invocation_authority():
    adapter = build_declared_runtime_adapter()
    adapter["governance"]["backendInvocationAllowed"] = True

    try:
        validate_runtime_adapter(
            adapter
        )
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Runtime adapter accepted backend invocation authority."
        )


def test_runtime_adapter_hash_is_stable():
    first = build_declared_runtime_adapter()
    second = build_declared_runtime_adapter()

    assert runtime_adapter_hash(first) == runtime_adapter_hash(second)
