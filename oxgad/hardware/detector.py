"""Read-only hardware observation and conservative classification."""

from __future__ import annotations

import copy
import os
import platform
import shutil
import subprocess
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from oxgad.hardware import HARDWARE_PROFILE_VERSION
from oxgad.hardware.validator import validate_hardware_profile


HARDWARE_DETECTOR_VERSION = "OX-HARDWARE-DETECTOR-1"

_DEVICE_NODES = (
    "/dev/kgsl-3d0",
    "/dev/dri/renderD128",
    "/dev/dri/card0",
)

_ARM_PART_NAMES = {
    "0xd05": "Cortex-A55",
    "0xd41": "Cortex-A78",
}

_RUNTIME_MODULES = {
    "torch": "torch",
    "tensorflow": "tensorflow",
    "onnxruntime": "onnxruntime",
    "numpy": "numpy",
    "psutil": "psutil",
    "vulkanPython": "vulkan",
}


class HardwareDetectionError(RuntimeError):
    """Hardware evidence could not be collected safely."""


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None


def _getprop(key: str) -> str | None:
    executable = shutil.which("getprop")
    if executable is None:
        return None

    try:
        result = subprocess.run(
            [executable, key],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    return value or None


def _probe_tool(name: str, *args: str) -> dict[str, bool]:
    executable = shutil.which(name)

    if executable is None:
        return {
            "toolAvailable": False,
            "probeSucceeded": False,
        }

    try:
        result = subprocess.run(
            [executable, *args],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "toolAvailable": True,
            "probeSucceeded": False,
        }

    return {
        "toolAvailable": True,
        "probeSucceeded": result.returncode == 0,
    }


def _parse_meminfo(text: str) -> dict[str, int]:
    values: dict[str, int] = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        key, remainder = line.split(":", 1)
        fields = remainder.strip().split()

        if not fields:
            continue

        try:
            values[key] = int(fields[0]) * 1024
        except ValueError:
            continue

    total = values.get("MemTotal", 0)

    if total <= 0:
        raise HardwareDetectionError(
            "MemTotal is unavailable."
        )

    return {
        "totalBytes": total,
        "availableBytes": values.get(
            "MemAvailable",
            values.get("MemFree", 0),
        ),
        "swapTotalBytes": values.get("SwapTotal", 0),
        "swapFreeBytes": values.get("SwapFree", 0),
    }


def _cpu_max_mhz(index: int) -> float | None:
    base = Path(f"/sys/devices/system/cpu/cpu{index}/cpufreq")

    for name in (
        "cpuinfo_max_freq",
        "scaling_max_freq",
    ):
        value = _read_text(base / name)

        if value is None:
            continue

        try:
            khz = int(value.strip())
        except ValueError:
            continue

        if khz > 0:
            return khz / 1000.0

    return None


def _parse_cpuinfo(
    text: str,
    logical_cores: int,
) -> dict[str, Any]:
    features: set[str] = set()
    clusters: dict[tuple[str, float | None], int] = {}

    for block in text.split("\n\n"):
        if not block.strip():
            continue

        fields: dict[str, str] = {}

        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

        feature_text = fields.get(
            "Features",
            fields.get("flags", ""),
        )
        features.update(feature_text.split())

        processor = fields.get("processor")
        if processor is None:
            continue

        try:
            index = int(processor)
        except ValueError:
            continue

        part = fields.get("CPU part", "").lower()
        model = _ARM_PART_NAMES.get(part)

        if model is None:
            model = (
                f"ARM-{part}"
                if part
                else "Unknown CPU"
            )

        key = (model, _cpu_max_mhz(index))
        clusters[key] = clusters.get(key, 0) + 1

    cluster_list = [
        {
            "model": model,
            "coreCount": count,
            "maxMHz": max_mhz,
        }
        for (model, max_mhz), count in sorted(
            clusters.items(),
            key=lambda item: (
                item[0][0],
                -1.0 if item[0][1] is None else item[0][1],
            ),
        )
    ]

    return {
        "architecture": platform.machine() or "unknown",
        "logicalCores": logical_cores,
        "features": sorted(features),
        "clusters": cluster_list,
    }


def collect_hardware_observation() -> dict[str, Any]:
    """Observe hardware without granting execution authority."""
    logical_cores = os.cpu_count() or 1
    cpuinfo = _read_text(Path("/proc/cpuinfo")) or ""
    meminfo = _read_text(Path("/proc/meminfo"))

    if meminfo is None:
        raise HardwareDetectionError(
            "/proc/meminfo is unavailable."
        )

    storage_path = Path.home()

    try:
        storage = shutil.disk_usage(storage_path)
    except OSError as exc:
        raise HardwareDetectionError(
            f"Cannot inspect storage: {exc}"
        ) from exc

    api_text = _getprop("ro.build.version.sdk")

    try:
        api_level = int(api_text) if api_text else None
    except ValueError:
        api_level = None

    return {
        "platform": {
            "system": platform.system() or "unknown",
            "release": platform.release() or "unknown",
            "machine": platform.machine() or "unknown",
            "androidVersion": _getprop(
                "ro.build.version.release"
            ),
            "androidApiLevel": api_level,
            "termuxVersion": os.environ.get(
                "TERMUX_VERSION"
            ),
        },
        "cpu": _parse_cpuinfo(cpuinfo, logical_cores),
        "memory": _parse_meminfo(meminfo),
        "storage": {
            "path": str(storage_path),
            "totalBytes": storage.total,
            "freeBytes": storage.free,
        },
        "deviceNodes": {
            path: Path(path).exists()
            for path in _DEVICE_NODES
        },
        "apiProbes": {
            "vulkan": _probe_tool(
                "vulkaninfo",
                "--summary",
            ),
            "opencl": _probe_tool("clinfo"),
            "cuda": _probe_tool("nvidia-smi", "-L"),
            "rocm": _probe_tool("rocminfo"),
        },
        "runtimePackages": {
            name: find_spec(module) is not None
            for name, module in _RUNTIME_MODULES.items()
        },
    }


def _api_capability(probe: dict[str, bool]) -> str:
    if (
        probe.get("toolAvailable") is True
        and probe.get("probeSucceeded") is True
    ):
        return "CONFIRMED"
    return "UNKNOWN"


def build_hardware_profile(
    observation: dict[str, Any],
) -> dict[str, Any]:
    """Classify identical evidence identically."""
    observed = copy.deepcopy(observation)

    try:
        platform_data = observed["platform"]
        cpu = observed["cpu"]
        memory = observed["memory"]
        storage = observed["storage"]
        device_nodes = observed["deviceNodes"]
        probes = observed["apiProbes"]
        runtimes = observed["runtimePackages"]
    except (KeyError, TypeError) as exc:
        raise HardwareDetectionError(
            "Incomplete hardware observation."
        ) from exc

    api_states = {
        name: {
            "toolAvailable": bool(
                probes[name]["toolAvailable"]
            ),
            "capability": _api_capability(probes[name]),
        }
        for name in ("vulkan", "opencl", "cuda", "rocm")
    }

    gpu_confirmed = any(
        value["capability"] == "CONFIRMED"
        for value in api_states.values()
    )

    node_present = any(
        bool(value)
        for value in device_nodes.values()
    )

    if gpu_confirmed:
        local_gpu_capability = "CONFIRMED"
        local_gpu_reasons = [
            "GPU_API_PROBE_CONFIRMED",
        ]
    else:
        local_gpu_capability = "UNKNOWN"
        local_gpu_reasons = [
            "GPU_API_UNVERIFIED",
            (
                "GPU_DEVICE_NODE_INSUFFICIENT"
                if node_present
                else "GPU_DEVICE_NODE_NOT_OBSERVED"
            ),
        ]

    architecture = str(cpu["architecture"]).lower()

    if (
        architecture in {
            "aarch64",
            "arm64",
            "x86_64",
            "amd64",
        }
        and int(cpu["logicalCores"]) > 0
        and int(memory["totalBytes"]) > 0
    ):
        local_cpp = {
            "capability": "CONFIRMED",
            "reasonCodes": [
                "SUPPORTED_NATIVE_ARCHITECTURE",
                "CPU_PRESENT",
                "MEMORY_PRESENT",
            ],
        }
    else:
        local_cpp = {
            "capability": "UNKNOWN",
            "reasonCodes": [
                "LOCAL_CPP_CAPABILITY_UNVERIFIED",
            ],
        }

    profile = {
        "profileVersion": HARDWARE_PROFILE_VERSION,
        "platform": platform_data,
        "cpu": cpu,
        "memory": memory,
        "storage": storage,
        "accelerators": {
            "deviceNodes": [
                {
                    "path": path,
                    "presence": (
                        "PRESENT" if bool(present) else "ABSENT"
                    ),
                }
                for path, present in sorted(
                    device_nodes.items()
                )
            ],
            "vulkan": api_states["vulkan"],
            "opencl": api_states["opencl"],
            "cuda": api_states["cuda"],
            "rocm": api_states["rocm"],
            "localGpuCapability": local_gpu_capability,
        },
        "runtimeTools": {
            name: (
                "INSTALLED" if bool(runtimes[name]) else "ABSENT"
            )
            for name in (
                "torch",
                "tensorflow",
                "onnxruntime",
                "numpy",
                "psutil",
                "vulkanPython",
            )
        },
        "executionProfiles": {
            "LOCAL_CPP": local_cpp,
            "LOCAL_GPU": {
                "capability": local_gpu_capability,
                "reasonCodes": local_gpu_reasons,
            },
            "ORIGINX_GPU": {
                "capability": "UNKNOWN",
                "reasonCodes": [
                    "REMOTE_CAPABILITY_NOT_PROBED",
                ],
            },
            "EXTERNAL_PROVIDER": {
                "capability": "UNKNOWN",
                "reasonCodes": [
                    "EXTERNAL_PROVIDER_NOT_PROBED",
                ],
            },
        },
        "governance": {
            "policy": "LOCAL_FIRST",
            "hardwareAvailabilityGrantsExecutionAuthority": False,
            "executionAllowed": False,
        },
    }

    validate_hardware_profile(profile)
    return profile


def detect_hardware_profile() -> dict[str, Any]:
    """Observe this host and return a validated profile."""
    return build_hardware_profile(
        collect_hardware_observation()
    )


__all__ = (
    "HARDWARE_DETECTOR_VERSION",
    "HardwareDetectionError",
    "build_hardware_profile",
    "collect_hardware_observation",
    "detect_hardware_profile",
)
