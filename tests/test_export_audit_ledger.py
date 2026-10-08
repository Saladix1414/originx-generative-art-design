import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.quality import (
    append_export_result,
    empty_export_audit_ledger,
    exported_ids,
)


def _result(status="exported"):
    return {
        "schema_version": "ox-local-export-result-1",
        "project": "originx-generative-art-design",
        "phase": "phase18",
        "export_id": "export-0001",
        "status": status,
        "written": {
            "manifest_path": "output/canonical/canonical-0001/manifest.json",
            "artifact_path": "output/canonical/canonical-0001/artifact.png",
        },
    }


def test_export_audit_ledger_matches_schema():
    ledger = append_export_result(
        empty_export_audit_ledger(),
        _result(),
    )

    schema = json.loads(Path("schemas/ox-export-audit-ledger-1.schema.json").read_text())
    jsonschema.validate(ledger, schema)

    assert ledger["schema_version"] == "ox-export-audit-ledger-1"
    assert ledger["entries"][0]["index"] == 0
    assert ledger["entries"][0]["status"] == "exported"


def test_export_audit_ledger_is_append_only_by_returning_new_ledger():
    ledger = empty_export_audit_ledger()
    next_ledger = append_export_result(ledger, _result())

    assert ledger["entries"] == []
    assert len(next_ledger["entries"]) == 1


def test_exported_ids_only_returns_exported_entries():
    ledger = empty_export_audit_ledger()
    ledger = append_export_result(ledger, _result(status="exported"))
    ledger = append_export_result(ledger, _result(status="blocked"))

    assert exported_ids(ledger) == ["export-0001"]


def test_export_audit_ledger_rejects_invalid_schema_version():
    result = _result()
    result["schema_version"] = "wrong"

    with pytest.raises(ValueError, match="schema version"):
        append_export_result(empty_export_audit_ledger(), result)
