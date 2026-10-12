from __future__ import annotations

from typing import Any


def build_z_image_runtime_load_plan() -> dict[str, Any]:
    command = [
        "/root/stable-diffusion.cpp/build/bin/sd-cli",
        "--diffusion-model",
        "models/z-image/z_image_turbo-Q4_0.gguf",
        "--llm",
        "models/z-image/Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "--vae",
        "models/z-image/z_image_vae.safetensors",
        "--backend",
        "cpu",
        "--params-backend",
        "disk",
        "--mmap",
        "--vae-tiling",
        "--vae-tile-size",
        "128x128",
        "--diffusion-fa",
        "-W",
        "256",
        "-H",
        "256",
        "--steps",
        "1",
        "--cfg-scale",
        "1.0",
        "-s",
        "1001",
        "-p",
        "OriginX runtime load preflight",
        "-o",
        "output/candidates/0001-runtime-preflight.png",
    ]

    return {
        "planVersion": "OX-Z-IMAGE-RUNTIME-LOAD-PLAN-1",
        "modelId": "OX-MODEL-001",
        "state": "DRY_RUN_NOT_AUTHORIZED",
        "command": command,
        "limits": {
            "width": 256,
            "height": 256,
            "steps": 1,
            "candidateCount": 1,
            "diskBackedParameters": True,
            "vaeTiling": True,
        },
        "observability": {
            "captureWallTime": True,
            "capturePeakRam": True,
            "captureThermals": True,
            "captureExitCode": True,
        },
        "governance": {
            "runtimeInvocationAllowed": False,
            "imageGenerationAllowed": False,
            "canonicalizationAllowed": False,
            "batchGenerationAllowed": False,
        },
    }
