from oxgad.models.acquisition import (
    MODEL_ACQUISITION_PLAN_REFRESH_VERSION,
    build_local_generator_model_acquisition_plan_refresh,
)


def test_model_acquisition_plan_refresh_is_declared_not_acquired():
    refresh = build_local_generator_model_acquisition_plan_refresh()

    assert refresh["refreshVersion"] == (
        MODEL_ACQUISITION_PLAN_REFRESH_VERSION
    )
    assert refresh["state"] == "DECLARED_NOT_ACQUIRED"
    assert refresh["plan"]["planVersion"] == "OX-MODEL-ACQUISITION-PLAN-1"
    assert refresh["plan"]["state"] == "DECLARED_NOT_ACQUIRED"

    assert refresh["availability"] == {
        "usableModelArtifactsPresent": False,
        "artifactPathBound": False,
        "artifactHashObserved": False,
        "artifactSizeObserved": False,
    }

    assert refresh["governance"] == {
        "downloadAllowed": False,
        "installationAllowed": False,
        "executionAllowed": False,
        "mediaGenerationAllowed": False,
        "refreshGrantsAcquisitionAuthority": False,
        "refreshGrantsExecutionAuthority": False,
    }


def test_model_acquisition_plan_refresh_preserves_existing_model_identity():
    refresh = build_local_generator_model_acquisition_plan_refresh()
    plan = refresh["plan"]

    assert plan["model"]["modelId"] == "originx.sd15.emaonly"
    assert plan["model"]["family"] == "stable-diffusion-1"
    assert plan["runtimeIntent"]["runtimeFamily"] == "stable-diffusion.cpp"
    assert plan["runtimeIntent"]["requestedTarget"] == "LOCAL_CPP"


def test_model_acquisition_plan_refresh_does_not_grant_generation():
    refresh = build_local_generator_model_acquisition_plan_refresh()

    assert refresh["governance"]["downloadAllowed"] is False
    assert refresh["governance"]["installationAllowed"] is False
    assert refresh["governance"]["executionAllowed"] is False
    assert refresh["governance"]["mediaGenerationAllowed"] is False
