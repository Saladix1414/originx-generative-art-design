"""Resumable executor for GENESIS-BATCH-0001 candidates."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import time
from pathlib import Path
from typing import Any

from oxgad.genesis.batch import (
    build_genesis_batch_plan,
    write_genesis_batch_contracts,
)
from oxgad.structure.canonical import canonical_sha256


REPO = Path(
    "/data/data/com.termux/files/home/"
    "originx-generative-art-design"
)
BATCH_ROOT = REPO / "output/genesis/batch-0001"
REPORT_ROOT = REPO / ".phase-reports/genesis-batch-0001"
MODEL = (
    REPO
    / "models/sd15/"
    "stable-diffusion-v1-5-pruned-emaonly-Q4_0.gguf"
)
RUNTIME = Path(
    "/root/stable-diffusion.cpp/build/bin/sd-cli"
)

MODEL_SIZE = 1566768416
MODEL_HASH = (
    "b8944e9fe0b69b36ae1b5bb0185b3a7b8ef14347"
    "fe0fa9af6c64c4829022261f"
)
RUNTIME_HASH = (
    "a57f5f195e0dea9b3d0461af92e528c7c25a6a98"
    "f0bf2edc771a2f5835252e42"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def memory_values() -> dict[str, int]:
    result = {}

    for line in Path("/proc/meminfo").read_text().splitlines():
        key, raw = line.split(":", 1)

        if key in {
            "MemTotal",
            "MemAvailable",
            "SwapTotal",
            "SwapFree",
        }:
            result[key] = int(raw.strip().split()[0])

    return result


def maximum_thermal_raw() -> int | None:
    values = []

    for path in Path("/sys/class/thermal").glob(
        "thermal_zone*/temp"
    ):
        try:
            value = int(path.read_text().strip())
        except (OSError, ValueError):
            continue

        if value > 0:
            values.append(value)

    return max(values) if values else None


def png_evidence(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        header = handle.read(24)

    if len(header) != 24:
        raise ValueError("PNG output is truncated.")

    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Output is not a PNG.")

    width, height = struct.unpack(">II", header[16:24])

    if (width, height) != (512, 512):
        raise ValueError(
            f"Unexpected PNG dimensions: {width}x{height}."
        )

    return {
        "path": str(path.relative_to(REPO)),
        "sizeBytes": path.stat().st_size,
        "width": width,
        "height": height,
        "sha256": "sha256:" + sha256_file(path),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def existing_success(
    token: dict[str, Any],
) -> bool:
    token_id = token["tokenId"]
    result_path = (
        REPORT_ROOT
        / f"token-{token_id:04d}"
        / "result.json"
    )

    if not result_path.is_file():
        return False

    result = json.loads(result_path.read_text())

    if result.get("state") != "CANDIDATE_GENERATED":
        return False

    output = REPO / token["candidatePath"]

    if not output.is_file():
        return False

    evidence = png_evidence(output)
    return evidence["sha256"] == result["media"]["sha256"]


def update_batch_progress(
    plan: dict[str, Any],
) -> dict[str, Any]:
    results = []

    for token in plan["tokens"]:
        path = (
            REPORT_ROOT
            / f"token-{token['tokenId']:04d}"
            / "result.json"
        )

        if path.is_file():
            results.append(json.loads(path.read_text()))

    completed = [
        item
        for item in results
        if item["state"] == "CANDIDATE_GENERATED"
    ]
    failed = [
        item
        for item in results
        if item["state"] == "FAILED"
    ]

    payload = {
        "progressVersion": "OX-GENESIS-BATCH-PROGRESS-1",
        "batchId": "GENESIS-BATCH-0001",
        "tokensRequested": 10,
        "tokensCompleted": len(completed),
        "tokensFailed": len(failed),
        "tokensApproved": 0,
        "tokensRejected": 0,
        "canonicalArtworks": 0,
        "modelId": "OX-MODEL-002",
        "modelHash": "sha256:" + MODEL_HASH,
        "state": (
            "FAILED"
            if failed
            else (
                "CANDIDATES_GENERATED_PENDING_REVIEW"
                if len(completed) == 10
                else "IN_PROGRESS"
            )
        ),
        "results": results,
        "nextBatchAllowed": False,
    }

    value = {
        **payload,
        "batchManifestHash": canonical_sha256(payload),
    }
    write_json(REPORT_ROOT / "progress.json", value)
    return value


def run_token(
    token: dict[str, Any],
) -> dict[str, Any]:
    token_id = token["tokenId"]
    report = REPORT_ROOT / f"token-{token_id:04d}"
    report.mkdir(parents=True, exist_ok=True)

    output = REPO / token["candidatePath"]

    if output.exists():
        raise RuntimeError(
            f"Refusing to overwrite existing output: {output}"
        )

    before = memory_values()

    if before["MemAvailable"] < 1_200_000:
        raise RuntimeError(
            "Less than 1.2 GB memory available before token."
        )

    thermal_before = maximum_thermal_raw()

    if (
        thermal_before is not None
        and thermal_before >= 80_000
    ):
        raise RuntimeError(
            "Thermal limit reached before token."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    log_path = report / "runtime.log"
    telemetry_path = report / "telemetry.jsonl"

    started = time.time()
    reason = None

    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            token["command"],
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
                telemetry.write(json.dumps({
                    "elapsedSeconds": elapsed,
                    "memory": memory,
                    "maximumThermalRaw": thermal,
                }) + "\n")

            if elapsed >= 5400:
                reason = "TIMEOUT"
            elif memory["MemAvailable"] < 350_000:
                reason = "CRITICAL_MEMORY"
            elif thermal is not None and thermal >= 80_000:
                reason = "THERMAL_LIMIT"

            if reason:
                process.terminate()

                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()

                break

            time.sleep(5)

        exit_code = process.wait()

    duration = int(time.time() - started)
    after = memory_values()
    thermal_after = maximum_thermal_raw()

    if (
        reason is None
        and exit_code == 0
        and output.is_file()
    ):
        media = png_evidence(output)
        state = "CANDIDATE_GENERATED"
    else:
        media = None
        state = "FAILED"

    result = {
        "resultVersion": "OX-GENESIS-CANDIDATE-RESULT-1",
        "batchId": "GENESIS-BATCH-0001",
        "tokenId": token_id,
        "serial": token["serial"],
        "canonicalName": token["canonicalName"],
        "state": state,
        "exitCode": exit_code,
        "stopReason": reason,
        "durationSeconds": duration,
        "identity": {
            "dnaHash": token["dnaHash"],
            "resonanceSignature": (
                token["resonanceSignature"]
            ),
            "glyphHash": token["glyphHash"],
            "artSpecHash": token["artSpecHash"],
            "renderPlanHash": token["renderPlanHash"],
            "bindingHash": token["bindingHash"],
            "runtimeSeed": token["seed"],
        },
        "memoryBefore": before,
        "memoryAfter": after,
        "thermalBeforeRaw": thermal_before,
        "thermalAfterRaw": thermal_after,
        "media": media,
        "quality": {
            "state": "PENDING_MANUAL_REVIEW",
            "canonicalApproved": False,
        },
    }

    write_json(report / "result.json", result)
    return result


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


def main() -> int:
    os.chdir(REPO)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    verify_preconditions()

    plan = write_genesis_batch_contracts(BATCH_ROOT)
    update_batch_progress(plan)

    for token in plan["tokens"]:
        if existing_success(token):
            print(token["serial"], "already completed")
            continue

        print(token["serial"], "starting", flush=True)

        try:
            result = run_token(token)
        except Exception as error:
            result = {
                "resultVersion": (
                    "OX-GENESIS-CANDIDATE-RESULT-1"
                ),
                "batchId": "GENESIS-BATCH-0001",
                "tokenId": token["tokenId"],
                "serial": token["serial"],
                "canonicalName": token["canonicalName"],
                "state": "FAILED",
                "stopReason": type(error).__name__,
                "error": str(error),
                "quality": {
                    "state": "NOT_REVIEWED",
                    "canonicalApproved": False,
                },
            }
            write_json(
                REPORT_ROOT
                / f"token-{token['tokenId']:04d}"
                / "result.json",
                result,
            )

        progress = update_batch_progress(plan)

        if result["state"] != "CANDIDATE_GENERATED":
            print(
                token["serial"],
                "failed; batch stopped",
                flush=True,
            )
            return 1

        print(
            token["serial"],
            "candidate generated",
            flush=True,
        )

        if progress["tokensCompleted"] < 10:
            time.sleep(120)

    progress = update_batch_progress(plan)

    print(json.dumps(progress, indent=2))
    print("BATCH STOPPED FOR QUALITY REVIEW")
    print("NO NEXT BATCH EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
