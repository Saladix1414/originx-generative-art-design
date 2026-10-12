from pathlib import Path

from oxgad.models.z_image_download_dry_run import (
    build_z_image_download_dry_run,
)


def test_download_dry_run_has_three_pinned_artifacts():
    value = build_z_image_download_dry_run()

    assert value["state"] == "DRY_RUN_ONLY"
    assert len(value["artifacts"]) == 3
    assert value["expectedSizeBytes"] == 6348318966
    assert value["networkInvoked"] is False
    assert value["filesWritten"] is False


def test_targets_remain_inside_model_directory():
    value = build_z_image_download_dry_run()
    root = Path(value["targetRoot"])

    for artifact in value["artifacts"]:
        target = Path(artifact["target"])
        assert target.parts[:len(root.parts)] == root.parts
        assert ".." not in target.parts


def test_dry_run_grants_no_authority():
    value = build_z_image_download_dry_run()

    assert value["governance"]["downloadAllowed"] is False
    assert value["governance"]["executionAllowed"] is False
    assert value["governance"]["canonicalizationAllowed"] is False
