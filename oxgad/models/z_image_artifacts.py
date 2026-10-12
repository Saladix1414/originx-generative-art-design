from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

Z_IMAGE_ARTIFACT_MANIFEST_VERSION = (
    "OX-Z-IMAGE-ARTIFACT-MANIFEST-1"
)

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "ox-z-image-artifact-manifest-1.schema.json"
)


def build_z_image_artifact_manifest() -> dict[str, Any]:
    manifest = {
        "manifestVersion": Z_IMAGE_ARTIFACT_MANIFEST_VERSION,
        "modelId": "OX-MODEL-001",
        "state": "EXPECTED_NOT_OBSERVED",
        "runtime": {
            "family": "stable-diffusion.cpp",
            "commit": "792bcd344c3fa4d14143b240d5f6cbb324583b18",
            "binarySha256": (
                "sha256:a57f5f195e0dea9b3d0461af92e528c7c25a6a98"
                "f0bf2edc771a2f5835252e42"
            ),
        },
        "artifacts": [
            {
                "role": "DIFFUSION_TRANSFORMER",
                "repository": "leejet/Z-Image-Turbo-GGUF",
                "revision": "c61c0e422dc8b541b7548cf33a4ef8302b0f8085",
                "filename": "z_image_turbo-Q4_0.gguf",
                "license": "Apache-2.0",
                "expectedSizeBytes": 3683370944,
                "expectedSha256": (
                    "sha256:3f15efb272efb7133373f2936fcd1c95"
                    "abeefd3222e2d9b28baa8182115e5040"
                ),
                "observed": False,
            },
            {
                "role": "TEXT_ENCODER_DEPENDENCY",
                "repository": "unsloth/Qwen3-4B-Instruct-2507-GGUF",
                "revision": "a06e946bb6b655725eafa393f4a9745d460374c9",
                "filename": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
                "license": "Apache-2.0",
                "expectedSizeBytes": 2497281120,
                "expectedSha256": (
                    "sha256:bf52d44a54b81d44219833556849529e"
                    "e96f09da673a38783dddc2e2eaf17881"
                ),
                "observed": False,
            },
            {
                "role": "VAE",
                "repository": "Tongyi-MAI/Z-Image-Turbo",
                "revision": "f332072aa78be7aecdf3ee76d5c247082da564a6",
                "filename": "vae/diffusion_pytorch_model.safetensors",
                "license": "Apache-2.0",
                "expectedSizeBytes": 167666902,
                "expectedSha256": (
                    "sha256:5fc08a93307850a89126de1e284972e1"
                    "a1d7bcbb061ed06edcfc2db5a2669dcd"
                ),
                "observed": False,
            },
        ],
        "totalExpectedSizeBytes": 6348318966,
        "governance": {
            "downloadAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
    }
    return validate_z_image_artifact_manifest(manifest)


def validate_z_image_artifact_manifest(
    value: dict[str, Any],
) -> dict[str, Any]:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(value, schema)
    return value
