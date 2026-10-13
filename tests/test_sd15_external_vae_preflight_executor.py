from oxgad.forge.sd15_external_vae_preflight_executor import (
    OUTPUT,
    VAE,
    build_command,
)


def _value(command, option):
    return command[command.index(option) + 1]


def test_command_binds_external_fp16_vae():
    command = build_command()

    assert _value(command, "--vae") == str(
        VAE.relative_to(VAE.parents[3])
    )
    assert _value(command, "--width") == "256"
    assert _value(command, "--height") == "256"
    assert _value(command, "--steps") == "1"
    assert _value(command, "--seed") == "1001"
    assert _value(command, "--output") == str(
        OUTPUT.relative_to(OUTPUT.parents[2])
    )


def test_command_uses_non_tiled_decode():
    command = build_command()

    assert "--vae-tiling" not in command
    assert "--vae-tile-size" not in command
