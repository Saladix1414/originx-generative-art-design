import json
from pathlib import Path


DOC = Path("docs/master-prompt/phase21-roadmap-closure.md")
CLOSURE = Path("docs/master-prompt/phase21-closure.json")


def test_master_prompt_roadmap_closure_records_all_phases():
    closure = json.loads(
        CLOSURE.read_text()
    )

    assert closure["phase"] == "MASTER_PROMPT_PHASE_21"
    assert closure["status"] == "closed"
    assert closure["closedPhases"] == 21
    assert closure["system"] == "OX-MASTER-PROMPT-1"


def test_master_prompt_roadmap_closure_preserves_boundaries():
    closure = json.loads(
        CLOSURE.read_text()
    )
    text = DOC.read_text()

    assert closure["readOnly"] is True
    assert closure["canonicalAuthority"] is False
    assert closure["manualApprovalRequired"] is True

    assert "does not:" in text
    assert "execute models" in text
    assert "generate media" in text
    assert "approve canonical artwork" in text


def test_master_prompt_roadmap_closure_hands_off_to_local_generator():
    closure = json.loads(
        CLOSURE.read_text()
    )
    text = DOC.read_text()

    assert (
        closure["handoff"]
        == "LOCAL GENERATOR PHASE 1 — Local Forge Runtime Plan Audit"
    )
    assert "OX-RENDER-1 → OriginX Local Forge → Candidate Media" in text
    assert "No model execution should happen" in text
