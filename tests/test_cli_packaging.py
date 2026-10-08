from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def test_pyproject_declares_cli_entrypoint():
    payload = tomllib.loads(Path("pyproject.toml").read_text())

    assert payload["project"]["name"] == "originx-generative-art-design"
    assert payload["project"]["scripts"]["oxgad"] == "oxgad.cli:main"


def test_pyproject_discovers_oxgad_package():
    payload = tomllib.loads(Path("pyproject.toml").read_text())

    assert payload["tool"]["setuptools"]["packages"]["find"]["include"] == ["oxgad*"]


def test_pyproject_does_not_define_network_or_model_commands():
    text = Path("pyproject.toml").read_text().lower()

    blocked = [
        "curl",
        "wget",
        "download",
        "upload",
        "publish",
        "mint",
        "stable-diffusion",
        "comfy",
        "automatic1111",
    ]

    for token in blocked:
        assert token not in text
