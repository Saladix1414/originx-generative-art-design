"""Execution gate for GENESIS-BATCH-0001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


GENESIS_BATCH_EXECUTION_GATE_VERSION = (
    "OX-GENESIS-BATCH-EXECUTION-GATE-1"
)

GENESIS_BATCH_EXECUTION_APPROVAL_PHRASE = (
    "I APPROVE GENESIS-BATCH-0001 TOKENS 0001 THROUGH 0010"
)

GENESIS_BATCH_EXECUTION_GATE_SCHEMA_PATH = Path(
    "schemas/ox-genesis-batch-execution-gate-1.schema.json"
)


def validate_genesis_batch_execution_gate(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:
    schema = json.loads(
        GENESIS_BATCH_EXECUTION_GATE_SCHEMA_PATH.read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(dict(value), schema)
    return value


def build_genesis_batch_execution_gate() -> dict[str, Any]:
    value = {
        "gateVersion": GENESIS_BATCH_EXECUTION_GATE_VERSION,
        "batchId": "GENESIS-BATCH-0001",
        "range": "#0001-#0010",
        "state": "PENDING_EXPLICIT_APPROVAL",
        "approval": {
            "required": True,
            "present": False,
            "phraseAccepted": False,
            "requiredPhrase": (
                GENESIS_BATCH_EXECUTION_APPROVAL_PHRASE
            ),
        },
        "limits": {
            "tokens": 10,
            "batchSize": 1,
            "width": 512,
            "height": 512,
            "steps": 12,
            "timeoutSecondsPerToken": 5400,
            "cooldownSecondsBetweenTokens": 120,
            "minimumMemAvailableKB": 1200000,
            "maximumThermalRaw": 80000,
        },
        "stopConditions": [
            "TOKEN_FAILURE",
            "RUNTIME_CRASH",
            "OUTPUT_MISSING",
            "LOW_AVAILABLE_MEMORY",
            "THERMAL_LIMIT",
            "DEVICE_RESTART",
            "MODEL_HASH_MISMATCH",
            "USER_INTERRUPTION",
        ],
        "governance": {
            "gateGrantsExecutionAuthority": False,
            "executionAllowed": False,
            "automaticRetryAllowed": False,
            "canonicalizationAllowed": False,
            "nextBatchAllowed": False,
            "finalModelPromotionAllowed": False,
        },
    }

    validate_genesis_batch_execution_gate(value)
    return value
