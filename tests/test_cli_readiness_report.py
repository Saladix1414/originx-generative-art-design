import json

from oxgad.cli import main


def test_cli_readiness_report_is_ready_for_default_fixtures(capsys):
    assert main(["readiness"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["ready"] is True
    assert output["contracts_valid"] is True
    assert output["fixtures_valid"] is True
    assert output["evidence_chain_complete"] is True
    assert output["contract_count"] == output["evidence_chain_count"]


def test_cli_readiness_report_blocks_unknown_fixture(tmp_path, capsys):
    fixture = tmp_path / "unknown.json"
    fixture.write_text("{}", encoding="utf-8")

    assert main(["readiness", "--fixtures", str(tmp_path)]) == 2

    output = json.loads(capsys.readouterr().out)

    assert output["ready"] is False
    assert output["contracts_valid"] is True
    assert output["fixtures_valid"] is False
