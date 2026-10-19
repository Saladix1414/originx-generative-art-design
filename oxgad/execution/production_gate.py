"""Authoritative fail-closed model execution gate for OriginX.

No model/backend execution should be authorized merely because an
historical plan, approval phrase, model binding, acquisition record,
or diagnostic contract exists.

Current operational governance always has precedence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]

SD15_STATUS_PATH = (
    REPO_ROOT
    / "docs"
    / "local-generator"
    / "phase96-sd15-operational-status.json"
)

GENESIS_MANIFEST_PATH = (
    REPO_ROOT
    / "output"
    / "manifests"
    / "genesis-batch-0001.json"
)

VALID_MODES = {
    "PRODUCTION",
    "DIAGNOSTIC",
}


class ProductionExecutionDenied(RuntimeError):
    """Raised when the authoritative execution gate denies inference."""

    def __init__(
        self,
        reason_codes: list[str],
    ) -> None:
        self.reason_codes = tuple(reason_codes)

        super().__init__(
            "OriginX execution denied: "
            + ", ".join(reason_codes)
        )


def _read_json(
    path: Path,
) -> dict[str, Any] | None:
    if not path.is_file():
        return None

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def _production_output_forbidden(
    output_path: str | Path | None,
) -> bool:
    if output_path is None:
        return False

    normalized = str(
        output_path
    ).replace(
        "\\",
        "/",
    ).lower()

    production_markers = (
        "/output/genesis/",
        "output/genesis/",
    )

    canonical_markers = (
        "/canonical/",
        "/candidate/",
    )

    return (
        any(
            marker in normalized
            for marker in production_markers
        )
        and any(
            marker in normalized
            for marker in canonical_markers
        )
    )


def evaluate_execution_gate(
    *,
    model_id: str,
    mode: str,
    model_status: Mapping[str, Any] | None,
    manifest: Mapping[str, Any] | None = None,
    render_plan: Mapping[str, Any] | None = None,
    runtime_binding: Mapping[str, Any] | None = None,
    token_execution_approved: bool = False,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Evaluate execution authority without invoking any backend."""

    if mode not in VALID_MODES:
        raise ValueError(
            f"Unsupported execution mode: {mode}"
        )

    reasons: list[str] = []

    if model_status is None:
        reasons.append(
            "MODEL_OPERATIONAL_STATUS_UNAVAILABLE"
        )
    else:
        if (
            model_status.get("modelId")
            != model_id
        ):
            reasons.append(
                "MODEL_OPERATIONAL_STATUS_ID_MISMATCH"
            )

        status = model_status.get(
            "status"
        )

        governance = model_status.get(
            "governance",
            {},
        )

        if (
            status
            == "REJECTED_FOR_PRODUCTION"
        ):
            reasons.append(
                "MODEL_REJECTED_FOR_PRODUCTION"
            )

        if (
            governance.get(
                "executionAllowed"
            )
            is not True
        ):
            reasons.append(
                "MODEL_EXECUTION_NOT_AUTHORIZED"
            )

        if mode == "PRODUCTION":
            if (
                status
                != "APPROVED_FOR_PRODUCTION"
            ):
                reasons.append(
                    "MODEL_NOT_APPROVED_FOR_PRODUCTION"
                )

        if mode == "DIAGNOSTIC":
            if (
                governance.get(
                    "additionalRendersAllowed"
                )
                is not True
            ):
                reasons.append(
                    "ADDITIONAL_RENDERS_NOT_ALLOWED"
                )

    if mode == "PRODUCTION":
        if manifest is None:
            reasons.append(
                "COLLECTION_MANIFEST_UNAVAILABLE"
            )
        else:
            production_model = (
                manifest.get(
                    "productionModel"
                )
            )

            if (
                production_model
                in (
                    None,
                    "",
                    "UNASSIGNED",
                )
            ):
                reasons.append(
                    "PRODUCTION_MODEL_UNASSIGNED"
                )
            elif (
                production_model
                != model_id
            ):
                reasons.append(
                    "PRODUCTION_MODEL_MISMATCH"
                )

            if (
                manifest.get(
                    "renderAuthorized"
                )
                is not True
            ):
                reasons.append(
                    "COLLECTION_RENDER_NOT_AUTHORIZED"
                )

        if render_plan is None:
            reasons.append(
                "RENDER_PLAN_UNAVAILABLE"
            )
        else:
            plan_model = render_plan.get(
                "modelBinding",
                {},
            )

            execution_policy = (
                render_plan.get(
                    "executionPolicy",
                    {},
                )
            )

            if (
                plan_model.get(
                    "status"
                )
                != "BOUND"
            ):
                reasons.append(
                    "RENDER_PLAN_UNBOUND"
                )

            if (
                execution_policy.get(
                    "executionAllowed"
                )
                is not True
            ):
                reasons.append(
                    "RENDER_PLAN_EXECUTION_DENIED"
                )

            bound_model_id = (
                plan_model.get(
                    "modelId"
                )
            )

            if (
                bound_model_id
                not in (
                    None,
                    model_id,
                )
            ):
                reasons.append(
                    "RENDER_PLAN_MODEL_MISMATCH"
                )

        if runtime_binding is None:
            reasons.append(
                "RUNTIME_BINDING_UNAVAILABLE"
            )
        else:
            runtime_authority = (
                runtime_binding.get(
                    "authority",
                    {},
                )
            )

            runtime_model = (
                runtime_binding.get(
                    "model",
                    {},
                )
            )

            if (
                runtime_authority.get(
                    "executionAllowed"
                )
                is not True
            ):
                reasons.append(
                    "RUNTIME_EXECUTION_DENIED"
                )

            runtime_model_id = (
                runtime_model.get(
                    "modelId"
                )
            )

            if (
                runtime_model_id
                != model_id
            ):
                reasons.append(
                    "RUNTIME_MODEL_MISMATCH"
                )

            plan_hash = None

            if render_plan is not None:
                plan_hash = (
                    render_plan.get(
                        "modelBinding",
                        {},
                    ).get(
                        "modelHash"
                    )
                )

            runtime_hash = (
                runtime_model.get(
                    "modelHash"
                )
            )

            if (
                plan_hash is not None
                and runtime_hash is not None
                and plan_hash
                != runtime_hash
            ):
                reasons.append(
                    "MODEL_HASH_MISMATCH"
                )

        if (
            token_execution_approved
            is not True
        ):
            reasons.append(
                "TOKEN_EXECUTION_APPROVAL_MISSING"
            )

    if mode == "DIAGNOSTIC":
        if _production_output_forbidden(
            output_path
        ):
            reasons.append(
                "DIAGNOSTIC_OUTPUT_PATH_FORBIDDEN"
            )

    # Stable deterministic ordering with no duplicates.
    reason_codes = list(
        dict.fromkeys(
            reasons
        )
    )

    return {
        "gateVersion": (
            "OX-PRODUCTION-EXECUTION-GATE-1"
        ),
        "modelId": model_id,
        "mode": mode,
        "allowed": not reason_codes,
        "reasonCodes": reason_codes,
        "authorityPrecedence": [
            "CURRENT_OPERATIONAL_MODEL_STATUS",
            "PRODUCTION_EXECUTION_GATE",
            "CURRENT_RENDER_PLAN",
            "CURRENT_RUNTIME_BINDING",
            "HISTORICAL_MODEL_REFERENCES",
        ],
    }


