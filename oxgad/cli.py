from __future__ import annotations

import argparse
import json
import jsonschema
from pathlib import Path
from typing import Any


FIXTURE_SCHEMA_MAP = {
    "canonical-promotion.json": "schemas/ox-canonical-promotion-1.schema.json",
    "project-readiness-summary.json": "schemas/ox-project-readiness-summary-1.schema.json",
}


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


def _validate_payload(path: str, schema_path: str) -> dict[str, Any]:
    payload = _load_json(path)
    schema = _load_json(schema_path)

    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as error:
        return {
            "path": path,
            "valid": False,
            "schema_version": payload.get("schema_version"),
            "schema_id": schema.get("$id"),
            "error": error.message,
        }

    return {
        "path": path,
        "valid": True,
        "schema_version": payload.get("schema_version"),
        "schema_id": schema.get("$id"),
    }


def _command_validate_fixture(args: argparse.Namespace) -> int:
    result = _validate_payload(args.path, args.schema)

    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key != "path"
            },
            sort_keys=True,
        )
    )

    return 0 if result["valid"] else 2


def _command_validate_fixtures(args: argparse.Namespace) -> int:
    directory = Path(args.directory)
    results = []

    for path in sorted(directory.glob("*.json")):
        schema_path = FIXTURE_SCHEMA_MAP.get(path.name)

        if schema_path is None:
            results.append(
                {
                    "path": str(path),
                    "valid": False,
                    "schema_version": None,
                    "schema_id": None,
                    "error": "no schema mapping",
                }
            )
            continue

        results.append(_validate_payload(str(path), schema_path))

    valid = all(result["valid"] for result in results)

    print(
        json.dumps(
            {
                "valid": valid,
                "count": len(results),
                "results": results,
            },
            sort_keys=True,
        )
    )

    return 0 if valid else 2


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

    validate_fixtures = subcommands.add_parser(
        "validate-fixtures",
        help="Validate all mapped JSON fixtures in a local directory.",
    )
    validate_fixtures.add_argument("directory")
    validate_fixtures.set_defaults(func=_command_validate_fixtures)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return args.func(args)
