import json

from oxgad.cli import main


def test_readiness_reports_master_prompt_chain_ready(capsys):
    assert main(["readiness"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["ready"] is True
    assert output["master_prompt_chain_ready"] is True
    assert output["contract_count"] == output["evidence_chain_count"]


def test_stability_reports_master_prompt_chain_ready(capsys):
    assert main(["stability"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["read_only"] is True
    assert output["master_prompt_chain_ready"] is True
    assert output["contract_count"] == output["evidence_chain_count"]


def test_evidence_chain_contains_master_prompt_chain(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["chain"][-1] == {
        "schema": "ox-master-prompt-evidence-chain-1.schema.json",
        "step": "master-prompt-chain",
    }
