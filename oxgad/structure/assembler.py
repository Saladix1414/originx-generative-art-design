"""OX-GAD PHASE 2D — deterministic OX-ART-SPEC-1 assembler."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from oxgad import ART_SPEC_VERSION
from oxgad.design.art_rules import (
    ART_RULE_CATALOG_VERSION,
    art_rule_hash,
    select_art_rules,
)
from oxgad.structure.canonical import (
    art_spec_hash,
    canonical_json,
)
from oxgad.structure.deterministic import (
    deterministic_choice,
    deterministic_index,
    resolve_seed,
)
from oxgad.structure.input import StructureInput
from oxgad.structure.validator import (
    ArtSpecValidationError,
    load_art_spec_schema,
    validate_art_spec,
)


STRUCTURE_ASSEMBLER_VERSION = (
    "OX-STRUCTURE-ASSEMBLER-1"
)


class ArtSpecAssemblyError(ValueError):
    """Raised when a complete Art Spec cannot be assembled."""


@dataclass(frozen=True, slots=True)
class ArtSpecAssembly:
    """Validated deterministic assembly result."""

    art_spec: dict[str, Any]
    art_spec_hash: str
    art_rule_hash: str
    seed: int


def _resolve_ref(
    ref: str,
    root: dict[str, Any],
) -> dict[str, Any]:
    prefix = "#/$defs/"

    if not ref.startswith(prefix):
        raise ArtSpecAssemblyError(
            f"Unsupported schema reference: {ref!r}."
        )

    name = ref[len(prefix):]

    try:
        resolved = root["$defs"][name]
    except KeyError as exc:
        raise ArtSpecAssemblyError(
            f"Unknown schema definition: {name!r}."
        ) from exc

    if not isinstance(resolved, dict):
        raise ArtSpecAssemblyError(
            f"Schema definition {name!r} is not an object."
        )

    return resolved


def _pattern_string(
    schema: dict[str, Any],
    *,
    namespace: str,
) -> str:
    pattern = schema.get("pattern")

    minimum = max(
        int(schema.get("minLength", 0)),
        1,
    )

    candidates = (
        "#0001",
        "sha256:" + ("0" * 64),
        "OriginX",
        namespace.replace(".", "-"),
        "x" * minimum,
    )

    if pattern is not None:
        regex = re.compile(pattern)

        for candidate in candidates:
            if regex.fullmatch(candidate):
                return candidate

        raise ArtSpecAssemblyError(
            "Unable to synthesize a value for "
            f"schema pattern {pattern!r}."
        )

    value = (
        namespace.replace(".", "-")
        or "originx"
    )

    if len(value) < minimum:
        value += "x" * (
            minimum - len(value)
        )

    maximum = schema.get("maxLength")

    if maximum is not None:
        value = value[: int(maximum)]

    return value


def _schema_value(
    schema: dict[str, Any],
    root: dict[str, Any],
    *,
    seed: int,
    namespace: str,
) -> Any:
    if "$ref" in schema:
        return _schema_value(
            _resolve_ref(
                schema["$ref"],
                root,
            ),
            root,
            seed=seed,
            namespace=namespace,
        )

    if "const" in schema:
        return copy.deepcopy(
            schema["const"]
        )

    if "enum" in schema:
        values = schema["enum"]

        if not values:
            raise ArtSpecAssemblyError(
                f"Empty enum at {namespace}."
            )

        return copy.deepcopy(
            deterministic_choice(
                values,
                seed=seed,
                namespace=(
                    f"{STRUCTURE_ASSEMBLER_VERSION}."
                    f"{namespace}.enum"
                ),
            )
        )

    if "default" in schema:
        return copy.deepcopy(
            schema["default"]
        )

    if "oneOf" in schema:
        branches = schema["oneOf"]

        index = deterministic_index(
            seed=seed,
            namespace=(
                f"{STRUCTURE_ASSEMBLER_VERSION}."
                f"{namespace}.oneOf"
            ),
            size=len(branches),
        )

        return _schema_value(
            branches[index],
            root,
            seed=seed,
            namespace=(
                f"{namespace}.oneOf[{index}]"
            ),
        )

    if "anyOf" in schema:
        branches = schema["anyOf"]

        index = deterministic_index(
            seed=seed,
            namespace=(
                f"{STRUCTURE_ASSEMBLER_VERSION}."
                f"{namespace}.anyOf"
            ),
            size=len(branches),
        )

        return _schema_value(
            branches[index],
            root,
            seed=seed,
            namespace=(
                f"{namespace}.anyOf[{index}]"
            ),
        )

    if "allOf" in schema:
        result: Any = {}

        for index, child in enumerate(
            schema["allOf"]
        ):
            value = _schema_value(
                child,
                root,
                seed=seed,
                namespace=(
                    f"{namespace}.allOf[{index}]"
                ),
            )

            if (
                isinstance(result, dict)
                and isinstance(value, dict)
            ):
                result.update(value)
            else:
                result = value

        return result

    schema_type = schema.get("type")

    if isinstance(schema_type, list):
        candidates = [
            item
            for item in schema_type
            if item != "null"
        ]

        if not candidates:
            return None

        schema_type = candidates[0]

    if schema_type == "object":
        result: dict[str, Any] = {}

        properties = schema.get(
            "properties",
            {},
        )

        for field in schema.get(
            "required",
            [],
        ):
            field_schema = properties.get(
                field
            )

            if not isinstance(
                field_schema,
                dict,
            ):
                raise ArtSpecAssemblyError(
                    "Required schema property has "
                    f"no definition: "
                    f"{namespace}.{field}"
                )

            result[field] = _schema_value(
                field_schema,
                root,
                seed=seed,
                namespace=(
                    f"{namespace}.{field}"
                ),
            )

        minimum = int(
            schema.get(
                "minProperties",
                0,
            )
        )

        additional = schema.get(
            "additionalProperties",
            True,
        )

        counter = 1

        while len(result) < minimum:
            key = f"originxField{counter}"
            counter += 1

            if additional is False:
                raise ArtSpecAssemblyError(
                    "Schema requires additional "
                    "properties but forbids them "
                    f"at {namespace}."
                )

            if isinstance(
                additional,
                dict,
            ):
                result[key] = _schema_value(
                    additional,
                    root,
                    seed=seed,
                    namespace=(
                        f"{namespace}.{key}"
                    ),
                )
            else:
                result[key] = (
                    f"originx-{counter}"
                )

        return result

    if schema_type == "array":
        minimum = int(
            schema.get(
                "minItems",
                0,
            )
        )

        items = schema.get(
            "items",
            {},
        )

        if not isinstance(items, dict):
            raise ArtSpecAssemblyError(
                "Unsupported array schema "
                f"at {namespace}."
            )

        return [
            _schema_value(
                items,
                root,
                seed=seed,
                namespace=(
                    f"{namespace}[{index}]"
                ),
            )
            for index in range(minimum)
        ]

    if schema_type == "string":
        return _pattern_string(
            schema,
            namespace=namespace,
        )

    if schema_type == "integer":
        if "minimum" in schema:
            value = int(
                schema["minimum"]
            )
        elif "exclusiveMinimum" in schema:
            value = (
                int(
                    schema[
                        "exclusiveMinimum"
                    ]
                )
                + 1
            )
        else:
            value = 0

        maximum = schema.get("maximum")

        if (
            maximum is not None
            and value > int(maximum)
        ):
            raise ArtSpecAssemblyError(
                "Impossible integer range "
                f"at {namespace}."
            )

        return value

    if schema_type == "number":
        if "minimum" in schema:
            value = float(
                schema["minimum"]
            )
        elif "exclusiveMinimum" in schema:
            value = (
                float(
                    schema[
                        "exclusiveMinimum"
                    ]
                )
                + 0.01
            )
        else:
            value = 0.0

        maximum = schema.get("maximum")

        if (
            maximum is not None
            and value > float(maximum)
        ):
            raise ArtSpecAssemblyError(
                "Impossible numeric range "
                f"at {namespace}."
            )

        return value

    if schema_type == "boolean":
        return False

    if schema_type == "null":
        return None

    raise ArtSpecAssemblyError(
        "Unsupported schema fragment at "
        f"{namespace}: {schema!r}"
    )


def _replace_list(
    block: dict[str, Any],
    key: str,
    values: list[str],
) -> None:
    if isinstance(
        block.get(key),
        list,
    ):
        block[key] = list(values)


def _replace_string(
    block: dict[str, Any],
    key: str,
    value: str,
) -> None:
    if isinstance(
        block.get(key),
        str,
    ):
        block[key] = value


def _replace_number(
    block: dict[str, Any],
    key: str,
    value: float,
) -> None:
    current = block.get(key)

    if (
        isinstance(
            current,
            (int, float),
        )
        and not isinstance(
            current,
            bool,
        )
    ):
        block[key] = value


def _replace_boolean(
    block: dict[str, Any],
    key: str,
    value: bool,
) -> None:
    if isinstance(
        block.get(key),
        bool,
    ):
        block[key] = value


def _decorate_feature(
    block: dict[str, Any],
    *,
    descriptor: str,
    materials: list[str],
    notes: list[str],
) -> None:
    for key in (
        "form",
        "geometry",
        "structure",
        "style",
        "profile",
        "description",
        "type",
        "shape",
    ):
        _replace_string(
            block,
            key,
            descriptor,
        )

    _replace_string(
        block,
        "condition",
        "weathered-controlled",
    )

    _replace_list(
        block,
        "materials",
        materials,
    )

    _replace_list(
        block,
        "palette",
        materials,
    )

    _replace_list(
        block,
        "notes",
        notes,
    )


def _decorate_detail_layer(
    block: dict[str, Any],
    priorities: list[str],
) -> None:
    for key in (
        "targets",
        "features",
        "priorities",
        "requirements",
        "notes",
    ):
        _replace_list(
            block,
            key,
            priorities,
        )

    if priorities:
        for key in (
            "focus",
            "description",
            "intent",
        ):
            _replace_string(
                block,
                key,
                priorities[0],
            )


def _resonance_label(
    value: Mapping[str, Any],
) -> str:
    spectrum = value.get("spectrum")

    if (
        isinstance(spectrum, str)
        and spectrum.strip()
    ):
        return spectrum.strip()

    return canonical_json(value)


def _apply_quality_thresholds(
    value: Any,
) -> None:
    targets = {
        "anatomy": 0.90,
        "silhouette": 0.85,
        "composition": 0.82,
        "traitCompliance": 0.95,
        "material": 0.80,
        "detail": 0.80,
        "identityConsistency": 0.95,
        "visualGrammar": 0.90,
        "artifact": 0.90,
    }

    if isinstance(value, dict):
        for key, child in value.items():
            if (
                key in targets
                and isinstance(
                    child,
                    (int, float),
                )
                and not isinstance(
                    child,
                    bool,
                )
            ):
                value[key] = targets[key]
            else:
                _apply_quality_thresholds(
                    child
                )

    elif isinstance(value, list):
        for child in value:
            _apply_quality_thresholds(
                child
            )


def _apply_semantics(
    art_spec: dict[str, Any],
    *,
    structure_input: StructureInput,
    seed: int,
    rules: dict[str, Any],
) -> None:
    art_spec["specVersion"] = (
        ART_SPEC_VERSION
    )

    art_spec["seed"] = seed

    art_spec["identity"] = {
        "tokenId": structure_input.token_id,
        "serial": structure_input.serial,
        "canonicalName": (
            structure_input.canonical_name
        ),
        "tier": structure_input.tier,
        "era": rules["era"],
        "generationTheme": (
            structure_input.generation_theme
        ),
        "dna": copy.deepcopy(
            dict(structure_input.dna)
        ),
        "dnaHash": (
            structure_input.dna_hash
        ),
    }

    dragon = art_spec["dragon"]

    dragon["archetype"] = str(
        structure_input.dna.get(
            "archetype",
            rules[
                "dragon"
            ][
                "silhouette"
            ],
        )
    )

    selected_materials = [
        rules["materials"]["primary"],
        rules["materials"]["secondary"],
        rules["materials"]["accent"],
    ]

    dragon_features = {
        "bodyStructure": (
            rules["dragon"]["bodyMass"],
            [
                rules["dragon"]["silhouette"],
                rules["era"],
            ],
        ),
        "head": (
            rules["dragon"]["head"],
            [
                "identity-preserving cranial structure",
            ],
        ),
        "horns": (
            rules["dragon"]["horns"],
            [
                "tier-consistent horn language",
            ],
        ),
        "eyes": (
            (
                "resonance-influenced "
                f"{_resonance_label(structure_input.resonance)} eyes"
            ),
            [
                "resonance remains narrative only",
            ],
        ),
        "body": (
            rules["dragon"]["silhouette"],
            [
                rules["dragon"]["bodyMass"],
            ],
        ),
        "scales": (
            rules["materials"]["primary"],
            [
                "material hierarchy must follow anatomy",
            ],
        ),
        "wings": (
            rules["dragon"]["wings"],
            [
                "structural wing anatomy before detail",
            ],
        ),
        "tail": (
            "anatomically balanced counterweight tail",
            [
                "tail follows body mass and pose",
            ],
        ),
        "armor": (
            rules["dragon"]["armor"],
            [
                rules["technology"]["language"],
            ],
        ),
        "mechanicalAugmentation": (
            rules[
                "dragon"
            ][
                "augmentation"
            ],
            [
                rules["technology"]["language"],
                "augmentation must preserve base identity",
            ],
        ),
        "markings": (
            (
                "controlled resonance-influenced "
                "structural markings"
            ),
            [
                _resonance_label(
                    structure_input.resonance
                ),
            ],
        ),
    }

    for field, (
        descriptor,
        notes,
    ) in dragon_features.items():
        block = dragon.get(field)

        if not isinstance(block, dict):
            raise ArtSpecAssemblyError(
                f"Expected dragon.{field} "
                "to be an object."
            )

        _decorate_feature(
            block,
            descriptor=descriptor,
            materials=selected_materials,
            notes=notes,
        )

    environment = art_spec[
        "environment"
    ]

    environment["biome"] = (
        f"{rules['era']} monumental biome"
    )

    environment["terrain"] = (
        f"{rules['materials']['primary']} "
        "megalithic terrain"
    )

    environment["atmosphere"] = (
        rules[
            "environment"
        ][
            "atmosphere"
        ]
    )

    environment["weather"] = (
        "controlled atmospheric weathering"
    )

    architecture = environment.get(
        "architecture"
    )

    if not isinstance(
        architecture,
        dict,
    ):
        raise ArtSpecAssemblyError(
            "Expected environment.architecture "
            "to be an object."
        )

    _decorate_feature(
        architecture,
        descriptor=rules[
            "environment"
        ][
            "architecture"
        ],
        materials=selected_materials,
        notes=[
            rules["technology"]["language"],
            "monumental OriginX environmental scale",
        ],
    )

    depth_layers = environment.get(
        "depthLayers"
    )

    if not isinstance(
        depth_layers,
        dict,
    ):
        raise ArtSpecAssemblyError(
            "Expected environment.depthLayers "
            "to be an object."
        )

    _replace_list(
        depth_layers,
        "foreground",
        [
            (
                f"{rules['materials']['primary']} "
                "terrain mass"
            ),
        ],
    )

    _replace_list(
        depth_layers,
        "midground",
        [
            rules[
                "environment"
            ][
                "architecture"
            ],
        ],
    )

    _replace_list(
        depth_layers,
        "background",
        [
            rules[
                "environment"
            ][
                "atmosphere"
            ],
        ],
    )

    camera = art_spec["camera"]

    camera["projection"] = "PERSPECTIVE"

    camera["lensMm"] = (
        deterministic_choice(
            (
                28,
                35,
                50,
            ),
            seed=seed,
            namespace=(
                f"{STRUCTURE_ASSEMBLER_VERSION}."
                "camera.lens"
            ),
        )
    )

    camera["height"] = "LOW"
    camera["pitchDegrees"] = -4.0
    camera["yawDegrees"] = 0.0
    camera["rollDegrees"] = 0.0

    camera["focalTarget"] = (
        structure_input.canonical_name
    )

    camera["distance"] = "WIDE"

    pose = art_spec["pose"]

    pose["stance"] = (
        "grounded monumental apex stance"
    )
    pose["motionState"] = (
        "controlled latent motion"
    )
    pose["headDirection"] = (
        "toward primary focal axis"
    )
    pose["wingState"] = (
        rules["dragon"]["wings"]
    )
    pose["tailFlow"] = (
        "counterbalancing structural arc"
    )
    pose["contactPoints"] = [
        "hind limbs grounded",
        "forelimb contact controlled",
    ]

    framing = art_spec["framing"]

    framing["aspectRatio"] = "1:1"
    framing["subjectOccupancy"] = 0.72
    framing["cropPolicy"] = (
        "FULL_BODY_REQUIRED"
    )
    framing["safeMargin"] = 0.08

    composition = art_spec[
        "composition"
    ]

    composition["dominance"] = (
        rules[
            "composition"
        ][
            "language"
        ]
    )
    composition["balance"] = (
        "controlled monumental balance"
    )
    composition["symmetry"] = (
        "NEAR_SYMMETRIC"
    )
    composition["ruleOfThirds"] = False
    composition["environmentRatio"] = 0.38
    composition["depthPriority"] = (
        "subject-first with monumental depth"
    )
    composition["leadingGeometry"] = [
        rules[
            "environment"
        ][
            "architecture"
        ],
        rules[
            "dragon"
        ][
            "silhouette"
        ],
    ]

    lighting = art_spec["lighting"]

    lighting["key"] = (
        rules[
            "lighting"
        ][
            "language"
        ]
    )
    lighting["fill"] = (
        "restrained environmental fill"
    )
    lighting["rim"] = (
        rules[
            "materials"
        ][
            "accent"
        ]
    )
    lighting["volumetrics"] = (
        rules[
            "environment"
        ][
            "atmosphere"
        ]
    )
    lighting["contrast"] = 0.82
    lighting["exposureBias"] = -0.25

    materials = art_spec["materials"]

    materials["libraryRefs"] = (
        selected_materials
    )

    materials["assignments"] = {
        "dragonPrimary": (
            rules[
                "materials"
            ][
                "primary"
            ]
        ),
        "dragonSecondary": (
            rules[
                "materials"
            ][
                "secondary"
            ]
        ),
        "energyAccent": (
            rules[
                "materials"
            ][
                "accent"
            ]
        ),
        "environmentPrimary": (
            rules[
                "materials"
            ][
                "primary"
            ]
        ),
    }

    materials["weatheringPolicy"] = (
        "physically coherent controlled weathering"
    )

    color_policy = art_spec[
        "colorPolicy"
    ]

    if isinstance(
        color_policy,
        dict,
    ):
        _replace_string(
            color_policy,
            "dominant",
            rules[
                "materials"
            ][
                "primary"
            ],
        )

        _replace_string(
            color_policy,
            "temperature",
            "controlled cinematic contrast",
        )

        _replace_string(
            color_policy,
            "palette",
            rules[
                "color"
            ][
                "palette"
            ],
        )

        _replace_list(
            color_policy,
            "palette",
            [
                rules[
                    "materials"
                ][
                    "primary"
                ],
                rules[
                    "materials"
                ][
                    "secondary"
                ],
                rules[
                    "materials"
                ][
                    "accent"
                ],
            ],
        )

        _replace_list(
            color_policy,
            "accents",
            [
                rules[
                    "materials"
                ][
                    "accent"
                ],
            ],
        )

    detail = art_spec["detail"]

    if not isinstance(
        detail,
        dict,
    ):
        raise ArtSpecAssemblyError(
            "Expected detail hierarchy "
            "to be an object."
        )

    for layer in (
        "macro",
        "meso",
        "micro",
    ):
        block = detail.get(layer)

        if not isinstance(
            block,
            dict,
        ):
            raise ArtSpecAssemblyError(
                f"Expected detail.{layer} "
                "to be an object."
            )

        priorities = list(
            rules[
                "detail"
            ][layer]
        )

        _decorate_detail_layer(
            block,
            priorities,
        )

    resonance = art_spec[
        "resonance"
    ]

    if not isinstance(
        resonance,
        dict,
    ):
        raise ArtSpecAssemblyError(
            "Expected resonance "
            "to be an object."
        )

    _replace_boolean(
        resonance,
        "narrativeOnly",
        True,
    )

    resonance_label = (
        _resonance_label(
            structure_input.resonance
        )
    )

    resonance_mapping = {
        "spectrum": resonance_label,
        "energyTopology": (
            "identity-preserving controlled topology"
        ),
        "accentGeometry": (
            rules[
                "dragon"
            ][
                "silhouette"
            ]
        ),
        "lightingRhythm": (
            rules[
                "lighting"
            ][
                "language"
            ]
        ),
        "glyphInfluence": (
            "subtle structural motif influence"
        ),
        "atmosphericBehavior": (
            rules[
                "environment"
            ][
                "atmosphere"
            ]
        ),
    }

    for key, value in (
        resonance_mapping.items()
    ):
        _replace_string(
            resonance,
            key,
            value,
        )

    render_intent = art_spec[
        "renderIntent"
    ]

    if isinstance(
        render_intent,
        dict,
    ):
        _replace_boolean(
            render_intent,
            "preserveIdentity",
            True,
        )

        _replace_number(
            render_intent,
            "detailDensity",
            0.82,
        )

    negative = art_spec[
        "negativeConstraints"
    ]

    if isinstance(
        negative,
        dict,
    ):
        _replace_boolean(
            negative,
            "allowDetailToMaskBadAnatomy",
            False,
        )

        _replace_list(
            negative,
            "forbiddenModes",
            list(
                rules[
                    "visualConstraints"
                ][
                    "forbiddenModes"
                ]
            ),
        )

    quality = art_spec[
        "qualityRequirements"
    ]

    if isinstance(
        quality,
        dict,
    ):
        _replace_boolean(
            quality,
            "requireManualApproval",
            True,
        )

        _replace_string(
            quality,
            "canonicalApprovalMode",
            "MANUAL_REQUIRED",
        )

        _apply_quality_thresholds(
            quality
        )


def assemble_art_spec(
    structure_input: StructureInput,
) -> ArtSpecAssembly:
    seed = resolve_seed(
        structure_input
    )

    rules = select_art_rules(
        tier=structure_input.tier,
        seed=seed,
    )

    if (
        rules.get("catalogVersion")
        != ART_RULE_CATALOG_VERSION
    ):
        raise ArtSpecAssemblyError(
            "Unexpected Art Rule Catalog version."
        )

    schema = load_art_spec_schema()

    art_spec = _schema_value(
        schema,
        schema,
        seed=seed,
        namespace="artSpec",
    )

    if not isinstance(
        art_spec,
        dict,
    ):
        raise ArtSpecAssemblyError(
            "OX-ART-SPEC schema did not "
            "produce an object."
        )

    _apply_semantics(
        art_spec,
        structure_input=structure_input,
        seed=seed,
        rules=rules,
    )

    try:
        validate_art_spec(
            art_spec
        )
    except ArtSpecValidationError as exc:
        raise ArtSpecAssemblyError(
            "Assembled OX-ART-SPEC-1 "
            "failed validation:\n"
            f"{exc}"
        ) from exc

    canonical_json(
        art_spec
    )

    return ArtSpecAssembly(
        art_spec=art_spec,
        art_spec_hash=art_spec_hash(
            art_spec
        ),
        art_rule_hash=art_rule_hash(
            tier=structure_input.tier,
            seed=seed,
        ),
        seed=seed,
    )
