import json

import pytest

from oxgad.cli import main


COMMANDS = [
    (
        ["schema", "tests/fixtures/cli/project-readiness-summary.json"],
        {"schema_version", "project", "phase"},
    ),
    (
        ["status", "tests/fixtures/cli/canonical-promotion.json"],
        {"status", "decision", "phase"},
    ),
    (
        [
            "validate-fixture",
            "tests/fixtures/cli/project-readiness-summary.json",
            "--schema",
            "schemas/ox-project-readiness-summary-1.schema.json",
        ],
        {"valid", "schema_version", "schema_id"},
    ),
    (
        ["validate-fixtures", "tests/fixtures/cli"],
        {"valid", "count", "results"},
    ),
    (
        ["contracts"],
        {"count", "contracts"},
    ),
    (
        ["validate-contracts"],
        {"valid", "count", "results"},
    ),
    (
        ["evidence-chain"],
        {"count", "chain"},
    ),
    (
        ["readiness"],
        {
            "ready",
            "contracts_valid",
            "fixtures_valid",
            "evidence_chain_complete",
        },
    ),
    (
        ["version"],
        {"project", "version"},
    ),
    (
        ["stability"],
        {
            "project",
            "version",
            "commands",
            "command_count",
            "read_only",
        },
    ),
]


@pytest.mark.parametrize(("argv", "keys"), COMMANDS)
def test_cli_commands_emit_json_objects(argv, keys, capsys):
    assert main(argv) == 0

    output = json.loads(capsys.readouterr().out)

    assert isinstance(output, dict)
    assert keys.issubset(output)
