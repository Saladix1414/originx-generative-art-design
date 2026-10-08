from pathlib import Path


NOTES = Path("docs/releases/phase8-35-local-evidence-pipeline.md")


def test_release_notes_draft_exists_and_covers_pipeline():
    text = NOTES.read_text()

    required = [
        "provenance manifest",
        "quality gate report",
        "canonical promotion decision",
        "canonical ledger",
        "canonical output manifest",
        "review pack",
        "release readiness decision",
        "release ledger",
        "local export plan",
        "local export dry run",
        "local export executor",
        "export audit ledger",
        "project readiness summary",
    ]

    for item in required:
        assert item in text


def test_release_notes_draft_covers_cli_surface():
    text = NOTES.read_text()

    for command in [
        "schema",
        "status",
        "validate-fixture",
        "validate-fixtures",
        "contracts",
        "validate-contracts",
        "evidence-chain",
        "readiness",
        "version",
        "stability",
    ]:
        assert command in text


def test_release_notes_draft_preserves_local_first_boundary():
    text = NOTES.read_text().lower()

    assert "local-first" in text
    assert "does not introduce" in text
    assert "network workflows" in text
    assert "model execution" in text
    assert "automatic upload" in text
