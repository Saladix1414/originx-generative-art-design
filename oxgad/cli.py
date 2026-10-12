from __future__ import annotations

import argparse
import importlib.metadata
import json
import jsonschema
from jsonschema import Draft202012Validator
from pathlib import Path
from oxgad.forge.runtime_adapter import build_declared_runtime_adapter, runtime_adapter_hash
from oxgad.forge.runtime_command_plan import (
    build_declared_runtime_command_plan,
    runtime_command_plan_hash,
)
from oxgad.forge.runtime_preflight import (
    build_runtime_preflight_bundle,
)
from oxgad.forge.candidate_dry_run import build_candidate_dry_run, candidate_dry_run_hash
from oxgad.master_prompt.evidence import build_prompt_evidence_chain, verify_prompt_evidence_chain
from typing import Any

from oxgad.models.acquisition import build_local_generator_model_acquisition_plan_refresh
from oxgad.models.artifact_evidence import build_missing_model_artifact_evidence
from oxgad.models.artifact_decision import build_blocked_model_artifact_acquisition_decision
from oxgad.master_prompt import (
    evaluate_master_prompt_quality,
    master_prompt_hash,
)


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
    {
        "step": "master-prompt-chain",
        "schema": "ox-master-prompt-evidence-chain-1.schema.json",
    },
    {
        "step": "candidate-provenance",
        "schema": "ox-candidate-provenance-hook-1.schema.json",
    },
    {
        "step": "candidate-manifest",
        "schema": "ox-candidate-manifest-1.schema.json",
    },
    {
        "step": "candidate-output",
        "schema": "ox-candidate-output-1.schema.json",
    },
    {
        "step": "runtime-adapter",
        "schema": "ox-runtime-adapter-1.schema.json",
    },
    {
        "step": "runtime-command-plan",
        "schema": "ox-runtime-command-plan-1.schema.json",
    },
    {
        "step": "runtime-preflight-bundle",
        "schema": "ox-runtime-preflight-bundle-1.schema.json",
    },
    {
        "step": "model-acquisition-refresh",
        "schema": "ox-model-acquisition-plan-refresh-1.schema.json",
    },
    {
        "step": "model-artifact-evidence",
        "schema": "ox-model-artifact-evidence-1.schema.json",
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
    "master-prompt-chain": "schemas/ox-master-prompt-evidence-chain-1.schema.json",
    "candidate-provenance": "schemas/ox-candidate-provenance-hook-1.schema.json",
    "runtime-adapter": "schemas/ox-runtime-adapter-1.schema.json",
    "runtime-command-plan": "schemas/ox-runtime-command-plan-1.schema.json",
    "runtime-preflight-bundle": "schemas/ox-runtime-preflight-bundle-1.schema.json",
    "model-acquisition-refresh": "schemas/ox-model-acquisition-plan-refresh-1.schema.json",
    "model-artifact-evidence": "schemas/ox-model-artifact-evidence-1.schema.json",
    "candidate-manifest": "schemas/ox-candidate-manifest-1.schema.json",
    "candidate-output": "schemas/ox-candidate-output-1.schema.json",
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



def _master_prompt_chain_ready() -> bool:
    return (
        "master-prompt-chain" in CONTRACT_SCHEMAS
        and any(
            item.get("step") == "master-prompt-chain"
            and item.get("schema")
            == "ox-master-prompt-evidence-chain-1.schema.json"
            for item in EVIDENCE_CHAIN
        )
    )


def _command_readiness(args: argparse.Namespace) -> int:
    contract_results = _contract_validation_results()
    fixture_results = _fixture_directory_results(Path(args.fixtures))

    contracts_valid = all(result["valid"] for result in contract_results)
    fixtures_valid = all(result["valid"] for result in fixture_results)
    evidence_chain_complete = len(EVIDENCE_CHAIN) == len(CONTRACT_SCHEMAS)
    master_prompt_chain_ready = _master_prompt_chain_ready()

    ready = (
        contracts_valid
        and fixtures_valid
        and evidence_chain_complete
        and master_prompt_chain_ready
    )

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
                "master_prompt_chain_ready": master_prompt_chain_ready,
            },
            sort_keys=True,
        )
    )

    return 0 if ready else 2


