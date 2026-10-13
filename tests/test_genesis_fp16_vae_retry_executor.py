from oxgad.genesis.fp16_vae_retry_executor import (
    OUTPUT,
    VAE,
    build_fp16_vae_retry_command,
)


def _value(command, option):
    return command[command.index(option) + 1]


def test_retry_is_only_for_token_0001():
    token, command = build_fp16_vae_retry_command()

    assert token["tokenId"] == 1
    assert token["serial"] == "#0001"
    assert _value(command, "--seed") == "5770080363699867898"


def test_retry_preserves_sampling():
    _, command = build_fp16_vae_retry_command()

    assert _value(command, "--width") == "384"
    assert _value(command, "--height") == "384"
    assert _value(command, "--steps") == "10"
    assert _value(command, "--cfg-scale") == "7.0"
    assert _value(command, "--sampling-method") == "dpm++2m"
    assert _value(command, "--scheduler") == "karras"


def test_retry_binds_external_vae_without_tiling():
    _, command = build_fp16_vae_retry_command()

    assert _value(command, "--vae") == str(
        VAE.relative_to(VAE.parents[3])
    )
    assert "--vae-tiling" not in command
    assert "--vae-tile-size" not in command
    assert _value(command, "--output") == str(
        OUTPUT.relative_to(OUTPUT.parents[5])
    )
