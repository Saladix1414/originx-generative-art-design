"""SD 1.5 Q4_0 local production candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


SD15_PRODUCTION_CANDIDATE_VERSION = (
    "OX-SD15-PRODUCTION-CANDIDATE-1"
)

SD15_PRODUCTION_CANDIDATE_SCHEMA_PATH = Path(
    "schemas/ox-sd15-production-candidate-1.schema.json"
)


def validate_sd15_production_candidate(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        SD15_PRODUCTION_CANDIDATE_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_sd15_production_candidate() -> dict[str, Any]:
    value = {
        "candidateVersion": SD15_PRODUCTION_CANDIDATE_VERSION,
        "modelId": "OX-MODEL-002",
        "modelName": "Stable Diffusion 1.5",
        "family": "stable-diffusion-1",
        "quantization": "Q4_0",
        "runtime": "stable-diffusion.cpp",
        "role": "PRIMARY_LOCAL_BASE_MODEL",
        "productionAlias": "OX-GENESIS-MODEL-1",
        "status": "CANDIDATE_FOR_FINAL_LOCAL_PRODUCTION",
        "targetCohort": {
            "count": 1000,
            "tier": "LEGENDARY",
            "era": "Genesis / Primordial Origin",
        },
        "source": {
            "provider": "HUGGING_FACE",
            "repository": (
                "second-state/stable-diffusion-v1-5-GGUF"
            ),
            "revision": (
                "031b5f5df991f511b3f5fa8fed6d99048ababb69"
            ),
            "baseRepository": (
                "stable-diffusion-v1-5/"
                "stable-diffusion-v1-5"
            ),
            "baseRevision": (
                "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
            ),
            "license": "CreativeML OpenRAIL-M",
            "gated": False,
        },
        "artifact": {
            "filename": (
                "stable-diffusion-v1-5-"
                "pruned-emaonly-Q4_0.gguf"
            ),
            "targetPath": (
                "models/sd15/"
                "stable-diffusion-v1-5-"
                "pruned-emaonly-Q4_0.gguf"
            ),
            "format": "GGUF",
            "quantization": "Q4_0",
            "expectedSizeBytes": 1566768416,
            "expectedSha256": (
                "sha256:"
                "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
                "fe0fa9af6c64c4829022261f"
            ),
            "bindingState": "DECLARED_NOT_ACQUIRED",
        },
        "runtimeCompatibility": {
            "runtimeFamily": "stable-diffusion.cpp",
            "runtimeCommit": (
                "792bcd344c3fa4d14143b240d5f6cbb324583b18"
            ),
            "runtimeBinarySha256": (
                "sha256:"
                "a57f5f195e0dea9b3d0461af92e528c7c25a6a98"
                "f0bf2edc771a2f5835252e42"
            ),
            "loadArgument": "--model",
            "q4_0Supported": True,
            "sd15Supported": True,
        },
        "expectedMemoryProfile": {
            "artifactResidentBytes": 1566768416,
            "runtimeOverheadIncluded": False,
            "mode": "CONSERVATIVE_CPU_MMAP",
            "batchSize": 1,
            "width": 512,
            "height": 512,
            "mmapRequired": True,
            "vaeTilingRequired": True,
            "risk": "REQUIRES_SINGLE_PREFLIGHT",
        },
        "artisticAuthority": {
            "baseModelDefinesIdentity": False,
            "governedBy": [
                "OriginX Art Grammar",
                "Structure Engine",
                "Render Compiler",
                "Resonance / Glyph influence",
                "Detail Engine",
                "Quality Engine",
            ],
        },
        "download": {
            "path": "AUTHORIZED_DOWNLOAD",
            "state": "PENDING_EXPLICIT_APPROVAL",
            "approvalRequired": True,
            "approvalPresent": False,
        },
        "governance": {
            "registrationGrantsDownloadAuthority": False,
            "registrationGrantsExecutionAuthority": False,
            "downloadAllowed": False,
            "executionAllowed": False,
            "batchGenerationAllowed": False,
            "canonicalizationAllowed": False,
            "finalProductionStatusGranted": False,
        },
    }

    validate_sd15_production_candidate(value)
    return value
