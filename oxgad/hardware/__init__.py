"""OriginX hardware capability domain."""

HARDWARE_PROFILE_VERSION = "OX-HARDWARE-PROFILE-1"

from oxgad.hardware.validator import (
    HARDWARE_SCHEMA_PATH,
    HardwareProfileValidationError,
    is_valid_hardware_profile,
    load_hardware_schema,
    validate_hardware_profile,
)
from oxgad.hardware.detector import (
    HARDWARE_DETECTOR_VERSION,
    HardwareDetectionError,
    build_hardware_profile,
    collect_hardware_observation,
    detect_hardware_profile,
)

__all__ = (
    "HARDWARE_PROFILE_VERSION",
    "HARDWARE_DETECTOR_VERSION",
    "HARDWARE_SCHEMA_PATH",
    "HardwareDetectionError",
    "HardwareProfileValidationError",
    "build_hardware_profile",
    "collect_hardware_observation",
    "detect_hardware_profile",
    "is_valid_hardware_profile",
    "load_hardware_schema",
    "validate_hardware_profile",
)
