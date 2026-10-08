import json

from oxgad.cli import main


def _run(argv, capsys):
    assert main(argv) == 0
    return json.loads(capsys.readouterr().out)


def test_release_recheck_version_and_stability(capsys):
    version = _run(["version"], capsys)

    assert version == {
        "project": "originx-generative-art-design",
        "version": "0.41.0",
    }

    stability = _run(["stability"], capsys)

    assert stability["version"] == "0.41.0"
    assert stability["read_only"] is True
    assert stability["contract_count"] == stability["evidence_chain_count"]


def test_release_recheck_contracts_fixtures_and_readiness(capsys):
    contracts = _run(["validate-contracts"], capsys)

    assert contracts["valid"] is True
    assert contracts["count"] >= 13

    fixtures = _run(["validate-fixtures", "tests/fixtures/cli"], capsys)

    assert fixtures["valid"] is True
    assert fixtures["count"] == 2

    readiness = _run(["readiness"], capsys)

    assert readiness["ready"] is True
    assert readiness["contracts_valid"] is True
    assert readiness["fixtures_valid"] is True
    assert readiness["evidence_chain_complete"] is True


def test_release_recheck_evidence_chain_matches_contracts(capsys):
    contracts = _run(["contracts"], capsys)
    chain = _run(["evidence-chain"], capsys)

    contract_schema_ids = {
        contract["schema_id"]
        for contract in contracts["contracts"]
    }

    assert chain["count"] == len(contract_schema_ids)

    for item in chain["chain"]:
        assert item["schema"] in contract_schema_ids
