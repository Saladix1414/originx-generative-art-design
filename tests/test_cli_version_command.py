import json

from oxgad.cli import main


def test_cli_version_reports_installed_package_version(capsys):
    assert main(["version"]) == 0

    output = json.loads(capsys.readouterr().out)

    assert output == {
        "project": "originx-generative-art-design",
        "version": "0.23.0",
    }
