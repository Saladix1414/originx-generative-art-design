import json
from pathlib import Path


MATURITY = Path("docs/architecture/phase40-local-pipeline-maturity.md")


def test_maturity_doc_covers_phase_range():
    text = MATURITY.read_text().lower()

    assert "phase 8 through phase 39" in text


def test_maturity_doc_covers_pipeline_scope():
    text = MATURITY.read_text().lower()

    for item in [
        "provenance",
        "quality gates",
        "canonical promotion",
        "canonical ledger",
        "canonical output manifest",
        "review pack",
        "release readiness",
        "release ledger",
        "local export plan",
        "local export dry run",
        "local export executor",
        "export audit ledger",
        "project readiness summary",
    ]:
        assert item in text


def test_maturity_doc_covers_cli_surface():
    text = MATURITY.read_text().lower()

    for item in [
        "schema inspection",
        "status inspection",
        "fixture validation",
        "contract validation",
        "evidence chain reporting",
        "readiness reporting",
        "version reporting",
        "stability reporting",
    ]:
        assert item in text


def test_phase_closures_8_through_40_are_closed():
    for phase in range(8, 41):
        closure = json.loads(
            Path(f"docs/architecture/phase{phase}-closure.json").read_text()
        )

        assert closure["phase"] == f"phase{phase}"
        assert closure["status"] == "closed"


def test_maturity_doc_preserves_local_first_boundary():
    text = MATURITY.read_text().lower()

    assert "local-first" in text
    assert "remote publishing" in text
    assert "network workflow" in text
    assert "model execution" in text
    assert "uncontrolled artifact movement" in text
