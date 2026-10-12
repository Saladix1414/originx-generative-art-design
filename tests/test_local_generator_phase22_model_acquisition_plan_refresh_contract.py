import json
from pathlib import Path

import jsonschema
import pytest

from oxgad.models.acquisition import (
    ModelAcquisitionPlanError,
    build_local_generator_model_acquisition_plan_refresh,
    validate_local_generator_model_acquisition_plan_refresh,
)


def test_model_acquisition_plan_refresh_schema_accepts_payload():
    refresh = build_local_generator_model_acquisition_plan_refresh()
    schema = json.loads(
        Path(
            "schemas/ox-model-acquisition-plan-refresh-1.schema.json"
        ).read_text()
    )

    jsonschema.validate(refresh, schema)
    validate_local_generator_model_acquisition_plan_refresh(refresh)


def test_model_acquisition_plan_refresh_rejects_download_authority():
    refresh = build_local_generator_model_acquisition_plan_refresh()
    refresh["governance"]["downloadAllowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_local_generator_model_acquisition_plan_refresh(refresh)


def test_model_acquisition_plan_refresh_rejects_artifact_presence_claim():
    refresh = build_local_generator_model_acquisition_plan_refresh()
    refresh["availability"]["usableModelArtifactsPresent"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_local_generator_model_acquisition_plan_refresh(refresh)


def test_model_acquisition_plan_refresh_requires_valid_inner_plan():
    refresh = build_local_generator_model_acquisition_plan_refresh()
    refresh["plan"]["state"] = "ACQUIRED"

    with pytest.raises(ModelAcquisitionPlanError):
        validate_local_generator_model_acquisition_plan_refresh(refresh)
