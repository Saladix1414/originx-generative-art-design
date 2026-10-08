import json
from pathlib import Path
import subprocess

from oxgad.cli import main


def _run(argv, capsys):
    assert main(argv) == 0
    return json.loads(capsys.readouterr().out)


def test_final_local_release_version_readiness_and_stability(capsys):
    version = _run(["version"], capsys)
    readiness = _run(["readiness"], capsys)
    stability = _run(["stability"], capsys)

    assert version["version"] == "0.41.0"
    assert readiness["ready"] is True
    assert stability["version"] == "0.41.0"
    assert stability["read_only"] is True
    assert stability["contract_count"] == stability["evidence_chain_count"]


def test_final_local_release_contracts_and_fixtures(capsys):
    contracts = _run(["validate-contracts"], capsys)
    fixtures = _run(["validate-fixtures", "tests/fixtures/cli"], capsys)

    assert contracts["valid"] is True
    assert contracts["count"] >= 13
    assert fixtures["valid"] is True
    assert fixtures["count"] == 2


def test_final_local_release_docs_exist():
    for path in [
        "docs/releases/phase8-35-local-evidence-pipeline.md",
        "docs/architecture/phase40-local-pipeline-maturity.md",
        "docs/architecture/phase44-release-tag-plan.md",
    ]:
        assert Path(path).is_file()


def test_final_local_release_tag_exists_and_points_to_head():
    tag = subprocess.check_output(
        ["git", "tag", "--list", "v0.41.0"],
        text=True,
    ).strip()

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()

    tag_commit = subprocess.check_output(
        ["git", "rev-list", "-n", "1", "v0.41.0"],
        text=True,
    ).strip()

    assert tag == "v0.41.0"
    assert tag_commit == head


def test_final_local_release_worktree_has_no_staged_files():
    staged = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"],
        text=True,
    ).strip()

    assert staged == ""
