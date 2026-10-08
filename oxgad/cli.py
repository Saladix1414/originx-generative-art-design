from __future__ import annotations

import argparse
import json
import jsonschema
from pathlib import Path
from typing import Any


def _load_json(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")

    return payload


def _command_schema(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)

    print(
        json.dumps(
            {
                "schema_version": payload.get("schema_version"),
                "project": payload.get("project"),
                "phase": payload.get("phase"),
            },
            sort_keys=True,
        )
    )

    return 0


def _command_status(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)

    print(
        json.dumps(
            {
                "status": payload.get("status"),
                "decision": payload.get("decision"),
                "phase": payload.get("phase"),
            },
            sort_keys=True,
        )
    )

    return 0


def _command_validate_fixture(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)
    schema = _load_json(args.schema)

    jsonschema.validate(payload, schema)

    print(
        json.dumps(
            {
                "valid": True,
                "schema_version": payload.get("schema_version"),
                "schema_id": schema.get("$id"),
            },
            sort_keys=True,
        )
    )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oxgad",
        description="OriginX GAD local inspection CLI.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)

    schema = subcommands.add_parser(
        "schema",
        help="Print schema identity fields from a JSON document.",
    )
    schema.add_argument("path")
    schema.set_defaults(func=_command_schema)

    status = subcommands.add_parser(
        "status",
        help="Print status or decision fields from a JSON document.",
    )
    status.add_argument("path")
    status.set_defaults(func=_command_status)

    validate_fixture = subcommands.add_parser(
        "validate-fixture",
        help="Validate a local JSON fixture against a local JSON schema.",
    )
    validate_fixture.add_argument("path")
    validate_fixture.add_argument("--schema", required=True)
    validate_fixture.set_defaults(func=_command_validate_fixture)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return args.func(args)