def _command_version(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "project": "originx-generative-art-design",
                "version": importlib.metadata.version(
                    "originx-generative-art-design"
                ),
            },
            sort_keys=True,
        )
    )

    return 0


def _command_stability(args: argparse.Namespace) -> int:
    parser = build_parser()
    command_names = []

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if choices:
            command_names = sorted(choices)
            break

    print(
        json.dumps(
            {
                "project": "originx-generative-art-design",
                "version": importlib.metadata.version(
                    "originx-generative-art-design"
                ),
                "commands": command_names,
                "command_count": len(command_names),
                "contract_count": len(CONTRACT_SCHEMAS),
                "fixture_count": len(FIXTURE_SCHEMA_MAP),
                "evidence_chain_count": len(EVIDENCE_CHAIN),
                "master_prompt_chain_ready": _master_prompt_chain_ready(),
                "read_only": True,
            },
            sort_keys=True,
        )
    )

    return 0


def _command_prompt_inspect(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)
    controlled = payload.get("controlled_vocabulary", {})
    prompt = payload.get("prompt", {})

    print(
        json.dumps(
            {
                "schema_version": payload.get("schema_version"),
                "prompt_id": payload.get("prompt_id"),
                "render_intent": controlled.get("render_intent"),
                "composition_profile": controlled.get("composition_profile"),
                "trait_family_count": len(controlled.get("trait_families", [])),
                "positive_length": len(str(prompt.get("positive", ""))),
                "negative_length": len(str(prompt.get("negative", ""))),
                "master_prompt_hash": master_prompt_hash(payload),
            },
            sort_keys=True,
        )
    )

    return 0



def _command_prompt_validate(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)
    schema = _load_json("schemas/ox-master-prompt-1.schema.json")

    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as error:
        print(
            json.dumps(
                {
                    "valid": False,
                    "schema_valid": False,
                    "quality_passed": False,
                    "error": error.message,
                },
                sort_keys=True,
            )
        )
        return 2

    quality = evaluate_master_prompt_quality(payload)
    valid = bool(quality["passed"])

    print(
        json.dumps(
            {
                "valid": valid,
                "schema_valid": True,
                "quality_passed": quality["passed"],
                "score": quality["score"],
                "master_prompt_hash": master_prompt_hash(payload),
                "gates": quality["gates"],
            },
            sort_keys=True,
        )
    )

    return 0 if valid else 2



def _command_prompt_chain(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)

    try:
        chain = build_prompt_evidence_chain(payload)
        valid = verify_prompt_evidence_chain(chain)
        chain_schema = _load_json(
            "schemas/ox-master-prompt-evidence-chain-1.schema.json"
        )
        jsonschema.validate(
            chain,
            chain_schema,
        )
    except (KeyError, TypeError, ValueError) as error:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": str(error),
                },
                sort_keys=True,
            )
        )
        return 2

    chain["valid"] = valid
    chain["schema_valid"] = True

    print(
        json.dumps(
            chain,
            sort_keys=True,
        )
    )

    return 0 if valid else 2



def _default_candidate_dry_run_forge_contract() -> dict[str, Any]:
    return {
        "forgeVersion": "OX-LOCAL-FORGE-1",
        "source": {
            "renderPlanVersion": "OX-RENDER-1",
            "renderPlanHash": "sha256:" + "a" * 64,
        },
        "hardware": {
            "profileVersion": "OX-HARDWARE-PROFILE-1",
            "requestedTarget": "LOCAL_CPP",
            "capability": "UNKNOWN",
        },
        "model": {
            "bindingState": "UNBOUND",
        },
        "execution": {
            "policy": "LOCAL_FIRST",
            "mode": "PREPARE_ONLY",
            "authorizationState": "BLOCKED",
            "executionAllowed": False,
        },
        "output": {
            "mediaGenerationAllowed": False,
            "canonicalArtworkAllowed": False,
        },
    }






