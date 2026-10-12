import json
from pathlib import Path

import jsonschema

from oxgad.forge import (
    build_declared_runtime_adapter,
    build_declared_runtime_command_plan,
    runtime_command_plan_hash,
    validate_runtime_command_plan,
)


SCHEMA = Path("schemas/ox-runtime-command-plan-1.schema.json")


def _plan():
    adapter = build_declared_runtime_adapter()

    return build_declared_runtime_command_plan(
        adapter
    )


def test_runtime_command_plan_schema_is_valid_draft_2020_12():
    schema = json.loads(
        SCHEMA.read_text()
    )

    jsonschema.Draft202012Validator.check_schema(
        schema
    )


def test_runtime_command_plan_is_not_executable():
    plan = _plan()

    assert plan["commandPlanVersion"] == "OX-RUNTIME-COMMAND-PLAN-1"
    assert plan["state"] == "DECLARED_NOT_EXECUTABLE"
    assert plan["command"] == {
        "executable": None,
        "argv": [],
        "cwd": None,
        "environment": {},
    }
    assert plan["governance"] == {
        "commandConstructionImplemented": False,
        "backendInvocationAllowed": False,
        "shellAllowed": False,
        "networkAllowed": False,
        "modelExecutionAllowed": False,
    }


def test_runtime_command_plan_validates_against_schema():
    plan = _plan()

    assert validate_runtime_command_plan(
        plan
    ) == plan


def test_runtime_command_plan_rejects_argv():
    plan = _plan()
    plan["command"]["argv"] = ["--prompt", "dragon"]

    try:
        validate_runtime_command_plan(
            plan
        )
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError(
            "Runtime command plan accepted argv."
        )


def test_runtime_command_plan_hash_is_stable():
    first = _plan()
    second = _plan()

    assert runtime_command_plan_hash(first) == runtime_command_plan_hash(second)
