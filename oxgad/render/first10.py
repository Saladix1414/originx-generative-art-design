"""Canonical first-10 OX-RENDER-1 evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from oxgad import ART_SPEC_VERSION, RENDER_VERSION
from oxgad.render.compiler import (
    RENDER_COMPILER_VERSION,
    RenderPlanCompilation,
    compile_render_plan,
)
from oxgad.render.validator import validate_render_plan
from oxgad.structure.canonical import canonical_json
from oxgad.structure.first10 import generate_first_10


RENDER_FIRST10_MANIFEST_VERSION = (
    "OX-RENDER-FIRST10-MANIFEST-1"
)


def generate_first_10_render_plans(
) -> tuple[RenderPlanCompilation, ...]:
    """Compile the canonical first ten Art Specs."""
    return tuple(
        compile_render_plan(assembly)
        for assembly in generate_first_10()
    )


def build_first_10_render_manifest() -> dict[str, Any]:
    """Build canonical evidence for first-ten Render Plans."""
    assemblies = generate_first_10()
    compilations = tuple(
        compile_render_plan(assembly)
        for assembly in assemblies
    )

    entries: list[dict[str, Any]] = []

    for assembly, compilation in zip(
        assemblies,
        compilations,
        strict=True,
    ):
        plan = compilation.render_plan
        validate_render_plan(plan)

        source = plan["source"]
        identity = plan["identity"]
        model = plan["modelBinding"]
        execution = plan["executionPolicy"]

        if source["artSpecHash"] != assembly.art_spec_hash:
            raise ValueError("Art Spec evidence mismatch.")

        if source["artRuleHash"] != assembly.art_rule_hash:
            raise ValueError("Art Rule evidence mismatch.")

        if source["designHash"] != assembly.design_hash:
            raise ValueError("Design evidence mismatch.")

        if source["seed"] != assembly.seed:
            raise ValueError("Seed evidence mismatch.")

        if model["status"] != "UNBOUND":
            raise ValueError("Model binding must remain UNBOUND.")

        if execution["executionAllowed"] is not False:
            raise ValueError("Execution must remain disabled.")

        entries.append({
            "tokenId": identity["tokenId"],
            "serial": identity["serial"],
            "canonicalName": identity["canonicalName"],
            "tier": identity["tier"],
            "era": identity["era"],
            "dnaHash": identity["dnaHash"],
            "seed": source["seed"],
            "artSpecHash": source["artSpecHash"],
            "artRuleHash": source["artRuleHash"],
            "designHash": source["designHash"],
            "renderPlanHash": compilation.render_plan_hash,
            "modelBindingStatus": model["status"],
            "executionAllowed": execution["executionAllowed"],
        })

    return {
        "manifestVersion": RENDER_FIRST10_MANIFEST_VERSION,
        "artSpecVersion": ART_SPEC_VERSION,
        "renderVersion": RENDER_VERSION,
        "renderCompilerVersion": RENDER_COMPILER_VERSION,
        "count": len(entries),
        "modelBindingStatus": "UNBOUND",
        "executionAllowed": False,
        "entries": entries,
    }


def write_first_10_render_manifest(
    path: str | Path,
) -> Path:
    """Write canonical first-ten Render Plan evidence."""
    destination = Path(path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    destination.write_text(
        canonical_json(
            build_first_10_render_manifest()
        ),
        encoding="utf-8",
    )
    return destination


__all__ = (
    "RENDER_FIRST10_MANIFEST_VERSION",
    "build_first_10_render_manifest",
    "generate_first_10_render_plans",
    "write_first_10_render_manifest",
)