def _load_current_status(
    model_id: str,
) -> dict[str, Any] | None:
    if model_id == "OX-MODEL-002":
        value = _read_json(
            SD15_STATUS_PATH
        )

        if value is None:
            return None

        if (
            value.get("modelId")
            != "OX-MODEL-002"
        ):
            return None

        return value

    # No current approved operational contract is known
    # for another model through this gate yet.
    #
    # Fail closed until an explicit operational-status
    # authority is registered.
    return None


def _token_contract_path(
    token_id: int,
    filename: str,
) -> Path:
    return (
        REPO_ROOT
        / "output"
        / "genesis"
        / "batch-0001"
        / f"token-{token_id:04d}"
        / "contracts"
        / filename
    )


def _token_execution_approved(
    token_id: int,
) -> bool:
    approval = _read_json(
        _token_contract_path(
            token_id,
            "execution-approval.json",
        )
    )

    if approval is None:
        return False

    return (
        approval.get(
            "executionAllowed"
        )
        is True
        and approval.get(
            "approved"
        )
        is True
    )


def assert_current_execution_allowed(
    *,
    model_id: str,
    token_id: int,
    mode: str,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load current repository authority and fail closed."""

    status = _load_current_status(
        model_id
    )

    manifest = None
    render_plan = None
    runtime_binding = None
    token_approved = False

    if mode == "PRODUCTION":
        manifest = _read_json(
            GENESIS_MANIFEST_PATH
        )

        render_plan = _read_json(
            _token_contract_path(
                token_id,
                "render-plan.json",
            )
        )

        runtime_binding = _read_json(
            _token_contract_path(
                token_id,
                "runtime-binding.json",
            )
        )

        token_approved = (
            _token_execution_approved(
                token_id
            )
        )

    decision = evaluate_execution_gate(
        model_id=model_id,
        mode=mode,
        model_status=status,
        manifest=manifest,
        render_plan=render_plan,
        runtime_binding=runtime_binding,
        token_execution_approved=token_approved,
        output_path=output_path,
    )

    if decision["allowed"] is not True:
        raise ProductionExecutionDenied(
            decision["reasonCodes"]
        )

    return decision


__all__ = (
    "ProductionExecutionDenied",
    "assert_current_execution_allowed",
    "evaluate_execution_gate",
)
