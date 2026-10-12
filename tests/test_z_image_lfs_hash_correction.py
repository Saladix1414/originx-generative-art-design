from oxgad.models.z_image_artifacts import (
    build_z_image_artifact_manifest,
)
from oxgad.models.z_image_download_dry_run import (
    build_z_image_download_dry_run,
)


EXPECTED_HASHES = {
    "DIFFUSION_TRANSFORMER": (
        "sha256:2bc57986874c84f7ec6d02d9d7070a53"
        "b0029954a0e38a6e1342eb91095572f5"
    ),
    "TEXT_ENCODER_DEPENDENCY": (
        "sha256:3605803b982cb64aead44f6c1b2ae36e"
        "3acdb41d8e46c8a94c6533bc4c67e597"
    ),
    "VAE": (
        "sha256:f5b59a26851551b67ae1fe58d32e7648"
        "6e1e812def4696a4bea97f16604d40a3"
    ),
}


def test_manifest_uses_git_lfs_content_hashes():
    value = build_z_image_artifact_manifest()

    observed = {
        item["role"]: item["expectedSha256"]
        for item in value["artifacts"]
    }

    assert observed == EXPECTED_HASHES


def test_dry_run_uses_git_lfs_content_hashes():
    value = build_z_image_download_dry_run()

    observed = {
        item["role"]: item["expectedSha256"]
        for item in value["artifacts"]
    }

    assert observed == EXPECTED_HASHES
