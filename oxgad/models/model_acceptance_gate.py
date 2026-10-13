"""Permanent OriginX Model Acceptance Gate."""

from __future__ import annotations

from typing import Any


MODEL_ACCEPTANCE_GATE_VERSION = (
    "OX-MODEL-ACCEPTANCE-GATE-1"
)

ORDERED_STAGES = (
    "HARDWARE_PREFLIGHT",
    "MINIMAL_INFERENCE_PREFLIGHT",
    "FULL_REPRESENTATIVE_GENERATION",
    "IMAGE_INTEGRITY_INSPECTION",
    "VISUAL_QUALITY_GATE",
    "PRODUCTION_PROMOTION",
)


def build_model_acceptance_gate() -> dict[str, Any]:
    return {
        "gateVersion": MODEL_ACCEPTANCE_GATE_VERSION,
        "invariant": (
            "ONE_STEP_PREFLIGHT != PRODUCTION_VALIDATION"
        ),
        "orderedStages": list(ORDERED_STAGES),
        "promotionRequirements": {
            "hardwarePreflightPassed": True,
            "minimalInferencePreflightPassed": True,
            "fullRepresentativeGenerationPassed": True,
            "imageIntegrityInspectionPassed": True,
            "visualQualityGatePassed": True,
            "allPriorStagesRequired": True,
        },
        "governance": {
            "oneStepPreflightGrantsProductionStatus": False,
            "stageSkippingAllowed": False,
            "silentWeightSubstitutionAllowed": False,
            "promotionRequiresExplicitEvidence": True,
        },
    }


def model_acceptance_passed(
    *,
    hardware_preflight: bool,
    minimal_inference_preflight: bool,
    full_representative_generation: bool,
    image_integrity_inspection: bool,
    visual_quality_gate: bool,
) -> bool:
    return all((
        hardware_preflight,
        minimal_inference_preflight,
        full_representative_generation,
        image_integrity_inspection,
        visual_quality_gate,
    ))


__all__ = (
    "MODEL_ACCEPTANCE_GATE_VERSION",
    "ORDERED_STAGES",
    "build_model_acceptance_gate",
    "model_acceptance_passed",
)
