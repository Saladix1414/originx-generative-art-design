import struct
from pathlib import Path

from oxgad.genesis.profile2_executor import (
    OUTPUT,
    build_profile_2_command,
    png_evidence_profile_2,
)


def _option(command, name):
    return command[command.index(name) + 1]


def test_profile_2_command_is_scoped_and_optimized():
    token, command = build_profile_2_command()

    assert token["tokenId"] == 1
    assert token["serial"] == "#0001"
    assert _option(command, "--width") == "384"
    assert _option(command, "--height") == "384"
    assert _option(command, "--steps") == "10"
    assert _option(command, "--sampling-method") == "dpm++2m"
    assert _option(command, "--scheduler") == "karras"
    assert _option(command, "--output") == str(
        OUTPUT.relative_to(OUTPUT.parents[5])
    )


def test_profile_2_keeps_batch_size_one():
    _, command = build_profile_2_command()

    assert "--batch-count" not in command
    assert "--batch-size" not in command


def test_png_evidence_requires_rgb8_384(tmp_path: Path):
    path = tmp_path / "candidate.png"
    header = (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", 384, 384)
        + bytes([8, 2, 0, 0, 0])
    )
    path.write_bytes(header)

    import oxgad.genesis.profile2_executor as module

    original_repo = module.REPO
    module.REPO = tmp_path

    try:
        value = png_evidence_profile_2(path)
    finally:
        module.REPO = original_repo

    assert value["width"] == 384
    assert value["height"] == 384
    assert value["bitsPerChannel"] == 8
    assert value["colorType"] == "RGB"