def _command_model_artifact_decision(args: argparse.Namespace) -> int:
    decision = build_blocked_model_artifact_acquisition_decision()
    print(json.dumps(decision, sort_keys=True))
    return 0

def _command_model_artifact_evidence(args: argparse.Namespace) -> int:
    evidence = build_missing_model_artifact_evidence()
    print(json.dumps(evidence, sort_keys=True))
    return 0

def _command_model_acquisition_plan(args: argparse.Namespace) -> int:
    refresh = build_local_generator_model_acquisition_plan_refresh()
    print(json.dumps(refresh, sort_keys=True))
    return 0

def _command_runtime_preflight(args: argparse.Namespace) -> int:
    adapter = build_declared_runtime_adapter(
        adapter_id=args.adapter_id,
        target=args.target,
        runtime_family=args.runtime_family,
        executable_path=args.executable_path,
        runtime_version=args.runtime_version,
    )
    command_plan = build_declared_runtime_command_plan(adapter)
    bundle = build_runtime_preflight_bundle(
        adapter,
        command_plan,
    )

    print(json.dumps(bundle, sort_keys=True))
    return 0

def _command_runtime_command_plan(args: argparse.Namespace) -> int:
    adapter = build_declared_runtime_adapter(
        adapter_id=args.adapter_id,
        target=args.target,
        runtime_family=args.runtime_family,
        executable_path=args.executable_path,
        runtime_version=args.runtime_version,
    )
    plan = build_declared_runtime_command_plan(adapter)
    plan["runtimeCommandPlanHash"] = runtime_command_plan_hash(plan)

    print(json.dumps(plan, sort_keys=True))
    return 0

def _command_candidate_dry_run(args: argparse.Namespace) -> int:
    dry_run = build_candidate_dry_run(
        candidate_id=args.candidate_id,
        media_path=args.media_path,
        render_plan_hash=args.render_plan_hash,
        forge_contract=_default_candidate_dry_run_forge_contract(),
        model_binding_hash=None,
    )
    dry_run["dryRunHash"] = candidate_dry_run_hash(
        dry_run
    )

    print(
        json.dumps(
            dry_run,
            sort_keys=True,
        )
    )

    return 0



