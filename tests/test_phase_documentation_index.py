import json
from pathlib import Path


PHASES = {
    8: "phase8-provenance.md",
    9: "phase9-quality-gates.md",
    10: "phase10-canonical-promotion-boundary.md",
    11: "phase11-canonical-ledger.md",
    12: "phase12-canonical-output-manifest.md",
    13: "phase13-review-pack.md",
    14: "phase14-release-readiness.md",
    15: "phase15-release-ledger.md",
    16: "phase16-local-export-plan.md",
    17: "phase17-local-export-dry-run.md",
    18: "phase18-local-export-executor.md",
    19: "phase19-export-audit-ledger.md",
    20: "phase20-project-readiness-summary.md",
}


def test_phase_index_links_phases_8_through_20():
    index = Path("docs/architecture/phase-index.md").read_text()

    for phase, filename in PHASES.items():
        assert f"Phase {phase}" in index
        assert filename in index
        assert Path("docs/architecture", filename).is_file()


def test_phase_closures_8_through_21_are_closed():
    for phase in range(8, 22):
        closure_path = Path(f"docs/architecture/phase{phase}-closure.json")
        assert closure_path.is_file()

        closure = json.loads(closure_path.read_text())

        assert closure["phase"] == f"phase{phase}"
        assert closure["status"] == "closed"
        assert "no push is executed" in [
            guarantee.lower()
            for guarantee in closure["guarantees"]
        ]


def test_phase_index_preserves_local_first_boundary():
    index = Path("docs/architecture/phase-index.md").read_text().lower()

    assert "local-first" in index
    assert "no phase" in index
    assert "model execution" in index
    assert "remote publishing" in index
