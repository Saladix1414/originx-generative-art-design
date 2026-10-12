from __future__ import annotations

from typing import Any

EXPECTED_ARTIFACT_BYTES = 6348318966
MINIMUM_FREE_STORAGE_BYTES = 12000000000


def assess_z_image_hardware(
    *,
    total_ram_bytes: int,
    available_ram_bytes: int,
    swap_total_bytes: int,
    free_storage_bytes: int,
) -> dict[str, Any]:
    storage_passed = free_storage_bytes >= MINIMUM_FREE_STORAGE_BYTES
    direct_ram_passed = available_ram_bytes >= EXPECTED_ARTIFACT_BYTES

    disk_backed_possible = (
        storage_passed
        and swap_total_bytes > 0
        and total_ram_bytes > 0
    )

    if direct_ram_passed:
        decision = "DIRECT_RAM_BENCHMARK_ELIGIBLE"
    elif disk_backed_possible:
        decision = "DISK_BACKED_BENCHMARK_ONLY"
    else:
        decision = "BLOCKED_INSUFFICIENT_RESOURCES"

    return {
        "preflightVersion": "OX-Z-IMAGE-HARDWARE-PREFLIGHT-1",
        "modelId": "OX-MODEL-001",
        "expectedArtifactBytes": EXPECTED_ARTIFACT_BYTES,
        "minimumFreeStorageBytes": MINIMUM_FREE_STORAGE_BYTES,
        "observed": {
            "totalRamBytes": total_ram_bytes,
            "availableRamBytes": available_ram_bytes,
            "swapTotalBytes": swap_total_bytes,
            "freeStorageBytes": free_storage_bytes,
        },
        "checks": {
            "storagePassed": storage_passed,
            "directRamPassed": direct_ram_passed,
            "diskBackedBenchmarkPossible": disk_backed_possible,
            "thermalBenchmarkPassed": False,
            "stabilityBenchmarkPassed": False,
        },
        "decision": decision,
        "governance": {
            "downloadAllowed": False,
            "executionAllowed": False,
            "canonicalizationAllowed": False,
        },
    }
