from pathlib import Path


README = Path("README.md")


def test_readme_documents_local_cli_commands():
    text = README.read_text()

    assert "## Local CLI" in text

    for command in [
        "oxgad schema",
        "oxgad status",
        "oxgad validate-fixtures",
        "oxgad validate-contracts",
        "oxgad contracts",
        "oxgad evidence-chain",
        "oxgad readiness",
        "oxgad version",
        "oxgad stability",
    ]:
        assert command in text


def test_readme_documents_editable_install():
    text = README.read_text()

    assert "python -m pip install -e ." in text


def test_readme_preserves_local_first_boundary():
    text = README.read_text().lower()

    assert "local-first" in text
    assert "read-only" in text
    assert "does not execute models" in text
    assert "call network services" in text
    assert "publish packages" in text
    assert "upload artifacts" in text
