import json
from pathlib import Path

from oxgad.design import load_art_spec_expansion_catalog


AUDIT = Path("docs/master-prompt/phase1-audit-baseline.md")
CLOSURE = Path("docs/master-prompt/phase1-closure.json")


def test_master_prompt_phase1_audit_exists():
    text = AUDIT.read_text().lower()

    assert "master prompt phase 1" in text
    assert "audit / baseline" in text
    assert "current repo authority" in text


def test_master_prompt_phase1_anchors_to_structured_truth():
    text = AUDIT.read_text()

    for item in [
        "OX-ART-SPEC-1",
        "OX-RENDER-1",
        "model identity",
        "generation parameters",
        "media hashes",
        "provenance",
    ]:
        assert item in text


def test_master_prompt_phase1_uses_loaded_catalog_baseline():
    catalog = load_art_spec_expansion_catalog()
    text = AUDIT.read_text().lower()

    for key in [
        "trait_families",
        "rarity_bands",
        "composition_profiles",
        "render_intents",
    ]:
        assert key in catalog

    for phrase in [
        "trait families",
        "rarity bands",
        "composition profiles",
        "render intents",
    ]:
        assert phrase in text


def test_master_prompt_phase1_documents_future_payload():
    text = AUDIT.read_text().lower()

    for item in [
        "identity input",
        "art spec hash",
        "render plan hash",
        "trait family evidence",
        "positive prompt text",
        "negative prompt text",
        "macro detail priorities",
        "meso detail priorities",
        "micro detail priorities",
        "provenance hooks",
    ]:
        assert item in text


def test_master_prompt_phase1_closure_metadata():
    closure = json.loads(CLOSURE.read_text())

    assert closure["roadmap"] == "master-prompt"
    assert closure["phase"] == "phase1"
    assert closure["status"] == "closed"
    assert closure["next"] == "master-prompt-phase2-contract"


def test_master_prompt_phase1_is_audit_only():
    text = AUDIT.read_text().lower()

    assert "audit-only" in text
    assert "does not create the master prompt schema" in text
    assert "build prompt strings" in text
    assert "execute models" in text
    assert "call network services" in text
