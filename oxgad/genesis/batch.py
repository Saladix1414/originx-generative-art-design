"""Prepare-only Genesis batch orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from oxgad.genesis.identity import build_genesis_identity
from oxgad.genesis.lore import build_genesis_lore
from oxgad.genesis.planning import (
    MODEL_HASH,
    build_genesis_batch_plans,
)
from oxgad.structure.canonical import (
    canonical_json,
    canonical_sha256,
)


GENESIS_BATCH_PLAN_VERSION = "OX-GENESIS-BATCH-PLAN-1"
GENESIS_BATCH_PLAN_SCHEMA_PATH = Path(
    "schemas/ox-genesis-batch-plan-1.schema.json"
)

MODEL_PATH = (
    "models/sd15/"
    "stable-diffusion-v1-5-pruned-emaonly-Q4_0.gguf"
)

RUNTIME_PATH = (
    "/root/stable-diffusion.cpp/build/bin/sd-cli"
)


def validate_genesis_batch_plan(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        GENESIS_BATCH_PLAN_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)

    payload = dict(value)
    observed = payload.pop("batchManifestHash")

    if observed != canonical_sha256(payload):
        raise ValueError("Genesis batch manifest hash mismatch.")

    return value


def _positive_prompt(
    identity: Mapping[str, Any],
    art_spec: Mapping[str, Any],
    lore: Mapping[str, Any],
) -> str:
    dna = identity["dna"]
    resonance = lore["resonance"]
    glyph = lore["glyph"]["geometry"]

    return (
        f"{identity['canonicalName']}, {identity['title']}. "
        "A unique colossal primordial dragon, ancient, foundational, "
        "monumental, dark, heavy, powerful and mysterious. "
        f"Body structure: {dna['bodyStructure']}. "
        f"Horn architecture: {dna['hornArchitecture']}. "
        f"Wing geometry: {dna['wingGeometry']}. "
        f"Pose: {dna['poseProfile']}. "
        "Believable quadrupedal dragon anatomy, massive coherent wings, "
        "balanced tail, clear monumental silhouette, full body visible. "
        f"Environment: {dna['environment']}, gothic megalithic architecture, "
        "mineral fog, controlled ash and primordial storm. "
        f"Materials: {dna['primaryMaterial']}, "
        f"{dna['secondaryMaterial']}, weathered stone, dark forged metal, "
        "ancient proto-technology. "
        f"Resonance class {resonance['resonanceClass']} influences "
        f"a restrained {glyph['spokes']}-spoke structural rhythm in horns, "
        "wings, cracks, engravings and architecture. "
        f"Lighting: {dna['lightingProfile']}, cinematic high contrast, "
        "restrained cyan and crimson mineral accents. "
        "Extreme physically coherent material detail, erosion, fractures, "
        "scratches, mineral deposits, scale variation, detailed eyes. "
        "Original OriginX visual grammar, cinematic dark fantasy realism, "
        "square composition, macro correctness before micro detail."
    )


def _negative_prompt() -> str:
    return (
        "generic fantasy dragon, franchise character, cartoon, anime, "
        "cute, toy, excessive neon, cyberpunk city, text, letters, logo, "
        "watermark, signature, duplicate dragon, extra heads, extra limbs, "
        "missing limbs, malformed anatomy, disconnected wings, tiny wings, "
        "broken tail, floating body, cropped body, blurry, low detail, "
        "flat lighting, plastic material, oversaturated colors"
    )


def build_genesis_batch_plan() -> dict[str, Any]:
    prepared = build_genesis_batch_plans()
    tokens = []

    for item in prepared:
        token_id = item["tokenId"]
        identity = build_genesis_identity(token_id)
        lore = build_genesis_lore(token_id)
        binding = item["binding"]

        token_dir = (
            f"output/genesis/batch-0001/"
            f"token-{token_id:04d}"
        )
        output_path = (
            f"{token_dir}/candidate/"
            f"token-{token_id:04d}-candidate-001.png"
        )

        command = [
            RUNTIME_PATH,
            "--model",
            MODEL_PATH,
            "--prompt",
            _positive_prompt(identity, item["artSpec"], lore),
            "--negative-prompt",
            _negative_prompt(),
            "--width",
            "512",
            "--height",
            "512",
            "--steps",
            str(binding["sampling"]["steps"]),
            "--cfg-scale",
            str(binding["sampling"]["cfg"]),
            "--sampling-method",
            binding["sampling"]["sampler"],
            "--seed",
            str(binding["sampling"]["seed"]),
            "--threads",
            "4",
            "--params-backend",
            "disk",
            "--mmap",
            "--vae-tiling",
            "--vae-tile-size",
            "128x128",
            "--output",
            output_path,
            "--verbose",
        ]

        tokens.append({
            "tokenId": token_id,
            "serial": identity["serial"],
            "canonicalName": identity["canonicalName"],
            "dnaHash": identity["dnaHash"],
            "resonanceSignature": lore[
                "resonance"
            ]["resonanceSignature"],
            "glyphHash": lore["glyph"]["svgHash"],
            "artSpecHash": item["artSpecHash"],
            "renderPlanHash": item["renderPlanHash"],
            "bindingHash": binding["bindingHash"],
            "seed": binding["sampling"]["seed"],
            "positivePrompt": command[4],
            "negativePrompt": command[6],
            "candidatePath": output_path,
            "command": command,
            "state": "PREPARED_NOT_EXECUTED",
            "canonical": False,
        })

    payload = {
        "batchPlanVersion": GENESIS_BATCH_PLAN_VERSION,
        "batchId": "GENESIS-BATCH-0001",
        "range": "#0001-#0010",
        "tokensRequested": 10,
        "model": {
            "modelId": "OX-MODEL-002",
            "productionAlias": "OX-GENESIS-MODEL-1",
            "modelHash": MODEL_HASH,
            "status": "CANDIDATE_PENDING_GENESIS_GATE",
        },
        "executionPolicy": {
            "mode": "SEQUENTIAL",
            "batchSize": 1,
            "stopOnFailure": True,
            "stopOnDeviceRestart": True,
            "timeoutSecondsPerToken": 5400,
            "cooldownSecondsBetweenTokens": 120,
            "minimumMemAvailableKB": 1200000,
            "maximumThermalRaw": 80000,
            "thermalLimitAppliedOnlyWhenSensorAvailable": True,
            "nextBatchAutomatic": False,
            "executionAllowed": False,
        },
        "tokens": tokens,
    }

    value = {
        **payload,
        "batchManifestHash": canonical_sha256(payload),
    }

    validate_genesis_batch_plan(value)
    return value


def write_genesis_batch_contracts(
    root: Path,
) -> dict[str, Any]:
    plan = build_genesis_batch_plan()
    prepared = build_genesis_batch_plans()

    root.mkdir(parents=True, exist_ok=True)

    for item in prepared:
        token_id = item["tokenId"]
        token_root = root / f"token-{token_id:04d}"
        contract_root = token_root / "contracts"
        candidate_root = token_root / "candidate"

        contract_root.mkdir(parents=True, exist_ok=True)
        candidate_root.mkdir(parents=True, exist_ok=True)

        documents = {
            "identity.json": build_genesis_identity(token_id),
            "lore.json": build_genesis_lore(token_id),
            "art-spec.json": item["artSpec"],
            "render-plan.json": item["renderPlan"],
            "runtime-binding.json": item["binding"],
        }

        for filename, value in documents.items():
            (contract_root / filename).write_text(
                canonical_json(value),
                encoding="utf-8",
            )

    (root / "batch-plan.json").write_text(
        canonical_json(plan),
        encoding="utf-8",
    )

    return plan
