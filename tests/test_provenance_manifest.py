import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.provenance import (
    build_provenance_manifest,
    verify_provenance_manifest,
)


VALID_SHA = "a" * 64


def test_provenance_manifest_matches_schema():
    manifest = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256=VALID_SHA,
        created_at="2026-10-08T18:00:00+00:00",
    )

    schema = json.loads(
        Path("schemas/ox-provenance-manifest-1.schema.json").read_text()
    )

    jsonschema.validate(manifest, schema)

    assert manifest["schema_version"] == "ox-provenance-manifest-1"
    assert manifest["project"] == "originx-generative-art-design"
    assert verify_provenance_manifest(manifest)


def test_provenance_manifest_rejects_invalid_output_hash():
    with pytest.raises(ValueError, match="output_sha256"):
        build_provenance_manifest(
            art_spec_id="token-0001",
            identity_input_id="identity-input-v1",
            model_registry_id="model-registry-v1",
            model_binding_id="binding-local-forge-v1",
            render_request_id="render-request-0001",
            render_backend_id="local-forge",
            output_artifact_id="candidate-0001",
            output_sha256="NOT_A_SHA",
        )


def test_provenance_manifest_detects_tampering():
    manifest = build_provenance_manifest(
        art_spec_id="token-0001",
        identity_input_id="identity-input-v1",
        model_registry_id="model-registry-v1",
        model_binding_id="binding-local-forge-v1",
        render_request_id="render-request-0001",
        render_backend_id="local-forge",
        output_artifact_id="candidate-0001",
        output_sha256=VALID_SHA,
    )

    manifest["output"]["artifact_id"] = "candidate-9999"

    assert verify_provenance_manifest(manifest) is False
