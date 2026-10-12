from __future__ import annotations

from pathlib import Path
from typing import Any

_TARGET_ROOT = Path("models/z-image")


def build_z_image_download_dry_run() -> dict[str, Any]:
    artifacts = [
        {
            "role": "DIFFUSION_TRANSFORMER",
            "url": (
                "https://huggingface.co/leejet/"
                "Z-Image-Turbo-GGUF/resolve/"
                "c61c0e422dc8b541b7548cf33a4ef8302b0f8085/"
                "z_image_turbo-Q4_0.gguf"
            ),
            "target": str(
                _TARGET_ROOT / "z_image_turbo-Q4_0.gguf"
            ),
            "expectedSizeBytes": 3683370944,
            "expectedSha256": (
                "sha256:3f15efb272efb7133373f2936fcd1c95"
                "abeefd3222e2d9b28baa8182115e5040"
            ),
        },
        {
            "role": "TEXT_ENCODER_DEPENDENCY",
            "url": (
                "https://huggingface.co/unsloth/"
                "Qwen3-4B-Instruct-2507-GGUF/resolve/"
                "a06e946bb6b655725eafa393f4a9745d460374c9/"
                "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
            ),
            "target": str(
                _TARGET_ROOT
                / "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
            ),
            "expectedSizeBytes": 2497281120,
            "expectedSha256": (
                "sha256:bf52d44a54b81d44219833556849529e"
                "e96f09da673a38783dddc2e2eaf17881"
            ),
        },
        {
            "role": "VAE",
            "url": (
                "https://huggingface.co/Tongyi-MAI/"
                "Z-Image-Turbo/resolve/"
                "f332072aa78be7aecdf3ee76d5c247082da564a6/"
                "vae/diffusion_pytorch_model.safetensors"
            ),
            "target": str(
                _TARGET_ROOT / "z_image_vae.safetensors"
            ),
            "expectedSizeBytes": 167666902,
            "expectedSha256": (
                "sha256:5fc08a93307850a89126de1e284972e1"
                "a1d7bcbb061ed06edcfc2db5a2669dcd"
            ),
        },
    ]

    return {
        "dryRunVersion": "OX-Z-IMAGE-DOWNLOAD-DRY-RUN-1",
        "modelId": "OX-MODEL-001",
        "state": "DRY_RUN_ONLY",
        "targetRoot": str(_TARGET_ROOT),
        "artifacts": artifacts,
        "expectedSizeBytes": sum(
            item["expectedSizeBytes"] for item in artifacts
        ),
        "networkInvoked": False,
        "filesWritten": False,
        "governance": {
            "downloadAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
    }
