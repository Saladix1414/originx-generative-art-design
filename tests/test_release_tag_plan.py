from pathlib import Path
import subprocess


PLAN = Path("docs/architecture/phase44-release-tag-plan.md")


def test_release_tag_plan_documents_tag_and_version():
    text = PLAN.read_text()

    assert "v0.41.0" in text
    assert "0.41.0" in text


def test_release_tag_plan_documents_preconditions():
    text = PLAN.read_text().lower()

    for item in [
        "all tests pass",
        "oxgad version",
        "oxgad readiness",
        "oxgad stability",
        "working tree contains no staged changes",
    ]:
        assert item in text


def test_release_tag_plan_does_not_create_tag():
    tags = subprocess.check_output(
        ["git", "tag", "--list", "v0.41.0"],
        text=True,
    ).strip()

    assert tags == ""


def test_release_tag_plan_documents_boundary():
    text = PLAN.read_text().lower()

    assert "does not create a git tag" in text
    assert "push a tag" in text
    assert "publish packages" in text
    assert "upload artifacts" in text
    assert "execute models" in text
    assert "call network services" in text
