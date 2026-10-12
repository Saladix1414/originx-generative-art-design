from oxgad.models.z_image_download import (
    build_blocked_z_image_download_plan,
)


def test_z_image_download_remains_blocked():
    value = build_blocked_z_image_download_plan()

    assert value["modelId"] == "OX-MODEL-001"
    assert value["checks"]["ramBenchmarkPassed"] is False
    assert value["approval"]["explicitApprovalPresent"] is False
    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["download"]["artifactCount"] == 3
    assert value["download"]["expectedSizeBytes"] == 6348318966
