import json
from pathlib import Path

import jsonschema

from oxgad.master_prompt import (
    build_prompt_evidence_chain,
    stable_prompt_hash,
)


FIXTURE = Path("tests/fixtures/master-prompt/candidate.json")
SCHEMA = Path("schemas/ox-master-prompt-evidence-chain-1.schema.json")


def _schema():
    return json.loads(SCHEMA.read_text())


def _prompt():
    payload = json.loads(FIXTURE.read_text())
    payload["render_binding"]["master_prompt_hash"] = stable_prompt_hash(
        payload
    )
    return payload


def test_prompt_evidence_chain_schema_is_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(_schema())


def test_prompt_evidence_chain_validates_generated_chain():
    chain = build_prompt_evidence_chain(_prompt())

    jsonschema.validate(chain, _schema())

    assert chain["chainVersion"] == "OX-MASTER-PROMPT-EVIDENCE-CHAIN-1"
    assert chain["authority"]["manualApprovalRequired"] is True


def test_prompt_evidence_chain_schema_rejects_bad_step_order():
    chain = build_prompt_evidence_chain(_prompt())
    chain["steps"][0]["step"] = "render-plan"

    validator = jsonschema.Draft202012Validator(_schema())
    errors = list(validator.iter_errors(chain))

    assert errors


def test_prompt_evidence_chain_schema_rejects_authority_escalation():
    chain = build_prompt_evidence_chain(_prompt())
    chain["authority"]["aiOutputIsCanonical"] = True

    validator = jsonschema.Draft202012Validator(_schema())
    errors = list(validator.iter_errors(chain))

    assert errors
