from __future__ import annotations

import argparse
import json
import jsonschema
from jsonschema import Draft202012Validator
from pathlib import Path
from typing import Any


EVIDENCE_CHAIN = [
    {
        "step": "provenance",
        "schema": "ox-provenance-manifest-1.schema.json",
    },
    {
        "step": "quality",
        "schema": "ox-quality-gate-report-1.schema.json",
    },
    {
        "step": "promotion",
        "schema": "ox-canonical-promotion-1.schema.json",
    },
    {
        "step": "canonical-ledger",
        "schema": "ox-canonical-ledger-1.schema.json",
    },
    {
        "step": "canonical-output",
        "schema": "ox-canonical-output-manifest-1.schema.json",
    },
    {
        "step": "review",
        "schema": "ox-review-pack-1.schema.json",
    },
    {
        "step": "release-readiness",
        "schema": "ox-release-readiness-1.schema.json",
    },
    {
        "step": "release-ledger",
        "schema": "ox-release-ledger-1.schema.json",
    },
    {
        "step": "export-plan",
        "schema": "ox-local-export-plan-1.schema.json",
    },
    {
        "step": "export-dry-run",
        "schema": "ox-local-export-dry-run-1.schema.json",
    },
    {
        "step": "export-result",
        "schema": "ox-local-export-result-1.schema.json",
    },
    {
        "step": "export-audit",
        "schema": "ox-export-audit-ledger-1.schema.json",
    },
    {
        "step": "project-readiness",
        "schema": "ox-project-readiness-summary-1.schema.json",
    },
]


CONTRACT_SCHEMAS = {
    "provenance": "schemas/ox-provenance-manifest-1.schema.json",
    "quality": "schemas/ox-quality-gate-report-1.schema.json",
    "promotion": "schemas/ox-canonical-promotion-1.schema.json",
    "ledger": "schemas/ox-canonical-ledger-1.schema.json",
    "output": "schemas/ox-canonical-output-manifest-1.schema.json",
    "review": "schemas/ox-review-pack-1.schema.json",
    "release": "schemas/ox-release-readiness-1.schema.json",
    "release-ledger": "schemas/ox-release-ledger-1.schema.json",
    "export-plan": "schemas/ox-local-export-plan-1.schema.json",
    "export-dry-run": "schemas/ox-local-export-dry-run-1.schema.json",
    "export-result": "schemas/ox-local-export-result-1.schema.json",
    "export-audit": "schemas/ox-export-audit-ledger-1.schema.json",
    "project-readiness": "schemas/ox-project-readiness-summary-1.schema.json",
}


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


def _fixture_directory_results(directory: Path) -> list[dict[str, Any]]:
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

    return results


def _command_validate_fixtures(args: argparse.Namespace) -> int:
    results = _fixture_directory_results(Path(args.directory))
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


def _command_contracts(args: argparse.Namespace) -> int:
    contracts = []

    for name, schema_path in sorted(CONTRACT_SCHEMAS.items()):
        schema = _load_json(schema_path)
        contracts.append(
            {
                "name": name,
                "schema_id": schema.get("$id"),
                "path": schema_path,
            }
        )

    print(
        json.dumps(
            {
                "count": len(contracts),
                "contracts": contracts,
            },
            sort_keys=True,
        )
    )

    return 0


def _contract_validation_results() -> list[dict[str, Any]]:
    results = []

    for name, schema_path in sorted(CONTRACT_SCHEMAS.items()):
        schema = _load_json(schema_path)

        try:
            Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as error:
            results.append(
                {
                    "name": name,
                    "path": schema_path,
                    "schema_id": schema.get("$id"),
                    "valid": False,
                    "error": error.message,
                }
            )
            continue

        results.append(
            {
                "name": name,
                "path": schema_path,
                "schema_id": schema.get("$id"),
                "valid": True,
            }
        )

    return results


def _command_validate_contracts(args: argparse.Namespace) -> int:
    results = _contract_validation_results()
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


def _command_evidence_chain(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "count": len(EVIDENCE_CHAIN),
                "chain": EVIDENCE_CHAIN,
            },
            sort_keys=True,
        )
    )

    return 0


def _command_readiness(args: argparse.Namespace) -> int:
    contract_results = _contract_validation_results()
    fixture_results = _fixture_directory_results(Path(args.fixtures))

    contracts_valid = all(result["valid"] for result in contract_results)
    fixtures_valid = all(result["valid"] for result in fixture_results)
    evidence_chain_complete = len(EVIDENCE_CHAIN) == len(CONTRACT_SCHEMAS)

    ready = contracts_valid and fixtures_valid and evidence_chain_complete

    print(
        json.dumps(
            {
                "ready": ready,
                "contracts_valid": contracts_valid,
                "contract_count": len(contract_results),
                "fixtures_valid": fixtures_valid,
                "fixture_count": len(fixture_results),
                "evidence_chain_complete": evidence_chain_complete,
                "evidence_chain_count": len(EVIDENCE_CHAIN),
            },
            sort_keys=True,
        )
    )

    return 0 if ready else 2


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

    contracts = subcommands.add_parser(
        "contracts",
        help="List local contract schemas known to the CLI.",
    )
    contracts.set_defaults(func=_command_contracts)

    validate_contracts = subcommands.add_parser(
        "validate-contracts",
        help="Validate all local contract schemas known to the CLI.",
    )
    validate_contracts.set_defaults(func=_command_validate_contracts)

    evidence_chain = subcommands.add_parser(
        "evidence-chain",
        help="Print the expected local evidence chain.",
    )
    evidence_chain.set_defaults(func=_command_evidence_chain)

    readiness = subcommands.add_parser(
        "readiness",
        help="Print local CLI readiness summary.",
    )
    readiness.add_argument(
        "--fixtures",
        default="tests/fixtures/cli",
        help="Local fixture directory to validate.",
    )
    readiness.set_defaults(func=_command_readiness)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return args.func(args)
