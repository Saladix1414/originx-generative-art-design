"""Executor for one authorized SD 1.5 FP16 VAE preflight."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import time
from pathlib import Path
from typing import Any

from oxgad.forge.sd15_external_vae_preflight_plan import (
    APPROVAL_PHRASE,
    build_external_vae_preflight_plan,
)
from oxgad.genesis.executor import (
    MODEL,
    MODEL_HASH,
    MODEL_SIZE,
    REPO,
    RUNTIME,
    RUNTIME_HASH,
    maximum_thermal_raw,
    memory_values,
    sha256_file,
    write_json,
)
from oxgad.structure.canonical import canonical_sha256


APPROVAL_ENV = "OX_SD15_FP16_VAE_PREFLIGHT_APPROVAL"
VAE = (
    REPO
    / "models/sd15/vae/"
    "sd15-official-vae-fp16.safetensors"
)
VAE_SIZE = 167335342
VAE_HASH = (
    "4fbcf0ebe55a0984f5a5e00d8c4521d52359af72"
    "29bb4d81890039d2aa16dd7c"
)
OUTPUT = (
    REPO
    / "output/candidates/"
    "0001-sd15-fp16-vae-preflight.png"
)
REPORT_ROOT = (
    REPO
    / ".phase-reports/"
    "sd15-fp16-vae-preflight"
)


def build_command() -> list[str]:
    return [
        str(RUNTIME),
        "--model",
        str(MODEL.relative_to(REPO)),
        "--vae",
        str(VAE.relative_to(REPO)),
        "--prompt",
        (
            "a monumental dark stone dragon, full body, "
            "clear silhouette, cinematic lighting"
        ),
        "--negative-prompt",
        (
            "vertical bands, stripes, corrupted image, "
            "malformed anatomy, text, watermark"
        ),
        "--width",
        "256",
        "--height",
        "256",
        "--steps",
        "1",
        "--cfg-scale",
        "7.0",
        "--sampling-method",
        "euler_a",
        "--seed",
        "1001",
        "--threads",
        "4",
        "--params-backend",
        "disk",
        "--mmap",
        "--output",
        str(OUTPUT.relative_to(REPO)),
        "--verbose",
    ]


def png_evidence(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        header = handle.read(29)

    if len(header) < 29:
        raise ValueError("PNG is truncated.")

    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG signature.")

    if header[12:16] != b"IHDR":
        raise ValueError("PNG IHDR is missing.")

    width, height = struct.unpack(">II", header[16:24])
    bit_depth = header[24]
    color_type = header[25]

    if (width, height) != (256, 256):
        raise ValueError("Unexpected PNG dimensions.")

    if bit_depth != 8 or color_type != 2:
        raise ValueError("Expected RGB8 PNG.")

    return {
        "path": str(path.relative_to(REPO)),
        "sizeBytes": path.stat().st_size,
        "width": width,
        "height": height,
        "format": "PNG",
        "colorType": "RGB",
        "bitsPerChannel": bit_depth,
        "sha256": "sha256:" + sha256_file(path),
    }


def verify_preconditions() -> dict[str, Any]:
    if os.environ.get(APPROVAL_ENV) != APPROVAL_PHRASE:
        raise RuntimeError("Exact preflight approval is required.")

    plan = build_external_vae_preflight_plan()

    if plan["request"]["batchSize"] != 1:
        raise RuntimeError("Preflight exceeds batch size one.")

    checks = (
        (MODEL, MODEL_SIZE, MODEL_HASH, "model"),
        (VAE, VAE_SIZE, VAE_HASH, "VAE"),
        (RUNTIME, None, RUNTIME_HASH, "runtime"),
    )

    for path, expected_size, expected_hash, label in checks:
        if not path.is_file():
            raise RuntimeError(f"{label} is missing.")

        if (
            expected_size is not None
            and path.stat().st_size != expected_size
        ):
            raise RuntimeError(f"{label} size mismatch.")

        if sha256_file(path) != expected_hash:
            raise RuntimeError(f"{label} hash mismatch.")

    if OUTPUT.exists():
        raise RuntimeError("Preflight output already exists.")

    if (REPORT_ROOT / "result.json").exists():
        raise RuntimeError(
            "Preflight result already exists; retry is forbidden."
        )

    memory = memory_values()

    if memory["MemAvailable"] < 1_800_000:
        raise RuntimeError(
            "Less than 1.8 GB memory available."
        )

    return plan


def execute() -> dict[str, Any]:
    plan = verify_preconditions()
    command = build_command()

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    authorization_payload = {
        "receiptVersion": (
            "OX-SD15-FP16-VAE-PREFLIGHT-AUTHORITY-1"
        ),
        "modelId": "OX-MODEL-002",
        "componentId": "OX-MODEL-002-VAE-FP16-1",
        "approvalPhraseAccepted": True,
        "planHash": plan["planHash"],
        "executionsAuthorized": 1,
        "genesisRetryAllowed": False,
    }
    write_json(
        REPORT_ROOT / "authorization.json",
        {
            **authorization_payload,
            "receiptHash": canonical_sha256(
                authorization_payload
            ),
        },
    )
    write_json(REPORT_ROOT / "plan.json", plan)

    before = memory_values()
    thermal_before = maximum_thermal_raw()
    started = time.time()
    stop_reason = None

    with (REPORT_ROOT / "runtime.log").open(
        "w",
        encoding="utf-8",
    ) as log:
        process = subprocess.Popen(
            command,
            cwd=REPO,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )

        while process.poll() is None:
            elapsed = int(time.time() - started)
            memory = memory_values()
            thermal = maximum_thermal_raw()

            with (REPORT_ROOT / "telemetry.jsonl").open(
                "a",
                encoding="utf-8",
            ) as telemetry:
                telemetry.write(
                    json.dumps({
                        "elapsedSeconds": elapsed,
                        "memory": memory,
                        "maximumThermalRaw": thermal,
                    })
                    + "\n"
                )

            if elapsed >= 900:
                stop_reason = "TIMEOUT"
            elif memory["MemAvailable"] < 350_000:
                stop_reason = "CRITICAL_MEMORY"
            elif thermal is not None and thermal >= 80_000:
                stop_reason = "THERMAL_LIMIT"

            if stop_reason:
                process.terminate()

                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                break

            time.sleep(5)

        exit_code = process.wait()

    duration = int(time.time() - started)
    media = None

    if (
        stop_reason is None
        and exit_code == 0
        and OUTPUT.is_file()
    ):
        try:
            media = png_evidence(OUTPUT)
            state = "OUTPUT_GENERATED_PENDING_VISUAL_REVIEW"
        except ValueError as error:
            state = "FAILED_VALIDATION"
            stop_reason = str(error)
    else:
        state = "FAILED"

        if stop_reason is None:
            stop_reason = (
                "OUTPUT_MISSING"
                if not OUTPUT.is_file()
                else "RUNTIME_EXIT_NONZERO"
            )

    payload = {
        "resultVersion": (
            "OX-SD15-FP16-VAE-PREFLIGHT-RESULT-1"
        ),
        "modelId": "OX-MODEL-002",
        "componentId": "OX-MODEL-002-VAE-FP16-1",
        "state": state,
        "exitCode": exit_code,
        "stopReason": stop_reason,
        "durationSeconds": duration,
        "modelHash": "sha256:" + MODEL_HASH,
        "vaeHash": "sha256:" + VAE_HASH,
        "command": command,
        "memoryBefore": before,
        "memoryAfter": memory_values(),
        "thermalBeforeRaw": thermal_before,
        "thermalAfterRaw": maximum_thermal_raw(),
        "media": media,
        "visualReview": {
            "required": True,
            "verticalBandingAbsent": None,
            "passed": None,
        },
        "governance": {
            "genesisRetryAllowed": False,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    result = {
        **payload,
        "resultHash": canonical_sha256(payload),
    }
    write_json(REPORT_ROOT / "result.json", result)
    return result


def main() -> int:
    result = execute()
    print(json.dumps(result, indent=2))

    if (
        result["state"]
        == "OUTPUT_GENERATED_PENDING_VISUAL_REVIEW"
    ):
        print("FP16 VAE PREFLIGHT OUTPUT GENERATED")
        print("MANUAL VISUAL REVIEW REQUIRED")
        return 0

    print("FP16 VAE PREFLIGHT FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
