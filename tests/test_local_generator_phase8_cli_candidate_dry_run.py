import json

from oxgad.cli import main


def test_candidate_dry_run_cli_outputs_prepare_only_json(capsys):
    assert main(["candidate-dry-run"]) == 0

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["dryRunVersion"] == "OX-CANDIDATE-DRY-RUN-1"
    assert output["state"] == "PREPARE_ONLY"
    assert output["executionDecision"]["decision"] == "DENY"
    assert output["authority"]["backendInvocationAllowed"] is False
    assert output["authority"]["mediaGenerated"] is False
    assert output["candidateOutput"]["media"]["mediaHash"] is None
    assert output["dryRunHash"].startswith("sha256:")


def test_candidate_dry_run_cli_accepts_explicit_candidate_fields(capsys):
    assert (
        main(
            [
                "candidate-dry-run",
                "--candidate-id",
                "candidate-token-0002-local-001",
                "--media-path",
                "output/candidates/token-0002/candidate-001.png",
                "--render-plan-hash",
                "sha256:" + "b" * 64,
            ]
        )
        == 0
    )

    output = json.loads(
        capsys.readouterr().out
    )

    assert output["candidateId"] == "candidate-token-0002-local-001"
    assert (
        output["candidateOutput"]["media"]["path"]
        == "output/candidates/token-0002/candidate-001.png"
    )
    assert (
        output["candidateOutput"]["source"]["renderPlanHash"]
        == "sha256:" + "b" * 64
    )
