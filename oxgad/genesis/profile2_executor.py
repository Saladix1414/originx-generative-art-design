"""Single-token executor for Genesis Render Profile 2."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import time
from pathlib import Path
from typing import Any

from oxgad.genesis.batch import build_genesis_batch_plan
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
from oxgad.genesis.render_profile import (
    APPROVAL_PHRASE,
    build_interruption_evidence,
    build_render_profile_2,
    build_token_0001_profile_2_gate,
)
from oxgad.structure.canonical import canonical_sha256


REPORT_ROOT = (
    REPO
    / ".phase-reports/genesis-batch-0001/"
    "token-0001/profile2"
)
OUTPUT = (
    REPO
    / "output/genesis/batch-0001/token-0001/"
    "candidate/token-0001-candidate-001-profile2.png"
)
APPROVAL_ENV = "OX_GENESIS_PROFILE2_APPROVAL"


def _set_option(
    command: list[str],
    option: str,
    value: str,
) -> None:
    try:
        index = command.index(option)
    except ValueError:
        command.extend([option, value])
    else:
        command[index + 1] = value


def build_profile_2_command() -> tuple[
    dict[str, Any],
    list[str],
]:
    plan = build_genesis_batch_plan()

    if plan["batchId"] != "GENESIS-BATCH-0001":
        raise RuntimeError("Unexpected batch plan.")

    if len(plan["tokens"]) != 10:
        raise RuntimeError("Unexpected token count.")

    token = plan["tokens"][0]

    if token["tokenId"] != 1 or token["serial"] != "#0001":
        raise RuntimeError("Executor is not scoped to Token #0001.")

    command = list(token["command"])

    _set_option(command, "--width", "384")
    _set_option(command, "--height", "384")
    _set_option(command, "--steps", "10")
    _set_option(command, "--cfg-scale", "7.0")
    _set_option(command, "--sampling-method", "dpm++2m")
    _set_option(command, "--scheduler", "karras")
    _set_option(command, "--output", str(OUTPUT.relative_to(REPO)))

    return token, command


def png_evidence_profile_2(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        header = handle.read(29)

    if len(header) < 29:
        raise ValueError("PNG output is truncated.")

    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Output is not a PNG.")

    if header[12:16] != b"IHDR":
        raise ValueError("PNG IHDR is missing.")

    width, height = struct.unpack(">II", header[16:24])
    bit_depth = header[24]
    color_type = header[25]

    if (width, height) != (384, 384):
        raise ValueError(
            f"Unexpected PNG dimensions: {width}x{height}."
        )

    if bit_depth != 8:
        raise ValueError(
            f"Unexpected PNG bit depth: {bit_depth}."
        )

    if color_type != 2:
        raise ValueError(
            "Expected RGB PNG color type 2, "
            f"received {color_type}."
        )

    return {
        "path": str(path.relative_to(REPO)),
        "sizeBytes": path.stat().st_size,
        "width": width,
        "height": height,
        "format": "PNG",
        "colorType": "RGB",
        "bitsPerChannel": bit_depth,
        "lossless": True,
        "sha256": "sha256:" + sha256_file(path),
    }


def verify_authority() -> tuple[dict[str, Any], dict[str, Any]]:
    supplied = os.environ.get(APPROVAL_ENV)

    if supplied != APPROVAL_PHRASE:
        raise RuntimeError(
            "Exact Profile 2 approval phrase is required."
        )

    profile = build_render_profile_2()
    gate = build_token_0001_profile_2_gate()

    if gate["limits"]["profileHash"] != profile["profileHash"]:
        raise RuntimeError("Profile and gate hashes disagree.")

    if gate["tokenId"] != 1 or gate["limits"]["tokens"] != 1:
        raise RuntimeError("Gate exceeds single-token authority.")

    return profile, gate


def verify_preconditions() -> None:
    if not MODEL.is_file():
        raise RuntimeError("Model artifact is missing.")

    if MODEL.stat().st_size != MODEL_SIZE:
        raise RuntimeError("Model size mismatch.")

    if sha256_file(MODEL) != MODEL_HASH:
        raise RuntimeError("Model hash mismatch.")

    if not RUNTIME.is_file():
        raise RuntimeError("Runtime binary is missing.")

    if sha256_file(RUNTIME) != RUNTIME_HASH:
        raise RuntimeError("Runtime hash mismatch.")

    if OUTPUT.exists():
        raise RuntimeError(
            f"Refusing to overwrite existing output: {OUTPUT}"
        )

    result_path = REPORT_ROOT / "result.json"

    if result_path.exists():
        raise RuntimeError(
            "A Profile 2 execution result already exists; "
            "automatic retry is forbidden."
        )

    memory = memory_values()

    if memory["MemAvailable"] < 1_200_000:
        raise RuntimeError(
            "Less than 1.2 GB memory available before execution."
        )

    thermal = maximum_thermal_raw()

    if thermal is not None and thermal >= 80_000:
        raise RuntimeError("Thermal limit reached before execution.")


def _write_authorization_receipt(
    profile: dict[str, Any],
    gate: dict[str, Any],
) -> None:
    payload = {
        "receiptVersion": (
            "OX-GENESIS-PROFILE2-EXECUTION-AUTHORITY-1"
        ),
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "approvalPhraseAccepted": True,
        "profileId": profile["profileId"],
        "profileHash": profile["profileHash"],
        "gateHash": gate["gateHash"],
        "limits": {
            "tokens": 1,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
        },
    }
    value = {
        **payload,
        "receiptHash": canonical_sha256(payload),
    }
    write_json(REPORT_ROOT / "authorization.json", value)


def execute() -> dict[str, Any]:
    profile, gate = verify_authority()
    verify_preconditions()

    token, command = build_profile_2_command()
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    write_json(
        REPORT_ROOT / "profile.json",
        profile,
    )
    write_json(
        REPORT_ROOT / "gate.json",
        gate,
    )
    write_json(
        REPORT_ROOT / "interruption-evidence.json",
        build_interruption_evidence(),
    )
    _write_authorization_receipt(profile, gate)

    before = memory_values()
    thermal_before = maximum_thermal_raw()
    started = time.time()
    stop_reason = None

    log_path = REPORT_ROOT / "runtime.log"
    telemetry_path = REPORT_ROOT / "telemetry.jsonl"

    with log_path.open("w", encoding="utf-8") as log:
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

            with telemetry_path.open(
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

            if elapsed >= 3600:
                stop_reason = "TIMEOUT"
            elif memory["MemAvailable"] < 350_000:
                stop_reason = "CRITICAL_MEMORY"
            elif thermal is not None and thermal >= 80_000:
                stop_reason = "THERMAL_LIMIT"

            if stop_reason is not None:
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
    after = memory_values()
    thermal_after = maximum_thermal_raw()
    media = None

    if (
        stop_reason is None
        and exit_code == 0
        and OUTPUT.is_file()
    ):
        try:
            media = png_evidence_profile_2(OUTPUT)
            state = "CANDIDATE_GENERATED"
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

    result_payload = {
        "resultVersion": (
            "OX-GENESIS-PROFILE2-CANDIDATE-RESULT-1"
        ),
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "serial": "#0001",
        "canonicalName": token["canonicalName"],
        "state": state,
        "exitCode": exit_code,
        "stopReason": stop_reason,
        "durationSeconds": duration,
        "profile": {
            "profileId": profile["profileId"],
            "profileHash": profile["profileHash"],
            "gateHash": gate["gateHash"],
        },
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
        "runtime": {
            "command": command,
            "memoryBefore": before,
            "memoryAfter": after,
            "thermalBeforeRaw": thermal_before,
            "thermalAfterRaw": thermal_after,
        },
        "media": media,
        "quality": {
            "state": (
                "PENDING_MANUAL_REVIEW"
                if state == "CANDIDATE_GENERATED"
                else "NOT_REVIEWED"
            ),
            "score": None,
            "canonicalApproved": False,
        },
        "governance": {
            "candidateIsCanonical": False,
            "automaticRetryAllowed": False,
            "nextTokenAllowed": False,
            "nextBatchAllowed": False,
            "upscaleAllowed": False,
        },
    }
    result = {
        **result_payload,
        "resultHash": canonical_sha256(result_payload),
    }
    write_json(REPORT_ROOT / "result.json", result)
    return result


def main() -> int:
    result = execute()
    print(json.dumps(result, indent=2))

    if result["state"] == "CANDIDATE_GENERATED":
        print("TOKEN #0001 CANDIDATE GENERATED")
        print("MANUAL QUALITY REVIEW REQUIRED")
        print("NO CANONICAL ARTWORK CREATED")
        print("NO NEXT TOKEN EXECUTED")
        return 0

    print("TOKEN #0001 PROFILE 2 EXECUTION FAILED")
    print("NO AUTOMATIC RETRY")
    print("NO NEXT TOKEN EXECUTED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
