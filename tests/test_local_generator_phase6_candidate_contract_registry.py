import json

from oxgad.cli import main


EXPECTED = {
    "candidate-output": "schemas/ox-candidate-output-1.schema.json",
    "candidate-manifest": "schemas/ox-candidate-manifest-1.schema.json",
    "candidate-provenance": "schemas/ox-candidate-provenance-hook-1.schema.json",
}


def test_candidate_contracts_are_registered(capsys):
    assert main(["contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    contracts = {
        item["name"]: item["path"]
        for item in output["contracts"]
    }

    for name, path in EXPECTED.items():
        assert contracts[name] == path


def test_candidate_contracts_validate(capsys):
    assert main(["validate-contracts"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["valid"] is True

    results = {
        item["name"]: item["valid"]
        for item in output["results"]
    }

    for name in EXPECTED:
        assert results[name] is True


def test_candidate_contracts_are_in_evidence_chain(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    steps = {
        item["step"]: item["schema"]
        for item in output["chain"]
    }

    assert steps["candidate-output"] == "ox-candidate-output-1.schema.json"
    assert steps["candidate-manifest"] == "ox-candidate-manifest-1.schema.json"
    assert (
        steps["candidate-provenance"]
        == "ox-candidate-provenance-hook-1.schema.json"
    )


def test_readiness_includes_candidate_contracts(capsys):
    assert main(["readiness"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["ready"] is True
    assert output["contract_count"] == output["evidence_chain_count"]
