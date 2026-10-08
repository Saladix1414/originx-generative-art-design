from pathlib import Path


PLAN = Path("docs/architecture/phase41-version-bump-plan.md")
PYPROJECT = Path("pyproject.toml")


def test_version_bump_plan_documents_current_and_next_version():
    text = PLAN.read_text()

    assert "0.23.0" in text
    assert "0.41.0" in text


def test_version_bump_plan_is_planning_only():
    text = PLAN.read_text().lower()

    assert "planning only" in text
    assert "does not change package metadata" in text
    assert "does not" in text
    assert "publish packages" in text
    assert "call network services" in text
    assert "execute models" in text


def test_phase42_updates_pyproject_version():
    text = PYPROJECT.read_text()

    assert 'version = "0.41.0"' in text
    assert 'version = "0.23.0"' not in text
