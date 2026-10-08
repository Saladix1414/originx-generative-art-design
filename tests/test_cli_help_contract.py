import pytest

from oxgad.cli import build_parser


COMMANDS = {
    "schema",
    "status",
    "validate-fixture",
    "validate-fixtures",
    "contracts",
    "validate-contracts",
    "evidence-chain",
    "readiness",
    "version",
    "stability",
    "prompt-inspect",
    "prompt-validate",
}


def _command_names():
    parser = build_parser()

    for action in parser._actions:
        choices = getattr(action, "choices", None)

        if choices:
            return set(choices)

    return set()


def test_cli_help_contract_exposes_expected_commands():
    assert _command_names() == COMMANDS


@pytest.mark.parametrize("command", sorted(COMMANDS))
def test_cli_help_contract_each_command_has_help(command, capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as raised:
        parser.parse_args([command, "--help"])

    assert raised.value.code == 0

    output = capsys.readouterr().out

    assert "usage:" in output
    assert command in output
