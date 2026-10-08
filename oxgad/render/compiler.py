"""Deterministic OX-ART-SPEC-1 to OX-RENDER-1 compiler."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from oxgad import RENDER_VERSION
from oxgad.design.art_rules import art_rule_hash
from oxgad.design.integration import integrated_design_hash
from oxgad.render.validator import validate_render_plan
from oxgad.structure.assembler import ArtSpecAssembly
from oxgad.structure.canonical import (
    art_spec_hash,
    canonical_json,
    canonical_sha256,
)


RENDER_COMPILER_VERSION = "OX-RENDER-COMPILER-1"


class RenderPlanCompilationError(ValueError):
    """Raised when canonical render compilation cannot proceed."""


@dataclass(frozen=True, slots=True)
class RenderPlanCompilation:
    render_plan: dict[str, Any]
    render_plan_hash: str


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def _segment(
    name: str,
    value: Any,
) -> str:
    return f"{name}={canonical_json(value)}"


def _validate_source_evidence(
    assembly: ArtSpecAssembly,
) -> None:
    art_spec = assembly.art_spec

    if art_spec.get("seed") != assembly.seed:
        raise RenderPlanCompilationError(
            "Art Spec seed does not match assembly evidence."
        )

    actual_art_spec_hash = art_spec_hash(art_spec)

    if actual_art_spec_hash != assembly.art_spec_hash:
        raise RenderPlanCompilationError(
            "Art Spec hash does not match assembly evidence."
        )

    identity = art_spec.get("identity")

    if not isinstance(identity, dict):
        raise RenderPlanCompilationError(
            "Art Spec identity is missing."
        )

    tier = identity.get("tier")

    if not isinstance(tier, str):
        raise RenderPlanCompilationError(
            "Art Spec tier is missing."
        )

    expected_rule_hash = art_rule_hash(
        tier=tier,
        seed=assembly.seed,
    )

    if expected_rule_hash != assembly.art_rule_hash:
        raise RenderPlanCompilationError(
            "Art Rule hash does not match deterministic evidence."
        )

    expected_design_hash = integrated_design_hash(
        tier=tier,
        seed=assembly.seed,
    )

    if expected_design_hash != assembly.design_hash:
        raise RenderPlanCompilationError(
            "Design hash does not match deterministic evidence."
        )


def _compile_prompt_segments(
    art_spec: dict[str, Any],
) -> list[str]:
    return [
        _segment("identity", art_spec["identity"]),
        _segment("dragon", art_spec["dragon"]),
        _segment("environment", art_spec["environment"]),
        _segment("pose", art_spec["pose"]),
        _segment("lighting", art_spec["lighting"]),
        _segment("colorPolicy", art_spec["colorPolicy"]),
        _segment("resonance", art_spec["resonance"]),
        _segment("renderIntent", art_spec["renderIntent"]),
        _segment("detail.macro", art_spec["detail"]["macro"]),
        _segment("detail.meso", art_spec["detail"]["meso"]),
        _segment("detail.micro", art_spec["detail"]["micro"]),
    ]


def _compile_negative_constraints(
    art_spec: dict[str, Any],
) -> list[str]:
    source = art_spec["negativeConstraints"]

    constraints = [
        "forbid:franchise-imitation",
        "forbid:watermark",
        "forbid:uncontrolled-text",
        "forbid:cartoon-styling",
        "forbid:detail-masking-bad-anatomy",
    ]

    constraints.extend(
        f"forbid-element:{value}"
        for value in source["forbiddenElements"]
    )

    return _ordered_unique(constraints)


def render_plan_hash(
    render_plan: dict[str, Any],
) -> str:
    validate_render_plan(render_plan)
    return canonical_sha256(render_plan)


def compile_render_plan(
    assembly: ArtSpecAssembly,
) -> RenderPlanCompilation:
    if not isinstance(assembly, ArtSpecAssembly):
        raise RenderPlanCompilationError(
            "compile_render_plan requires ArtSpecAssembly."
        )

    _validate_source_evidence(assembly)

    art_spec = deepcopy(assembly.art_spec)
    identity = art_spec["identity"]
    framing = art_spec["framing"]
    composition = art_spec["composition"]
    render_intent = art_spec["renderIntent"]

    render_plan: dict[str, Any] = {
        "renderVersion": RENDER_VERSION,
        "source": {
            "artSpecVersion": art_spec["specVersion"],
            "artSpecHash": assembly.art_spec_hash,
            "artRuleHash": assembly.art_rule_hash,
            "designHash": assembly.design_hash,
            "seed": assembly.seed,
        },
        "identity": {
            "tokenId": identity["tokenId"],
            "serial": identity["serial"],
            "canonicalName": identity["canonicalName"],
            "tier": identity["tier"],
            "era": identity["era"],
            "dnaHash": identity["dnaHash"],
        },
        "promptProgram": {
            "compilerPolicy": "STRUCTURED_DETERMINISTIC",
            "identityPreservation": True,
            "orderedSegments": _compile_prompt_segments(
                art_spec
            ),
        },
        "negativeProgram": {
            "compilerPolicy": "STRUCTURED_DETERMINISTIC",
            "constraints": _compile_negative_constraints(
                art_spec
            ),
        },
        "camera": deepcopy(art_spec["camera"]),
        "composition": {
            "dominance": composition["dominance"],
            "balance": composition["balance"],
            "symmetry": composition["symmetry"],
            "ruleOfThirds": composition["ruleOfThirds"],
            "environmentRatio": composition["environmentRatio"],
            "depthPriority": composition["depthPriority"],
            "leadingGeometry": deepcopy(
                composition["leadingGeometry"]
            ),
            "cropPolicy": framing["cropPolicy"],
            "subjectOccupancy": framing["subjectOccupancy"],
            "safeMargin": framing["safeMargin"],
        },
        "materials": deepcopy(art_spec["materials"]),
        "sampling": {
            "sampler": "UNBOUND",
            "steps": 1,
            "cfg": 0.0,
            "denoise": 1.0,
            "seed": assembly.seed,
        },
        "resolution": {
            "width": render_intent["targetResolution"]["width"],
            "height": render_intent["targetResolution"]["height"],
            "aspectRatio": framing["aspectRatio"],
        },
        "modelBinding": {
            "status": "UNBOUND",
            "modelName": None,
            "modelVersion": None,
            "modelHash": None,
            "requiredCapabilities": [
                "text-conditioned-image-generation",
            ],
        },
        "conditioning": {
            "loraSlots": [],
            "controlNetSlots": [],
        },
        "detailPolicy": {
            "authorityOrder": [
                "MACRO",
                "MESO",
                "MICRO",
            ],
            "macroFirst": True,
            "microCannotMaskBadAnatomy": True,
            "detailDensity": render_intent["detailDensity"],
        },
        "upscalePolicy": {
            "mode": "DISABLED",
            "enabled": False,
            "targetResolution": None,
        },
        "executionPolicy": {
            "policy": "LOCAL_FIRST",
            "providerIndependent": True,
            "executionAllowed": False,
            "target": "UNBOUND",
        },
    }

    validate_render_plan(render_plan)

    return RenderPlanCompilation(
        render_plan=render_plan,
        render_plan_hash=canonical_sha256(render_plan),
    )


__all__ = (
    "RENDER_COMPILER_VERSION",
    "RenderPlanCompilation",
    "RenderPlanCompilationError",
    "compile_render_plan",
    "render_plan_hash",
)
