from oxgad.hardware.z_image_preflight import (
    assess_z_image_hardware,
)


def test_phone_requires_disk_backed_benchmark():
    value = assess_z_image_hardware(
        total_ram_bytes=5721546752,
        available_ram_bytes=1739636736,
        swap_total_bytes=8589934592,
        free_storage_bytes=57000000000,
    )

    assert value["checks"]["storagePassed"] is True
    assert value["checks"]["directRamPassed"] is False
    assert value["checks"]["diskBackedBenchmarkPossible"] is True
    assert value["decision"] == "DISK_BACKED_BENCHMARK_ONLY"
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False


def test_insufficient_storage_blocks_benchmark():
    value = assess_z_image_hardware(
        total_ram_bytes=5721546752,
        available_ram_bytes=1739636736,
        swap_total_bytes=8589934592,
        free_storage_bytes=1000000000,
    )

    assert value["checks"]["storagePassed"] is False
    assert value["decision"] == "BLOCKED_INSUFFICIENT_RESOURCES"