def _command_runtime_adapter(args: argparse.Namespace) -> int:
    adapter = build_declared_runtime_adapter(
        adapter_id=args.adapter_id,
        target=args.target,
        runtime_family=args.runtime_family,
        executable_path=args.executable_path,
        runtime_version=args.runtime_version,
    )
    adapter["runtimeAdapterHash"] = runtime_adapter_hash(
        adapter
    )

    print(
        json.dumps(
            adapter,
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

    version = subcommands.add_parser(
        "version",
        help="Print installed package version.",
    )
    version.set_defaults(func=_command_version)

    stability = subcommands.add_parser(
        "stability",
        help="Print local CLI stability summary.",
    )
    stability.set_defaults(func=_command_stability)

    prompt_inspect = subcommands.add_parser(
        "prompt-inspect",
        help="Inspect a local OX-MASTER-PROMPT-1 payload.",
    )
    prompt_inspect.add_argument("path")
    prompt_inspect.set_defaults(func=_command_prompt_inspect)


    prompt_validate = subcommands.add_parser(
        "prompt-validate",
        help="Validate an OX master prompt payload.",
    )
    prompt_validate.add_argument(
        "path",
        help="Path to an OX-MASTER-PROMPT-1 JSON payload.",
    )
    prompt_validate.set_defaults(
        func=_command_prompt_validate
    )


    prompt_chain = subcommands.add_parser(
        "prompt-chain",
        help="Print the OX master prompt evidence chain.",
    )
    prompt_chain.add_argument(
        "path",
        help="Path to an OX-MASTER-PROMPT-1 JSON payload.",
    )
    prompt_chain.set_defaults(
        func=_command_prompt_chain
    )


    candidate_dry_run = subcommands.add_parser(
        "candidate-dry-run",
        help="Build a prepare-only candidate dry run.",
    )
    candidate_dry_run.add_argument(
        "--candidate-id",
        default="candidate-token-0001-local-001",
        help="Candidate identifier.",
    )
    candidate_dry_run.add_argument(
        "--media-path",
        default="output/candidates/token-0001/candidate-001.png",
        help="Planned candidate media path.",
    )
    candidate_dry_run.add_argument(
        "--render-plan-hash",
        default="sha256:" + "a" * 64,
        help="Render plan hash to bind into the dry run.",
    )
    candidate_dry_run.set_defaults(
        func=_command_candidate_dry_run
    )


    runtime_adapter = subcommands.add_parser(
        "runtime-adapter",
        help="Print the declared local runtime adapter.",
    )
    runtime_adapter.add_argument(
        "--adapter-id",
        default="originx.local_cpp.stable_diffusion_cpp",
        help="Runtime adapter identifier.",
    )
    runtime_adapter.add_argument(
        "--target",
        default="LOCAL_CPP",
        choices=["LOCAL_CPP", "LOCAL_GPU"],
        help="Runtime target.",
    )
    runtime_adapter.add_argument(
        "--runtime-family",
        default="stable-diffusion.cpp",
        choices=["stable-diffusion.cpp", "unknown"],
        help="Runtime family.",
    )
    runtime_adapter.add_argument(
        "--executable-path",
        default=None,
        help="Declared executable path. This is not invoked.",
    )
    runtime_adapter.add_argument(
        "--runtime-version",
        default=None,
        help="Declared runtime version.",
    )
    runtime_adapter.set_defaults(
        func=_command_runtime_adapter
    )


    runtime_command_plan_parser = subcommands.add_parser(
        "runtime-command-plan",
        help="Emit declared local runtime command plan.",
    )
    runtime_command_plan_parser.add_argument(
        "--adapter-id",
        default="originx.local.declared-runtime",
    )
    runtime_command_plan_parser.add_argument(
        "--target",
        default="LOCAL_CPP",
        choices=["LOCAL_CPP", "LOCAL_GPU"],
    )
    runtime_command_plan_parser.add_argument(
        "--runtime-family",
        default="stable-diffusion.cpp",
    )
    runtime_command_plan_parser.add_argument(
        "--executable-path",
        default=None,
    )
    runtime_command_plan_parser.add_argument(
        "--runtime-version",
        default=None,
    )
    runtime_command_plan_parser.set_defaults(
        func=_command_runtime_command_plan
    )


    runtime_preflight = subcommands.add_parser(
        "runtime-preflight",
        help="Emit blocked local runtime preflight bundle.",
    )
    runtime_preflight.add_argument(
        "--adapter-id",
        default="originx.local_cpp.stable_diffusion_cpp",
        help="Runtime adapter identifier.",
    )
    runtime_preflight.add_argument(
        "--target",
        default="LOCAL_CPP",
        choices=["LOCAL_CPP", "LOCAL_GPU"],
        help="Runtime target.",
    )
    runtime_preflight.add_argument(
        "--runtime-family",
        default="stable-diffusion.cpp",
        choices=["stable-diffusion.cpp", "unknown"],
        help="Runtime family.",
    )
    runtime_preflight.add_argument(
        "--executable-path",
        default=None,
        help="Declared executable path. This is not invoked.",
    )
    runtime_preflight.add_argument(
        "--runtime-version",
        default=None,
        help="Declared runtime version.",
    )
    runtime_preflight.set_defaults(
        func=_command_runtime_preflight
    )


    model_acquisition_plan = subcommands.add_parser(
        "model-acquisition-plan",
        help="Print declared local model acquisition plan refresh.",
    )
    model_acquisition_plan.set_defaults(
        func=_command_model_acquisition_plan
    )


    model_artifact_evidence = subcommands.add_parser(
        "model-artifact-evidence",
        help="Print missing local model artifact evidence.",
    )
    model_artifact_evidence.set_defaults(
        func=_command_model_artifact_evidence
    )


    model_artifact_decision = subcommands.add_parser(
        "model-artifact-decision",
        help="Print blocked local model artifact acquisition decision.",
    )
    model_artifact_decision.set_defaults(
        func=_command_model_artifact_decision
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return args.func(args)
