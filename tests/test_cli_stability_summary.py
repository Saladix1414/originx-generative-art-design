import json

from oxgad.cli import main


def test_cli_stability_summary_reports_stable_surface(capsys):
    assert main(["stability"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output["project"] == "originx-generative-art-design"
    assert output["version"] == "0.41.0"
    assert output["read_only"] is True
    assert output["contract_count"] == output["evidence_chain_count"]
    assert output["fixture_count"] == 2
    assert output["command_count"] == len(output["commands"])
    assert "stability" in output["commands"]
    assert "readiness" in output["commands"]
    assert "version" in output["commands"]
