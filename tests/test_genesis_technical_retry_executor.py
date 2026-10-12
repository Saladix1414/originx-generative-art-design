from oxgad.genesis.technical_retry_executor import (
    OUTPUT,
    build_technical_retry_command,
)


def _value(command, option):
    return command[command.index(option) + 1]


def test_retry_is_scoped_to_token_0001():
    token, command = build_technical_retry_command()

    assert token["tokenId"] == 1
    assert token["serial"] == "#0001"
    assert _value(command, "--seed") == "5770080363699867898"


def test_retry_preserves_profile_2_sampling():
    _, command = build_technical_retry_command()

    assert _value(command, "--width") == "384"
    assert _value(command, "--height") == "384"
    assert _value(command, "--steps") == "10"
    assert _value(command, "--sampling-method") == "dpm++2m"
    assert _value(command, "--scheduler") == "karras"
    assert _value(command, "--cfg-scale") == "7.0"


def test_retry_changes_only_vae_decode_and_output():
    _, command = build_technical_retry_command()

    assert "--vae-tiling" not in command
    assert "--vae-tile-size" not in command
    assert _value(command, "--output") == str(
        OUTPUT.relative_to(OUTPUT.parents[5])
    )
