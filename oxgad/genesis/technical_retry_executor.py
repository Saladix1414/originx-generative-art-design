"""Single authorized technical retry executor for Genesis #0001."""

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
from oxgad.genesis.profile2_executor import (
    build_profile_2_command,
    png_evidence_profile_2,
)
from oxgad.genesis.technical_retry import (
    CANDIDATE_HASH,
    RETRY_APPROVAL_PHRASE,
    build_candidate_rejection,
    build_technical_retry_plan,
)
from oxgad.structure.canonical import canonical_sha256


APPROVAL_ENV = "OX_GENESIS_TECHNICAL_RETRY_APPROVAL"
REPORT_ROOT = (
    REPO
    / ".phase-reports/genesis-batch-0001/"
    "token-0001/technical-retry-1"
)
OUTPUT = (
    REPO
    / "output/genesis/batch-0001/token-0001/"
    "candidate/token-0001-candidate-002-technical-retry-1.png"
)
SOURCE_OUTPUT = (
    REPO
    / "output/genesis/batch-0001/token-0001/"
    "candidate/token-0001-candidate-001-profile2.png"
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


def _remove_option_pair(
    command: list[str],
    option: str,
) -> None:
    if option not in command:
        return

    index = command.index(option)
    del command[index:index + 2]


def build_technical_retry_command() -> tuple[
    dict[str, Any],
    list[str],
]:
    token, command = build_profile_2_command()

    _remove_flag(command, "--vae-tiling")
    _remove_option_pair(command, "--vae-tile-size")
    _set_option(
        command,
        "--output",
        str(OUTPUT.relative_to(REPO)),
    )

    if "--vae-tiling" in command:
        raise RuntimeError("VAE tiling flag was not removed.")

    if "--vae-tile-size" in command:
        raise RuntimeError("VAE tile size was not removed.")

    return token, command


def verify_authority() -> dict[str, Any]:
    supplied = os.environ.get(APPROVAL_ENV)

    if supplied != RETRY_APPROVAL_PHRASE:
        raise RuntimeError(
            "Exact technical retry approval phrase is required."
        )

    plan = build_technical_retry_plan()

    if plan["tokenId"] != 1:
        raise RuntimeError("Retry plan is not scoped to Token #0001.")

    if plan["limits"]["attempts"] != 1:
        raise RuntimeError("Retry plan exceeds one attempt.")

    if plan["singleChange"]["retryMode"] != "NON_TILED":
        raise RuntimeError("Unexpected retry decode mode.")

    return plan


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

    if not SOURCE_OUTPUT.is_file():
        raise RuntimeError("Rejected source candidate is missing.")

    if "sha256:" + sha256_file(SOURCE_OUTPUT) != CANDIDATE_HASH:
        raise RuntimeError("Rejected source candidate hash mismatch.")

    if OUTPUT.exists():
        raise RuntimeError(
            f"Refusing to overwrite retry output: {OUTPUT}"
        )

    if (REPORT_ROOT / "result.json").exists():
        raise RuntimeError(
            "Technical retry result already exists; "
            "another attempt is forbidden."
        )

    memory = memory_values()

    if memory["MemAvailable"] < 1_800_000:
        raise RuntimeError(
            "Less than 1.8 GB memory available before retry."
        )

    thermal = maximum_thermal_raw()

    if thermal is not None and thermal >= 80_000:
        raise RuntimeError("Thermal limit reached before retry.")


def execute() -> dict[str, Any]:
    plan = verify_authority()
    verify_preconditions()
    token, command = build_technical_retry_command()

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    write_json(REPORT_ROOT / "retry-plan.json", plan)
    write_json(
        REPORT_ROOT / "source-rejection.json",
        build_candidate_rejection(),
    )

    authorization_payload = {
        "receiptVersion": (
            "OX-GENESIS-TECHNICAL-RETRY-AUTHORITY-1"
        ),
        "retryId": plan["retryId"],
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": 1,
        "approvalPhraseAccepted": True,
        "retryPlanHash": plan["retryPlanHash"],
        "attemptsAuthorized": 1,
        "canonicalizationAllowed": False,
        "nextTokenAllowed": False,
    }
    authorization = {
        **authorization_payload,
        "receiptHash": canonical_sha256(
            authorization_payload
        ),
    }
    write_json(
        REPORT_ROOT / "authorization.json",
        authorization,
    )

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
            state = "CANDIDATE_GENERATED_PENDING_REVIEW"
        except ValueError as error:
            state = "FAILED_VALIDATION"
            stop_reason = str(error)
    else:
        state = "FAILED_TECHNICAL_RETRY"

        if stop_reason is None:
            stop_reason = (
                "OUTPUT_MISSING"
                if not OUTPUT.is_file()
                else "RUNTIME_EXIT_NONZERO"
            )

    payload = {
        "resultVersion": (
            "OX-GENESIS-TECHNICAL-RETRY-RESULT-1"
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
        "singleChange": {
            "component": "VAE_DECODE",
            "previousMode": "TILED_128X128",
            "retryMode": "NON_TILED",
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
        "sourceCandidate": {
            "state": "REJECTED_TECHNICAL_ARTIFACT",
            "mediaHash": CANDIDATE_HASH,
        },
        "media": media,
        "quality": {
            "state": (
                "PENDING_MANUAL_REVIEW"
                if state
                == "CANDIDATE_GENERATED_PENDING_REVIEW"
                else "NOT_REVIEWED"
            ),
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
        print("TECHNICAL RETRY CANDIDATE GENERATED")
        print("MANUAL QUALITY REVIEW REQUIRED")
        print("NO CANONICAL ARTWORK CREATED")
        print("NO NEXT TOKEN EXECUTED")
        return 0

    print("TECHNICAL RETRY FAILED")
    print("NO FURTHER RETRY AUTHORIZED")
    print("NO NEXT TOKEN EXECUTED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
