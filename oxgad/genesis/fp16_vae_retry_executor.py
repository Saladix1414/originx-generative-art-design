"""Single Genesis #0001 retry using the verified FP16 VAE."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

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
from oxgad.genesis.fp16_vae_retry import (
    APPROVAL_PHRASE,
    build_external_vae_preflight_review,
    build_fp16_vae_genesis_retry_plan,
)
from oxgad.genesis.profile2_executor import (
    build_profile_2_command,
    png_evidence_profile_2,
)
from oxgad.structure.canonical import canonical_sha256


APPROVAL_ENV = "OX_GENESIS_FP16_VAE_RETRY_APPROVAL"
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
    / "output/genesis/batch-0001/token-0001/"
    "candidate/token-0001-candidate-003-fp16-vae.png"
)
REPORT_ROOT = (
    REPO
    / ".phase-reports/genesis-batch-0001/"
    "token-0001/fp16-vae-retry"
)


def _set_option(
    command: list[str],
    option: str,
    value: str,
) -> None:
    index = command.index(option)
    command[index + 1] = value


def _remove_flag(
    command: list[str],
    option: str,
) -> None:
    if option in command:
        command.remove(option)


def _remove_pair(
    command: list[str],
    option: str,
) -> None:
    if option in command:
        index = command.index(option)
        del command[index:index + 2]


def build_fp16_vae_retry_command() -> tuple[
    dict[str, Any],
    list[str],
]:
    token, command = build_profile_2_command()

    _remove_flag(command, "--vae-tiling")
    _remove_pair(command, "--vae-tile-size")

    model_index = command.index("--model")
    command[model_index + 2:model_index + 2] = [
        "--vae",
        str(VAE.relative_to(REPO)),
    ]

    _set_option(
        command,
        "--output",
        str(OUTPUT.relative_to(REPO)),
    )

    if command.count("--vae") != 1:
        raise RuntimeError("External VAE binding is ambiguous.")

    if "--vae-tiling" in command:
        raise RuntimeError("Unexpected VAE tiling.")

    return token, command


def verify_preconditions() -> dict[str, Any]:
    if os.environ.get(APPROVAL_ENV) != APPROVAL_PHRASE:
        raise RuntimeError("Exact FP16 VAE retry approval required.")

    plan = build_fp16_vae_genesis_retry_plan()

    if plan["tokenId"] != 1:
        raise RuntimeError("Plan exceeds Token #0001 scope.")

    if plan["limits"]["attempts"] != 1:
        raise RuntimeError("Plan exceeds one attempt.")

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
        raise RuntimeError("Retry output already exists.")

    if (REPORT_ROOT / "result.json").exists():
        raise RuntimeError(
            "Retry result already exists; another run is forbidden."
        )

    memory = memory_values()

    if memory["MemAvailable"] < 1_800_000:
        raise RuntimeError(
            "Less than 1.8 GB memory available."
        )

    thermal = maximum_thermal_raw()

    if thermal is not None and thermal >= 80_000:
        raise RuntimeError("Thermal limit reached.")

    return plan


def execute() -> dict[str, Any]:
    plan = verify_preconditions()
    token, command = build_fp16_vae_retry_command()

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    write_json(REPORT_ROOT / "retry-plan.json", plan)
    write_json(
        REPORT_ROOT / "preflight-review.json",
        build_external_vae_preflight_review(),
    )

    authority_payload = {
        "receiptVersion": (
            "OX-GENESIS-FP16-VAE-RETRY-AUTHORITY-1"
        ),
        "retryId": plan["retryId"],
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "approvalPhraseAccepted": True,
        "retryPlanHash": plan["retryPlanHash"],
        "attemptsAuthorized": 1,
        "nextTokenAllowed": False,
    }
    write_json(
        REPORT_ROOT / "authorization.json",
        {
            **authority_payload,
            "receiptHash": canonical_sha256(authority_payload),
        },
    )

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

            if elapsed >= 2400:
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
            media = png_evidence_profile_2(OUTPUT)
            state = "CANDIDATE_GENERATED_PENDING_REVIEW"
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
            "OX-GENESIS-FP16-VAE-RETRY-RESULT-1"
        ),
        "retryId": plan["retryId"],
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "canonicalName": token["canonicalName"],
        "state": state,
        "exitCode": exit_code,
        "stopReason": stop_reason,
        "durationSeconds": duration,
        "identity": {
            "dnaHash": token["dnaHash"],
            "resonanceSignature": token[
                "resonanceSignature"
            ],
            "glyphHash": token["glyphHash"],
            "artSpecHash": token["artSpecHash"],
            "renderPlanHash": token["renderPlanHash"],
            "bindingHash": token["bindingHash"],
            "runtimeSeed": token["seed"],
        },
        "model": {
            "modelId": "OX-MODEL-002",
            "modelHash": "sha256:" + MODEL_HASH,
        },
        "vae": {
            "componentId": "OX-MODEL-002-VAE-FP16-1",
            "sha256": "sha256:" + VAE_HASH,
            "precision": "FP16",
            "decodeMode": "NON_TILED",
        },
        "runtime": {
            "command": command,
            "memoryBefore": before,
            "memoryAfter": memory_values(),
            "thermalBeforeRaw": thermal_before,
            "thermalAfterRaw": maximum_thermal_raw(),
        },
        "media": media,
        "quality": {
            "state": (
                "PENDING_MANUAL_REVIEW"
                if state
                == "CANDIDATE_GENERATED_PENDING_REVIEW"
                else "NOT_REVIEWED"
            ),
            "score": None,
            "canonicalApproved": False,
        },
        "governance": {
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "upscaleAllowed": False,
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
        == "CANDIDATE_GENERATED_PENDING_REVIEW"
    ):
        print("FP16 VAE GENESIS CANDIDATE GENERATED")
        print("MANUAL QUALITY REVIEW REQUIRED")
        print("NO CANONICAL ARTWORK CREATED")
        print("NO NEXT TOKEN EXECUTED")
        return 0

    print("FP16 VAE GENESIS RETRY FAILED")
    print("NO AUTOMATIC RETRY")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
