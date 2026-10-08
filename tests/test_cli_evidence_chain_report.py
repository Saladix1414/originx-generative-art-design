import json

from oxgad.cli import main


EXPECTED_STEPS = [
    "provenance",
    "quality",
    "promotion",
    "canonical-ledger",
    "canonical-output",
    "review",
    "release-readiness",
    "release-ledger",
    "export-plan",
    "export-dry-run",
    "export-result",
    "export-audit",
    "project-readiness",
    "master-prompt-chain",
]


def test_cli_evidence_chain_reports_expected_order(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["count"] == len(EXPECTED_STEPS)

    steps = [
        item["step"]
        for item in output["chain"]
    ]

    assert steps == EXPECTED_STEPS


def test_cli_evidence_chain_reports_schema_ids(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    schema_ids = {
        item["schema"]
        for item in output["chain"]
    }

    assert "ox-provenance-manifest-1.schema.json" in schema_ids
    assert "ox-quality-gate-report-1.schema.json" in schema_ids
    assert "ox-master-prompt-evidence-chain-1.schema.json" in schema_ids


def test_cli_evidence_chain_includes_master_prompt_chain(capsys):
    assert main(["evidence-chain"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["chain"][-1]["step"] == "master-prompt-chain"
    assert (
        output["chain"][-1]["schema"]
        == "ox-master-prompt-evidence-chain-1.schema.json"
    )
