from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from oxgad.forge.validator import (
    LOCAL_FORGE_VERSION,
    validate_local_forge_request,
)
from oxgad.hardware import (
    HARDWARE_PROFILE_VERSION,
    HardwareProfileValidationError,
    validate_hardware_profile,
)


LOCAL_FORGE_PREPARATION_VERSION = (
    "OX-LOCAL-FORGE-PREPARATION-1"
)

_LOCAL_TARGETS = {
    "LOCAL_CPP",
    "LOCAL_GPU",
}

_HASH_PATTERN = re.compile(
    r"^sha256:[0-9a-f]{64}$"
)


class LocalForgePreparationError(ValueError):
    pass


def prepare_local_forge_request(
    *,
    render_plan_hash: str,
    hardware_profile: dict[str, Any],
    requested_target: str,
) -> dict[str, Any]:
    if (
        not isinstance(render_plan_hash, str)
        or _HASH_PATTERN.fullmatch(render_plan_hash) is None
    ):
        raise LocalForgePreparationError(
            "render_plan_hash must be canonical sha256 evidence"
        )

    if requested_target not in _LOCAL_TARGETS:
        raise LocalForgePreparationError(
            "requested_target must be LOCAL_CPP or LOCAL_GPU"
        )

    profile = deepcopy(hardware_profile)

    try:
        validate_hardware_profile(profile)
    except HardwareProfileValidationError as exc:
        raise LocalForgePreparationError(
            "invalid hardware profile"
        ) from exc

    if profile["profileVersion"] != HARDWARE_PROFILE_VERSION:
        raise LocalForgePreparationError(
            "unsupported hardware profile version"
        )

    capability = profile["executionProfiles"][
        requested_target
    ]["capability"]

    request = {
        "forgeVersion": LOCAL_FORGE_VERSION,
        "source": {
            "renderPlanVersion": "OX-RENDER-1",
            "renderPlanHash": render_plan_hash,
        },
        "hardware": {
            "profileVersion": HARDWARE_PROFILE_VERSION,
            "requestedTarget": requested_target,
            "capability": capability,
        },
        "model": {
            "bindingState": "UNBOUND",
        },
        "execution": {
            "policy": "LOCAL_FIRST",
            "mode": "PREPARE_ONLY",
            "authorizationState": "BLOCKED",
            "executionAllowed": False,
        },
        "output": {
            "mediaGenerationAllowed": False,
            "canonicalArtworkAllowed": False,
        },
    }

    validate_local_forge_request(request)

    return request
